"""
Generate PDF VA Reports from AI analysis
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from google.cloud import storage
from datetime import datetime
import io
import uuid
import os


class ReportGenerator:
    def __init__(self, firestore_client):
        self.db = firestore_client
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'valorstream-reports')
        
    def generate_pdf_report(self, soldier_id, events, analysis):
        """Generate PDF VA benefits report"""
        try:
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=36
            )
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a2e'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
            
            styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#0f3460'),
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold'
            ))
            
            styles.add(ParagraphStyle(
                name='Subsection',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.HexColor('#16213e'),
                spaceAfter=8,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ))
            
            # Title
            title = Paragraph("VERIFIED MILITARY SERVICE RECORD", styles['CustomTitle'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Subtitle
            subtitle = Paragraph("VA Benefits Pre-Application Assessment", styles['Heading2'])
            elements.append(subtitle)
            elements.append(Spacer(1, 20))
            
            # Header Information Table
            report_id = str(uuid.uuid4())[:8].upper()
            soldier_data = [
                ['Soldier ID:', soldier_id],
                ['Report Generated:', datetime.now().strftime('%B %d, %Y at %H:%M UTC')],
                ['Total Events Analyzed:', str(len(events))],
                ['Report ID:', report_id],
                ['Documentation Quality:', analysis.get('documentation_quality', 'N/A')]
            ]
            
            soldier_table = Table(soldier_data, colWidths=[2*inch, 4*inch])
            soldier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(soldier_table)
            elements.append(Spacer(1, 30))
            
            # Executive Summary
            elements.append(Paragraph("EXECUTIVE SUMMARY", styles['SectionHeader']))
            summary_text = analysis.get('summary', 'No summary available')
            elements.append(Paragraph(summary_text, styles['BodyText']))
            elements.append(Spacer(1, 20))
            
            # Risk Score (if available)
            risk_score = analysis.get('overall_risk_score', 'N/A')
            if risk_score != 'N/A':
                risk_text = f"<b>Overall Health Risk Score:</b> {risk_score}/100"
                elements.append(Paragraph(risk_text, styles['BodyText']))
                elements.append(Spacer(1, 20))
            
            # Verified Exposures
            elements.append(Paragraph("VERIFIED EXPOSURES", styles['SectionHeader']))
            
            if 'verified_exposures' in analysis and analysis['verified_exposures']:
                exposure_data = [['Exposure Type', 'Count', 'Severity', 'Date Range']]
                
                for exp in analysis['verified_exposures']:
                    exposure_data.append([
                        exp.get('type', 'Unknown'),
                        str(exp.get('count', 0)),
                        exp.get('severity', 'N/A'),
                        exp.get('date_range', 'N/A')
                    ])
                
                exposure_table = Table(exposure_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
                exposure_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                
                elements.append(exposure_table)
            else:
                elements.append(Paragraph("No exposure data available", styles['BodyText']))
            
            elements.append(Spacer(1, 30))
            
            # Health Risk Analysis
            elements.append(Paragraph("HEALTH RISK ANALYSIS", styles['SectionHeader']))
            
            if 'health_risks' in analysis:
                # Immediate Risks
                elements.append(Paragraph("<b>Immediate Health Concerns:</b>", styles['Subsection']))
                immediate_risks = analysis['health_risks'].get('immediate', [])
                if immediate_risks:
                    for risk in immediate_risks:
                        elements.append(Paragraph(f"• {risk}", styles['BodyText']))
                else:
                    elements.append(Paragraph("• None identified", styles['BodyText']))
                
                elements.append(Spacer(1, 15))
                
                # Long-term Risks
                elements.append(Paragraph("<b>Long-term Health Concerns:</b>", styles['Subsection']))
                long_term_risks = analysis['health_risks'].get('long_term', [])
                if long_term_risks:
                    for risk in long_term_risks:
                        elements.append(Paragraph(f"• {risk}", styles['BodyText']))
                else:
                    elements.append(Paragraph("• None identified", styles['BodyText']))
            
            elements.append(Spacer(1, 30))
            
            # Recommended Medical Examinations
            elements.append(Paragraph("RECOMMENDED MEDICAL EXAMINATIONS", styles['SectionHeader']))
            
            if 'medical_exams' in analysis and analysis['medical_exams']:
                exam_data = [['Priority', 'Examination', 'Reason']]
                
                for exam in analysis['medical_exams']:
                    priority = exam.get('priority', 'MEDIUM')
                    exam_name = exam.get('exam', 'Unknown')
                    reason = exam.get('reason', 'N/A')
                    
                    exam_data.append([priority, exam_name, reason])
                
                exam_table = Table(exam_data, colWidths=[1*inch, 2.5*inch, 2.5*inch])
                exam_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                
                elements.append(exam_table)
            else:
                elements.append(Paragraph("No specific examinations recommended at this time.", styles['BodyText']))
            
            elements.append(Spacer(1, 30))
            
            # Potential VA Disability Claims
            elements.append(Paragraph("POTENTIAL VA DISABILITY CLAIMS", styles['SectionHeader']))
            
            if 'va_claims' in analysis and analysis['va_claims']:
                claims_data = [['Disability Category', 'Evidence Strength', 'Supporting Events']]
                
                for claim in analysis['va_claims']:
                    category = claim.get('category', 'Unknown')
                    strength = claim.get('evidence_strength', 'N/A')
                    events_count = str(claim.get('supporting_events', 0))
                    
                    claims_data.append([category, strength, events_count])
                
                claims_table = Table(claims_data, colWidths=[3*inch, 2*inch, 1*inch])
                claims_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                
                elements.append(claims_table)
            else:
                elements.append(Paragraph("Claims analysis pending further medical evaluation.", styles['BodyText']))
            
            elements.append(Spacer(1, 30))
            
            # Priority Health Concerns
            if 'priority_concerns' in analysis and analysis['priority_concerns']:
                elements.append(Paragraph("PRIORITY HEALTH CONCERNS", styles['SectionHeader']))
                for i, concern in enumerate(analysis['priority_concerns'], 1):
                    elements.append(Paragraph(f"{i}. ⚠️ {concern}", styles['BodyText']))
                elements.append(Spacer(1, 30))
            
            # Documentation Summary
            elements.append(Paragraph("DOCUMENTATION SUMMARY", styles['SectionHeader']))
            
            quality = analysis.get('documentation_quality', 'UNKNOWN')
            total_analyzed = analysis.get('total_events_analyzed', len(events))
            
            summary_text = f"""
            <b>Documentation Quality:</b> {quality}<br/>
            <b>Total Events Documented:</b> {total_analyzed}<br/>
            <b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
            <br/>
            This report provides verified documentation of service-related exposures 
            suitable for VA benefits claims. All data is sourced from real-time 
            battlefield IoT sensors and validated through AI analysis. This comprehensive 
            record eliminates the need for retrospective evidence gathering and provides 
            strong support for disability claims.
            """
            
            elements.append(Paragraph(summary_text, styles['BodyText']))
            
            # Footer
            elements.append(Spacer(1, 40))
            footer_text = """
            <i>This report is generated by ValorStream, a real-time battlefield data 
            documentation system designed to ensure every service member's exposures are 
            properly recorded and preserved for VA benefits claims. For questions or 
            additional documentation, contact your unit's medical officer or VA benefits coordinator.</i>
            """
            elements.append(Paragraph(footer_text, styles['BodyText']))
            
            # Build PDF
            doc.build(elements)
            
            # Upload to Cloud Storage
            pdf_data = buffer.getvalue()
            report_url, report_id_full = self.upload_to_storage(pdf_data, soldier_id)
            
            return report_url, report_id_full
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def upload_to_storage(self, pdf_data, soldier_id):
        """Upload PDF to Google Cloud Storage"""
        try:
            report_id = f"{soldier_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filename = f"reports/{report_id}.pdf"
            
            # Get or create bucket
            try:
                bucket = self.storage_client.bucket(self.bucket_name)
                if not bucket.exists():
                    bucket = self.storage_client.create_bucket(
                        self.bucket_name,
                        location=os.getenv('GCP_REGION', 'us-east1')
                    )
            except Exception as e:
                print(f"Warning: Could not access bucket: {e}")
                # Return local file path as fallback
                return f"/tmp/{report_id}.pdf", report_id
            
            blob = bucket.blob(filename)
            
            # Upload
            blob.upload_from_string(
                pdf_data,
                content_type='application/pdf'
            )
            
            # Make public (for demo - use signed URLs in production)
            blob.make_public()
            
            return blob.public_url, report_id
            
        except Exception as e:
            print(f"Error uploading to storage: {e}")
            # Save locally as fallback
            local_path = f"/tmp/{report_id}.pdf"
            with open(local_path, 'wb') as f:
                f.write(pdf_data)
            return local_path, report_id