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
- Kullanıcıların şikâyet/geri bildirim göndermesi
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
| Oturum ve güvenlik yapılandırması | Flask session, python-dotenv, Werkzeug parola hashleme |

## Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları uygulayın. Komutları proje ana klasöründe çalıştırın.

### Gereksinimler

- Python 3
- Node.js ve npm

### 1. Projeyi indirme

GitHub deposunu klonladıktan sonra proje klasörüne girin:

```bash
git clone GITHUB_DEPO_LINKI
cd RUTINO
```

GitHub deposu henüz oluşturulmadıysa, indirdiğiniz proje klasörünü açarak sonraki adımlara geçebilirsiniz.

### 2. Python sanal ortamını oluşturma

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

### 3. Python paketlerini yükleme

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

`FLASK_SECRET_KEY` en az 32 karakter olmalıdır. Yönetici e-posta adresi ve şifresi de tanımlanmalıdır. Gerçek gizli anahtarları ve şifreleri GitHub'a yüklemeyin.

### 5. Flask sunucusunu başlatma

Proje ana klasöründe:

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

Vite geliştirme sunucusu `http://127.0.0.1:5173` adresinde açılır. Uygulamayı tarayıcıda bu adres üzerinden görüntüleyebilirsiniz. Geliştirme ortamında Vite, `/api` isteklerini Flask sunucusuna yönlendirir.

## Yapay Zekânın Kullanıldığı Aşamalar

Projenin geliştirilmesi sırasında ChatGPT, yardımcı bir yapay zekâ aracı olarak kullanılmıştır:

- **Proje planlama:** Alışkanlık takip uygulamasının temel amacının, kullanıcı ihtiyaçlarının ve geliştirilecek özelliklerin planlanmasında fikir desteği alınmıştır.
- **Kod geliştirme:** React arayüzü ve Flask tarafındaki bazı kodların oluşturulması, düzenlenmesi ve açıklanması süreçlerinde destek alınmıştır.
- **Hata ayıklama:** Geliştirme sırasında karşılaşılan hata mesajlarının değerlendirilmesi ve olası çözüm yollarının belirlenmesinde kullanılmıştır.
- **Dokümantasyon:** Kurulum yönergelerinin ve bu README dosyasının hazırlanmasında yararlanılmıştır.

Yapay zekâ tarafından sunulan öneriler doğrudan kabul edilmek yerine proje kodu ve uygulama davranışı üzerinden değerlendirilmiş, uygun görülenler projeye uygulanmıştır.

## Proje Bağlantıları

- **GitHub deposu:** GitHub deposu oluşturulduktan sonra bağlantı eklenecektir.
- **Canlı uygulama:** Uygulama Netlify, Vercel veya uygun bir sunucu/platform üzerinde yayınlandıktan sonra bağlantı eklenecektir.
