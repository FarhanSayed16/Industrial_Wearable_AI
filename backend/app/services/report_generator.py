"""
Industrial Wearable AI — PDF Report Generator
Generates formatted shift reports using ReportLab.
"""
import io
import time
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_shift_report_pdf(
    session_id: str,
    worker_name: str,
    started_at: datetime,
    ended_at: datetime | None,
    aggregates: Dict[str, Any],
    events: List[Dict[str, Any]]
) -> bytes:
    """
    Generates a PDF report for a single worker session.
    Returns the PDF as a byte string.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    subtitle_style = styles['Heading3']
    normal_style = styles['Normal']

    elements = []

    # Title
    elements.append(Paragraph("Industrial Wearable AI", title_style))
    elements.append(Paragraph("Worker Shift Report", title_style))
    elements.append(Spacer(1, 20))

    # Header section
    started_str = started_at.strftime("%Y-%m-%d %H:%M:%S") if started_at else "N/A"
    ended_str = ended_at.strftime("%Y-%m-%d %H:%M:%S") if ended_at else "Ongoing"
    duration_min = round((ended_at - started_at).total_seconds() / 60) if ended_at and started_at else "N/A"

    header_data = [
        ["Worker:", worker_name, "Session ID:", str(session_id)[:8] + "..."],
        ["Start Time:", started_str, "End Time:", ended_str],
        ["Duration:", f"{duration_min} mins", "Generated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
    ]

    header_table = Table(header_data, colWidths=[80, 150, 80, 150])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # Summary Stats
    elements.append(Paragraph("Shift Summary", subtitle_style))
    active_pct = aggregates.get('active_pct', 0)
    idle_pct = aggregates.get('idle_pct', 0)
    adjusting_pct = aggregates.get('adjusting_pct', 0)
    error_pct = aggregates.get('error_pct', 0)
    productivity = aggregates.get('productivity_score', 0)

    stats_data = [
        ["Productivity Score:", f"{productivity:.1f}%"],
        ["Time Active Data:", f"{active_pct:.1f}% Sewing, {adjusting_pct:.1f}% Adjusting"],
        ["Time Idle / Error:", f"{idle_pct:.1f}% Idle, {error_pct:.1f}% Error"],
        ["Total Alerts:", str(aggregates.get('alert_count', 0))],
    ]

    stats_table = Table(stats_data, colWidths=[150, 300])
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 20))

    # Risk Event Log
    elements.append(Paragraph("Significant Risk Events", subtitle_style))
    risk_events = [e for e in events if e.get('risk_ergo') or e.get('risk_fatigue') or e.get('label') == 'error']
    
    if not risk_events:
        elements.append(Paragraph("No significant risk events recorded during this shift.", normal_style))
    else:
        event_data = [["Time", "Activity", "Ergonomic Risk", "Fatigue Risk"]]
        # Limit to 30 events for the PDF to avoid huge tables
        for e in risk_events[:30]:
            ts_str = datetime.fromtimestamp(e['ts']/1000).strftime("%H:%M:%S")
            ergo = "Yes" if e.get('risk_ergo') else "No"
            fatigue = "Yes" if e.get('risk_fatigue') else "No"
            event_data.append([ts_str, str(e.get('label', '')).title(), ergo, fatigue])
        
        event_table = Table(event_data, colWidths=[100, 150, 120, 120])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(event_table)
        
        if len(risk_events) > 30:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"...and {len(risk_events) - 30} more events (truncated).", normal_style))

    # Build PDF
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
