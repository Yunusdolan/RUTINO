from database import db  # db tek instance, circular import hatasını önlemek için sadece import
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(100), nullable=False)
    ad_soyad = db.Column(db.String(120))
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefon = db.Column(db.String(20))
    profil_foto = db.Column(db.String(200), default="default.png")
    sifre = db.Column(db.String(200), nullable=False)
    puan = db.Column(db.Integer, default=0)
    seviye = db.Column(db.String(50), default="Başlangıç Çaylak")
    rozetler = db.Column(db.JSON, default=list)


class Aliskanlik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanici.id"), nullable=False)
    ad = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(100))
    siklik = db.Column(db.String(50))
    tarih = db.Column(db.String(20))
    saat = db.Column(db.String(20))

    tamamlama_tarihleri = db.Column(
        MutableList.as_mutable(PickleType),
        default=list
    )

class Sikayet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mesaj = db.Column(db.Text, nullable=False)
    tarih = db.Column(db.String(20))


class HabitRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    aliskanlik_id = db.Column(db.Integer, db.ForeignKey('aliskanlik.id'), nullable=False)
    tarih = db.Column(db.Date, nullable=False)
