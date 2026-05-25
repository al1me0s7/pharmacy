from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
import sys
from datetime import datetime
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import Database

def translate_delivery_method(method):
    translations = {
        'home': 'Доставка додому',
        'self_pickup': 'Самовивіз з аптеки',
        'nova_poshta': 'Нова Пошта',
        'ukrposhta': 'Укрпошта',
        'post_nova': 'Нова Пошта',
        'post_ukr': 'Укрпошта',
        'post': 'Пошта',
        'address': 'Доставка за адресою'
    }
    return translations.get(method, method)

def translate_status(status):
    translations = {
        'active': 'АКТИВНЕ',
        'expired': 'ПРОСТРОЧЕНО',
        'collected': 'ОТРИМАНО',
        'cancelled': 'СКАСОВАНО',
        'pending': 'ОЧІКУВАННЯ',
        'processing': 'ОБРОБЛЯЄТЬСЯ',
        'ready': 'ГОТОВО',
        'received': 'ОТРИМАНО',
        'shipped': 'ВІДПРАВЛЕНО'
    }
    return translations.get(status.lower(), status.upper())

# шрифт для кирилиці
try:
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuBold', 'DejaVuSans-Bold.ttf'))
    FONT_NAME = 'DejaVu'
    FONT_BOLD = 'DejaVuBold'
except Exception:
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    print("Warning: DejaVuSans.ttf not found")


def generate_order_pdf(order, items, user, pharmacy=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=2*cm, 
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # стилі
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        alignment=TA_CENTER,
        leading=28
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        leading=14
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        leading=13
    )
    
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#111827'),
        leading=14
    )

    story.append(Paragraph("ЧЕК ЗАМОВЛЕННЯ", title_style))
    story.append(Paragraph("Онлайн-аптека", subtitle_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Розділювач
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Інформація про замовлення
    city_name = None
    if order.get('city_name'):
        city_name = order.get('city_name')
    elif pharmacy and pharmacy.get('city_name'):
        city_name = pharmacy.get('city_name')
    elif pharmacy and pharmacy.get('city_id'):
        city_row = Database.fetchone('SELECT city_name FROM cities WHERE city_id = %s', (pharmacy.get('city_id'),))
        if city_row:
            city_name = city_row.get('city_name', '')
    address_full = order.get('delivery_address', '-')

    order_info = [
        [Paragraph("Номер замовлення:", label_style), Paragraph(f"#{order.get('order_id', '-')}", value_style)],
        [Paragraph("Дата:", label_style), Paragraph(str(order.get('order_date', '-')), value_style)],
        [Paragraph("Клієнт:", label_style), Paragraph(user.get('full_name', '-'), value_style)],
        [Paragraph("Телефон:", label_style), Paragraph(user.get('phone_number', '-'), value_style)],
        [Paragraph("Спосіб доставки:", label_style), Paragraph(f"{translate_delivery_method(order.get('delivery_method', '-'))}", value_style)],
        [Paragraph("Місто:", label_style), Paragraph(city_name if city_name else '-', value_style)],
        [Paragraph("Адреса доставки:", label_style), Paragraph(address_full, value_style)],
    ]
    # Додаємо коментар після адреси, якщо є
    if order.get('comment'):
        order_info.append([Paragraph("Коментар:", label_style), Paragraph(str(order.get('comment')), value_style)])
    order_info.append([
        Paragraph("Спосіб оплати:", label_style),
        Paragraph(f"{'Накладний платіж' if order.get('payment_method') == 'cash_on_delivery' else 'Оплата карткою' if order.get('payment_method') == 'card_online' else order.get('payment_method', '-')}", value_style)
    ])
    if order.get('payment_method') == 'card_online':
        order_info.append([Paragraph("Статус оплати:", label_style), Paragraph(f"<font color='#059669'><b>УСПІШНО</b></font>", value_style)])

    if pharmacy:
        city_name = Database.fetchone('SELECT city_name FROM cities WHERE city_id = %s', (pharmacy.get('city_id'),))
        city_name = city_name.get('city_name') if city_name else ''
        order_info.append([Paragraph("Назва аптеки:", label_style), Paragraph(f"{pharmacy.get('pharmacy_name', '-')}", value_style)])
        if city_name:
            order_info.append([Paragraph("Місто:", label_style), Paragraph(f"{city_name}", value_style)])
        if pharmacy.get('address'):
            order_info.append([Paragraph("Адреса аптеки:", label_style), Paragraph(f"{pharmacy.get('address')}", value_style)])
        if pharmacy.get('contact_phone'):
            order_info.append([Paragraph("Телефон аптеки:", label_style), Paragraph(f"{pharmacy.get('contact_phone')}", value_style)])
    
    order_table = Table(order_info, colWidths=[4.2*cm, 12.8*cm])
    order_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9fafb')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    
    story.append(order_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Розділювач
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Заголовок таблиці товарів
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=12,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12
    )
    story.append(Paragraph("ТОВАРИ", section_header_style))
    
    # Таблиця товарів
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=colors.HexColor('#374151'),
        alignment=TA_CENTER
    )
    
    data = [[
        Paragraph('НАЙМЕНУВАННЯ', ParagraphStyle('THLeft', parent=table_header_style, alignment=TA_LEFT)),
        Paragraph('К-СТЬ', table_header_style),
        Paragraph('ЦІНА', ParagraphStyle('THRight', parent=table_header_style, alignment=TA_RIGHT)),
        Paragraph('СУМА', ParagraphStyle('THRight', parent=table_header_style, alignment=TA_RIGHT))
    ]]
    
    item_style = ParagraphStyle('ItemStyle', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#374151'))
    item_num_style = ParagraphStyle('ItemNum', parent=item_style, alignment=TA_CENTER)
    item_price_style = ParagraphStyle('ItemPrice', parent=item_style, alignment=TA_RIGHT)
    item_total_style = ParagraphStyle('ItemTotal', parent=item_style, alignment=TA_RIGHT, fontName=FONT_BOLD)
    
    for item in items:
        name = item.get('name', f"ID:{item.get('medicine_id', '')}")
        qty = int(item.get('quantity', 1) or 1)
        price = float(item.get('price_at_purchase') or 0)
        subtotal = float(item.get('subtotal') or price * qty)
        
        data.append([
            Paragraph(name[:60], item_style),
            Paragraph(str(qty), item_num_style),
            Paragraph(f"{price:.2f} грн", item_price_style),
            Paragraph(f"{subtotal:.2f} грн", item_total_style)
        ])
    
    item_table = Table(data, colWidths=[9*cm, 2*cm, 3*cm, 3*cm])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    story.append(item_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Загальна сума
    total = float(order.get('total_sum', 0) or 0)
    
    total_table_data = [[
        Paragraph("ЗАГАЛЬНА СУМА:", ParagraphStyle('TotalLabel', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=14, textColor=colors.HexColor('#1e40af'))),
        Paragraph(f"{total:.2f} грн", ParagraphStyle('TotalValue', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=16, textColor=colors.HexColor('#1e40af'), alignment=TA_RIGHT))
    ]]
    
    total_table = Table(total_table_data, colWidths=[11*cm, 6*cm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#1e40af')),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 0.6*cm))
    
    # Розділювач
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=0, spaceBefore=0.6*cm))
    
    # Футер
    story.append(Spacer(1, 0.4*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    story.append(Paragraph("Дякуємо за покупку!", footer_style))
    story.append(Paragraph("Бережіть своє здоров'я!", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_booking_pdf(booking, user, medicine, pharmacy, city=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2*cm,
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # стилі
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=24,
        textColor=colors.HexColor('#059669'),
        spaceAfter=6,
        alignment=TA_CENTER,
        leading=28
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        leading=13
    )
    
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#111827'),
        leading=14
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=12,
        textColor=colors.HexColor('#059669'),
        spaceAfter=12,
        spaceBefore=8
    )
    
    # Заголовок
    story.append(Paragraph("ПІДТВЕРДЖЕННЯ БРОНЮВАННЯ", title_style))
    story.append(Paragraph("Онлайн-аптека", subtitle_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Розділювач
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Інформація про бронювання
    story.append(Paragraph("ДЕТАЛІ БРОНЮВАННЯ", section_header_style))
    
    booking_info = [
        [Paragraph("Номер бронювання:", label_style), Paragraph(f"#{booking.get('booking_id')}", value_style)],
        [Paragraph("Дата бронювання:", label_style), Paragraph(f"{str(booking.get('booking_date', ''))[:19]}", value_style)],
        [Paragraph("Статус:", label_style), Paragraph(f"<font color='#059669'><b>{translate_status(booking.get('status', 'active'))}</b></font>", value_style)],
    ]
    
    if booking.get('pickup_deadline'):
        booking_info.append([Paragraph("Забрати до:", label_style), Paragraph(f"<font color='#dc2626'><b>{str(booking.get('pickup_deadline'))[:19]}</b></font>", value_style)])
    
    booking_table = Table(booking_info, colWidths=[4.5*cm, 12.5*cm])
    booking_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(booking_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Інформація про клієнта
    story.append(Paragraph("КЛІЄНТ", section_header_style))
    
    user_info = [
        [Paragraph("Ім'я:", label_style), Paragraph(f"{user.get('full_name', 'N/A')}", value_style)],
        [Paragraph("Телефон:", label_style), Paragraph(f"{user.get('phone_number', '-')}", value_style)],
    ]
    
    user_table = Table(user_info, colWidths=[4.5*cm, 12.5*cm])
    user_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(user_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Інформація про ліки
    story.append(Paragraph("ЗАБРОНОВАНИЙ ПРЕПАРАТ", section_header_style))
    
    if medicine:
        med_name = medicine.get('name', 'N/A')
        med_form = medicine.get('form', '-')
        med_dosage = medicine.get('dosage', '-')
        med_manufacturer = medicine.get('manufacturer', '-')
        med_description = medicine.get('description', '')
        med_prescription = medicine.get('prescription_required', False)
    else:
        med_name = "Див. перелік товарів нижче"
        med_form = "-"
        med_dosage = "-"
        med_manufacturer = "-"
        med_description = ""
        med_prescription = False

    # створюємо список data, використовуючи змінні вище
    med_info = [
        [Paragraph("Номер бронювання:", label_style), Paragraph(str(booking.get('booking_id')), value_style)],
        [Paragraph("Дата створення:", label_style), Paragraph(str(booking.get('booking_date')), value_style)],
        [Paragraph("Статус:", label_style), Paragraph(translate_status(booking.get('status', 'pending')), value_style)],
        [Paragraph("Аптека:", label_style), Paragraph(pharmacy.get('pharmacy_name', 'N/A'), value_style)],
        [Paragraph("Адреса аптеки:", label_style), Paragraph(pharmacy.get('address', 'N/A'), value_style)],
        
        # Використовуємо змінні, які ми створили вище
        [Paragraph("Основний препарат:", label_style), Paragraph(med_name, value_style)],
        [Paragraph("Форма випуску:", label_style), Paragraph(med_form, value_style)],
        [Paragraph("Дозування:", label_style), Paragraph(med_dosage, value_style)],
        [Paragraph("Виробник:", label_style), Paragraph(med_manufacturer, value_style)],
    ]
    
    if med_description:
        med_info.append([Paragraph("Опис:", label_style), Paragraph(med_description, value_style)])
    
    if med_prescription:
        med_info.append([Paragraph("Рецепт:", label_style), Paragraph("<font color='#dc2626'><b>ПОТРІБЕН РЕЦЕПТ</b></font>", value_style)])
    
    med_table = Table(med_info, colWidths=[4.5*cm, 12.5*cm])
    med_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(med_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Інформація про аптеку
    story.append(Paragraph("АПТЕКА ДЛЯ ОТРИМАННЯ", section_header_style))
    
    pharm_info = []
    
    if city:
        pharm_info.append([Paragraph("Місто:", label_style), Paragraph(f"{city.get('city_name', 'N/A')}", value_style)])
    
    pharm_info.extend([
        [Paragraph("Назва:", label_style), Paragraph(f"{pharmacy.get('pharmacy_name', 'N/A')}", value_style)],
        [Paragraph("Адреса:", label_style), Paragraph(f"{pharmacy.get('address', '')}", value_style)],
    ])
    
    if pharmacy.get('contact_phone'):
        pharm_info.append([Paragraph("Телефон:", label_style), Paragraph(f"{pharmacy.get('contact_phone')}", value_style)])
    
    if pharmacy.get('working_hours'):
        pharm_info.append([Paragraph("Режим роботи:", label_style), Paragraph(f"{pharmacy.get('working_hours')}", value_style)])
    
    pharm_table = Table(pharm_info, colWidths=[4.5*cm, 12.5*cm])
    pharm_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(pharm_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Розділювач
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Важлива інформація
    important_box_data = [[
        Paragraph("<b>ВАЖЛИВА ІНФОРМАЦІЯ</b>", ParagraphStyle('ImpTitle', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=11, textColor=colors.HexColor('#dc2626'), alignment=TA_CENTER, spaceAfter=8)),
    ]]
    
    important_table = Table(important_box_data, colWidths=[17*cm])
    important_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef2f2')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#dc2626')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    story.append(important_table)
    story.append(Spacer(1, 0.2*cm))
    
    # Футер
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=3
    )
    
    story.append(Paragraph("• Зверніться до аптеки для отримання броні у вказаний термін", footer_style))
    story.append(Paragraph("• При собі мати документ, що посвідчує особу", footer_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Дякуємо за вибір нашої аптеки!", ParagraphStyle('FooterBold', parent=footer_style, fontName=FONT_BOLD, fontSize=10)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_payment_receipt_pdf(order, items, user, masked_card, expiry_date, total):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=2*cm, 
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Власні стилі
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=24,
        textColor=colors.HexColor('#059669'),
        spaceAfter=6,
        alignment=TA_CENTER,
        leading=28
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        leading=13
    )
    
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#111827'),
        leading=14
    )
    
    # Заголовок
    story.append(Paragraph("КВИТАНЦІЯ ПРО ОПЛАТУ", title_style))
    story.append(Paragraph("Онлайн-аптека", subtitle_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Розділювач
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=0.4*cm, spaceBefore=0))
    
    story.append(Spacer(1, 0.5*cm))
    
    # ІНФОРМАЦІЯ ПРО ОПЛАТУ
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=12,
        textColor=colors.HexColor('#059669'),
        spaceAfter=12
    )
    story.append(Paragraph("ІНФОРМАЦІЯ ПРО ОПЛАТУ", section_header_style))
    
    # Інформація про оплату
    receipt_info = [
        [Paragraph("Номер замовлення:", label_style), Paragraph(f"#{order.get('order_id', 'N/A')}", value_style)],
        [Paragraph("Дата оплати:", label_style), Paragraph(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", value_style)],
        [Paragraph("ПІБ платника:", label_style), Paragraph(f"{user.get('full_name', 'N/A')}", value_style)],
        [Paragraph("Номер телефону:", label_style), Paragraph(f"{user.get('phone_number', 'N/A')}", value_style)],
        [Paragraph("Спосіб оплати:", label_style), Paragraph(f"Оплата карткою", value_style)],
        [Paragraph("Номер картки:", label_style), Paragraph(f"{masked_card}", value_style)],
        [Paragraph("Сума оплати:", label_style), Paragraph(f"<b>{total:.2f} грн</b>", value_style)],
    ]
    
    receipt_table = Table(receipt_info, colWidths=[4.2*cm, 12.8*cm])
    receipt_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(receipt_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ОТРИМУВАЧ
    story.append(Paragraph("ОТРИМУВАЧ", section_header_style))
    
    recipient_info = [
        [Paragraph("Онлайн-аптека:", label_style), Paragraph(f"Онлайн-аптека", value_style)],
        [Paragraph("Статус оплати:", label_style), Paragraph(f"<font color='#059669'><b>УСПІШНО</b></font>", value_style)],
    ]
    
    recipient_table = Table(recipient_info, colWidths=[4.2*cm, 12.8*cm])
    recipient_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(recipient_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Розділювач
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Футер
    story.append(Spacer(1, 0.4*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    story.append(Paragraph("Дякуємо за оплату!", ParagraphStyle('FooterBold', parent=footer_style, fontName=FONT_BOLD, fontSize=10)))
    story.append(Paragraph("Транзакція успішно завершена", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_multi_booking_pdf(booking, user, items_data, pharmacy, city=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2*cm,
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # стилі
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=24,
        textColor=colors.HexColor('#059669'),
        spaceAfter=6,
        alignment=TA_CENTER,
        leading=28
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        leading=13
    )
    
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#111827'),
        leading=14
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=12,
        textColor=colors.HexColor('#059669'),
        spaceAfter=12,
        spaceBefore=8
    )
    
    # Заголовок
    story.append(Paragraph("ПІДТВЕРДЖЕННЯ БРОНЮВАННЯ", title_style))
    story.append(Paragraph("Онлайн-аптека", subtitle_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Розділювач
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Інформація про бронювання
    story.append(Paragraph("ДЕТАЛІ БРОНЮВАННЯ", section_header_style))
    
    booking_info = [
        [Paragraph("Номер бронювання:", label_style), Paragraph(f"#{booking.get('booking_id')}", value_style)],
        [Paragraph("Дата бронювання:", label_style), Paragraph(f"{str(booking.get('booking_date', ''))[:19]}", value_style)],
        [Paragraph("Статус:", label_style), Paragraph(f"<font color='#059669'><b>{translate_status(booking.get('status', 'active'))}</b></font>", value_style)],
    ]
    
    if booking.get('pickup_deadline'):
        booking_info.append([Paragraph("Забрати до:", label_style), Paragraph(f"<font color='#dc2626'><b>{str(booking.get('pickup_deadline'))[:19]}</b></font>", value_style)])
    
    booking_table = Table(booking_info, colWidths=[4.5*cm, 12.5*cm])
    booking_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(booking_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Інформація про клієнта
    story.append(Paragraph("КЛІЄНТ", section_header_style))
    
    user_info = [
        [Paragraph("Ім'я:", label_style), Paragraph(f"{user.get('full_name', 'N/A')}", value_style)],
        [Paragraph("Телефон:", label_style), Paragraph(f"{user.get('phone_number', '-')}", value_style)],
    ]
    
    user_table = Table(user_info, colWidths=[4.5*cm, 12.5*cm])
    user_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(user_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Таблиця забронированих ліків
    story.append(Paragraph("ЗАБРОНИРОВАНІ ПРЕПАРАТИ", section_header_style))
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=colors.HexColor('#374151'),
        alignment=TA_CENTER
    )
    
    data = [[
        Paragraph('НАЙМЕНУВАННЯ', ParagraphStyle('THLeft', parent=table_header_style, alignment=TA_LEFT)),
        Paragraph('К-СТЬ', table_header_style),
        Paragraph('ЦІНА', ParagraphStyle('THRight', parent=table_header_style, alignment=TA_RIGHT)),
        Paragraph('СУМА', ParagraphStyle('THRight', parent=table_header_style, alignment=TA_RIGHT))
    ]]
    
    item_style = ParagraphStyle('ItemStyle', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#374151'))
    item_num_style = ParagraphStyle('ItemNum', parent=item_style, alignment=TA_CENTER)
    item_price_style = ParagraphStyle('ItemPrice', parent=item_style, alignment=TA_RIGHT)
    item_total_style = ParagraphStyle('ItemTotal', parent=item_style, alignment=TA_RIGHT, fontName=FONT_BOLD)
    
    total_sum = 0
    for item in items_data:
        name = item.get('name', 'Unknown')
        qty = int(item.get('quantity', 1))
        price = float(item.get('unit_price', 0))
        subtotal = price * qty
        total_sum += subtotal
        
        data.append([
            Paragraph(name[:60], item_style),
            Paragraph(str(qty), item_num_style),
            Paragraph(f"{price:.2f} грн", item_price_style),
            Paragraph(f"{subtotal:.2f} грн", item_total_style)
        ])
    
    items_table = Table(data, colWidths=[9*cm, 2*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Сума бронювання
    total_table_data = [[
        Paragraph("ЗАГАЛЬНА СУМА:", ParagraphStyle('TotalLabel', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=12, textColor=colors.HexColor('#059669'))),
        Paragraph(f"{total_sum:.2f} грн", ParagraphStyle('TotalValue', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=14, textColor=colors.HexColor('#059669'), alignment=TA_RIGHT))
    ]]
    
    total_table = Table(total_table_data, colWidths=[11*cm, 6*cm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#059669')),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Інформація про аптеку
    story.append(Paragraph("АПТЕКА ДЛЯ ОТРИМАННЯ", section_header_style))
    
    pharm_info = []
    
    if city:
        pharm_info.append([Paragraph("Місто:", label_style), Paragraph(f"{city.get('city_name', 'N/A')}", value_style)])
    
    pharm_info.extend([
        [Paragraph("Назва:", label_style), Paragraph(f"{pharmacy.get('pharmacy_name', 'N/A')}", value_style)],
        [Paragraph("Адреса:", label_style), Paragraph(f"{pharmacy.get('address', '')}", value_style)],
    ])
    
    if pharmacy.get('contact_phone'):
        pharm_info.append([Paragraph("Телефон:", label_style), Paragraph(f"{pharmacy.get('contact_phone')}", value_style)])
    
    if pharmacy.get('working_hours'):
        pharm_info.append([Paragraph("Режим роботи:", label_style), Paragraph(f"{pharmacy.get('working_hours')}", value_style)])
    
    pharm_table = Table(pharm_info, colWidths=[4.5*cm, 12.5*cm])
    pharm_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(pharm_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Розділювач
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Футер
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=3
    )
    
    story.append(Paragraph("• При собі мати документ, що посвідчує особу та рецепт від лікаря, якщо препарат рецептурний", footer_style))
    story.append(Paragraph("Дякуємо за вибір нашої аптеки!", ParagraphStyle('FooterBold', parent=footer_style, fontName=FONT_BOLD, fontSize=10)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_sales_report_pdf(date_from, date_to, orders_data, total_revenue):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2*cm,
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=22,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        alignment=TA_CENTER,
        leading=26
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Заголовок
    story.append(Paragraph("ЗВІТ ПРО ПРОДАЖІ", title_style))
    story.append(Paragraph(f"Період: {date_from} - {date_to}", subtitle_style))
    story.append(Spacer(1, 0.4*cm))
    
    # Розділювач
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Підсумки
    summary_data = [
        [Paragraph("ЗАГАЛЬНА СТАТИСТИКА", ParagraphStyle('SummaryTitle', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=12, textColor=colors.HexColor('#1e40af')))]
    ]
    
    summary_table = Table(summary_data, colWidths=[17*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Основна статистика
    stats_info = [
        [Paragraph(f"Кількість замовлень:", ParagraphStyle('Label', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10)), Paragraph(f"{len(orders_data)}", styles['Normal'])],
        [Paragraph(f"Загальна сума продажів:", ParagraphStyle('Label', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10)), Paragraph(f"{total_revenue:.2f} грн", styles['Normal'])],
        [Paragraph(f"Середня вартість замовлення:", ParagraphStyle('Label', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10)), Paragraph(f"{total_revenue/len(orders_data):.2f} грн" if orders_data else "0.00 грн", styles['Normal'])],
    ]
    
    stats_table = Table(stats_info, colWidths=[10*cm, 7*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Таблиця замовлень
    if orders_data:
        story.append(Paragraph("СПИСОК ЗАМОВЛЕНЬ", ParagraphStyle('SectionTitle', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=12, textColor=colors.HexColor('#1e40af'), spaceAfter=12)))
        
        data = [[
            Paragraph('ID', ParagraphStyle('TH', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
            Paragraph('Дата', ParagraphStyle('TH', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
            Paragraph('Сума', ParagraphStyle('TH', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_RIGHT)),
            Paragraph('Статус', ParagraphStyle('TH', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, alignment=TA_CENTER)),
        ]]
        
        for order in orders_data[:50]:  # Максимум 50 замовлень на сторінці
            data.append([
                Paragraph(f"#{order.get('order_id')}", ParagraphStyle('TD', parent=styles['Normal'], fontSize=8)),
                Paragraph(f"{str(order.get('order_date', ''))[:10]}", ParagraphStyle('TD', parent=styles['Normal'], fontSize=8)),
                Paragraph(f"{order.get('total_sum', 0):.2f} грн", ParagraphStyle('TD', parent=styles['Normal'], fontSize=8, alignment=TA_RIGHT)),
                Paragraph(f"{order.get('delivery_status', 'unknown')}", ParagraphStyle('TD', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)),
            ])
        
        orders_table = Table(data, colWidths=[2*cm, 4*cm, 4*cm, 4*cm])
        orders_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        story.append(orders_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Футер
    story.append(Paragraph("Звіт згенерований автоматично", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_customer_report_pdf(customer_data, orders_data, bookings_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2*cm,
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=22,
        textColor=colors.HexColor('#059669'),
        spaceAfter=6,
        alignment=TA_CENTER,
        leading=26
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Заголовок
    story.append(Paragraph("ЗВІТ ПРО ПОКУПЦЯ", title_style))
    story.append(Paragraph(f"{customer_data.get('full_name', 'Unknown')}", subtitle_style))
    story.append(Spacer(1, 0.4*cm))
    
    # Розділювач
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=0.4*cm, spaceBefore=0))
    
    # Персональна інформація
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=10)
    value_style = ParagraphStyle('Value', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10)
    
    personal_info = [
        [Paragraph("Ім'я та прізвище:", label_style), Paragraph(f"{customer_data.get('full_name', '')} {customer_data.get('last_name', '')}", value_style)],
        [Paragraph("Email:", label_style), Paragraph(f"{customer_data.get('email', '-')}", value_style)],
        [Paragraph("Телефон:", label_style), Paragraph(f"{customer_data.get('phone_number', '-')}", value_style)],
        [Paragraph("Адреса:", label_style), Paragraph(f"{customer_data.get('address', '-')}", value_style)],
        [Paragraph("Місто:", label_style), Paragraph(f"{customer_data.get('city', '-')}", value_style)],
        [Paragraph("Дата реєстрації:", label_style), Paragraph(f"{str(customer_data.get('registration_date', ''))[:10]}", value_style)],
    ]
    
    personal_table = Table(personal_info, colWidths=[4*cm, 13*cm])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 0.4*cm))
    
    # Статистика покупця
    story.append(Paragraph("СТАТИСТИКА", ParagraphStyle('SectionTitle', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=12, textColor=colors.HexColor('#059669'), spaceAfter=12)))
    
    total_spent = sum(float(o.get('total_sum', 0)) for o in orders_data)
    stats_info = [
        [Paragraph(f"Замовлень:", label_style), Paragraph(f"{len(orders_data)}", value_style)],
        [Paragraph(f"Бронювань:", label_style), Paragraph(f"{len(bookings_data)}", value_style)],
        [Paragraph(f"Всього витрачено:", label_style), Paragraph(f"{total_spent:.2f} грн", value_style)],
        [Paragraph(f"Середнє замовлення:", label_style), Paragraph(f"{total_spent/len(orders_data):.2f} грн" if orders_data else "0.00 грн", value_style)],
    ]
    
    stats_table = Table(stats_info, colWidths=[4*cm, 13*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1fae5')),
    ]))
    
    story.append(stats_table)
    
    # Футер
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Звіт згенерований автоматично", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ParagraphStyle('Footer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer