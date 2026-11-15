"""Document generation: demand letters, price lists and broker forms.

PDFs are produced with reportlab. If reportlab is unavailable the service
falls back to a plain-text document so the demo never breaks.
"""
import io
import logging
from datetime import date

from django.core.files.base import ContentFile
from django.utils import timezone

from ..models import CompanyProfile, Document

logger = logging.getLogger(__name__)


def _reportlab():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as pdfcanvas
        return pdfcanvas, A4, mm
    except Exception:  # pragma: no cover
        logger.warning('reportlab unavailable - falling back to text documents')
        return None, None, None


def _money(value):
    return f'Rs. {value:,.2f}'


def build_demand_letter_pdf(booking):
    """Generate the demand letter for an approved booking."""
    pdfcanvas, A4, mm = _reportlab()
    company = CompanyProfile.load()
    customer = booking.customer
    plot = booking.plot

    buffer = io.BytesIO()
    if pdfcanvas is None:
        buffer.write(
            f"DEMAND LETTER\n\n"
            f"Ref: {booking.id}\n"
            f"Date: {timezone.now():%d %b %Y}\n\n"
            f"Dear {customer.name},\n\n"
            f"Your booking for plot {plot.plot_number} in {plot.project.name} "
            f"({plot.project.code}) has been approved.\n"
            f"Plot area: {plot.size_sq_yds} sq yds | Facing: {plot.get_facing_display()}\n"
            f"Total cost: {_money(plot.total_cost)}\n"
            f"Token received: {_money(booking.token_amount)}\n\n"
            f"Kindly contact {company.rm_name} at {company.rm_phone}.\n"
            .encode('utf-8')
        )
        return buffer.getvalue(), 'text/plain'

    c = pdfcanvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left, right = 20 * mm, width - 20 * mm

    c.setFont('Helvetica-Bold', 16)
    c.drawString(left, height - 25 * mm, company.name)
    c.setFont('Helvetica', 9)
    c.drawString(left, height - 31 * mm, f'{company.support_email}  |  {company.support_phone}')

    c.setStrokeColorRGB(0.12, 0.22, 0.39)
    c.setLineWidth(1.2)
    c.line(left, height - 34 * mm, right, height - 34 * mm)

    c.setFont('Helvetica-Bold', 13)
    c.drawString(left, height - 48 * mm, 'DEMAND LETTER')
    c.setFont('Helvetica', 9.5)
    c.drawString(right - 45 * mm, height - 48 * mm, f'Ref: DL/{booking.id:05d}')
    c.drawString(right - 45 * mm, height - 54 * mm, f'Date: {timezone.now():%d %b %Y}')

    y = height - 68 * mm
    c.setFont('Helvetica', 10)
    c.drawString(left, y, f'Dear {customer.name},')
    y -= 8 * mm

    for line in [
        'We are pleased to inform you that your booking request has been',
        'approved by the company. The details of your allotment are given below.',
    ]:
        c.drawString(left, y, line)
        y -= 6 * mm

    y -= 2 * mm
    rows = [
        ('Booking reference', f'BK-{booking.id:05d}'),
        ('Project', f'{plot.project.name} ({plot.project.code})'),
        ('Location', plot.project.location or '-'),
        ('Plot number', plot.plot_number),
        ('Plot area', f'{plot.size_sq_yds} sq. yds'),
        ('Facing', plot.get_facing_display()),
        ('Rate (BSP)', f'Rs. {plot.bsp:,.2f} / sq. yd'),
        ('PLC', f'{plot.plc_pct}%'),
        ('Discount', f'{plot.discount_pct}%'),
        ('Total cost', _money(plot.total_cost)),
        ('Token received', f'{_money(booking.token_amount)} ({booking.get_payment_mode_display()})'),
        ('Payment mode', booking.get_payment_mode_display()),
    ]
    for label, value in rows:
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(left, y, label)
        c.setFont('Helvetica', 9.5)
        c.drawString(left + 48 * mm, y, str(value))
        c.setStrokeColorRGB(0.85, 0.87, 0.91)
        c.line(left, y - 2 * mm, right, y - 2 * mm)
        y -= 7 * mm

    y -= 4 * mm
    c.setFont('Helvetica', 10)
    c.drawString(left, y, 'Kindly contact your relationship manager to complete the')
    y -= 6 * mm
    c.drawString(left, y, 'remaining formalities and payment schedule.')

    y -= 16 * mm
    c.setFont('Helvetica', 9.5)
    c.drawString(left, y, f'Yours faithfully,')
    y -= 6 * mm
    c.setFont('Helvetica-Bold', 10)
    c.drawString(left, y, f'{company.rm_name}')
    c.setFont('Helvetica', 9.5)
    c.drawString(left, y - 5 * mm, f'Relationship Manager  |  {company.rm_phone}  |  {company.rm_email}')

    c.save()
    return buffer.getvalue(), 'application/pdf'


def build_price_list_pdf(project):
    """Price list for a project, grouped by plot."""
    pdfcanvas, A4, mm = _reportlab()
    company = CompanyProfile.load()
    buffer = io.BytesIO()

    if pdfcanvas is None:
        lines = [f'PRICE LIST - {project.name} ({project.code})', '']
        for plot in project.plots.all():
            lines.append(
                f'{plot.plot_number}\t{plot.size_sq_yds} sq yd\t{plot.get_facing_display()}'
                f'\tRs. {plot.total_cost:,.2f}\t{plot.get_status_display()}'
            )
        buffer.write('\n'.join(lines).encode('utf-8'))
        return buffer.getvalue(), 'text/plain'

    c = pdfcanvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left, right = 18 * mm, width - 18 * mm

    c.setFont('Helvetica-Bold', 15)
    c.drawString(left, height - 24 * mm, company.name)
    c.setFont('Helvetica', 9)
    c.drawString(left, height - 30 * mm, f'{company.support_email}  |  {company.support_phone}')

    c.setFont('Helvetica-Bold', 13)
    c.drawString(left, height - 44 * mm, f'PRICE LIST - {project.name}')
    c.setFont('Helvetica', 9.5)
    c.drawString(left, height - 50 * mm, f'Project code: {project.code}   Location: {project.location}')
    c.drawString(left, height - 56 * mm, f'Generated: {timezone.now():%d %b %Y}')

    y = height - 66 * mm
    headers = ['Plot', 'Area (sq yd)', 'Facing', 'BSP', 'PLC', 'Disc.', 'Total', 'Status']
    widths = [18 * mm, 26 * mm, 24 * mm, 24 * mm, 14 * mm, 14 * mm, 30 * mm, 22 * mm]

    c.setFillColorRGB(0.12, 0.22, 0.39)
    c.rect(left, y - 4 * mm, sum(widths), 7 * mm, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont('Helvetica-Bold', 8.5)
    x = left
    for head, w in zip(headers, widths):
        c.drawString(x + 1.5 * mm, y - 2 * mm, head)
        x += w
    c.setFillColorRGB(0, 0, 0)
    y -= 11 * mm

    c.setFont('Helvetica', 8.5)
    for plot in project.plots.all():
        if y < 22 * mm:
            c.showPage()
            y = height - 25 * mm
        values = [
            plot.plot_number,
            str(plot.size_sq_yds),
            plot.get_facing_display(),
            f'{plot.bsp:,.0f}',
            f'{plot.plc_pct}%',
            f'{plot.discount_pct}%',
            f'{plot.total_cost:,.0f}',
            plot.get_status_display(),
        ]
        x = left
        for value, w in zip(values, widths):
            c.drawString(x + 1.5 * mm, y, value)
            x += w
        c.setStrokeColorRGB(0.88, 0.9, 0.94)
        c.line(left, y - 2 * mm, left + sum(widths), y - 2 * mm)
        y -= 6 * mm

    c.setFont('Helvetica-Oblique', 7.5)
    c.drawString(left, 15 * mm, 'Prices are indicative and subject to revision. '
                                'PLC and discount as applicable at the time of booking.')
    c.save()
    return buffer.getvalue(), 'application/pdf'


def build_kyc_summary_pdf(broker):
    """One-page summary of the broker's submitted KYC details."""
    pdfcanvas, A4, mm = _reportlab()
    company = CompanyProfile.load()
    buffer = io.BytesIO()

    if pdfcanvas is None:
        buffer.write(
            f'KYC SUMMARY\n\nBroker: {broker}\nEmail: {broker.user.email}\n'
            f'PAN: {broker.pan_number}\nGST: {broker.gst_number}\n'
            f'RERA: {broker.rera_number}\nStatus: {broker.kyc_status}\n'.encode('utf-8')
        )
        return buffer.getvalue(), 'text/plain'

    c = pdfcanvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 20 * mm
    c.setFont('Helvetica-Bold', 15)
    c.drawString(left, height - 25 * mm, company.name)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(left, height - 38 * mm, 'BROKER KYC SUMMARY')
    c.setFont('Helvetica', 10)

    y = height - 52 * mm
    rows = [
        ('Broker name', broker.user.get_full_name() or broker.user.username),
        ('Email', broker.user.email),
        ('Phone', broker.phone or '-'),
        ('PAN number', broker.pan_number or '-'),
        ('Aadhaar number', broker.aadhaar_number or '-'),
        ('GST number', broker.gst_number or '-'),
        ('RERA number', broker.rera_number or '-'),
        ('Bank account', broker.bank_account or '-'),
        ('IFSC', broker.ifsc or '-'),
        ('Agreement accepted', 'Yes' if broker.agreement_accepted else 'No'),
        ('KYC status', broker.get_kyc_status_display()),
        ('Documents uploaded', broker.documents.filter(kind__in=Document.KYC_KINDS).count()),
    ]
    for label, value in rows:
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(left, y, label)
        c.setFont('Helvetica', 9.5)
        c.drawString(left + 50 * mm, y, str(value))
        c.setStrokeColorRGB(0.85, 0.87, 0.91)
        c.line(left, y - 2 * mm, width - 20 * mm, y - 2 * mm)
        y -= 8 * mm

    c.setFont('Helvetica-Oblique', 8)
    c.drawString(left, 20 * mm, f'Generated on {date.today():%d %B %Y} by {company.name}.')
    c.save()
    return buffer.getvalue(), 'application/pdf'


def save_document(kind, title, content, content_type, broker=None, booking=None):
    """Persist generated bytes as a Document row."""
    doc = Document(broker=broker, booking=booking, kind=kind, title=title)
    filename = f"{kind}_{title.replace(' ', '_')[:40]}.pdf"
    if content_type == 'text/plain':
        filename = filename.replace('.pdf', '.txt')
    doc.file.save(filename, ContentFile(content), save=False)
    doc.content_type = content_type
    doc.size_bytes = len(content)
    doc.save()
    return doc
