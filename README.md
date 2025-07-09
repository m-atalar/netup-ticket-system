# NetUP Destek Takip Sistemi

NetUP ERP Destek Takip Sistemi, müşteri destek taleplerini kayıt altına almak, yönetmek, filtrelemek, görselleştirmek ve raporlamak amacıyla geliştirilmiş bir web uygulamasıdır.

## 🚀 Özellikler

- 🔐 Rol Tabanlı Giriş Sistemi (Admin / Agent)
- 📝 Yeni destek talebi oluşturma (agent ve admin)
- 📋 Tüm talepleri listeleme (sadece admin)
- 🔎 Arama ve durum filtreleme
- 🧭 Mini Dashboard (istatistik kartları + son talep kutusu)
- 📊 Grafik ile talepleri görselleştirme (Chart.js)
- 📁 CSV ve PDF çıktısı alma (filtreli veri dahil)
- 🔁 Durum güncelleme, düzenleme, silme (admin için)
- 👤 Agent’lar sadece kendi taleplerini görebilir
- 💡 Bootstrap 5 ile responsive ve kullanıcı dostu arayüz
- 🧱 Jinja2 ve `base.html` ile şablon mirası (template inheritance)

## 👥 Giriş Bilgileri (Demo)

| Rol     | Kullanıcı Adı | Şifre     |
|---------|----------------|-----------|
| Admin   | `admin`        | `admin123`|
| Agent   | `agent`        | `agent123`|

## ⚙️ Kullanılan Teknolojiler

- Python 3 + Flask
- Flask-Login
- Flask-Migrate + SQLAlchemy
- SQLite (geliştirme aşamasında)
- Bootstrap 5
- Chart.js
- PDFKit + wkhtmltopdf

## 🧪 Kurulum

```bash
git clone https://github.com/m-atalar/netup-ticket-system.git
cd netup-ticket-system
python -m venv venv
venv\Scripts\activate   # (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
