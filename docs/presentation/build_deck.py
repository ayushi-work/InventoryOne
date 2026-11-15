"""Generate the InventoryOne Broker Web App presentation (10 slides)."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn

NAVY = RGBColor(0x1F, 0x38, 0x64)
TEAL = RGBColor(0x2E, 0x9E, 0x8F)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
AMBER = RGBColor(0xF2, 0x9E, 0x1B)
RED = RGBColor(0xC0, 0x39, 0x2B)
LIGHT = RGBColor(0xF2, 0xF4, 0xF8)
LINE = RGBColor(0xD5, 0xDC, 0xE8)
GRAY = RGBColor(0x55, 0x55, 0x55)
DARK = RGBColor(0x22, 0x22, 0x22)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
COUNTER = {'n': 0}


def new_slide():
    return prs.slides.add_slide(BLANK)


def rect(s, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, lw=1.0):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    return sh


def arrow(s, x1, y1, x2, y2, color=GRAY, lw=1.5, dash=False, head=True):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    ln = c.line._get_or_add_ln()
    if dash:
        d = ln.makeelement(qn('a:prstDash'), {'val': 'dash'})
        ln.append(d)
    if head:
        te = ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
        ln.append(te)
    return c


def text(s, x, y, w, h, lines, size=15, color=DARK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, bold=False, space=5, line_spacing=1.05):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    first = True
    for item in lines:
        if isinstance(item, str):
            item = {'t': item}
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = item.get('align', align)
        p.level = item.get('lvl', 0)
        p.space_after = Pt(item.get('space', space))
        p.line_spacing = item.get('ls', line_spacing)
        label = item['t']
        if item.get('bullet'):
            label = ('•  ' if item.get('lvl', 0) == 0 else '–  ') + label
        r = p.add_run()
        r.text = label
        r.font.size = Pt(item.get('size', size))
        r.font.bold = item.get('bold', bold)
        r.font.color.rgb = item.get('color', color)
        r.font.name = 'Calibri'
    return tb


def content_slide(title, kicker=None):
    COUNTER['n'] += 1
    s = new_slide()
    rect(s, 0, 0, 13.333, 1.0, fill=NAVY)
    rect(s, 0, 1.0, 13.333, 0.045, fill=TEAL)
    text(s, 0.45, 0.12, 11.0, 0.78, [{'t': title, 'size': 27, 'bold': True, 'color': WHITE}],
         anchor=MSO_ANCHOR.MIDDLE)
    if kicker:
        text(s, 0.5, 1.12, 12.3, 0.3, [{'t': kicker, 'size': 12, 'color': TEAL, 'bold': True}])
    text(s, 0.45, 7.12, 9.0, 0.3, [{'t': 'InventoryOne — Broker Web App', 'size': 9, 'color': GRAY}])
    text(s, 12.2, 7.12, 0.8, 0.3, [{'t': f'{COUNTER["n"]}', 'size': 10, 'color': GRAY,
                                      'align': PP_ALIGN.RIGHT}])
    return s


# =========================================================================
# Slide 1 — Title
# =========================================================================
COUNTER['n'] += 1
s = new_slide()
rect(s, 0, 0, 13.333, 7.5, fill=NAVY)
rect(s, 0, 2.35, 13.333, 0.06, fill=TEAL)
text(s, 0.9, 0.65, 11.5, 0.5, [{'t': 'SE & DP LAB — STUDENT PRESENTATION', 'size': 14,
                                 'color': TEAL, 'bold': True}])
text(s, 0.9, 1.15, 11.5, 1.2, [{'t': 'InventoryOne', 'size': 54, 'bold': True, 'color': WHITE}])
text(s, 0.9, 2.55, 11.5, 0.7, [{'t': 'Broker Web App — Real-Estate Plot Booking Platform',
                                 'size': 22, 'color': RGBColor(0xCF, 0xD8, 0xE8)}])
text(s, 0.9, 3.7, 11.5, 0.4, [{'t': 'Selected Software System', 'size': 14, 'color': TEAL, 'bold': True}])
text(s, 0.9, 4.05, 11.5, 0.9, [
    {'t': 'A digital platform for registered brokers to view live plot inventory, register customers, ', 'size': 15, 'color': WHITE, 'space': 0},
    {'t': 'raise booking requests, track commissions and receive notifications.', 'size': 15, 'color': WHITE},
])
rect(s, 0.9, 5.25, 5.4, 1.3, fill=RGBColor(0x2A, 0x48, 0x7A))
text(s, 1.15, 5.4, 5.0, 0.4, [{'t': 'Group Members', 'size': 13, 'color': TEAL, 'bold': True}])
text(s, 1.15, 5.78, 5.0, 0.7, [{'t': 'Avni', 'size': 17, 'color': WHITE, 'bold': True, 'space': 2},
                               {'t': 'Ayushi', 'size': 17, 'color': WHITE, 'bold': True}])
text(s, 6.6, 5.4, 6.2, 1.1, [{'t': 'Domain: Real Estate / Property Management', 'size': 13, 'color': WHITE, 'space': 4},
                             {'t': 'Methodology: Agile', 'size': 13, 'color': WHITE}], anchor=MSO_ANCHOR.MIDDLE)

# =========================================================================
# Slide 2 — Introduction, Problem Statement, Objectives
# =========================================================================
s = content_slide('Introduction, Problem Statement & Objectives')
col_w = 4.0
# Introduction
rect(s, 0.45, 1.55, col_w, 5.3, fill=LIGHT, line=LINE)
rect(s, 0.45, 1.55, col_w, 0.5, fill=TEAL)
text(s, 0.6, 1.58, col_w - 0.3, 0.45, [{'t': 'Introduction', 'size': 15, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.7, 2.2, col_w - 0.5, 4.5, [
    {'t': 'Real-estate plot booking today relies on manual coordination between brokers and the company.', 'bullet': True},
    {'t': 'Brokers must call/visit the office to check availability, raise bookings and track earnings.', 'bullet': True},
    {'t': 'InventoryOne is a self-service web app giving brokers live plot visibility and digital bookings.', 'bullet': True},
    {'t': 'Administrators manage projects, inventory, approvals and commissions from one dashboard.', 'bullet': True},
], size=13)

# Problem statement
x2 = 4.75
rect(s, x2, 1.55, col_w, 5.3, fill=LIGHT, line=LINE)
rect(s, x2, 1.55, col_w, 0.5, fill=RED)
text(s, x2 + 0.15, 1.58, col_w - 0.3, 0.45, [{'t': 'Problem Statement', 'size': 15, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, x2 + 0.25, 2.2, col_w - 0.5, 4.5, [
    {'t': 'Stale inventory data and no live visibility of plot availability.', 'bullet': True},
    {'t': 'Slow, error-prone booking through phone/email and spreadsheets.', 'bullet': True},
    {'t': 'No transparent commission tracking for brokers.', 'bullet': True},
    {'t': 'Limited service hours and heavy manual coordination.', 'bullet': True},
], size=13)

# Objectives
x3 = 9.05
rect(s, x3, 1.55, col_w, 5.3, fill=LIGHT, line=LINE)
rect(s, x3, 1.55, col_w, 0.5, fill=GREEN)
text(s, x3 + 0.15, 1.58, col_w - 0.3, 0.45, [{'t': 'Objectives', 'size': 15, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, x3 + 0.25, 2.2, col_w - 0.5, 4.5, [
    {'t': 'Secure OTP-based broker login and KYC verification.', 'bullet': True},
    {'t': 'Live, colour-coded plot availability (available / hold / sold).', 'bullet': True},
    {'t': 'Customer registration and booking with company approval.', 'bullet': True},
    {'t': 'Automated commission, TDS and document management.', 'bullet': True},
    {'t': 'Real-time notifications and support tickets.', 'bullet': True},
], size=13)

# =========================================================================
# Slide 3 — Functional & Non-Functional Requirements
# =========================================================================
s = content_slide('Major Functional & Non-Functional Requirements')
rect(s, 0.45, 1.5, 7.9, 5.35, fill=LIGHT, line=LINE)
rect(s, 0.45, 1.5, 7.9, 0.5, fill=NAVY)
text(s, 0.6, 1.53, 7.6, 0.45, [{'t': 'Functional Requirements', 'size': 15, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.7, 2.1, 7.5, 4.6, [
    {'t': 'OTP-based broker registration, login and session expiry.', 'bullet': True},
    {'t': 'KYC upload (PAN, Aadhaar, GST, cancelled cheque) + RERA & bank details.', 'bullet': True},
    {'t': 'Active project listing with project details.', 'bullet': True},
    {'t': 'Live colour-coded plot availability: green = available, amber = on hold, red = sold.', 'bullet': True},
    {'t': 'Plot details: size, facing, PLC, BSP, total cost, discount.', 'bullet': True},
    {'t': 'Customer registration linked to the broker.', 'bullet': True},
    {'t': 'Booking requests with token amount and payment mode.', 'bullet': True},
    {'t': 'Administrator approval/rejection of bookings (plot sold / released).', 'bullet': True},
    {'t': 'Commission tracking with TDS and net payable; document downloads.', 'bullet': True},
    {'t': 'Notifications and support tickets.', 'bullet': True},
], size=12.5)

rect(s, 8.6, 1.5, 4.28, 5.35, fill=LIGHT, line=LINE)
rect(s, 8.6, 1.5, 4.28, 0.5, fill=TEAL)
text(s, 8.75, 1.53, 4.0, 0.45, [{'t': 'Non-Functional Requirements', 'size': 15, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 8.8, 2.1, 3.95, 4.6, [
    {'t': 'Usability: simple, minimal training.', 'bullet': True},
    {'t': 'Performance: operations respond < 2 s.', 'bullet': True},
    {'t': 'Security: role-based access; HTTPS; protected OTP/KYC.', 'bullet': True},
    {'t': 'Reliability: no loss of booking/commission data.', 'bullet': True},
    {'t': 'Scalability: supports more projects, plots, brokers.', 'bullet': True},
    {'t': 'Maintainability: modular and documented.', 'bullet': True},
    {'t': 'Responsiveness: works on desktop and mobile.', 'bullet': True},
], size=13)

# =========================================================================
# Slide 4 — Actors & Use Case Diagram
# =========================================================================
s = content_slide('Actors & UML Use Case Diagram')
# System boundary
rect(s, 3.55, 1.5, 6.9, 5.35, fill=RGBColor(0xF7, 0xF9, 0xFC), line=NAVY, lw=1.5)
text(s, 3.65, 1.52, 6.7, 0.3, [{'t': 'InventoryOne — Broker Web App', 'size': 11, 'bold': True, 'color': NAVY,
                                 'align': PP_ALIGN.CENTER}])
# Actors
rect(s, 0.4, 3.35, 2.5, 1.0, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 0.4, 3.35, 2.5, 1.0, [{'t': 'Broker', 'size': 16, 'bold': True, 'color': WHITE, 'align': PP_ALIGN.CENTER}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.4, 4.4, 2.5, 0.5, [{'t': '(Primary Actor)', 'size': 10, 'color': GRAY, 'align': PP_ALIGN.CENTER}])
rect(s, 10.45, 3.35, 2.5, 1.0, fill=TEAL, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, 10.45, 3.35, 2.5, 1.0, [{'t': 'Company', 'size': 15, 'bold': True, 'color': WHITE, 'align': PP_ALIGN.CENTER, 'space': 0},
                                {'t': 'Administrator', 'size': 15, 'bold': True, 'color': WHITE, 'align': PP_ALIGN.CENTER}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 10.45, 4.4, 2.5, 0.5, [{'t': '(Secondary Actor)', 'size': 10, 'color': GRAY, 'align': PP_ALIGN.CENTER}])

# Broker use cases (left column)
broker_uc = ['Register / OTP Login', 'Complete KYC', 'View Plot Availability',
             'Register Customer', 'Raise Booking Request', 'Track Commission']
y = 1.95
for uc in broker_uc:
    rect(s, 3.75, y, 3.1, 0.6, fill=RGBColor(0xE4, 0xF2, 0xEF), line=TEAL,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 3.75, y, 3.1, 0.6, [{'t': uc, 'size': 11.5, 'color': NAVY, 'align': PP_ALIGN.CENTER}],
         anchor=MSO_ANCHOR.MIDDLE)
    y += 0.78
# Admin use cases (right column)
admin_uc = ['Approve / Reject Booking', 'Manage Projects & Inventory', 'Manage Commissions']
y = 2.55
for uc in admin_uc:
    rect(s, 7.15, y, 3.1, 0.6, fill=RGBColor(0xFB, 0xF3, 0xE2), line=AMBER,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 7.15, y, 3.1, 0.6, [{'t': uc, 'size': 11.5, 'color': NAVY, 'align': PP_ALIGN.CENTER}],
         anchor=MSO_ANCHOR.MIDDLE)
    y += 0.78
# associations
for uc_y in [2.25, 3.03, 3.81, 4.59, 5.37, 6.15]:
    arrow(s, 2.9, 3.85, 3.75, uc_y, color=GRAY, lw=1.0)
for uc_y in [2.85, 3.63, 4.41]:
    arrow(s, 10.45, 3.85, 10.25, uc_y, color=GRAY, lw=1.0)
text(s, 0.4, 5.05, 2.6, 1.6, [
    {'t': 'External systems:', 'size': 11, 'bold': True, 'color': NAVY, 'space': 2},
    {'t': 'OTP/SMS Gateway, AWS S3, Firebase FCM, Google Maps.', 'size': 10.5, 'color': GRAY},
], size=10.5)
text(s, 10.45, 5.05, 2.6, 1.6, [
    {'t': 'Relationships:', 'size': 11, 'bold': True, 'color': NAVY, 'space': 2},
    {'t': '<<include>> Authenticate Broker & Validate KYC; <<extend>> Upload KYC Documents.', 'size': 10, 'color': GRAY},
], size=10)

# =========================================================================
# Slide 5 — DFD Level 0 (Context Diagram)
# =========================================================================
s = content_slide('Data Flow Diagram — DFD Level 0 (Context Diagram)')
# central process
rect(s, 4.9, 2.9, 3.55, 1.9, fill=RGBColor(0xE4, 0xF2, 0xEF), line=TEAL,
     shape=MSO_SHAPE.OVAL, lw=2.0)
text(s, 4.9, 2.9, 3.55, 1.9, [{'t': '0', 'size': 12, 'bold': True, 'color': TEAL, 'align': PP_ALIGN.CENTER, 'space': 0},
                              {'t': 'InventoryOne', 'size': 15, 'bold': True, 'color': NAVY, 'align': PP_ALIGN.CENTER, 'space': 0},
                              {'t': 'Broker Web App', 'size': 13, 'color': NAVY, 'align': PP_ALIGN.CENTER}],
     anchor=MSO_ANCHOR.MIDDLE)

def entity(x, y, label, fill=NAVY):
    rect(s, x, y, 2.35, 0.9, fill=fill, line=None)
    text(s, x, y, 2.35, 0.9, [{'t': label, 'size': 12.5, 'bold': True, 'color': WHITE,
                               'align': PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE)

entity(0.4, 3.45, 'Broker')
entity(10.55, 3.45, 'Company\nAdministrator')
entity(5.45, 1.35, 'OTP / SMS\nGateway', fill=TEAL)
entity(5.45, 5.55, 'Firebase\nCloud Messaging', fill=TEAL)
entity(10.55, 1.35, 'AWS S3', fill=TEAL)

arrow(s, 2.78, 3.7, 4.9, 3.5, color=NAVY)
text(s, 2.7, 3.05, 2.4, 0.4, [{'t': 'credentials, KYC, booking request', 'size': 9, 'color': NAVY}])
arrow(s, 4.9, 4.15, 2.78, 4.15, color=GREEN)
text(s, 2.7, 4.2, 2.4, 0.4, [{'t': 'availability, status, commissions', 'size': 9, 'color': GREEN}])
arrow(s, 10.55, 3.7, 8.45, 3.5, color=NAVY)
text(s, 8.5, 3.05, 2.4, 0.4, [{'t': 'approve / reject, manage', 'size': 9, 'color': NAVY}])
arrow(s, 8.45, 4.15, 10.55, 4.15, color=GREEN)
text(s, 8.5, 4.2, 2.4, 0.4, [{'t': 'pending bookings, reports', 'size': 9, 'color': GREEN}])
arrow(s, 6.6, 2.25, 6.6, 2.95, color=TEAL)
text(s, 6.85, 2.35, 2.5, 0.4, [{'t': 'OTP request / verify', 'size': 9, 'color': TEAL}])
arrow(s, 6.6, 4.8, 6.6, 5.55, color=TEAL)
text(s, 6.85, 5.05, 2.5, 0.4, [{'t': 'push notifications', 'size': 9, 'color': TEAL}])
arrow(s, 8.45, 3.15, 10.55, 1.8, color=TEAL)
text(s, 8.6, 2.0, 2.4, 0.4, [{'t': 'documents', 'size': 9, 'color': TEAL}])
text(s, 0.45, 6.55, 12.4, 0.6, [
    {'t': 'Level 1 processes: 1.0 Authentication · 2.0 KYC · 3.0 Project & Inventory · 4.0 Customer & Booking · 5.0 Commission · 6.0 Notification.  '
          'Data stores: D1 Brokers, D2 Projects/Plots, D3 Customers, D4 Bookings, D5 Commissions.', 'size': 10.5, 'color': GRAY},
])

# =========================================================================
# Slide 6 — Software Architecture & Major Modules
# =========================================================================
s = content_slide('Software Architecture & Major Modules')
layers = [
    ('Presentation Layer', 'Next.js + TypeScript — Broker & Admin web UI (responsive)', NAVY),
    ('API Layer', 'Django REST Framework — OTP/Token auth, REST endpoints', TEAL),
    ('Business / Application Modules', 'Auth · KYC · Project & Inventory · Customer · Booking · Commission · Notification · Support · Admin', GREEN),
    ('Data & External Services', 'PostgreSQL · Redis · AWS S3 · Firebase FCM · Google Maps · OTP/SMS Gateway', RGBColor(0x6A, 0x3F, 0x9E)),
]
y = 1.55
for name, desc, color in layers:
    rect(s, 0.45, y, 8.4, 1.05, fill=LIGHT, line=color, lw=1.5)
    rect(s, 0.45, y, 0.18, 1.05, fill=color)
    text(s, 0.8, y + 0.08, 7.9, 0.4, [{'t': name, 'size': 14, 'bold': True, 'color': NAVY}])
    text(s, 0.8, y + 0.5, 7.9, 0.5, [{'t': desc, 'size': 11, 'color': GRAY}])
    y += 1.25
# module list
rect(s, 9.15, 1.55, 3.73, 5.15, fill=RGBColor(0xF7, 0xF9, 0xFC), line=LINE)
text(s, 9.3, 1.65, 3.4, 0.4, [{'t': 'Major Modules', 'size': 14, 'bold': True, 'color': NAVY}])
text(s, 9.3, 2.1, 3.45, 4.5, [
    {'t': 'Authentication (OTP)', 'bullet': True},
    {'t': 'KYC Verification', 'bullet': True},
    {'t': 'Project & Inventory', 'bullet': True},
    {'t': 'Customer Management', 'bullet': True},
    {'t': 'Booking & Approval', 'bullet': True},
    {'t': 'Commission & TDS', 'bullet': True},
    {'t': 'Notification', 'bullet': True},
    {'t': 'Documents', 'bullet': True},
    {'t': 'Support Tickets', 'bullet': True},
    {'t': 'Admin & Reports', 'bullet': True},
], size=12)

# =========================================================================
# Slide 7 — Cohesion, Coupling & Design Considerations
# =========================================================================
s = content_slide('Module Cohesion, Coupling & Design Considerations')
col = 4.05
# Cohesion
rect(s, 0.45, 1.5, col, 5.35, fill=LIGHT, line=GREEN, lw=1.5)
rect(s, 0.45, 1.5, col, 0.5, fill=GREEN)
text(s, 0.6, 1.53, col - 0.3, 0.45, [{'t': 'Cohesion (High / Functional)', 'size': 14, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.65, 2.15, col - 0.45, 4.6, [
    {'t': 'Each module performs exactly one responsibility.', 'bullet': True},
    {'t': 'Authentication → only identity verification.', 'bullet': True, 'lvl': 1},
    {'t': 'KYC → only document/verification handling.', 'bullet': True, 'lvl': 1},
    {'t': 'Commission → only commission & TDS computation.', 'bullet': True, 'lvl': 1},
    {'t': 'Notification → only message delivery.', 'bullet': True, 'lvl': 1},
    {'t': 'Benefit: easier testing, reuse and maintenance.', 'bullet': True},
], size=12.5)
# Coupling
x2 = 4.78
rect(s, x2, 1.5, col, 5.35, fill=LIGHT, line=TEAL, lw=1.5)
rect(s, x2, 1.5, col, 0.5, fill=TEAL)
text(s, x2 + 0.15, 1.53, col - 0.3, 0.45, [{'t': 'Coupling (Low)', 'size': 14, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, x2 + 0.2, 2.15, col - 0.45, 4.6, [
    {'t': 'Modules communicate via clean interfaces.', 'bullet': True},
    {'t': 'Auth ↔ OTP gateway — message coupling.', 'bullet': True, 'lvl': 1},
    {'t': 'Booking ↔ Inventory — data coupling (plot status).', 'bullet': True, 'lvl': 1},
    {'t': 'Admin → Booking — control coupling (approve/reject).', 'bullet': True, 'lvl': 1},
    {'t': 'Benefit: change in one module minimally affects others.', 'bullet': True},
], size=12.5)
# Design considerations
x3 = 9.11
rect(s, x3, 1.5, col, 5.35, fill=LIGHT, line=AMBER, lw=1.5)
rect(s, x3, 1.5, col, 0.5, fill=AMBER)
text(s, x3 + 0.15, 1.53, col - 0.3, 0.45, [{'t': 'Design Considerations', 'size': 14, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, x3 + 0.2, 2.15, col - 0.45, 4.6, [
    {'t': 'Modularization & information hiding.', 'bullet': True},
    {'t': 'Abstraction: services hide implementation.', 'bullet': True},
    {'t': 'SOLID principles applied:', 'bullet': True},
    {'t': 'SRP, OCP, LSP, ISP, DIP.', 'bullet': True, 'lvl': 1},
    {'t': 'Object-oriented model: Broker, Project, Plot, Customer, Booking, Commission.', 'bullet': True},
    {'t': 'Top-down decomposition + bottom-up integration.', 'bullet': True},
], size=12.5)

# =========================================================================
# Slide 8 — SDLC Model
# =========================================================================
s = content_slide('SDLC Model Suitable for the System', 'Agile — incremental sprints with continuous feedback')
steps = ['Product\nBacklog', 'Sprint\nPlanning', 'Development', 'Testing', 'Sprint\nReview', 'Retrospective']
x = 0.5
sw = 1.85
gap = 0.19
for i, st in enumerate(steps):
    rx = x + i * (sw + gap)
    rect(s, rx, 1.7, sw, 1.2, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, rx, 1.7, sw, 1.2, [{'t': st, 'size': 12.5, 'bold': True, 'color': WHITE, 'align': PP_ALIGN.CENTER}],
         anchor=MSO_ANCHOR.MIDDLE)
    if i < len(steps) - 1:
        arrow(s, rx + sw, 2.3, rx + sw + gap, 2.3, color=TEAL)
arrow(s, 12.0, 3.0, 12.0, 3.7, color=TEAL)
arrow(s, 12.0, 3.7, 1.4, 3.7, color=TEAL)
arrow(s, 1.4, 3.7, 1.4, 2.9, color=TEAL)
text(s, 4.6, 3.52, 5.0, 0.4, [{'t': 'Next sprint (iterative loop)', 'size': 11, 'color': TEAL, 'align': PP_ALIGN.CENTER}])

rect(s, 0.45, 4.15, 12.43, 2.7, fill=LIGHT, line=LINE)
text(s, 0.65, 4.25, 12.0, 0.4, [{'t': 'Justification', 'size': 14, 'bold': True, 'color': NAVY}])
text(s, 0.65, 4.7, 6.0, 2.0, [
    {'t': 'Requirements evolve — Agile supports change through short sprints.', 'bullet': True},
    {'t': 'Delivers working increments early (auth → inventory → booking → commission).', 'bullet': True},
    {'t': 'Continuous testing and broker feedback improve quality.', 'bullet': True},
], size=12.5)
text(s, 6.9, 4.7, 5.85, 2.0, [
    {'t': 'Two-member team suits short, focused iterations.', 'bullet': True},
    {'t': 'Sprint plan (1–6): setup → DB/login/KYC → inventory → booking → commission → notifications.', 'bullet': True},
    {'t': 'Git feature branches + pull requests enable collaboration.', 'bullet': True},
], size=12.5)

# =========================================================================
# Slide 9 — Challenges, Security & Improvements
# =========================================================================
s = content_slide('Major Challenges, Security Concerns & Improvements')
col = 4.05
# Challenges
rect(s, 0.45, 1.5, col, 5.35, fill=LIGHT, line=RED, lw=1.5)
rect(s, 0.45, 1.5, col, 0.5, fill=RED)
text(s, 0.6, 1.53, col - 0.3, 0.45, [{'t': 'Major Challenges', 'size': 14, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.65, 2.15, col - 0.45, 4.6, [
    {'t': 'Ensuring real-time plot availability accuracy.', 'bullet': True},
    {'t': 'Preventing double booking of the same plot.', 'bullet': True},
    {'t': 'Handling KYC document uploads and validation.', 'bullet': True},
    {'t': 'Integrating multiple third-party services (OTP, S3, maps, FCM).', 'bullet': True},
    {'t': 'Accurate commission and TDS computation.', 'bullet': True},
], size=12.5)
# Security
x2 = 4.78
rect(s, x2, 1.5, col, 5.35, fill=LIGHT, line=NAVY, lw=1.5)
rect(s, x2, 1.5, col, 0.5, fill=NAVY)
text(s, x2 + 0.15, 1.53, col - 0.3, 0.45, [{'t': 'Security Concerns', 'size': 14, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, x2 + 0.2, 2.15, col - 0.45, 4.6, [
    {'t': 'OTP reuse / brute-force attempts.', 'bullet': True},
    {'t': 'Protecting sensitive KYC & bank data.', 'bullet': True},
    {'t': 'Role-based access for admin functions.', 'bullet': True},
    {'t': 'Secure document storage (S3, encryption).', 'bullet': True},
    {'t': 'HTTPS everywhere; no secrets in logs.', 'bullet': True},
], size=12.5)
# Improvements
x3 = 9.11
rect(s, x3, 1.5, col, 5.35, fill=LIGHT, line=GREEN, lw=1.5)
rect(s, x3, 1.5, col, 0.5, fill=GREEN)
text(s, x3 + 0.15, 1.53, col - 0.3, 0.45, [{'t': 'Possible Improvements', 'size': 14, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, x3 + 0.2, 2.15, col - 0.45, 4.6, [
    {'t': 'Integrated payment gateway & digital demand letters.', 'bullet': True},
    {'t': 'QR-based booking and biometric login.', 'bullet': True},
    {'t': 'Analytics dashboard for sales & inventory.', 'bullet': True},
    {'t': 'Offline/PWA support and native mobile app.', 'bullet': True},
    {'t': 'AI-based lead & price recommendations.', 'bullet': True},
], size=12.5)

# =========================================================================
# Slide 10 — Key Learnings & Conclusion
# =========================================================================
s = content_slide('Key Learnings & Conclusion')
rect(s, 0.45, 1.5, 6.0, 5.35, fill=LIGHT, line=NAVY, lw=1.5)
rect(s, 0.45, 1.5, 6.0, 0.5, fill=NAVY)
text(s, 0.6, 1.53, 5.7, 0.45, [{'t': 'Key Learnings', 'size': 15, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.65, 2.15, 5.65, 4.6, [
    {'t': 'Applied the full SDLC: requirements → design → implementation.', 'bullet': True},
    {'t': 'Wrote a structured SRS and traced it to user stories.', 'bullet': True},
    {'t': 'Modelled actors, use cases and data flows.', 'bullet': True},
    {'t': 'Understood modularity, high cohesion and low coupling.', 'bullet': True},
    {'t': 'Practised Agile sprints and Git/GitHub collaboration.', 'bullet': True},
    {'t': 'Learned secure design for sensitive broker and KYC data.', 'bullet': True},
], size=12.5)
rect(s, 6.78, 1.5, 6.1, 5.35, fill=RGBColor(0xE4, 0xF2, 0xEF), line=TEAL, lw=1.5)
rect(s, 6.78, 1.5, 6.1, 0.5, fill=TEAL)
text(s, 6.93, 1.53, 5.8, 0.45, [{'t': 'Conclusion', 'size': 15, 'bold': True, 'color': WHITE}],
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 6.98, 2.15, 5.75, 4.6, [
    {'t': 'InventoryOne digitises real-estate plot booking for brokers.', 'bullet': True},
    {'t': 'Provides live inventory, digital bookings and transparent commissions.', 'bullet': True},
    {'t': 'A modular, secure, scalable and maintainable web application.', 'bullet': True},
    {'t': 'Built iteratively with Agile, enabling continuous improvement.', 'bullet': True},
    {'t': 'Foundation ready for payments, analytics and mobile expansion.', 'bullet': True},
], size=12.5)

out = '/Users/ayushi/college/InventoryOne/docs/presentation/InventoryOne-Presentation.pptx'
prs.save(out)
print('Saved:', out, '| slides:', len(prs.slides._sldIdLst))
