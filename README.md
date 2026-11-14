# RUTINO – Alışkanlık Takip Sistemi

RUTINO, kullanıcıların günlük alışkanlıklarını planlamasına, tamamladıkları alışkanlıkları takip etmesine ve kişisel gelişimlerini puan ve rozetlerle görmesine yardımcı olan web tabanlı bir alışkanlık takip uygulamasıdır.

## Özellikler

- Kullanıcı hesabı oluşturma ve giriş yapma
- Alışkanlık ekleme, düzenleme, silme ve tamamlama
- Alışkanlıkları kategori, tarih ve saat bilgileriyle takip etme
- Alışkanlık takvimi üzerinden planları görüntüleme
- Tamamlanan alışkanlıklardan puan kazanma
- Kullanıcı puanına göre seviye ilerlemesi
- Hedeflere göre rozet kazanma ve rozetleri görüntüleme
- Profil bilgilerini ve profil fotoğrafını güncelleme
- Mevcut şifreyi doğrulayarak şifre değiştirme
- Kullanıcıların şikâyet ve geri bildirim göndermesi
- Yönetici girişi ve yönetim panelinden kullanıcıları, alışkanlıkları ve şikâyetleri yönetme

## Kullanılan Teknolojiler

| Alan | Teknoloji |
|---|---|
| Ön yüz | React 18 |
| Ön yüz geliştirme ve derleme | Vite 6 |
| Arayüz | HTML, CSS, JavaScript |
| Sunucu tarafı | Python, Flask |
| Veritabanı işlemleri | Flask-SQLAlchemy, SQLAlchemy |
| Veritabanı | SQLite |
| Oturum ve güvenlik yapılandırması | Flask Session, python-dotenv, Werkzeug parola hashleme |

## Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları uygulayın.

### Gereksinimler

- Python 3
- Node.js ve npm
- Git

### 1. Projeyi indirme

Terminal veya komut satırında aşağıdaki komutları çalıştırın:

```bash
git clone https://github.com/Yunusdolan/RUTINO.git
cd RUTINO
```

### 2. Python sanal ortamını oluşturma

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```powershell
py -m venv .venv
.venv\Scripts\activate
```

### 3. Python paketlerini yükleme

Proje ana klasöründe aşağıdaki komutu çalıştırın:

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarlama

Proje ana klasöründe `.env` adlı bir dosya oluşturun ve aşağıdaki değişkenleri kendi yerel geliştirme ortamınıza göre tanımlayın:

```env
FLASK_SECRET_KEY=buraya_en_az_32_karakterlik_gizli_anahtar
ADMIN_EMAIL=yonetici_eposta_adresi
ADMIN_PASSWORD=yonetici_sifresi
FLASK_DEBUG=true
SESSION_COOKIE_SECURE=false
```

`FLASK_SECRET_KEY` en az 32 karakter olmalıdır. Yönetici e-posta adresi ve şifresi de tanımlanmalıdır.

**Önemli:** Gerçek gizli anahtarları, yönetici şifresini veya diğer hassas bilgileri GitHub'a yüklemeyin.

### 5. Flask sunucusunu başlatma

Proje ana klasöründe aşağıdaki komutu çalıştırın:

```bash
python main.py
```

Flask sunucusu varsayılan olarak `http://127.0.0.1:5000` adresinde çalışır.

### 6. React ön yüzünü başlatma

Yeni bir terminal açın ve proje içindeki `frontend` klasörüne geçin:

```bash
cd frontend
npm install
npm run dev
```

Vite geliştirme sunucusu `http://127.0.0.1:5173` adresinde açılır. Uygulamayı tarayıcıda bu adres üzerinden görüntüleyebilirsiniz.

Geliştirme ortamında Vite, `/api` isteklerini Flask sunucusuna yönlendirir. Bu nedenle Flask ve Vite sunucularının aynı anda çalışması gerekir.

### 7. Üretim derlemesi

React uygulamasının üretim sürümünü oluşturmak için `frontend` klasöründe aşağıdaki komutu çalıştırın:

```bash
npm run build
```

Derleme sonucunda oluşturulan dosyalar, Vite yapılandırmasına göre Flask tarafından sunulan `static/react` klasörüne aktarılır.

## Yapay Zekânın Kullanıldığı Aşamalar

Projenin geliştirilmesi sırasında ChatGPT, yardımcı bir yapay zekâ aracı olarak kullanılmıştır:

- **Proje planlama:** Alışkanlık takip uygulamasının temel amacının, kullanıcı ihtiyaçlarının ve geliştirilecek özelliklerin planlanmasında fikir desteği alınmıştır.
- **Kod geliştirme:** React arayüzü ve Flask tarafındaki bazı kodların oluşturulması, düzenlenmesi ve açıklanması süreçlerinde destek alınmıştır.
- **Hata ayıklama:** Geliştirme sırasında karşılaşılan hata mesajlarının değerlendirilmesi ve olası çözüm yollarının belirlenmesinde kullanılmıştır.
- **Dokümantasyon:** Kurulum yönergelerinin ve bu README dosyasının hazırlanmasında yararlanılmıştır.

Yapay zekâ tarafından sunulan öneriler doğrudan kabul edilmek yerine proje kodu ve uygulama davranışı üzerinden değerlendirilmiş, uygun görülenler projeye uygulanmıştır.

## Proje Bağlantıları

- **GitHub Deposu:** https://github.com/Yunusdolan/RUTINO
- **Canlı Uygulama:** https://rutino.onrender.com
