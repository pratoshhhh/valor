"""
ValorStream Cloud Functions
Main entry point for all serverless functions
"""

import functions_framework
from flask import jsonify
import json
import os
from google.cloud import firestore

# Import our modules
from event_processor import EventProcessor
from ai_analyzer import AIAnalyzer
from report_generator import ReportGenerator
from confluent_metrics import ConfluentMetrics

# Initialize clients
db = firestore.Client()
event_processor = EventProcessor(db)
ai_analyzer = AIAnalyzer()
report_generator = ReportGenerator(db)
confluent_metrics = ConfluentMetrics()

@functions_framework.http
def get_confluent_metrics(request):
    """HTTP endpoint to get Confluent Cloud metrics"""
    try:
        metric_type = request.args.get('type', 'health')
        
        if metric_type == 'cluster':
            metrics = confluent_metrics.get_cluster_metrics()
        elif metric_type == 'topics':
            metrics = confluent_metrics.get_all_topics_metrics()
        elif metric_type == 'consumers':
            metrics = confluent_metrics.get_consumer_groups_metrics()
        elif metric_type == 'health':
            metrics = confluent_metrics.get_health_status()
        else:
            return jsonify({'error': 'Invalid metric type'}), 400
        
        return jsonify({
            'status': 'success',
            'data': metrics
        }), 200
        
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return jsonify({'error': str(e)}), 500

@functions_framework.http
def ingest_events(request):
    """HTTP endpoint to receive events from Confluent HTTP Sink Connector"""
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return jsonify({'error': 'No data provided'}), 400
        
        events = request_json if isinstance(request_json, list) else [request_json]
        
        processed_count = 0
        errors = []
        
        for event in events:
            try:
                result = event_processor.process_event(event)
                
                if result['success']:
                    processed_count += 1
                    
                    if event.get('severity') in ['HIGH', 'CRITICAL']:
                        event_processor.create_health_alert(event)
                else:
                    errors.append({
                        'event_id': event.get('event_id'),
                        'error': result.get('error')
                    })
                    
            except Exception as e:
                errors.append({
                    'event_id': event.get('event_id'),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'processed': processed_count,
            'total': len(events),
            'errors': errors
        }), 200
        
    except Exception as e:
        print(f"Error in ingest_events: {e}")
        return jsonify({'error': str(e)}), 500


@functions_framework.http
def generate_va_report(request):
    """Generate VA benefits report for a soldier using AI analysis"""
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json or 'soldier_id' not in request_json:
            return jsonify({'error': 'soldier_id required'}), 400
        
        soldier_id = request_json['soldier_id']
        
        # Get soldier's events
        events = event_processor.get_soldier_events(soldier_id)
        
        if not events:
            return jsonify({'error': 'No events found for soldier'}), 404
        
        # Analyze with AI
        print(f"Analyzing {len(events)} events for {soldier_id}...")
        analysis = ai_analyzer.analyze_deployment(soldier_id, events)
        
        # Generate PDF report
        print("Generating PDF report...")
        report_url, report_id = report_generator.generate_pdf_report(
            soldier_id, 
            events, 
            analysis
        )
        
        # Store report metadata
        db.collection('va_reports').document(report_id).set({
            'soldier_id': soldier_id,
            'report_url': report_url,
            'generated_at': firestore.SERVER_TIMESTAMP,
            'event_count': len(events),
            'analysis_summary': analysis.get('summary', '')
        })
        
        return jsonify({
            'status': 'success',
            'report_url': report_url,
            'report_id': report_id,
            'event_count': len(events)
        }), 200
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500


@functions_framework.http
def get_soldier_summary(request):
    """Get aggregated summary for a soldier"""
    try:
        soldier_id = request.args.get('soldier_id')
        
        if not soldier_id:
            return jsonify({'error': 'soldier_id parameter required'}), 400
        
        summary_doc = db.collection('soldier_summaries').document(soldier_id).get()
        
        if not summary_doc.exists:
            return jsonify({'error': 'Soldier not found'}), 404
        
        return jsonify(summary_doc.to_dict()), 200
        
    except Exception as e:
        print(f"Error fetching summary: {e}")
        return jsonify({'error': str(e)}), 500
