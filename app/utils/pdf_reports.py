from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
from app.models import Database

# Реєстрація шрифта
try:
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuBold', 'DejaVuSans-Bold.ttf'))
    FONT_NAME = 'DejaVu'
    FONT_BOLD = 'DejaVuBold'
except Exception:
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'


def translate_status(status):
    translations = {
        'new': 'Нове',
        'pending': 'В очікуванні',
        'processing': 'Обробляється',
        'ready': 'Готово',
        'completed': 'Завершено',
        'delivered': 'Доставлено',
        'cancelled': 'Скасовано',
        'received': 'Отримано',
        'expired': 'Термін закінчився',
        'confirmed': 'Підтверджено',
        'declined': 'Відхилено',
        'unknown': 'Невідомий'
    }
    return translations.get(status, status)


def generate_sales_report_pdf(date_from, date_to):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Заголовок
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=16, textColor=colors.HexColor('#059669'), spaceAfter=6, alignment=TA_CENTER)
    story.append(Paragraph("ЗВІТ ПО ЗАМОВЛЕННЯХ", title_style))
    
    date_style = ParagraphStyle('DateRange', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11, textColor=colors.HexColor('#6b7280'), spaceAfter=20, alignment=TA_CENTER)
    story.append(Paragraph(f"Період: {date_from} — {date_to}", date_style))
    
    # Отримати дані з БД
    orders = Database.fetchall(
        'SELECT * FROM orders WHERE DATE(order_date) >= %s AND DATE(order_date) <= %s ORDER BY order_date DESC',
        (date_from, date_to)
    )
    
    # Отримати дані користувачів
    user_data = {}
    for order in orders:
        user_id = order.get('user_id')
        if user_id and user_id not in user_data:
            user = Database.fetchone('SELECT full_name, phone_number FROM users WHERE user_id = %s', (user_id,))
            if user:
                user_data[user_id] = {
                    'name': user.get('full_name', 'N/A'),
                    'phone': user.get('phone_number', 'N/A')
                }
            else:
                user_data[user_id] = {'name': 'N/A', 'phone': 'N/A'}
    
    # Таблиця замовлень
    orders_data_list = []
    orders_data_list.append([
        Paragraph("<b>№</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
        Paragraph("<b>Дата</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
        Paragraph("<b>Клієнт</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9)),
        Paragraph("<b>Телефон</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=8, alignment=TA_CENTER)),
        Paragraph("<b>Сума</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_RIGHT)),
        Paragraph("<b>Статус</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
    ])
    
    total_sum = 0
    for order in orders:
        order_date = str(order.get('order_date', '')).split()[0]
        user_id = order.get('user_id')
        user_info = user_data.get(user_id, {'name': 'N/A', 'phone': 'N/A'})
        amount = float(order.get('total_sum', 0))
        total_sum += amount
        status = translate_status(order.get('delivery_status', 'unknown'))
        
        orders_data_list.append([
            Paragraph(str(order.get('order_id', '')), ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, alignment=TA_CENTER)),
            Paragraph(order_date, ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, alignment=TA_CENTER)),
            Paragraph(user_info['name'][:25], ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8)),
            Paragraph(user_info['phone'][:15], ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=7, alignment=TA_CENTER)),
            Paragraph(f"{amount:.2f}", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, alignment=TA_RIGHT)),
            Paragraph(status, ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, alignment=TA_CENTER)),
        ])
    
    # Підсумок
    orders_data_list.append([
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
        Paragraph(f"<b>РАЗОМ: {len(orders)}</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9)),
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
        Paragraph(f"<b>{total_sum:.2f}</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_RIGHT)),
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
    ])
    
    orders_table = Table(orders_data_list, colWidths=[1.5*cm, 2*cm, 4*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    orders_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1fae5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#065f46')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dcfce7')),
        ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#059669')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
    ]))
    
    story.append(orders_table)
    
    # Футер
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Звіт згенерований автоматично", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_bookings_report_pdf(date_from, date_to):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Заголовок
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=16, textColor=colors.HexColor('#059669'), spaceAfter=6, alignment=TA_CENTER)
    story.append(Paragraph("ЗВІТ ПО БРОНЮВАННЯМ", title_style))
    
    date_style = ParagraphStyle('DateRange', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11, textColor=colors.HexColor('#6b7280'), spaceAfter=20, alignment=TA_CENTER)
    story.append(Paragraph(f"Період: {date_from} — {date_to}", date_style))
    
    # Отримати дані з БД
    bookings = Database.fetchall(
        'SELECT * FROM bookings WHERE DATE(booking_date) >= %s AND DATE(booking_date) <= %s ORDER BY booking_date DESC',
        (date_from, date_to)
    )
    
    # Отримати дані користувачів
    user_data = {}
    for booking in bookings:
        user_id = booking.get('user_id')
        if user_id and user_id not in user_data:
            user = Database.fetchone('SELECT full_name, phone_number FROM users WHERE user_id = %s', (user_id,))
            if user:
                user_data[user_id] = {
                    'name': user.get('full_name', 'N/A'),
                    'phone': user.get('phone_number', 'N/A')
                }
            else:
                user_data[user_id] = {'name': 'N/A', 'phone': 'N/A'}
    
    # Таблиця бронювань
    bookings_data_list = []
    bookings_data_list.append([
        Paragraph("<b>№</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
        Paragraph("<b>Дата</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
        Paragraph("<b>Клієнт</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9)),
        Paragraph("<b>Телефон</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=8, alignment=TA_CENTER)),
        Paragraph("<b>Статус</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
    ])
    
    for booking in bookings:
        booking_date = str(booking.get('booking_date', '')).split()[0]
        user_id = booking.get('user_id')
        user_info = user_data.get(user_id, {'name': 'N/A', 'phone': 'N/A'})
        status = translate_status(booking.get('status', 'unknown'))
        
        bookings_data_list.append([
            Paragraph(str(booking.get('booking_id', '')), ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, alignment=TA_CENTER)),
            Paragraph(booking_date, ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, alignment=TA_CENTER)),
            Paragraph(user_info['name'][:25], ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8)),
            Paragraph(user_info['phone'][:15], ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=7, alignment=TA_CENTER)),
            Paragraph(status, ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, alignment=TA_CENTER)),
        ])
    
    # Підсумок
    bookings_data_list.append([
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
        Paragraph(f"<b>РАЗОМ: {len(bookings)}</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9)),
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
    ])
    
    bookings_table = Table(bookings_data_list, colWidths=[1.8*cm, 2.5*cm, 4.5*cm, 3*cm, 3*cm])
    bookings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1fae5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#065f46')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dcfce7')),
        ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#059669')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ]))
    
    story.append(bookings_table)
    
    # Футер
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Звіт згенерований автоматично", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_revenue_report_pdf(date_from, date_to):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Заголовок
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=16, textColor=colors.HexColor('#059669'), spaceAfter=6, alignment=TA_CENTER)
    story.append(Paragraph("ЗВІТ ПО ДОХОДУ", title_style))
    
    date_style = ParagraphStyle('DateRange', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11, textColor=colors.HexColor('#6b7280'), spaceAfter=20, alignment=TA_CENTER)
    story.append(Paragraph(f"Період: {date_from} — {date_to}", date_style))
    
    # Отримати дані з БД
    orders = Database.fetchall(
        'SELECT DATE(order_date) as order_date, SUM(total_sum) as daily_sum FROM orders WHERE DATE(order_date) >= %s AND DATE(order_date) <= %s GROUP BY DATE(order_date) ORDER BY order_date DESC',
        (date_from, date_to)
    )
    
    # Таблиця доходу
    revenue_data_list = []
    revenue_data_list.append([
        Paragraph("<b>Дата</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_CENTER)),
        Paragraph("<b>Дохід (грн)</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_RIGHT)),
    ])
    
    total_revenue = 0
    for row in orders:
        order_date = str(row.get('order_date', ''))
        daily_sum = float(row.get('daily_sum', 0))
        total_revenue += daily_sum
        
        revenue_data_list.append([
            Paragraph(order_date, ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{daily_sum:.2f}", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, alignment=TA_RIGHT)),
        ])
    
    # Підсумок
    revenue_data_list.append([
        Paragraph("<b>РАЗОМ:</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_CENTER)),
        Paragraph(f"<b>{total_revenue:.2f}</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_RIGHT)),
    ])
    
    revenue_table = Table(revenue_data_list, colWidths=[4*cm, 4*cm])
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef3c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#92400e')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#fffbeb')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fbbf24')),
        ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#f59e0b')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    
    story.append(revenue_table)
    
    # Футер
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Звіт згенерований автоматично", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_medicines_report_pdf(date_from, date_to):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Заголовок
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=16, textColor=colors.HexColor('#059669'), spaceAfter=6, alignment=TA_CENTER)
    story.append(Paragraph("ЗВІТ ПО ЛІКАХ", title_style))
    
    date_style = ParagraphStyle('DateRange', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11, textColor=colors.HexColor('#6b7280'), spaceAfter=20, alignment=TA_CENTER)
    story.append(Paragraph(f"Період: {date_from} — {date_to}", date_style))
    
    # Отримати дані з БД
    medicines = Database.fetchall(
        '''SELECT om.medicine_id, m.name, SUM(om.quantity) as total_sold, SUM(om.subtotal) as revenue
           FROM order_medicine om
           JOIN medicines m ON om.medicine_id = m.medicine_id
           JOIN orders o ON om.order_id = o.order_id
           WHERE DATE(o.order_date) >= %s AND DATE(o.order_date) <= %s
           GROUP BY om.medicine_id, m.name
           ORDER BY total_sold DESC
           LIMIT 20''',
        (date_from, date_to)
    )
    
    # Таблиця ліків
    medicines_data_list = []
    medicines_data_list.append([
        Paragraph("<b>№</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_CENTER)),
        Paragraph("<b>Назва препарату</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10)),
        Paragraph("<b>Продано (шт)</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_CENTER)),
        Paragraph("<b>Дохід (грн)</b>", ParagraphStyle('TableHeader', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_RIGHT)),
    ])
    
    total_qty = 0
    total_revenue = 0
    for idx, med in enumerate(medicines, 1):
        qty = int(med.get('total_sold', 0))
        revenue = float(med.get('revenue', 0))
        total_qty += qty
        total_revenue += revenue
        
        medicines_data_list.append([
            Paragraph(str(idx), ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, alignment=TA_CENTER)),
            Paragraph(med.get('name', 'N/A'), ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9)),
            Paragraph(str(qty), ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{revenue:.2f}", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, alignment=TA_RIGHT)),
        ])
    
    # Підсум
    medicines_data_list.append([
        Paragraph("", ParagraphStyle('TableCell', parent=styles['Normal'])),
        Paragraph("<b>РАЗОМ:</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10)),
        Paragraph(f"<b>{total_qty}</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_CENTER)),
        Paragraph(f"<b>{total_revenue:.2f}</b>", ParagraphStyle('TableCell', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10, alignment=TA_RIGHT)),
    ])
    
    meds_table = Table(medicines_data_list, colWidths=[1*cm, 8*cm, 2.5*cm, 2.5*cm])
    meds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1fae5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#065f46')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dcfce7')),
        ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#059669')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
    ]))
    
    story.append(meds_table)
    
    # Футер
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Звіт згенерований автоматично", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
