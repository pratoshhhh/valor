"""
ValorStream Cloud Functions
Main entry point for all serverless functions
"""

import functions_framework
from flask import jsonify
import json
import os
from google.cloud import firestore, storage
import google.generativeai as genai
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
import io

# Import our modules
from event_processor import EventProcessor
from ai_analyzer import AIAnalyzer
from report_generator import ReportGenerator
from confluent_metrics import ConfluentMetrics

# Initialize clients
db = firestore.Client()
storage_client = storage.Client()
event_processor = EventProcessor(db)
ai_analyzer = AIAnalyzer()
report_generator = ReportGenerator(db)
confluent_metrics = ConfluentMetrics()

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured")
else:
    print("⚠️  Warning: GEMINI_API_KEY not set. AI analysis will use mock data.")

def add_cors_headers(response):
    """Add CORS headers to allow frontend access"""
    headers = {
        'Access-Control-Allow-Origin': '*',  # Change to your domain in production: 'https://your-domain.com'
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '3600'
    }
    
    # If response is a tuple, add headers
    if isinstance(response, tuple):
        return (response[0], response[1], headers)
    
    # If response is a Response object
    if hasattr(response, 'headers'):
        for key, value in headers.items():
            response.headers[key] = value
        return response
    
    # Otherwise return with headers
    return (response, 200, headers)


# API Key Authentication (OPTIONAL - uncomment to enable)
def verify_api_key(request):
    """
    Verify API key from request headers
    Uncomment this function and the checks below to enable authentication
    """
    # Get API key from environment variable
    VALID_API_KEY = os.environ.get('API_KEY', 'your-secret-api-key-here')
    
    # Get API key from request header
    request_api_key = request.headers.get('Authorization', '')
    
    # Remove 'Bearer ' prefix if present
    if request_api_key.startswith('Bearer '):
        request_api_key = request_api_key[7:]
    
    # Verify API key
    if request_api_key != VALID_API_KEY:
        return False
    
    return True

@functions_framework.http
def get_health_alerts(request):
    """Get all health alerts from Firestore"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    try:
        # SIMPLE QUERY - No filtering, no sorting
        alerts_ref = db.collection('health_alerts')
        docs = alerts_ref.stream()
        
        alerts = []
        for doc in docs:
            alert_data = doc.to_dict()
            alert_data['id'] = doc.id
            alerts.append(alert_data)
        
        # Add CORS headers
        headers = {'Access-Control-Allow-Origin': '*'}
        
        return (jsonify({
            'status': 'success',
            'alerts': alerts,
            'count': len(alerts)
        }), 200, headers)
        
    except Exception as e:
        print(f"Error fetching alerts: {str(e)}")
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({
            'status': 'error',
            'error': str(e),
            'alerts': [],
            'count': 0
        }), 500, headers)
    
@functions_framework.http
def resolve_alert(request):
    """Mark a health alert as resolved"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, PUT',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json or 'alert_id' not in request_json:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'alert_id required'}), 400, headers)
        
        alert_id = request_json['alert_id']
        resolution_notes = request_json.get('notes', '')
        resolved_by = request_json.get('resolved_by', 'System')
        
        # Update the alert
        alert_ref = db.collection('health_alerts').document(alert_id)
        alert_doc = alert_ref.get()
        
        if not alert_doc.exists:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'Alert not found'}), 404, headers)
        
        alert_ref.update({
            'status': 'resolved',
            'resolved_at': firestore.SERVER_TIMESTAMP,
            'resolved_by': resolved_by,
            'resolution_notes': resolution_notes
        })
        
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({
            'status': 'success',
            'message': 'Alert resolved',
            'alert_id': alert_id
        }), 200, headers)
        
    except Exception as e:
        print(f"Error resolving alert: {e}")
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({'error': str(e)}), 500, headers)

@functions_framework.http
def get_confluent_metrics(request):
    """HTTP endpoint to get Confluent Cloud metrics"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
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
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'Invalid metric type'}), 400, headers)
        
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({
            'status': 'success',
            'data': metrics
        }), 200, headers)
        
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({'error': str(e)}), 500, headers)

@functions_framework.http
def ingest_events(request):
    """HTTP endpoint to receive events from Confluent HTTP Sink Connector"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'No data provided'}), 400, headers)
        
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
        
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({
            'status': 'success',
            'processed': processed_count,
            'total': len(events),
            'errors': errors
        }), 200, headers)
        
    except Exception as e:
        print(f"Error in ingest_events: {e}")
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({'error': str(e)}), 500, headers)


@functions_framework.http
def generate_va_report(request):
    """
    Generate VA report for a soldier using Gemini AI
    ENHANCED VERSION with Gemini AI and PDF generation
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    try:
        # Get request data
        request_data = request.get_json()
        soldier_id = request_data.get('soldier_id')
        
        if not soldier_id:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'soldier_id is required'}), 400, headers)
        
        print(f"📄 Generating VA report for {soldier_id}...")
        
        # Get soldier data
        soldier_ref = db.collection('soldiers').document(soldier_id)
        soldier_doc = soldier_ref.get()
        
        if not soldier_doc.exists:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'Soldier not found'}), 404, headers)
        
        soldier_data = soldier_doc.to_dict()
        soldier_data['soldier_id'] = soldier_id
        
        # Get soldier's health alerts
        alerts_ref = db.collection('health_alerts').where('soldier_id', '==', soldier_id)
        alerts = [doc.to_dict() for doc in alerts_ref.stream()]
        
        print(f"📊 Found {len(alerts)} health alerts for {soldier_id}")
        
        # Generate AI analysis
        ai_analysis = generate_gemini_analysis(soldier_data, alerts)
        
        # Create PDF
        pdf_buffer = create_va_pdf_report(soldier_data, alerts, ai_analysis)
        
        # Upload to Cloud Storage
        report_url = upload_report_to_storage(pdf_buffer, soldier_id)
        
        # Save report metadata to Firestore
        report_id = save_va_report_metadata(soldier_id, report_url, ai_analysis)
        
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({
            'status': 'success',
            'soldier_id': soldier_id,
            'report_url': report_url,
            'report_id': report_id,
            'generated_at': datetime.utcnow().isoformat(),
            'analysis_summary': ai_analysis.get('summary', ''),
            'event_count': len(alerts)
        }), 200, headers)
        
    except Exception as e:
        print(f"❌ Error generating VA report: {str(e)}")
        import traceback
        traceback.print_exc()
        
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({
            'status': 'error',
            'error': str(e)
        }), 500, headers)


def generate_gemini_analysis(soldier_data, alerts):
    """
    Use Gemini AI to analyze soldier's health data
    """
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY not set. Using mock analysis.")
        return {
            'summary': f"Soldier {soldier_data.get('name', 'Unknown')} has {len(alerts)} documented health events requiring medical evaluation and potential VA claim consideration.",
            'risk_level': 'MODERATE',
            'recommendations': [
                'Complete comprehensive medical evaluation with VA healthcare provider',
                'Document all symptoms and their impact on daily activities',
                'Gather supporting evidence including service records and buddy statements',
                'File VA disability claim within one year of separation',
                'Consider legal assistance from Veterans Service Organization (VSO)'
            ],
            'exposure_summary': f"Documented {len(alerts)} health events during deployment including exposure to combat-related hazards.",
            'service_connection': 'Multiple potential service-connected conditions identified. Recommend thorough medical nexus evaluation to establish connection between service and current health status.'
        }
    
    try:
        # Prepare data for AI analysis
        name = soldier_data.get('name', 'Unknown')
        rank = soldier_data.get('rank', 'Unknown')
        deployment = soldier_data.get('deployment_location', 'Unknown')
        health_score = soldier_data.get('health_score', 0)
        unit = soldier_data.get('unit', 'Unknown')
        
        # Summarize alerts
        critical_count = len([a for a in alerts if a.get('severity') == 'CRITICAL'])
        high_count = len([a for a in alerts if a.get('severity') == 'HIGH'])
        medium_count = len([a for a in alerts if a.get('severity') == 'MEDIUM'])
        event_types = list(set([a.get('event_type', 'Unknown') for a in alerts]))
        
        # Create prompt for Gemini
        prompt = f"""You are a VA (Veterans Affairs) medical analyst specializing in service-connected disability claims. Analyze this soldier's health data to help prepare a comprehensive VA disability claim report.

SOLDIER INFORMATION:
- Name: {name}
- Rank: {rank}
- Unit: {unit}
- Deployment Location: {deployment}
- Current Health Score: {health_score}/100
- Total Health Events: {len(alerts)}
- Critical Events: {critical_count}
- High Severity Events: {high_count}
- Medium Severity Events: {medium_count}
- Event Types: {', '.join(event_types)}

RECENT HEALTH EVENTS:
{format_alerts_for_gemini(alerts[:15])}

Based on this data, provide a thorough analysis for VA claim purposes:

1. SUMMARY: A concise medical summary (2-3 sentences) highlighting the most significant health concerns and their potential service connection.

2. RISK LEVEL: Overall health risk assessment. Choose ONE: LOW, MODERATE, HIGH, or CRITICAL

3. RECOMMENDATIONS: Provide 4-6 specific, actionable recommendations for:
   - Medical evaluations needed
   - Documentation to gather
   - VA claim filing steps
   - Specialists to consult
   - Support resources

4. EXPOSURE SUMMARY: Detailed summary of environmental, combat, and occupational exposures documented in the health events. Be specific about burn pits, blast exposures, toxic substances, etc.

5. SERVICE CONNECTION: Analysis of potential service-connected conditions based on the documented exposures. List specific conditions that may qualify for VA disability rating.

Format your response as valid JSON with these exact keys: summary, risk_level, recommendations (array of strings), exposure_summary, service_connection

Ensure the JSON is properly formatted and can be parsed."""

        print("🤖 Calling Gemini AI for analysis...")
        
        # Call Gemini API
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        print("✅ Received Gemini response")
        
        # Parse AI response
        analysis_text = response.text
        
        # Try to extract JSON from response
        import re
        
        # Remove markdown code blocks if present
        analysis_text = re.sub(r'```json\s*', '', analysis_text)
        analysis_text = re.sub(r'```\s*', '', analysis_text)
        
        # Look for JSON in the response
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            print("✅ Successfully parsed Gemini JSON response")
        else:
            print("⚠️  Could not parse JSON from Gemini response, using fallback")
            # Fallback: parse as text
            analysis = {
                'summary': analysis_text[:300] if len(analysis_text) > 300 else analysis_text,
                'risk_level': 'MODERATE',
                'recommendations': [
                    'Complete comprehensive medical evaluation',
                    'File VA disability claim',
                    'Gather supporting documentation',
                    'Consult with Veterans Service Organization (VSO)'
                ],
                'exposure_summary': f"Documented {len(alerts)} health events during deployment",
                'service_connection': 'Medical review required for service connection determination'
            }
        
        return analysis
        
    except Exception as e:
        print(f"⚠️  AI analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'summary': f"Soldier has {len(alerts)} documented health events. AI analysis temporarily unavailable - manual review recommended.",
            'risk_level': 'MODERATE',
            'recommendations': [
                'Complete medical evaluation with VA provider',
                'Consult VA representative for claim filing',
                'Document all symptoms in detail',
                'Gather service records and evidence'
            ],
            'exposure_summary': f"{len(alerts)} documented health events including {', '.join(event_types[:3])}",
            'service_connection': 'Requires detailed medical review for service connection determination'
        }


def format_alerts_for_gemini(alerts):
    """Format alerts for Gemini AI prompt"""
    formatted = []
    for i, alert in enumerate(alerts, 1):
        event_type = alert.get('event_type', 'Unknown')
        severity = alert.get('severity', 'Unknown')
        timestamp = alert.get('timestamp', 'Unknown')
        details = alert.get('details', {})
        
        formatted.append(f"{i}. {event_type} ({severity}) - {timestamp}")
        if details:
            # Format details nicely
            detail_str = ', '.join([f"{k}: {v}" for k, v in details.items() if k != 'description'])
            if detail_str:
                formatted.append(f"   {detail_str}")
    
    return '\n'.join(formatted)


def create_va_pdf_report(soldier_data, alerts, ai_analysis):
    """
    Create professional PDF report using ReportLab
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=1  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title Page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("VALOR Health Monitoring System", title_style))
    story.append(Paragraph("Veterans Affairs Disability Claim Report", heading_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Soldier Information Section
    story.append(Paragraph("I. Soldier Information", heading_style))
    soldier_info = [
        ['Field', 'Value'],
        ['Name:', soldier_data.get('name', 'N/A')],
        ['Rank:', soldier_data.get('rank', 'N/A')],
        ['Soldier ID:', soldier_data.get('soldier_id', 'N/A')],
        ['Unit:', soldier_data.get('unit', 'N/A')],
        ['Deployment Location:', soldier_data.get('deployment_location', 'N/A')],
        ['Current Health Score:', f"{soldier_data.get('health_score', 0)}/100"],
        ['Status:', soldier_data.get('status', 'N/A').upper()]
    ]
    t = Table(soldier_info, colWidths=[2.5*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*inch))
    
    # AI Medical Analysis Section
    story.append(Paragraph("II. Medical Analysis (AI-Generated)", heading_style))
    
    # Summary
    summary_text = ai_analysis.get('summary', 'N/A')
    story.append(Paragraph(f"<b>Executive Summary:</b>", styles['BodyText']))
    story.append(Paragraph(summary_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Risk Level
    risk_level = ai_analysis.get('risk_level', 'MODERATE')
    risk_color = {
        'CRITICAL': '#d32f2f',
        'HIGH': '#f57c00',
        'MODERATE': '#fbc02d',
        'LOW': '#388e3c'
    }.get(risk_level, '#666666')
    
    story.append(Paragraph(f"<b>Risk Level:</b> <font color='{risk_color}'><b>{risk_level}</b></font>", styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    recommendations = ai_analysis.get('recommendations', [])
    if recommendations:
        story.append(Paragraph("<b>Recommendations for VA Claim:</b>", styles['BodyText']))
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
    
    # Exposure Summary
    exposure_summary = ai_analysis.get('exposure_summary', 'N/A')
    story.append(Paragraph("<b>Documented Exposures:</b>", styles['BodyText']))
    story.append(Paragraph(exposure_summary, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Service Connection
    service_connection = ai_analysis.get('service_connection', 'N/A')
    story.append(Paragraph("<b>Service Connection Analysis:</b>", styles['BodyText']))
    story.append(Paragraph(service_connection, styles['BodyText']))
    story.append(Spacer(1, 0.4*inch))
    
    # Health Events Summary Section
    story.append(Paragraph(f"III. Health Events Summary ({len(alerts)} Total Events)", heading_style))
    
    # Count by severity
    critical_alerts = [a for a in alerts if a.get('severity') == 'CRITICAL']
    high_alerts = [a for a in alerts if a.get('severity') == 'HIGH']
    medium_alerts = [a for a in alerts if a.get('severity') == 'MEDIUM']
    low_alerts = [a for a in alerts if a.get('severity') == 'LOW']
    
    summary_data = [
        ['Severity Level', 'Event Count', 'Percentage'],
        ['CRITICAL', str(len(critical_alerts)), f"{(len(critical_alerts)/len(alerts)*100):.1f}%" if alerts else "0%"],
        ['HIGH', str(len(high_alerts)), f"{(len(high_alerts)/len(alerts)*100):.1f}%" if alerts else "0%"],
        ['MEDIUM', str(len(medium_alerts)), f"{(len(medium_alerts)/len(alerts)*100):.1f}%" if alerts else "0%"],
        ['LOW', str(len(low_alerts)), f"{(len(low_alerts)/len(alerts)*100):.1f}%" if alerts else "0%"],
        ['TOTAL', str(len(alerts)), '100%']
    ]
    
    t2 = Table(summary_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.4*inch))
    
    # Critical Events Detail
    if critical_alerts or high_alerts:
        story.append(Paragraph("IV. Critical and High-Severity Events", heading_style))
        
        important_alerts = critical_alerts + high_alerts
        important_alerts = sorted(important_alerts, 
                                 key=lambda x: x.get('timestamp', ''), 
                                 reverse=True)[:10]  # Show top 10
        
        for i, alert in enumerate(important_alerts, 1):
            severity_color = '#d32f2f' if alert.get('severity') == 'CRITICAL' else '#f57c00'
            
            event_text = f"<b>{i}. {alert.get('event_type', 'Unknown Event')}</b>"
            story.append(Paragraph(event_text, styles['BodyText']))
            
            details_list = [
                f"<font color='{severity_color}'><b>Severity: {alert.get('severity', 'N/A')}</b></font>",
                f"Timestamp: {alert.get('timestamp', 'N/A')}",
                f"Location: {alert.get('location', 'N/A')}"
            ]
            
            # Add specific details if available
            if 'details' in alert and isinstance(alert['details'], dict):
                for key, value in alert['details'].items():
                    if key != 'description' and value is not None:
                        details_list.append(f"{key.replace('_', ' ').title()}: {value}")
            
            story.append(Paragraph(' | '.join(details_list), styles['Normal']))
            
            # Add description if available
            if 'details' in alert and isinstance(alert['details'], dict):
                desc = alert['details'].get('description', '')
                if desc:
                    story.append(Paragraph(f"<i>{desc}</i>", styles['Normal']))
            
            story.append(Spacer(1, 0.15*inch))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("_" * 100, styles['Normal']))
    story.append(Paragraph(
        "<i>This report was generated by the VALOR Health Monitoring System using AI-assisted analysis. "
        "It is intended to support VA disability claim documentation and should be reviewed by qualified "
        "medical professionals. This report does not constitute a medical diagnosis.</i>",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def upload_report_to_storage(pdf_buffer, soldier_id):
    """
    Upload PDF to Google Cloud Storage
    """
    try:
        bucket_name = os.environ.get('GCS_BUCKET_NAME', 'valorstream-reports')
        
        print(f"📤 Uploading report to bucket: {bucket_name}")
        
        bucket = storage_client.bucket(bucket_name)
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        blob_name = f"va_reports/{soldier_id}_{timestamp}.pdf"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_file(pdf_buffer, content_type='application/pdf')
        
        # Make public (for easy access - change to signed URLs for production)
        blob.make_public()
        
        print(f"✅ Report uploaded successfully: {blob.public_url}")
        
        return blob.public_url
        
    except Exception as e:
        print(f"⚠️  Storage upload error: {e}")
        # Return mock URL if storage fails
        return f"https://storage.googleapis.com/valorstream-reports/va_reports/{soldier_id}_mock.pdf"


def save_va_report_metadata(soldier_id, report_url, ai_analysis):
    """
    Save report metadata to Firestore
    """
    try:
        report_ref = db.collection('va_reports').document()
        report_id = report_ref.id
        
        report_ref.set({
            'soldier_id': soldier_id,
            'report_url': report_url,
            'generated_at': firestore.SERVER_TIMESTAMP,
            'risk_level': ai_analysis.get('risk_level'),
            'summary': ai_analysis.get('summary'),
            'status': 'completed',
            'report_id': report_id
        })
        
        print(f"✅ Report metadata saved to Firestore: {report_id}")
        
        return report_id
        
    except Exception as e:
        print(f"⚠️  Error saving report metadata: {e}")
        return f"report_{soldier_id}_{datetime.utcnow().timestamp()}"


@functions_framework.http
def get_soldier_summary(request):
    """Get aggregated summary for a soldier"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    try:
        soldier_id = request.args.get('soldier_id')
        
        if not soldier_id:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'soldier_id parameter required'}), 400, headers)
        
        # Try soldier_summaries collection first
        summary_doc = db.collection('soldier_summaries').document(soldier_id).get()
        
        if summary_doc.exists:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify(summary_doc.to_dict()), 200, headers)
        
        # Fallback: get from soldiers collection
        soldier_doc = db.collection('soldiers').document(soldier_id).get()
        
        if not soldier_doc.exists:
            headers = {'Access-Control-Allow-Origin': '*'}
            return (jsonify({'error': 'Soldier not found'}), 404, headers)
        
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify(soldier_doc.to_dict()), 200, headers)
        
    except Exception as e:
        print(f"Error fetching summary: {e}")
        headers = {'Access-Control-Allow-Origin': '*'}
        return (jsonify({'error': str(e)}), 500, headers)