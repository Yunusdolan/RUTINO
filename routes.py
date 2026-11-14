# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app, send_from_directory
import hmac
from datetime import datetime,timedelta,time
from database import db
from models import Kullanici, Aliskanlik, Sikayet
import os
import base64
from werkzeug.utils import secure_filename
from sqlalchemy import func
from badge_rules import BADGE_RULES
from werkzeug.security import generate_password_hash, check_password_hash


routes = Blueprint('routes', __name__)



KATEGORI_PUAN = {
    "ders": 1,
    "spor": 2,
    "saglik": 2,
    "kisisel_gelisim": 1
}



# =====================
# YARDIMCI FONKSİYONLAR
# =====================
def is_logged_in():
    return 'logged_in' in session or 'admin_logged_in' in session

def get_current_user():
    if 'logged_in' in session:
        return Kullanici.query.filter_by(email=session.get('email')).first()
    return None

def seviye_hesapla(puan):
    if puan < 10:
        return "Başlangıç Çaylak"
    elif puan < 25:
        return "Kararlı Başlangıç"
    elif puan < 50:
        return "Disiplinli Gelişen"
    elif puan < 80:
        return "Alışkanlık Ustası"
    else:
        return "Efsane Seviye "

# LOGIN
@routes.route('/', methods=['GET', 'POST'])
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return send_from_directory(
            os.path.join(current_app.root_path, 'static', 'react'),
            'index.html'
        )

    email = request.form.get('email')
    password = request.form.get('password')

    kullanici = Kullanici.query.filter_by(email=email).first()

    if kullanici and check_password_hash(kullanici.sifre, password):
        session['logged_in'] = True
        session['email'] = kullanici.email
        session['kullanici_id'] = kullanici.id
        return redirect(url_for('routes.dashboard'))

    flash("Hatalı e-posta veya şifre.", "danger")
    return redirect(url_for('routes.login'))


# REGISTER
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if Kullanici.query.filter_by(email=email).first():
            flash("Bu e-posta zaten kayıtlı.", "danger")
            return render_template('register.html')

        if Kullanici.query.filter_by(kullanici_adi=username).first():
            flash("Bu kullanıcı adı zaten kullanımda.", "danger")
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        yeni = Kullanici(
            kullanici_adi=username,
            email=email,
            sifre=hashed_password
        )

        db.session.add(yeni)
        db.session.commit()

        flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
        return redirect(url_for('routes.login'))

    return render_template('register.html')

# DASHBOARD
@routes.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('routes.login'))

    kullanici = get_current_user()
    if not kullanici:
        return redirect(url_for('routes.logout'))

    bugun = datetime.now().strftime("%Y-%m-%d")

    tum_aliskanliklar = Aliskanlik.query.filter_by(
        kullanici_id=kullanici.id
    ).all()

    mevcut_aliskanliklar = []
    tamamlanan_aliskanliklar = []

    for alis in tum_aliskanliklar:
        if alis.tamamlama_tarihleri and bugun in alis.tamamlama_tarihleri:
            tamamlanan_aliskanliklar.append(alis)
        else:
            mevcut_aliskanliklar.append(alis)

    CATEGORY_COLORS = {
        "ders": "#0d6efd",
        "spor": "#198754",
        "saglik": "#dc3545",
        "kisisel_gelisim": "#6f42c1"
    }


    calendar_events = []

    for alis in mevcut_aliskanliklar:
        if not alis.tarih:
            continue

        calendar_events.append({
            "title": alis.ad.upper(),
            "start": alis.tarih,
            "backgroundColor": CATEGORY_COLORS.get(alis.kategori, "#0d6efd"),
            "borderColor": CATEGORY_COLORS.get(alis.kategori, "#0d6efd"),
            "textColor": "#ffffff"
        })



    return render_template(
        'dashboard.html',
        user=kullanici,
        mevcut_aliskanliklar=mevcut_aliskanliklar,
        tamamlanan_aliskanliklar=tamamlanan_aliskanliklar,
        bugun=bugun,
        calendar_events=calendar_events
    )


# API: Kullanıcı detaylarını getir
@routes.route('/api/get_user_details')
def api_get_user_details():
    if 'admin_logged_in' not in session:
        return jsonify({"error": "Admin olarak giriş yapın."}), 403

    eposta = request.args.get('eposta')
    kullanici = Kullanici.query.filter_by(email=eposta).first()

    if not kullanici:
        return jsonify({"error": "Kullanıcı bulunamadı."})

    # Kullanıcının alışkanlıkları
    aliskanliklar = []
    for a in Aliskanlik.query.filter_by(kullanici_id=kullanici.id).all():
        aliskanliklar.append({
            "id": a.id,
            "ad": a.ad,
            "kategori": a.kategori,
            "siklik": a.siklik,
            "tamamlama_tarihleri": [
                tarih.tarih if hasattr(tarih, "tarih") else tarih
                for tarih in getattr(a, "tamamlama_tarihleri", [])
            ]
        })

    return jsonify({
        "user": {
            "id": kullanici.id,
            "kullanici_adi": kullanici.kullanici_adi,
            "eposta": kullanici.email,
            "puan": kullanici.puan,
            "seviye": kullanici.seviye,
            "aliskanliklar": aliskanliklar
        }
    })


#ALIŞKANLIK EKLEME
@routes.route('/add_habit', methods=['POST'])
def add_habit():
    if 'logged_in' not in session:
        return redirect(url_for('routes.login'))

    kullanici = get_current_user()
    if not kullanici:
        return redirect(url_for('routes.logout'))

    ad = request.form.get('ad')
    kategori = request.form.get('kategori')
    siklik = request.form.get('siklik')
    tarih = request.form.get('tarih')   # YYYY-MM-DD
    saat = request.form.get('saat')     # HH:MM

    #  Tarih & saat zorunlu
    if not tarih or not saat:
        flash("Tarih ve saat seçmelisiniz.", "danger")
        return redirect(url_for('routes.dashboard'))

    #  TARİH + SAAT BİRLEŞTİRME
    secilen_datetime = datetime.strptime(
        f"{tarih} {saat}",
        "%Y-%m-%d %H:%M"
    )

    simdi = datetime.now()

    #  Geçmiş datetime engeli
    if secilen_datetime < simdi:
        flash("Geçmiş bir tarih veya saat için alışkanlık ekleyemezsiniz.", "danger")
        return redirect(url_for('routes.dashboard'))

    #  Aynı isim kontrolü
    if Aliskanlik.query.filter_by(kullanici_id=kullanici.id, ad=ad).first():
        flash(f"'{ad}' adlı alışkanlık zaten var.", "warning")
        return redirect(url_for('routes.dashboard'))

    yeni = Aliskanlik(
        kullanici_id=kullanici.id,
        ad=ad,
        kategori=kategori,
        siklik=siklik,
        tarih=tarih,   # istersen date olarak da ayırabiliriz
        saat=saat,
        tamamlama_tarihleri=[]
    )

    db.session.add(yeni)
    db.session.commit()

    flash(f"'{ad}' alışkanlığı eklendi.", "success")
    return redirect(url_for('routes.dashboard'))

# ALIŞKANLIK TAMAMLAMA
@routes.route('/complete_habit/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    if 'logged_in' not in session:
        return redirect(url_for('routes.login'))

    alis = Aliskanlik.query.get(habit_id)
    kullanici = get_current_user()
    today = datetime.now().strftime("%Y-%m-%d")

    if alis and kullanici:
        if not alis.tamamlama_tarihleri:
            alis.tamamlama_tarihleri = []

        if today not in alis.tamamlama_tarihleri:
            # alışkanlığı tamamla
            alis.tamamlama_tarihleri.append(today)

            #  kategoriye göre puan ekle
            puan_ekle = KATEGORI_PUAN.get(alis.kategori, 1)
            kullanici.puan += puan_ekle

            #  seviye güncelle
            kullanici.seviye = seviye_hesapla(kullanici.puan)
            # ROZET KONTROLÜ (TEK SATIR)
            rozet_kontrol(kullanici)
            db.session.commit()

            flash(
                f"'{alis.ad}' tamamlandı! +{puan_ekle} puan kazandın 🎉",
                "success"
            )
        else:
            flash("Bu alışkanlık bugün zaten tamamlandı.", "info")

    return redirect(url_for('routes.dashboard'))


#ALIŞKANLIK SİLME
@routes.route('/delete_habit/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    if not session.get('logged_in'):
        return redirect(url_for('routes.login'))

    alis = Aliskanlik.query.filter_by(
        id=habit_id,
        kullanici_id=session['kullanici_id']
    ).first()

    if not alis:
        flash("Alışkanlık bulunamadı.", "danger")
        return redirect(url_for('routes.dashboard'))

    ad = alis.ad  # silmeden önce sakla
    db.session.delete(alis)
    db.session.commit()

    flash(f"'{ad}' silindi.", "info")
    return redirect(url_for('routes.dashboard'))

#ALIŞKANLIK GÜNCELLEME
@routes.route('/update_habit/<int:habit_id>', methods=['POST'])
def update_habit(habit_id):
    if not session.get('logged_in'):
        return redirect(url_for('routes.login'))

    alis = Aliskanlik.query.filter_by(
        id=habit_id,
        kullanici_id=session['kullanici_id']
    ).first()

    if not alis:
        flash("Alışkanlık bulunamadı.", "danger")
        return redirect(url_for('routes.dashboard'))

    ad = request.form.get('ad')
    if not ad:
        flash("Alışkanlık adı boş bırakılamaz.", "warning")
        return redirect(url_for('routes.dashboard'))

    alis.ad = ad
    alis.kategori = request.form.get('kategori')
    alis.tarih = request.form.get('tarih')
    alis.saat = request.form.get('saat')
    alis.siklik = request.form.get('siklik')

    db.session.commit()
    flash(f"'{alis.ad}' başarıyla güncellendi.", "success")

    return redirect(url_for('routes.dashboard'))

@routes.route('/rozetler')
def rozetler():
    if 'logged_in' not in session:
        return redirect(url_for('routes.login'))

    user = get_current_user()
    rozetler = get_user_badges(user.id)   

    return render_template(
        "rozetler.html",
        user=user,
        rozetler=rozetler
    )


#ROZET KONTROL FONKSİYONU
def rozet_kontrol(user):
    rozetler = get_user_badges(user.id)

    yeni_kazanilanlar = []

    for r in rozetler:
        if r["tamamlandi"]:
            yeni_kazanilanlar.append(r["ad"])

    return yeni_kazanilanlar


def get_user_badges(user_id):
    habits = Aliskanlik.query.filter_by(kullanici_id=user_id).all()

    counts = {
        "spor": 0,
        "ders": 0,
        "kisisel_gelisim": 0,
        "saglik": 0,
        "gece": 0,
        "sabah": 0
    }

    for habit in habits:
        if not habit.tamamlama_tarihleri:
            continue

        for t in habit.tamamlama_tarihleri:
            dt = None

            # Tarih + Saat
            if len(t) == 16:  
                dt = datetime.strptime(t, "%Y-%m-%d %H:%M")

            # Sadece Tarih
            elif len(t) == 10:  # YYYY-MM-DD
                dt = datetime.strptime(t, "%Y-%m-%d")

            else:
                continue

            #  Saat rozetleri 
            if len(t) == 16:
                saat = dt.time()

                if saat >= time(20, 0):
                    counts["gece"] += 1

                if saat < time(9, 0):
                    counts["sabah"] += 1

            # Tanımlı kategoriler için kategori rozetlerini say.
            if habit.kategori in counts:
                counts[habit.kategori] += 1

    result = []

    for badge in BADGE_RULES:
        mevcut = counts.get(badge["kategori"], 0)
        yuzde = min(int((mevcut / badge["hedef"]) * 100), 100)

        result.append({
            "ad": badge["ad"],
            "aciklama": badge["aciklama"],
            "kategori": badge["kategori"],
            "mevcut": mevcut,
            "hedef": badge["hedef"],
            "yuzde": yuzde,
            "tamamlandi": mevcut >= badge["hedef"]
        })

    return result



# ADMIN LOGIN
@routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return send_from_directory(
            os.path.join(current_app.root_path, 'static', 'react'),
            'index.html'
        )

    email = (request.form.get('email') or '').strip()
    password = request.form.get('password') or ''

    admin_email = current_app.config['ADMIN_EMAIL']
    admin_password = current_app.config['ADMIN_PASSWORD']

    email_valid = hmac.compare_digest(
        email.lower(),
        admin_email.lower()
    )

    password_valid = hmac.compare_digest(
        password,
        admin_password
    )

    if email_valid and password_valid:
        session.clear()
        session['admin_logged_in'] = True
        session.permanent = True

        return redirect(url_for('routes.admin_dashboard'))

    flash("Hatalı admin e-posta veya şifre", "danger")
    return redirect(url_for('routes.admin_login'))



# ADMIN DASHBOARD
@routes.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('routes.admin_login'))

    users = Kullanici.query.all()
    sikayetler = Sikayet.query.all()

    return render_template(
        "admin_dashboard.html",
        users=users,
        sikayetler=sikayetler
    )

# ADMIN: KULLANICI SİL
@routes.route('/admin_delete_user/<int:kullanici_id>', methods=['POST'])
def admin_delete_user(kullanici_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('routes.admin_login'))

    kullanici = Kullanici.query.get_or_404(kullanici_id)
    db.session.delete(kullanici)
    db.session.commit()

    flash("Kullanıcı silindi", "success")
    return redirect(url_for('routes.admin_dashboard'))


#ADMİN ALIŞKANLIK SİLME
@routes.route('/admin_delete_habit/<int:habit_id>', methods=['POST'])
def admin_delete_habit(habit_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('routes.admin_login'))

    aliskanlik = Aliskanlik.query.get(habit_id)
    if aliskanlik:
        db.session.delete(aliskanlik)
        db.session.commit()

        db.session.expire_all()  

        flash("Alışkanlık silindi", "success")

    return redirect(url_for('routes.admin_dashboard'))



# ADMIN: ŞİKAYET SİL
@routes.route('/admin_delete_sikayet/<int:sikayet_id>', methods=['POST'])
def admin_delete_sikayet(sikayet_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('routes.admin_login'))

    sikayet = Sikayet.query.get_or_404(sikayet_id)
    db.session.delete(sikayet)
    db.session.commit()

    flash("Şikayet silindi", "success")
    return redirect(url_for('routes.admin_dashboard'))


#PROFİL GÖRÜNTÜLEME VE GÜNCELLEME
@routes.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'logged_in' not in session:
        return redirect(url_for('routes.login'))

    kullanici = get_current_user()
    if not kullanici:
        return redirect(url_for('routes.logout'))

    if request.method == 'POST':
        kullanici.ad_soyad = request.form.get('ad_soyad')
        kullanici.email = request.form.get('email')
        kullanici.telefon = request.form.get('telefon')

        file = request.files.get('profil_foto')
        if file and file.filename:
            from uuid import uuid4
            filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
            file.save(os.path.join('static/uploads', filename))
            kullanici.profil_foto = filename

        db.session.commit()
        flash("Profiliniz başarıyla güncellendi!", "success")
        return redirect(url_for('routes.profil'))

    return render_template('profil.html', user=kullanici)



#ŞİFRE GÜNCELLEME
@routes.route('/change_password', methods=['POST'])
def change_password():
    if 'logged_in' not in session:
        return redirect(url_for('routes.login'))

    kullanici = get_current_user()
    if not kullanici:
        return redirect(url_for('routes.logout'))

    mevcut_sifre = request.form.get('current_password')
    yeni_sifre = request.form.get('new_password')
    yeni_sifre_tekrar = request.form.get('confirm_password')

    if not check_password_hash(kullanici.sifre, mevcut_sifre):
        flash("Mevcut şifre yanlış.", "danger")
        return redirect(url_for('routes.profil'))

    if yeni_sifre != yeni_sifre_tekrar:
        flash("Yeni şifreler eşleşmiyor.", "warning")
        return redirect(url_for('routes.profil'))

    kullanici.sifre = generate_password_hash(yeni_sifre)
    db.session.commit()

    flash("Şifre başarıyla güncellendi!", "success")
    return redirect(url_for('routes.profil'))


#Şikayet Gönderme
@routes.route('/send_complaint', methods=['POST'])
def send_complaint():
    if 'logged_in' not in session:
        return redirect(url_for('routes.login'))

    kullanici = get_current_user()

    mesaj = request.form.get('mesaj')
    tarih = datetime.now().strftime("%Y-%m-%d")

    yeni_sikayet = Sikayet(
        ad_soyad = kullanici.ad_soyad or kullanici.kullanici_adi,
        email = kullanici.email,
        mesaj = mesaj,
        tarih = tarih
    )

    db.session.add(yeni_sikayet)
    db.session.commit()

    flash("Şikayetiniz başarıyla iletildi. Teşekkür ederiz!", "success")
    return redirect(url_for('routes.dashboard'))

# LOGOUT
@routes.route('/logout')
def logout():
    session.clear()   
    flash("Çıkış yapıldı", "info")
    return redirect(url_for('routes.login'))





# =====================
# REACT AUTH API
# Mevcut HTML tabanli login/register rotalari korunur.
# React arayuzu bu JSON endpoint'lerini kullanir.
# =====================
@routes.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    if not session.get('logged_in'):
        return jsonify({"authenticated": False, "user": None}), 200

    kullanici = get_current_user()
    if not kullanici:
        session.clear()
        return jsonify({"authenticated": False, "user": None}), 200

    return jsonify({
        "authenticated": True,
        "user": {
            "id": kullanici.id,
            "username": kullanici.kullanici_adi,
            "name": kullanici.ad_soyad,
            "email": kullanici.email,
            "points": kullanici.puan,
            "level": kullanici.seviye,
            "profile_photo": kullanici.profil_foto
        }
    })


@routes.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({"message": "E-posta ve şifre zorunludur."}), 400

    kullanici = Kullanici.query.filter(
        func.lower(Kullanici.email) == email
    ).first()

    if not kullanici or not check_password_hash(kullanici.sifre, password):
        return jsonify({"message": "E-posta veya şifre hatalı."}), 401

    session.clear()
    session['logged_in'] = True
    session['email'] = kullanici.email
    session['kullanici_id'] = kullanici.id

    return jsonify({
        "message": "Giriş başarılı.",
        "user": {
            "id": kullanici.id,
            "username": kullanici.kullanici_adi,
            "name": kullanici.ad_soyad,
            "email": kullanici.email,
            "points": kullanici.puan,
            "level": kullanici.seviye,
            "profile_photo": kullanici.profil_foto
        }
    })


@routes.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not username or not email or not password:
        return jsonify({"message": "Tüm alanları doldurmalısınız."}), 400

    if len(username) < 3:
        return jsonify({"message": "Kullanıcı adı en az 3 karakter olmalıdır."}), 400

    if len(password) < 6:
        return jsonify({"message": "Şifre en az 6 karakter olmalıdır."}), 400

    if Kullanici.query.filter(func.lower(Kullanici.email) == email).first():
        return jsonify({"message": "Bu e-posta zaten kayıtlı."}), 409

    if Kullanici.query.filter_by(kullanici_adi=username).first():
        return jsonify({"message": "Bu kullanıcı adı zaten kullanımda."}), 409

    yeni = Kullanici(
        kullanici_adi=username,
        email=email,
        sifre=generate_password_hash(password)
    )
    db.session.add(yeni)
    db.session.commit()

    return jsonify({
        "message": "Kayıt başarılı! Şimdi giriş yapabilirsiniz."
    }), 201


@routes.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    session.clear()
    return jsonify({"message": "Oturum kapatıldı."}), 200


# React frontend ve geliştirme ortamı için basit servis kontrolü.
@routes.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'ok',
        'message': 'Flask backend bağlantısı başarılı.'
    })

# ==========================================
# RUTINO - REACT DASHBOARD API
# ==========================================

def habit_to_dict(habit, today):
    dates = habit.tamamlama_tarihleri or []

    return {
        "id": habit.id,
        "name": habit.ad,
        "category": habit.kategori,
        "frequency": habit.siklik,
        "date": habit.tarih,
        "time": habit.saat,
        "completed_today": today in dates
    }


@routes.route('/api/dashboard', methods=['GET'])
def api_dashboard():

    if not session.get('logged_in'):
        return jsonify({"message": "Oturum açmalısınız."}), 401

    user = get_current_user()

    if not user:
        return jsonify({"message": "Kullanıcı bulunamadı."}), 404

    today = datetime.now().date()
    today_string = today.strftime("%Y-%m-%d")

    habits = Aliskanlik.query.filter_by(
        kullanici_id=user.id
    ).all()

    active = []
    completed = []

    for habit in habits:
        item = habit_to_dict(habit, today_string)

        if item["completed_today"]:
            completed.append(item)
        else:
            active.append(item)

    # Son 7 günlük ilerleme
    weekly_data = []

    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        day_string = day.strftime("%Y-%m-%d")

        completed_count = sum(
            1 for habit in habits
            if day_string in (habit.tamamlama_tarihleri or [])
        )

        weekly_data.append({
            "date": day_string,
            "day": day.strftime("%a"),
            "completed": completed_count
        })

    weekly_total = sum(
        item["completed"] for item in weekly_data
    )

    possible_total = len(habits) * 7

    weekly_progress = (
        round((weekly_total / possible_total) * 100)
        if possible_total > 0 else 0
    )

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.kullanici_adi,
            "email": user.email,
            "points": user.puan,
            "level": user.seviye,
            "profile_photo": user.profil_foto
        },
        "active_habits": active,
        "completed_habits": completed,
        "weekly_data": weekly_data,
        "weekly_progress": weekly_progress,
        "today": today_string
    })


# ==========================================
# ALIŞKANLIK EKLEME
# ==========================================

@routes.route('/api/habits', methods=['POST'])
def api_add_habit():

    if not session.get('logged_in'):
        return jsonify({"message": "Oturum açmalısınız."}), 401

    user = get_current_user()
    data = request.get_json(silent=True) or {}

    if not user:
        return jsonify({"message": "Kullanıcı bulunamadı."}), 404

    name = (data.get("name") or "").strip()
    category = data.get("category")
    frequency = data.get("frequency")
    habit_date = data.get("date")
    habit_time = data.get("time")

    if not all([name, category, frequency, habit_date, habit_time]):
        return jsonify({"message": "Tüm alanları doldurun."}), 400

    if category not in KATEGORI_PUAN:
        return jsonify({"message": "Geçersiz kategori."}), 400

    if frequency not in ["gunluk", "haftalik"]:
        return jsonify({"message": "Geçersiz sıklık."}), 400

    try:
        selected = datetime.strptime(
            f"{habit_date} {habit_time}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return jsonify({"message": "Geçersiz tarih veya saat."}), 400

    if selected < datetime.now():
        return jsonify({"message": "Geçmiş bir tarih seçemezsiniz."}), 400

    existing = Aliskanlik.query.filter_by(
        kullanici_id=user.id,
        ad=name
    ).first()

    if existing:
        return jsonify({"message": "Bu alışkanlık zaten mevcut."}), 409

    habit = Aliskanlik(
        kullanici_id=user.id,
        ad=name,
        kategori=category,
        siklik=frequency,
        tarih=habit_date,
        saat=habit_time,
        tamamlama_tarihleri=[]
    )

    db.session.add(habit)
    db.session.commit()

    return jsonify({
        "message": "Alışkanlık eklendi.",
        "habit": habit_to_dict(
            habit,
            datetime.now().strftime("%Y-%m-%d")
        )
    }), 201


# ==========================================
# ALIŞKANLIK TAMAMLAMA
# ==========================================


@routes.route('/api/habits/<int:habit_id>/complete', methods=['POST'])
def api_complete_habit(habit_id):

    if not session.get('logged_in'):
        return jsonify({"message": "Oturum açmalısınız."}), 401

    user = get_current_user()

    if not user:
        return jsonify({"message": "Kullanıcı bulunamadı."}), 404

    habit = Aliskanlik.query.filter_by(
        id=habit_id,
        kullanici_id=user.id
    ).first()

    if not habit:
        return jsonify({"message": "Alışkanlık bulunamadı."}), 404

    today_date = datetime.now().date()

    # Başlangıç tarihini kontrol et
    try:
        start_date = datetime.strptime(
            habit.tarih, "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return jsonify({
            "message": "Alışkanlığın başlangıç tarihi geçersiz."
        }), 400

    # Başlangıç tarihinden önce tamamlama yapılamaz
    if today_date < start_date:
        return jsonify({
            "message": "Bu alışkanlık henüz başlamadı."
        }), 400

    # Haftalık alışkanlıklar 7 günde bir tamamlanabilir
    if habit.siklik == "haftalik":
        days_passed = (today_date - start_date).days

        if days_passed % 7 != 0:
            return jsonify({
                "message": "Bu haftalık alışkanlığın planlanan günü değil."
            }), 400

    elif habit.siklik != "gunluk":
        return jsonify({
            "message": "Alışkanlık sıklığı geçersiz."
        }), 400

    today = today_date.strftime("%Y-%m-%d")

    dates = list(habit.tamamlama_tarihleri or [])

    # Aynı gün ikinci kez puan kazanılmasını engelle
    if today in dates:
        return jsonify({
            "message": "Bu alışkanlık bugün zaten tamamlandı."
        }), 409

    # Tamamlanma tarihini kaydet
    dates.append(today)
    habit.tamamlama_tarihleri = dates

    # Puan hesaplama
    earned_points = KATEGORI_PUAN.get(
        habit.kategori, 1
    )

    user.puan += earned_points
    user.seviye = seviye_hesapla(user.puan)

    # Rozet kontrolü
    rozet_kontrol(user)

    db.session.commit()

    return jsonify({
        "message": "Alışkanlık başarıyla tamamlandı!",
        "earned_points": earned_points,
        "points": user.puan,
        "level": user.seviye
    }), 200


# ==========================================
# ALIŞKANLIK SİLME
# ==========================================

@routes.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def api_delete_habit(habit_id):

    if not session.get('logged_in'):
        return jsonify({"message": "Oturum açmalısınız."}), 401

    user = get_current_user()

    habit = Aliskanlik.query.filter_by(
        id=habit_id,
        kullanici_id=user.id
    ).first() if user else None

    if not habit:
        return jsonify({"message": "Alışkanlık bulunamadı."}), 404

    db.session.delete(habit)
    db.session.commit()

    return jsonify({"message": "Alışkanlık silindi."})


# ==========================================
# ALIŞKANLIK DÜZENLEME
# ==========================================

@routes.route('/api/habits/<int:habit_id>', methods=['PUT'])
def api_update_habit(habit_id):

    if not session.get('logged_in'):
        return jsonify({"message": "Oturum açmalısınız."}), 401

    user = get_current_user()

    habit = Aliskanlik.query.filter_by(
        id=habit_id,
        kullanici_id=user.id
    ).first() if user else None

    if not habit:
        return jsonify({"message": "Alışkanlık bulunamadı."}), 404

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    category = data.get("category")
    frequency = data.get("frequency")
    habit_date = data.get("date")
    habit_time = data.get("time")

    if not all([name, category, frequency, habit_date, habit_time]):
        return jsonify({"message": "Tüm alanları doldurun."}), 400

    if category not in KATEGORI_PUAN:
        return jsonify({"message": "Geçersiz kategori."}), 400

    if frequency not in ["gunluk", "haftalik"]:
        return jsonify({"message": "Geçersiz sıklık."}), 400

    try:
        datetime.strptime(
            f"{habit_date} {habit_time}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return jsonify({"message": "Geçersiz tarih veya saat."}), 400

    duplicate = Aliskanlik.query.filter(
        Aliskanlik.kullanici_id == user.id,
        Aliskanlik.ad == name,
        Aliskanlik.id != habit_id
    ).first()

    if duplicate:
        return jsonify({"message": "Bu isimde başka bir alışkanlık var."}), 409

    habit.ad = name
    habit.kategori = category
    habit.siklik = frequency
    habit.tarih = habit_date
    habit.saat = habit_time

    db.session.commit()

    return jsonify({"message": "Alışkanlık güncellendi."})

# ==========================================

# ==========================================
# RUTINO - PROFİL VE ROZET API
# ==========================================

def api_user_dict(user):
    return {
        "id": user.id,
        "username": user.kullanici_adi,
        "name": user.ad_soyad or "",
        "email": user.email,
        "phone": user.telefon or "",
        "points": user.puan or 0,
        "level": user.seviye or "Başlangıç Çaylak",
        "profile_photo": user.profil_foto or "default.png"
    }


@routes.route('/api/profile', methods=['GET', 'PUT'])
def api_profile():
    if not session.get('logged_in'):
        return jsonify({"message": "Oturum açmalısınız."}), 401

    user = get_current_user()
    if not user:
        return jsonify({"message": "Kullanıcı bulunamadı."}), 404

    if request.method == 'GET':
        return jsonify({"user": api_user_dict(user)})

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()

    if len(username) < 3:
        return jsonify({"message": "Kullanıcı adı en az 3 karakter olmalıdır."}), 400
    if not email or "@" not in email:
        return jsonify({"message": "Geçerli bir e-posta adresi girin."}), 400

    username_owner = Kullanici.query.filter(
        func.lower(Kullanici.kullanici_adi) == username.lower(),
        Kullanici.id != user.id
    ).first()
    if username_owner:
        return jsonify({"message": "Bu kullanıcı adı başka bir hesapta kullanılıyor."}), 409

    email_owner = Kullanici.query.filter(
        func.lower(Kullanici.email) == email,
        Kullanici.id != user.id
    ).first()
    if email_owner:
        return jsonify({"message": "Bu e-posta adresi başka bir hesapta kullanılıyor."}), 409

    user.kullanici_adi = username
    user.ad_soyad = name or None
    user.email = email
    user.telefon = phone or None
    session['email'] = email

    photo_data = data.get("profile_photo_data")
    if photo_data:
        try:
            header, encoded = photo_data.split(",", 1)
            allowed_image_types = {
                "data:image/jpeg;base64",
                "data:image/png;base64",
                "data:image/webp;base64",
                "data:image/gif;base64"
            }
            if header not in allowed_image_types:
                return jsonify({"message": "JPG, PNG, WEBP veya GIF formatında fotoğraf yükleyin."}), 400
            image_bytes = base64.b64decode(encoded, validate=True)
            if len(image_bytes) > 5 * 1024 * 1024:
                return jsonify({"message": "Fotoğraf en fazla 5 MB olabilir."}), 400

            extension = "jpg"
            if "image/png" in header:
                extension = "png"
            elif "image/webp" in header:
                extension = "webp"
            elif "image/gif" in header:
                extension = "gif"

            from uuid import uuid4
            upload_folder = os.path.join("static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"profile_{uuid4().hex}.{extension}"
            with open(os.path.join(upload_folder, filename), "wb") as image_file:
                image_file.write(image_bytes)
            user.profil_foto = filename
        except (ValueError, OSError):
            db.session.rollback()
            return jsonify({"message": "Profil fotoğrafı kaydedilemedi."}), 400

    db.session.commit()
    return jsonify({
        "message": "Profil bilgilerin başarıyla güncellendi.",
        "user": api_user_dict(user)
    })
# ==========================================
# REACT - ŞİKAYET GÖNDERME API
# ==========================================

@routes.route('/api/complaints', methods=['POST'])
def api_send_complaint():

    if not session.get('logged_in'):
        return jsonify({
            "message": "Şikâyet göndermek için giriş yapmalısınız."
        }), 401

    kullanici = get_current_user()

    if not kullanici:
        return jsonify({
            "message": "Kullanıcı bulunamadı."
        }), 404

    data = request.get_json(silent=True) or {}
    mesaj = (data.get('mesaj') or '').strip()

    if not mesaj:
        return jsonify({
            "message": "Şikâyet mesajı boş bırakılamaz."
        }), 400

    if len(mesaj) < 10:
        return jsonify({
            "message": "Şikâyet mesajı en az 10 karakter olmalıdır."
        }), 400

    if len(mesaj) > 2000:
        return jsonify({
            "message": "Şikâyet mesajı en fazla 2000 karakter olabilir."
        }), 400

    yeni_sikayet = Sikayet(
        ad_soyad=kullanici.ad_soyad or kullanici.kullanici_adi,
        email=kullanici.email,
        mesaj=mesaj,
        tarih=datetime.now().strftime("%Y-%m-%d")
    )

    try:
        db.session.add(yeni_sikayet)
        db.session.commit()

        return jsonify({
            "message": "Şikâyetiniz başarıyla yöneticiye iletildi. Teşekkür ederiz!"
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            "message": "Şikâyet gönderilemedi. Lütfen tekrar deneyin."
        }), 500
# ADMIN LOGOUT
@routes.route('/admin_logout')
def admin_logout():
    session.clear()
    flash("Yönetici oturumu kapatıldı.", "info")
    return redirect(url_for('routes.admin_login'))

@routes.route('/api/badges', methods=['GET'])
def api_badges():
    if not session.get('logged_in'):
        return jsonify({"message": "Oturum açmalısınız."}), 401

    user = get_current_user()
    if not user:
        return jsonify({"message": "Kullanıcı bulunamadı."}), 404

    user_badges = get_user_badges(user.id)
    badges = [{
        "name": item["ad"],
        "description": item["aciklama"],
        "category": item["kategori"],
        "current": item["mevcut"],
        "target": item["hedef"],
        "progress": item["yuzde"],
        "completed": item["tamamlandi"]
    } for item in user_badges]

    earned_count = sum(1 for item in badges if item["completed"])
    return jsonify({
        "badges": badges,
        "earned_count": earned_count,
        "total_count": len(badges)
    })


@routes.route('/api/calendar', methods=['GET'])
def api_calendar():
    if not session.get('logged_in'):
        return jsonify({'message': 'Oturum açmalısınız.'}), 401
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı.'}), 404

    import calendar
    from datetime import date

    month_str = request.args.get('month', '')
    try:
        year, month = map(int, month_str.split('-'))
        if not (1 <= year <= 9999 and 1 <= month <= 12):
            raise ValueError()
        days_count = calendar.monthrange(year, month)[1]
    except (ValueError, TypeError):
        return jsonify({'message': 'Ay YYYY-MM biçiminde olmalı.'}), 400

    habits = Aliskanlik.query.filter_by(kullanici_id=user.id).all()
    days = []
    for day in range(1, days_count + 1):
        current = date(year, month, day)
        day_string = current.isoformat()
        planned = []
        for habit in habits:
            try:
                start = date.fromisoformat(habit.tarih)
            except (TypeError, ValueError):
                continue
            if current < start:
                continue
            # Haftalık alışkanlıklar başlangıç tarihinden itibaren 7 günde bir planlanır.
            if habit.siklik == 'haftalik' and (current - start).days % 7 != 0:
                continue
            if habit.siklik not in ('gunluk', 'haftalik'):
                continue
            completed = day_string in (habit.tamamlama_tarihleri or [])
            planned.append({
                'id': habit.id,
                'name': habit.ad,
                'completed': completed
            })
        days.append({
            'date': day_string,
            'planned_count': len(planned),
            'completed_count': sum(1 for item in planned if item['completed']),
            'habits': planned
        })
    return jsonify({'month': month_str, 'days': days})
