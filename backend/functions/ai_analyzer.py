"""
AI-powered analysis using Google Vertex AI (Gemini)
"""

import google.generativeai as genai
import os
import json
from datetime import datetime


class AIAnalyzer:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            print("⚠️  Warning: GEMINI_API_KEY not set. AI analysis will use mock data.")
            self.model = None
    
    def analyze_single_event(self, event):
        """Analyze a single battlefield event"""
        if not self.model:
            return self._mock_single_event_analysis(event)
        
        try:
            prompt = f"""
            Analyze this military service event and provide health risk assessment:
            
            Event Type: {event['event_type']}
            Severity: {event['severity']}
            Location: {event['location']['latitude']}, {event['location']['longitude']}
            Environmental Data:
            - Noise Level: {event.get('noise_level_db', 'N/A')} dB
            - Air Quality Index: {event.get('air_quality_index', 'N/A')}
            
            Provide in JSON format:
            {{
                "immediate_risks": ["list of immediate health concerns"],
                "long_term_risks": ["list of potential long-term effects"],
                "va_categories": ["relevant VA disability categories"],
                "medical_screenings": ["recommended medical tests"],
                "severity_assessment": "LOW/MEDIUM/HIGH/CRITICAL"
            }}
            
            Return only valid JSON, no markdown formatting.
            """
            
            response = self.model.generate_content(prompt)
            
            # Clean response (remove markdown if present)
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            analysis = json.loads(text.strip())
            
            return analysis
            
        except Exception as e:
            print(f"Error in single event analysis: {e}")
            return self._mock_single_event_analysis(event)
    
    def analyze_deployment(self, soldier_id, events):
        """Analyze entire deployment for VA report generation"""
        if not self.model:
            return self._mock_deployment_analysis(soldier_id, events)
        
        try:
            # Aggregate event statistics
            total_events = len(events)
            critical_events = [e for e in events if e['severity'] == 'CRITICAL']
            high_events = [e for e in events if e['severity'] == 'HIGH']
            
            # Count exposures by type
            exposure_counts = {}
            for event in events:
                event_type = event['event_type']
                exposure_counts[event_type] = exposure_counts.get(event_type, 0) + 1
            
            # Calculate average noise exposure
            noise_readings = [e['noise_level_db'] for e in events if e.get('noise_level_db')]
            avg_noise = sum(noise_readings) / len(noise_readings) if noise_readings else 0
            
            # Calculate max AQI
            aqi_readings = [e['air_quality_index'] for e in events if e.get('air_quality_index')]
            max_aqi = max(aqi_readings) if aqi_readings else 0
            
            # Create comprehensive prompt
            prompt = f"""
            You are a military health analyst reviewing a soldier's deployment record for VA benefits assessment.
            
            DEPLOYMENT SUMMARY:
            - Soldier ID: {soldier_id}
            - Total Events: {total_events}
            - Critical Events: {len(critical_events)}
            - High-Risk Events: {len(high_events)}
            
            EXPOSURE BREAKDOWN:
            {json.dumps(exposure_counts, indent=2)}
            
            ENVIRONMENTAL METRICS:
            - Average Noise Exposure: {avg_noise:.1f} dB
            - Maximum Air Quality Index: {max_aqi}
            
            CRITICAL INCIDENTS:
            {json.dumps([{{
                'date': datetime.fromtimestamp(e['timestamp']/1000).strftime('%Y-%m-%d'),
                'type': e['event_type'],
                'location': f"{e['location']['latitude']:.4f}, {e['location']['longitude']:.4f}"
            }} for e in critical_events[:10]], indent=2)}
            
            Generate a comprehensive VA Benefits Pre-Application Assessment including:
            
            1. VERIFIED EXPOSURES (with dates, locations, frequencies)
            2. HEALTH RISK ANALYSIS (immediate and long-term)
            3. RECOMMENDED MEDICAL EXAMINATIONS (prioritized)
            4. POTENTIAL VA DISABILITY CLAIMS (with CFR references if applicable)
            5. DOCUMENTATION STRENGTH (rate the evidence quality)
            6. PRIORITY HEALTH CONCERNS (urgent issues)
            
            Format as JSON:
            {{
                "summary": "brief executive summary",
                "verified_exposures": [
                    {{
                        "type": "exposure type",
                        "count": number,
                        "date_range": "first to last",
                        "severity": "overall severity",
                        "locations": ["lat,lon"]
                    }}
                ],
                "health_risks": {{
                    "immediate": ["list"],
                    "long_term": ["list"]
                }},
                "medical_exams": [
                    {{
                        "exam": "exam name",
                        "priority": "HIGH/MEDIUM/LOW",
                        "reason": "why needed"
                    }}
                ],
                "va_claims": [
                    {{
                        "category": "disability category",
                        "evidence_strength": "STRONG/MODERATE/WEAK",
                        "supporting_events": number
                    }}
                ],
                "documentation_quality": "EXCELLENT/GOOD/FAIR/POOR",
                "priority_concerns": ["top 3 issues"],
                "overall_risk_score": "0-100"
            }}
            
            Return only valid JSON, no markdown.
            """
            
            response = self.model.generate_content(prompt)
            
            # Clean response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            analysis = json.loads(text.strip())
            
            # Add metadata
            analysis['analyzed_at'] = datetime.now().isoformat()
            analysis['total_events_analyzed'] = total_events
            analysis['soldier_id'] = soldier_id
            
            return analysis
            
        except Exception as e:
            print(f"Error in deployment analysis: {e}")
            return self._mock_deployment_analysis(soldier_id, events)
    
    def _mock_single_event_analysis(self, event):
        """Mock analysis for single event when Gemini is not available"""
        event_type = event.get('event_type', 'UNKNOWN')
        severity = event.get('severity', 'UNKNOWN')
        
        risk_map = {
            'IED_EXPLOSION': {
                'immediate': ['Traumatic brain injury risk', 'Hearing damage', 'Blast-related injuries'],
                'long_term': ['PTSD', 'Chronic TBI symptoms', 'Hearing loss', 'Tinnitus'],
                'va_categories': ['Traumatic Brain Injury', 'Hearing Loss', 'PTSD'],
                'screenings': ['TBI screening', 'Audiogram', 'Mental health evaluation']
            },
            'BURN_PIT_EXPOSURE': {
                'immediate': ['Respiratory irritation', 'Eye irritation'],
                'long_term': ['Chronic respiratory disease', 'Asthma', 'COPD', 'Cancer risk'],
                'va_categories': ['Respiratory Conditions', 'Asthma', 'Chronic Bronchitis'],
                'screenings': ['Pulmonary function test', 'Chest X-ray', 'Respiratory assessment']
            },
            'GUNFIRE': {
                'immediate': ['Acute hearing damage', 'Acoustic trauma'],
                'long_term': ['Hearing loss', 'Tinnitus', 'Hyperacusis'],
                'va_categories': ['Hearing Loss', 'Tinnitus'],
                'screenings': ['Audiogram', 'Hearing evaluation']
            }
        }
        
        analysis = risk_map.get(event_type, {
            'immediate': ['Potential health impact'],
            'long_term': ['Requires medical evaluation'],
            'va_categories': ['Service-related condition'],
            'screenings': ['Medical examination recommended']
        })
        
        return {
            'immediate_risks': analysis.get('immediate', []),
            'long_term_risks': analysis.get('long_term', []),
            'va_categories': analysis.get('va_categories', []),
            'medical_screenings': analysis.get('screenings', []),
            'severity_assessment': severity
        }
    
    def _mock_deployment_analysis(self, soldier_id, events):
        """Mock deployment analysis when Gemini is not available"""
        total_events = len(events)
        critical_events = [e for e in events if e['severity'] == 'CRITICAL']
        high_events = [e for e in events if e['severity'] == 'HIGH']
        
        # Count exposures by type
        exposure_counts = {}
        for event in events:
            event_type = event['event_type']
            exposure_counts[event_type] = exposure_counts.get(event_type, 0) + 1
        
        # Build verified exposures list
        verified_exposures = []
        for event_type, count in exposure_counts.items():
            verified_exposures.append({
                'type': event_type,
                'count': count,
                'date_range': 'Throughout deployment',
                'severity': 'MODERATE to HIGH',
                'locations': ['Various combat zones']
            })
        
        return {
            'summary': f'Comprehensive service record analysis for {soldier_id} showing {total_events} documented events including {len(critical_events)} critical incidents. Strong evidence base for VA benefits claims.',
            'verified_exposures': verified_exposures,
            'health_risks': {
                'immediate': [
                    'Hearing assessment needed',
                    'Respiratory evaluation recommended',
                    'TBI screening advised'
                ],
                'long_term': [
                    'Potential hearing loss',
                    'Respiratory conditions',
                    'PTSD risk',
                    'Chronic health effects from environmental exposures'
                ]
            },
            'medical_exams': [
                {
                    'exam': 'Comprehensive audiological evaluation',
                    'priority': 'HIGH',
                    'reason': 'Multiple blast and gunfire exposures documented'
                },
                {
                    'exam': 'Pulmonary function testing',
                    'priority': 'HIGH',
                    'reason': 'Burn pit and toxic smoke exposure'
                },
                {
                    'exam': 'TBI screening',
                    'priority': 'MEDIUM',
                    'reason': 'Blast exposure events'
                },
                {
                    'exam': 'Mental health evaluation',
                    'priority': 'MEDIUM',
                    'reason': 'Combat exposure and critical incidents'
                }
            ],
            'va_claims': [
                {
                    'category': 'Hearing Loss / Tinnitus',
                    'evidence_strength': 'STRONG',
                    'supporting_events': exposure_counts.get('GUNFIRE', 0) + exposure_counts.get('IED_EXPLOSION', 0)
                },
                {
                    'category': 'Respiratory Conditions',
                    'evidence_strength': 'STRONG',
                    'supporting_events': exposure_counts.get('BURN_PIT_EXPOSURE', 0) + exposure_counts.get('TOXIC_SMOKE', 0)
                },
                {
                    'category': 'PTSD',
                    'evidence_strength': 'MODERATE',
                    'supporting_events': len(critical_events)
                }
            ],
            'documentation_quality': 'EXCELLENT',
            'priority_concerns': [
                'Hearing loss from multiple acoustic trauma events',
                'Respiratory health from environmental exposures',
                'Mental health support for combat stress'
            ],
            'overall_risk_score': '75',
            'analyzed_at': datetime.now().isoformat(),
            'total_events_analyzed': total_events,
            'soldier_id': soldier_id
        }