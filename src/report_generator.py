"""
FinSight AI — Monthly Financial Health Report Generator
Computes month-specific financial health metrics and generates downloadable PDF statements.
"""

import io
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config.settings import CURRENCY_SYMBOL


def compute_monthly_health_report(transactions: pd.DataFrame, user: dict, period_str: str) -> dict:
    """
    Computes all analytical metrics for a specific month (e.g., '2026-08').
    """
    if transactions.empty:
        return {}

    df = transactions.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M').astype(str)

    # Filter to chosen month
    month_df = df[df['year_month'] == period_str].copy()
    if month_df.empty:
        return {}

    total_spent = float(month_df['amount'].sum())
    transaction_count = len(month_df)
    
    income = float(user.get('income', user.get('monthly_income', 0))) if user else 0.0
    budget = float(user.get('budget', user.get('monthly_budget', 0))) if user else 0.0
    
    # Net savings & utilization
    net_savings = (income - total_spent) if income > 0 else (budget - total_spent if budget > 0 else 0)
    utilization_pct = (total_spent / budget * 100) if budget > 0 else 0.0
    
    # Category Breakdown for this month
    cat_summary = month_df.groupby('category')['amount'].agg(['sum', 'count']).reset_index()
    cat_summary.columns = ['category', 'total_amount', 'tx_count']
    cat_summary['percentage'] = (cat_summary['total_amount'] / total_spent * 100) if total_spent > 0 else 0
    cat_summary = cat_summary.sort_values('total_amount', ascending=False)

    # Anomaly detection for this month relative to history
    # Simple Z-score within category
    anomalies = []
    for cat in month_df['category'].unique():
        cat_history = df[df['category'] == cat]['amount']
        if len(cat_history) >= 3:
            mean = cat_history.mean()
            std = cat_history.std()
            if std > 0:
                outliers = month_df[(month_df['category'] == cat) & ((month_df['amount'] - mean) / std > 2.0)]
                for _, row in outliers.iterrows():
                    anomalies.append({
                        'date': str(row['date'].strftime('%Y-%m-%d')),
                        'category': row['category'],
                        'amount': float(row['amount']),
                        'description': str(row.get('description', '')),
                        'z_score': round(float((row['amount'] - mean) / std), 2)
                    })

    # Financial Health Score calculation (0 - 100)
    score = 100
    if budget > 0:
        if utilization_pct > 100:
            score -= min(40, (utilization_pct - 100) * 1.5)
        elif utilization_pct > 85:
            score -= (utilization_pct - 85) * 1.0
        else:
            score += 5  # Bonus for remaining disciplined
            
    # Deduct for anomalies
    score -= len(anomalies) * 8
    score = max(10, min(100, round(score)))

    # Grade
    if score >= 85:
        grade = "Excellent (A+)"
        status_color = "#10B981"
    elif score >= 70:
        grade = "Good (B)"
        status_color = "#3B82F6"
    elif score >= 50:
        grade = "Needs Attention (C)"
        status_color = "#F59E0B"
    else:
        grade = "Critical Overspend (D)"
        status_color = "#EF4444"

    return {
        'period': period_str,
        'total_spent': total_spent,
        'transaction_count': transaction_count,
        'income': income,
        'budget': budget,
        'net_savings': net_savings,
        'utilization_pct': utilization_pct,
        'health_score': score,
        'grade': grade,
        'status_color': status_color,
        'categories': cat_summary.to_dict(orient='records'),
        'anomalies': anomalies,
        'top_transactions': month_df.sort_values('amount', ascending=False).head(5).to_dict(orient='records')
    }


def generate_monthly_pdf(report: dict, user: dict) -> bytes:
    """
    Generates a PDF monthly statement.
    Uses 'Rs.' prefix for currency to ensure standard PDF font glyph compatibility.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    section_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=6
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # 1. Header Banner Table
    username = user.get('username', 'User') if user else 'User'
    period = report.get('period', 'N/A')
    date_str = datetime.now().strftime("%d %b %Y")

    header_data = [
        [
            Paragraph("<b>FinSight AI</b><br/><font size=8 color='#64748B'>Personal Financial Intelligence</font>", title_style),
            Paragraph(f"<b>MONTHLY AUDIT STATEMENT</b><br/>Period: <b>{period}</b><br/>Issued: {date_str}", subtitle_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[300, 240])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#D97706'), spaceBefore=2, spaceAfter=12))

    # 2. Executive KPI Cards Table
    income = report.get('income', 0)
    budget = report.get('budget', 0)
    spent = report.get('total_spent', 0)
    savings = report.get('net_savings', 0)
    score = report.get('health_score', 0)
    grade = report.get('grade', 'N/A')

    kpi_data = [
        [
            Paragraph("<b>Monthly Budget</b>", subtitle_style),
            Paragraph("<b>Total Spent</b>", subtitle_style),
            Paragraph("<b>Net Savings / Balance</b>", subtitle_style),
            Paragraph("<b>Financial Health Score</b>", subtitle_style)
        ],
        [
            Paragraph(f"<b>Rs. {budget:,.0f}</b>", cell_bold),
            Paragraph(f"<b>Rs. {spent:,.0f}</b>", cell_bold),
            Paragraph(f"<b>Rs. {savings:,.0f}</b>", cell_bold),
            Paragraph(f"<b>{score}/100</b> ({grade})", cell_bold)
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[135, 135, 135, 135])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 12))

    # 3. Category Breakdown Table
    story.append(Paragraph("Category Spending Breakdown", section_h2))
    cat_rows = [
        [
            Paragraph("<b>Category</b>", cell_bold),
            Paragraph("<b>Txns</b>", cell_bold),
            Paragraph("<b>Amount (INR)</b>", cell_bold),
            Paragraph("<b>Share (%)</b>", cell_bold)
        ]
    ]
    for c in report.get('categories', [])[:10]:
        cat_rows.append([
            Paragraph(str(c['category']), cell_style),
            Paragraph(str(c['tx_count']), cell_style),
            Paragraph(f"Rs. {c['total_amount']:,.0f}", cell_style),
            Paragraph(f"{c['percentage']:.1f}%", cell_style)
        ])

    t_cat = Table(cat_rows, colWidths=[200, 70, 150, 120])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0'))
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 10))

    # 4. Irregular Anomalies (if any)
    anomalies = report.get('anomalies', [])
    if anomalies:
        story.append(Paragraph(f"Flagged Spending Anomalies ({len(anomalies)} Detected)", section_h2))
        anom_rows = [
            [
                Paragraph("<b>Date</b>", cell_bold),
                Paragraph("<b>Category</b>", cell_bold),
                Paragraph("<b>Amount (INR)</b>", cell_bold),
                Paragraph("<b>Description / Notes</b>", cell_bold)
            ]
        ]
        for a in anomalies[:5]:
            anom_rows.append([
                Paragraph(str(a['date']), cell_style),
                Paragraph(str(a['category']), cell_style),
                Paragraph(f"Rs. {a['amount']:,.0f}", cell_style),
                Paragraph(f"Deviates by {a.get('z_score', 'N/A')} sigma", cell_style)
            ])
        t_anom = Table(anom_rows, colWidths=[100, 130, 120, 190])
        t_anom.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0'))
        ]))
        story.append(t_anom)
        story.append(Spacer(1, 10))

    # 5. Strategic Notes & Recommendations
    story.append(Paragraph("Advisory Notes & Key Recommendations", section_h2))
    notes = [
        f"• <b>Budget Utilization:</b> You consumed <b>{report.get('utilization_pct', 0):.1f}%</b> of your allocated monthly budget.",
        f"• <b>Primary Expense Driver:</b> Your highest spending area was <b>{report.get('categories', [{}])[0].get('category', 'N/A')}</b> accounting for Rs. {report.get('categories', [{}])[0].get('total_amount', 0):,.0f}.",
    ]
    if report.get('utilization_pct', 0) > 100:
        notes.append("• <b>Overspend Alert:</b> Target a 10-15% reduction in discretionary shopping and dining out next month to restore positive cash flow.")
    else:
        notes.append(f"• <b>Savings Trajectory:</b> Positive surplus of <b>Rs. {savings:,.0f}</b> successfully achieved this period. Consider deploying surplus into your emergency fund.")

    for n in notes:
        story.append(Paragraph(n, cell_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceBefore=2, spaceAfter=8))
    story.append(Paragraph("<font size=7 color='#64748B'>Confidential Financial Document • Auto-generated by FinSight AI Engine • Valid for Academic Review & Demonstration</font>", subtitle_style))

    # Build PDF
    doc.build(story)
    return buf.getvalue()
