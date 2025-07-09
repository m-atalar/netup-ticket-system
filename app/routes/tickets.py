from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, abort
from flask_login import login_required, current_user
from app.models import db, Ticket
from datetime import datetime
import csv, io, pdfkit
from functools import wraps

bp = Blueprint('tickets', __name__, url_prefix='/ticket')

def check_permission(ticket):
    if current_user.role == 'admin':
        return  # Her şeye erişebilir
    if current_user.role == 'agent' and ticket.contact_name == current_user.username:
        return  # Sadece kendi talebine erişebilir
    abort(403)  # Diğer durumlarda erişim reddedilir

# 🔐 Admin yetkisi gerektiren işlemler için
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# 🎫 Yeni destek talebi oluştur
@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        company_name = request.form['company_name']
        # Eğer giriş yapan agent ise onun bilgileriyle doldur
        if current_user.role == 'agent':
            contact_name = current_user.username
            email = current_user.email
        else:
            contact_name = request.form['contact_name']
            email = request.form['email']
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        priority = request.form['priority']

        ticket = Ticket(
            company_name=company_name,
            contact_name=contact_name,
            email=email,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status='Bekliyor',
            created_at=datetime.utcnow()
        )

        db.session.add(ticket)
        db.session.commit()

        flash("Destek talebiniz başarıyla oluşturuldu.", "success")
        return redirect(url_for('tickets.create_ticket'))

    return render_template('ticket_form.html')

# 🧭 Dashboard sayfası
@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total = Ticket.query.count()
    waiting = Ticket.query.filter_by(status='Bekliyor').count()
    working = Ticket.query.filter_by(status='Üzerinde Çalışılıyor').count()
    resolved = Ticket.query.filter_by(status='Çözüldü').count()
    last_ticket = Ticket.query.order_by(Ticket.created_at.desc()).first()

    return render_template('dashboard.html', total=total, waiting=waiting, working=working, resolved=resolved, last_ticket=last_ticket)

# 📋 Tüm talepler (filtreleme + grafik)
@bp.route('/admin/tickets')
@login_required
@admin_required
def list_tickets():
    q = request.args.get('q', '').lower()
    status_filter = request.args.get('status', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = Ticket.query

    if q:
        query = query.filter(
            (Ticket.company_name.ilike(f'%{q}%')) |
            (Ticket.title.ilike(f'%{q}%')) |
            (Ticket.status.ilike(f'%{q}%'))
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at <= end)
        except ValueError:
            pass

    tickets = query.order_by(Ticket.created_at.desc()).all()

    # Grafik verisi
    status_counts = {'Bekliyor': 0, 'Üzerinde Çalışılıyor': 0, 'Çözüldü': 0}
    for t in tickets:
        if t.status in status_counts:
            status_counts[t.status] += 1

    chart_labels = list(status_counts.keys())
    chart_data = list(status_counts.values())

    return render_template('admin_ticket_list.html',
                           tickets=tickets,
                           chart_labels=chart_labels,
                           chart_data=chart_data)

# 🔁 Durum güncelle
@bp.route('/admin/tickets/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_ticket_status(id):
    ticket = Ticket.query.get_or_404(id)

    if ticket.status == 'Bekliyor':
        ticket.status = 'Üzerinde Çalışılıyor'
    elif ticket.status == 'Üzerinde Çalışılıyor':
        ticket.status = 'Çözüldü'
    elif ticket.status == 'Çözüldü':
        ticket.status = 'Bekliyor'

    db.session.commit()
    flash(f"Ticket #{ticket.id} durumu güncellendi: {ticket.status}", "info")
    return redirect(url_for('tickets.list_tickets'))

# 📤 CSV dışa aktar
@bp.route('/admin/tickets/export')
@login_required
@admin_required
def export_tickets():
    q = request.args.get('q', '').lower()
    status_filter = request.args.get('status', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = Ticket.query

    if q:
        query = query.filter(
            (Ticket.company_name.ilike(f'%{q}%')) |
            (Ticket.title.ilike(f'%{q}%')) |
            (Ticket.status.ilike(f'%{q}%'))
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at <= end)
        except ValueError:
            pass

    tickets = query.order_by(Ticket.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Firma', 'İlgili Kişi', 'Konu', 'Durum', 'Aciliyet', 'Tarih'])

    for t in tickets:
        writer.writerow([
            t.id,
            t.company_name,
            t.contact_name,
            t.title,
            t.status,
            t.priority,
            t.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=tickets.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

# 📄 PDF rapor
@bp.route('/admin/tickets/report')
@login_required
@admin_required
def export_report_pdf():
    q = request.args.get('q', '').lower()
    status_filter = request.args.get('status', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = Ticket.query

    if q:
        query = query.filter(
            (Ticket.company_name.ilike(f'%{q}%')) |
            (Ticket.title.ilike(f'%{q}%')) |
            (Ticket.status.ilike(f'%{q}%'))
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at <= end)
        except ValueError:
            pass

    tickets = query.order_by(Ticket.created_at.desc()).all()

    date_range_str = ""
    if start_date and end_date:
        date_range_str = f"{start_date} - {end_date}"
    elif start_date:
        date_range_str = f"{start_date} sonrası"
    elif end_date:
        date_range_str = f"{end_date} öncesi"
    else:
        date_range_str = "Tüm Kayıtlar"

    rendered = render_template('report_template.html', tickets=tickets, now=datetime.utcnow(), date_range=date_range_str)
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=destek_raporu.pdf'
    return response

@bp.route('/my-tickets')
@login_required
def my_tickets():
    q = request.args.get('q', '').lower()

    query = Ticket.query.filter_by(contact_name=current_user.username)

    if q:
        query = query.filter(
            (Ticket.company_name.ilike(f'%{q}%')) |
            (Ticket.title.ilike(f'%{q}%')) |
            (Ticket.status.ilike(f'%{q}%'))
        )

    tickets = query.order_by(Ticket.created_at.desc()).all()

    # 🔢 İstatistikler
    total = len(tickets)
    waiting = len([t for t in tickets if t.status == 'Bekliyor'])
    working = len([t for t in tickets if t.status == 'Üzerinde Çalışılıyor'])
    resolved = len([t for t in tickets if t.status == 'Çözüldü'])

    last_ticket = tickets[0] if tickets else None

    return render_template(
        'my_tickets.html',
        tickets=tickets,
        total=total,
        waiting=waiting,
        working=working,
        resolved=resolved,
        last_ticket=last_ticket
    )



@bp.route('/admin/tickets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    check_permission(ticket)

    if request.method == 'POST':
        ticket.company_name = request.form['company_name']
        ticket.contact_name = request.form['contact_name']
        ticket.email = request.form['email']
        ticket.title = request.form['title']
        ticket.description = request.form['description']
        ticket.category = request.form['category']
        ticket.priority = request.form['priority']
        ticket.status = request.form['status']

        db.session.commit()
        flash(f"Ticket #{ticket.id} güncellendi.", "success")
        return redirect(url_for('tickets.list_tickets'))

    return render_template('edit_ticket.html', ticket=ticket)

@bp.route('/admin/tickets/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    check_permission(ticket)
    db.session.delete(ticket)
    db.session.commit()
    flash(f"Ticket #{ticket.id} silindi.", "warning")
    return redirect(url_for('tickets.list_tickets'))
