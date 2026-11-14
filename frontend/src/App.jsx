
import { useEffect, useState } from 'react';
import { apiRequest } from './lib/api';
import Dashboard from './components/Dashboard';

const initialForm = { email: '', password: '', username: '' };

function Brand() {
  return (
    <a className="brand" href="/" aria-label="Rutino ana sayfa">
      <span className="brand-mark">R</span>
      <span>rutino<span className="brand-dot">.</span></span>
    </a>
  );
}

function AuthPage({ mode, setMode, onAuthenticated }) {
  const isRegister = mode === 'register';
  const [form, setForm] = useState(initialForm);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
    setError('');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    setNotice('');

    try {
      if (isRegister) {
        const result = await apiRequest('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            username: form.username.trim(),
            email: form.email.trim(),
            password: form.password,
          }),
        });

        setNotice(result.message || 'Kayıt başarılı. Şimdi giriş yapabilirsiniz.');
        setForm({ ...initialForm, email: form.email });
        setMode('login');
      } else {
        const result = await apiRequest('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({
            email: form.email.trim(),
            password: form.password,
          }),
        });

        onAuthenticated(result.user);
      }
    } catch (err) {
      setError(err.message || 'Bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-intro">
        <Brand />
        <div className="intro-copy">
          <span className="eyebrow">
            <span className="eyebrow-dot" /> DAHA İYİ BİR RUTİN, HER GÜN
          </span>
          <h1>Küçük adımlar,<br /><span>büyük değişimler.</span></h1>
          <p>
            Hedeflerini alışkanlıklara dönüştür. İlerlemeni takip et,
            puanlarını topla ve kendi gelişim hikâyeni oluştur.
          </p>
          <div className="quote-card">
            <span className="quote-mark">“</span>
            <strong>
              Başlamak için mükemmel olman gerekmez. Ama mükemmel olmak
              için başlaman gerekir.
            </strong>
            <span className="quote-caption">RUTINO • HER GÜN BİRAZ DAHA İYİ</span>
          </div>
        </div>
        <span className="intro-footer">RUTINO · Alışkanlık Takip Sistemi</span>
      </section>

      <section className="auth-side">
        <div className="auth-card">
          <div className="auth-card-heading">
            <span className="card-kicker">RUTİNİNİ OLUŞTUR</span>
            <span className="card-icon">✳</span>
          </div>

          <h2>{isRegister ? 'Aramıza katıl.' : 'Tekrar hoş geldin.'}</h2>

          <p className="auth-subtitle">
            {isRegister
              ? 'Yeni bir başlangıç için hesabını oluştur.'
              : 'Alışkanlık yolculuğuna kaldığın yerden devam et.'}
          </p>

          {notice && <div className="form-alert success" role="status">{notice}</div>}
          {error && <div className="form-alert error" role="alert">{error}</div>}

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <label className="field">
                <span>Kullanıcı adı</span>
                <input
                  type="text"
                  autoComplete="username"
                  placeholder="Kullanıcı adın"
                  value={form.username}
                  onChange={(event) => update('username', event.target.value)}
                  minLength={3}
                  required
                />
              </label>
            )}

            <label className="field">
              <span>E-posta</span>
              <input
                type="email"
                autoComplete="email"
                placeholder="ornek@mail.com"
                value={form.email}
                onChange={(event) => update('email', event.target.value)}
                required
              />
            </label>

            <label className="field">
              <span>Şifre</span>
              <input
                type="password"
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                placeholder={isRegister ? 'En az 6 karakter' : 'Şifren'}
                value={form.password}
                onChange={(event) => update('password', event.target.value)}
                minLength={isRegister ? 6 : undefined}
                required
              />
            </label>

            <button className="submit-button" type="submit" disabled={busy}>
              {busy ? 'Lütfen bekle…' : isRegister ? 'Hesap Oluştur' : 'Giriş Yap'}
              <span aria-hidden="true">↗</span>
            </button>
          </form>

          <div className="auth-switch">
            <span>{isRegister ? 'Zaten hesabın var mı?' : 'Henüz hesabın yok mu?'}</span>
            <button
              type="button"
              onClick={() => {
                setMode(isRegister ? 'login' : 'register');
                setError('');
                setNotice('');
              }}
            >
              {isRegister ? 'Giriş yap' : 'Kayıt ol'}
            </button>
          </div>

          <a className="admin-link" href="/admin_login">
            Yönetici girişi
          </a>
        </div>

        <p className="auth-side-footer">
          Küçük adımlar, sürdürülebilir alışkanlıklar.
        </p>
      </section>
    </main>
  );
}

// YÖNETİCİ GİRİŞ EKRANI
function AdminLoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');

    try {
      const response = await fetch('/admin_login', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          email: email.trim(),
          password,
        }),
      });

      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      if (!response.ok) {
        setError('Yönetici girişi başarısız oldu.');
      } else {
        window.location.href = '/admin_dashboard';
      }
    } catch (err) {
      setError('Sunucuya bağlanılamadı. Lütfen tekrar deneyin.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-intro">
        <Brand />
        <div className="intro-copy">
          <span className="eyebrow">
            <span className="eyebrow-dot" /> RUTINO YÖNETİM
          </span>
          <h1>Kontrol sende,<br /><span>gelişim devam etsin.</span></h1>
          <p>
            Yönetici hesabınla giriş yaparak RUTINO yönetim alanına erişebilirsin.
          </p>
        </div>
        <span className="intro-footer">RUTINO · Yönetici Paneli</span>
      </section>

      <section className="auth-side">
        <div className="auth-card">
          <div className="auth-card-heading">
            <span className="card-kicker">YÖNETİCİ ALANI</span>
            <span className="card-icon">✳</span>
          </div>

          <h2>Yönetici girişi.</h2>
          <p className="auth-subtitle">
            Yönetim paneline erişmek için bilgilerini gir.
          </p>

          {error && <div className="form-alert error" role="alert">{error}</div>}

          <form onSubmit={handleSubmit}>
            <label className="field">
              <span>Yönetici e-postası</span>
              <input
                type="email"
                autoComplete="username"
                placeholder="Yönetici e-postası"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </label>

            <label className="field">
              <span>Şifre</span>
              <input
                type="password"
                autoComplete="current-password"
                placeholder="Yönetici şifresi"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </label>

            <button className="submit-button" type="submit" disabled={busy}>
              {busy ? 'Kontrol ediliyor…' : 'Yönetici girişi'}
              <span aria-hidden="true">↗</span>
            </button>
          </form>

          <a className="admin-link" href="/login">
            Kullanıcı girişine dön
          </a>
        </div>

        <p className="auth-side-footer">
          RUTINO · Yönetim alanı
        </p>
      </section>
    </main>
  );
}

function SignedIn({ user, onLogout }) {
  return <Dashboard user={user} onLogout={onLogout} />;
}

function App() {
  const isAdminLogin = window.location.pathname === '/admin_login';

  const [mode, setMode] = useState(
    window.location.pathname === '/register' ? 'register' : 'login'
  );
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    if (isAdminLogin) {
      setCheckingSession(false);
      return;
    }

    let active = true;

    apiRequest('/api/auth/me')
      .then((data) => {
        if (active && data.authenticated) {
          setUser(data.user);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (active) setCheckingSession(false);
      });

    return () => {
      active = false;
    };
  }, [isAdminLogin]);

  useEffect(() => {
    if (isAdminLogin) return;

    const path = mode === 'register' ? '/register' : '/login';

    if (window.location.pathname !== path) {
      window.history.replaceState({}, '', path);
    }
  }, [mode, isAdminLogin]);

  async function logout() {
    try {
      await apiRequest('/api/auth/logout', { method: 'POST' });
      setUser(null);
      setMode('login');
    } catch (err) {
      window.alert(err.message);
    }
  }

  // Yönetici girişi normal kullanıcı oturumundan bağımsızdır.
  if (isAdminLogin) {
    return <AdminLoginPage />;
  }

  if (checkingSession) {
    return (
      <main className="loading-screen">
        <Brand />
        <p>Oturum kontrol ediliyor…</p>
      </main>
    );
  }

  return user
    ? <SignedIn user={user} onLogout={logout} />
    : <AuthPage
        mode={mode}
        setMode={setMode}
        onAuthenticated={setUser}
      />;
}

export default App;
