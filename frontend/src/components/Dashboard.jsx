
import { useCallback, useEffect, useState } from 'react';
import { apiRequest } from '../lib/api';
import HabitCalendar from './HabitCalendar';

const categories = [
  { value: 'ders', label: 'Ders', icon: '📚', color: '#7189b8' },
  { value: 'spor', label: 'Spor', icon: '🏃', color: '#6d9872' },
  { value: 'saglik', label: 'Sağlık', icon: '🌿', color: '#c47b70' },
  { value: 'kisisel_gelisim', label: 'Kişisel Gelişim', icon: '✨', color: '#9b83b8' },
];

const emptyForm = {
  name: '',
  category: 'ders',
  frequency: 'gunluk',
  date: '',
  time: '09:00',
};

function categoryInfo(value) {
  return categories.find((item) => item.value === value) || categories[0];
}

function getToday() {
  return new Date().toLocaleDateString('en-CA');
}

function HabitForm({ initialValue, onSave, onCancel, saving }) {
  const [form, setForm] = useState(initialValue || {
    ...emptyForm,
    date: getToday(),
  });

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function submit(event) {
    event.preventDefault();
    onSave(form);
  }

  return (
    <form className="habit-form" onSubmit={submit}>
      <label>
        Alışkanlık adı
        <input
          value={form.name}
          onChange={(e) => update('name', e.target.value)}
          placeholder="Örn. 30 dakika kitap oku"
          required
          maxLength={100}
        />
      </label>

      <div className="habit-form-grid">
        <label>
          Kategori
          <select
            value={form.category}
            onChange={(e) => update('category', e.target.value)}
          >
            {categories.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Sıklık
          <select
            value={form.frequency}
            onChange={(e) => update('frequency', e.target.value)}
          >
            <option value="gunluk">Günlük</option>
            <option value="haftalik">Haftalık</option>
          </select>
        </label>

        <label>
          Tarih
          <input
            type="date"
            value={form.date}
            onChange={(e) => update('date', e.target.value)}
            required
          />
        </label>

        <label>
          Saat
          <input
            type="time"
            value={form.time}
            onChange={(e) => update('time', e.target.value)}
            required
          />
        </label>
      </div>

      <div className="habit-form-actions">
        <button className="dashboard-primary" type="submit" disabled={saving}>
          {saving ? 'Kaydediliyor…' : 'Kaydet'}
        </button>
        <button className="dashboard-secondary" type="button" onClick={onCancel}>
          İptal
        </button>
      </div>
    </form>
  );
}

function HabitCard({ habit, onComplete, onEdit, onDelete, busy }) {
  const category = categoryInfo(habit.category);

  return (
    <article className="habit-card">
      <div
        className="habit-icon"
        style={{ backgroundColor: `${category.color}18` }}
      >
        {category.icon}
      </div>

      <div className="habit-info">
        <strong>{habit.name}</strong>
        <span>
          {category.label} · {habit.frequency === 'gunluk' ? 'Günlük' : 'Haftalık'}
        </span>
        <small>{habit.time || 'Saat belirtilmedi'}</small>
      </div>

      <div className="habit-actions">
        <button
          className="habit-complete"
          onClick={() => onComplete(habit.id)}
          disabled={busy}
          title="Tamamla"
        >
          ✓
        </button>
        <button
          className="habit-edit"
          onClick={() => onEdit(habit)}
          disabled={busy}
          title="Düzenle"
        >
          ✎
        </button>
        <button
          className="habit-delete"
          onClick={() => onDelete(habit.id)}
          disabled={busy}
          title="Sil"
        >
          ×
        </button>
      </div>
    </article>
  );
}

function Dashboard({ user, onLogout }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [modal, setModal] = useState(null);
  const [busy, setBusy] = useState(false);
  const [activePage, setActivePage] = useState('dashboard');
  const [profile, setProfile] = useState(null);
  const [profileForm, setProfileForm] = useState({ username: '', name: '', email: '', phone: '' });
  const [profilePhoto, setProfilePhoto] = useState('');
  const [badges, setBadges] = useState([]);
  const [badgesSummary, setBadgesSummary] = useState({ earned: 0, total: 0 });
  const [sectionLoading, setSectionLoading] = useState(false);
  const [complaintMessage, setComplaintMessage] = useState('');
  const [complaintBusy, setComplaintBusy] = useState(false);
  const [complaintNotice, setComplaintNotice] = useState('');
  const [complaintError, setComplaintError] = useState('');

  const loadDashboard = useCallback(async () => {
    try {
      setError('');
      const result = await apiRequest('/api/dashboard');
      setData(result);
    } catch (err) {
      setError(err.message || 'Dashboard yüklenemedi.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);


  async function loadProfile() {
    setSectionLoading(true);
    try {
      const result = await apiRequest('/api/profile', { method: 'GET' });
      setProfile(result.user);
      setProfileForm({
        username: result.user.username || '',
        name: result.user.name || '',
        email: result.user.email || '',
        phone: result.user.phone || '',
      });
      setProfilePhoto('');
    } catch (err) {
      setError(err.message || 'Profil bilgileri yüklenemedi.');
    } finally {
      setSectionLoading(false);
    }
  }

  async function loadBadges() {
    setSectionLoading(true);
    try {
      const result = await apiRequest('/api/badges', { method: 'GET' });
      setBadges(result.badges || []);
      setBadgesSummary({
        earned: result.earned_count || 0,
        total: result.total_count || 0,
      });
    } catch (err) {
      setError(err.message || 'Rozetler yüklenemedi.');
    } finally {
      setSectionLoading(false);
    }
  }

  useEffect(() => {
    if (activePage === 'profile') loadProfile();
    if (activePage === 'badges') loadBadges();
  }, [activePage]);

  function readPhoto(file) {
    if (!file) {
      setProfilePhoto('');
      return;
    }
    if (!file.type.startsWith('image/')) {
      setError('Lütfen bir görsel dosyası seçin.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('Profil fotoğrafı en fazla 5 MB olabilir.');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => setProfilePhoto(String(reader.result || ''));
    reader.onerror = () => setError('Fotoğraf okunamadı. Tekrar deneyin.');
    reader.readAsDataURL(file);
  }
  async function sendComplaint(event) {
    event.preventDefault();

    const message = complaintMessage.trim();

    if (message.length < 10) {
      setComplaintError('Şikâyet mesajı en az 10 karakter olmalıdır.');
      return;
    }

    if (message.length > 2000) {
      setComplaintError('Şikâyet mesajı en fazla 2000 karakter olabilir.');
      return;
    }

    setComplaintBusy(true);
    setComplaintError('');
    setComplaintNotice('');

    try {
      const result = await apiRequest('/api/complaints', {
        method: 'POST',
        body: JSON.stringify({
          mesaj: message,
        }),
      });

      setComplaintNotice(
        result.message || 'Şikâyetiniz başarıyla gönderildi.'
      );

      setComplaintMessage('');

    } catch (err) {
      setComplaintError(
        err.message || 'Şikâyet gönderilemedi.'
      );
    } finally {
      setComplaintBusy(false);
    }
  }
  async function saveProfile(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    setNotice('');

    try {
      const result = await apiRequest('/api/profile', {
        method: 'PUT',
        body: JSON.stringify({
          ...profileForm,
          profile_photo_data: profilePhoto || null,
        }),
      });
      setProfile(result.user);
      setProfileForm({
        username: result.user.username || '',
        name: result.user.name || '',
        email: result.user.email || '',
        phone: result.user.phone || '',
      });
      setProfilePhoto('');
      setNotice(result.message || 'Profil bilgilerin güncellendi.');
      await loadDashboard();
    } catch (err) {
      setError(err.message || 'Profil güncellenemedi.');
    } finally {
      setBusy(false);
    }
  }

  async function saveHabit(form) {
    setBusy(true);
    setNotice('');

    try {
      if (modal?.type === 'edit') {
        await apiRequest(`/api/habits/${modal.habit.id}`, {
          method: 'PUT',
          body: JSON.stringify(form),
        });
        setNotice('Alışkanlık güncellendi.');
      } else {
        await apiRequest('/api/habits', {
          method: 'POST',
          body: JSON.stringify(form),
        });
        setNotice('Yeni alışkanlık eklendi.');
      }

      setModal(null);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function completeHabit(id) {
    setBusy(true);
    setError('');
    setNotice('');

    try {
      const result = await apiRequest(`/api/habits/${id}/complete`, {
        method: 'POST',
      });
      setNotice(`${result.message} +${result.earned_points} puan kazandın!`);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function deleteHabit(id) {
    if (!window.confirm('Bu alışkanlığı silmek istediğine emin misin?')) return;

    setBusy(true);
    setError('');

    try {
      const result = await apiRequest(`/api/habits/${id}`, {
        method: 'DELETE',
      });
      setNotice(result.message);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return <main className="dashboard-loading">RUTINO hazırlanıyor…</main>;
  }

  if (!data) {
    return (
      <main className="dashboard-loading">
        <p>{error || 'Veriler yüklenemedi.'}</p>
        <button className="dashboard-primary" onClick={loadDashboard}>Tekrar dene</button>
      </main>
    );
  }

  const active = data.active_habits || [];
  const completed = data.completed_habits || [];
  const dashboardUser = data.user || user;
  const totalHabits = active.length + completed.length;
  const progress = data.weekly_progress || 0;

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <a className="brand" href="/"><span className="brand-mark">R</span><span>rutino<span className="brand-dot">.</span></span></a>
        <div className="dashboard-header-right">
          <span className="header-user">{dashboardUser.username}</span>
          <button className="text-button" onClick={onLogout}>Çıkış yap</button>
        </div>
      </header>

      <nav className="dashboard-nav" aria-label="Ana menü">
        <button className={activePage === 'dashboard' ? 'active' : ''} onClick={() => setActivePage('dashboard')}>Genel Bakış</button>
        <button className={activePage === 'badges' ? 'active' : ''} onClick={() => setActivePage('badges')}>Rozetler</button>
        <button className={activePage === 'profile' ? 'active' : ''} onClick={() => setActivePage('profile')}>Profilim</button>
        <button className={activePage === 'complaints' ? 'active' : ''} onClick={() => { setActivePage('complaints'); setComplaintError(''); setComplaintNotice('');}}> Şikâyetler </button>
      </nav>

      {activePage === 'dashboard' ? (
      <div className="dashboard-container">
        <section className="dashboard-welcome">
          <div>
            <span className="eyebrow"><span className="eyebrow-dot" /> BUGÜN KENDİN İÇİN BİR ADIM AT</span>
            <h1>Hoş geldin, <span>{dashboardUser.username}.</span></h1>
            <p>Her gün attığın küçük adımlar, büyük değişimlere dönüşür.</p>
          </div>
          <div className="date-chip">
            {new Date().toLocaleDateString('tr-TR', {
              weekday: 'long', day: 'numeric', month: 'long'
            })}
          </div>
        </section>

        {(error || notice) && (
          <div className={`dashboard-message ${error ? 'message-error' : 'message-success'}`} role="status">
            {error || notice}
            <button onClick={() => { setError(''); setNotice(''); }}>×</button>
          </div>
        )}

        <section className="stats-grid">
          <article className="stat-card">
            <span>TOPLAM PUAN</span>
            <strong>{dashboardUser.points ?? 0}</strong>
            <small>Alışkanlıklarından kazandığın</small>
          </article>
          <article className="stat-card">
            <span>MEVCUT SEVİYE</span>
            <strong className="level-value">{dashboardUser.level || 'Başlangıç Çaylak'}</strong>
            <small>Gelişmeye devam et</small>
          </article>
          <article className="stat-card">
            <span>BUGÜN TAMAMLANAN</span>
            <strong>{completed.length}<small className="stat-total"> / {totalHabits}</small></strong>
            <small>Alışkanlık</small>
          </article>
          <article className="stat-card">
            <span>HAFTALIK İLERLEME</span>
            <strong>%{progress}</strong>
            <div className="mini-progress"><span style={{ width: `${progress}%` }} /></div>
          </article>
        </section>

        <div className="dashboard-columns">
          <section className="dashboard-panel habits-panel">
            <div className="panel-heading">
              <div>
                <span className="card-kicker">GÜNLÜK RUTİNİN</span>
                <h2>Alışkanlıkların</h2>
              </div>
              <button className="dashboard-primary add-button" onClick={() => setModal({ type: 'add' })}>
                + Yeni alışkanlık
              </button>
            </div>

            {active.length === 0 ? (
              <div className="empty-state">
                <span>🌱</span>
                <strong>Bugün için aktif alışkanlığın yok.</strong>
                <p>Yeni bir alışkanlık ekleyerek başlayabilirsin.</p>
              </div>
            ) : (
              <div className="habit-list">
                {active.map((habit) => (
                  <HabitCard
                    key={habit.id}
                    habit={habit}
                    onComplete={completeHabit}
                    onEdit={(item) => setModal({
                      type: 'edit',
                      habit: item,
                    })}
                    onDelete={deleteHabit}
                    busy={busy}
                  />
                ))}
              </div>
            )}

            <div className="completed-section">
              <div className="completed-heading">
                <h3>Bugün tamamlananlar</h3>
                <span>{completed.length}</span>
              </div>
              {completed.length === 0 ? (
                <p className="muted-text">Henüz tamamlanan alışkanlık yok.</p>
              ) : (
                completed.map((habit) => (
                  <div className="completed-item" key={habit.id}>
                    <span>✓</span>
                    <strong>{habit.name}</strong>
                    <small>Tamamlandı</small>
                  </div>
                ))
              )}
            </div>
          </section>

          <aside className="dashboard-panel progress-panel">
            <span className="card-kicker">İLERLEMENİ TAKİP ET</span>
            <h2>Haftalık görünüm</h2>
            <div className="week-chart">
              {(data.weekly_data || []).map((day) => {
                const date = new Date(`${day.date}T12:00:00`);
                const label = date.toLocaleDateString('tr-TR', { weekday: 'short' });
                const max = Math.max(1, ...data.weekly_data.map((item) => item.completed));
                const height = Math.max(8, (day.completed / max) * 100);

                return (
                  <div className="week-day" key={day.date}>
                    <strong>{day.completed}</strong>
                    <div className="week-bar-track">
                      <span style={{ height: `${height}%` }} />
                    </div>
                    <small>{label}</small>
                  </div>
                );
              })}
            </div>

            <div className="weekly-summary">
              <span>Son 7 gündeki tamamlamalar</span>
              <strong>{(data.weekly_data || []).reduce((sum, day) => sum + day.completed, 0)}</strong>
            </div>

            <div className="progress-note">
              <span>✦</span>
              <p>İstikrar, küçük adımların tekrarıyla oluşur. Bugün de kendin için bir adım at!</p>
            </div>
          </aside>
        </div>
        <HabitCalendar refreshKey={data} />
      </div>
      ) : activePage === 'profile' ? (
        <div className="dashboard-container section-container">
          <section className="dashboard-panel profile-panel">
            <div className="section-title">
              <span className="card-kicker">HESAP AYARLARIN</span>
              <h2>Profilim</h2>
              <p>Kişisel bilgilerini buradan güncelleyebilirsin.</p>
            </div>

            {sectionLoading ? <div className="section-loading">Profil bilgilerin yükleniyor…</div> : (
              <form className="profile-form" onSubmit={saveProfile}>
                <div className="profile-photo-area">
                  <div className="profile-avatar">
                    {(profilePhoto || (profile?.profile_photo && profile.profile_photo !== 'default.png'))
                      ? <img src={profilePhoto || `/static/uploads/${profile.profile_photo}`} alt="Profil fotoğrafı" />
                      : <span>{(profileForm.username || 'R').slice(0, 1).toUpperCase()}</span>}
                  </div>
                  <label className="photo-upload">
                    Fotoğraf seç
                    <input type="file" accept="image/*" onChange={(event) => readPhoto(event.target.files?.[0])} />
                  </label>
                  <small>JPG, PNG veya başka bir görsel · En fazla 5 MB</small>
                </div>

                <div className="profile-fields">
                  <label>
                    Kullanıcı adı
                    <input value={profileForm.username} onChange={(event) => setProfileForm((current) => ({ ...current, username: event.target.value }))} minLength={3} maxLength={100} required />
                  </label>
                  <label>
                    Ad soyad
                    <input value={profileForm.name} onChange={(event) => setProfileForm((current) => ({ ...current, name: event.target.value }))} maxLength={120} placeholder="Adınız ve soyadınız" />
                  </label>
                  <label>
                    E-posta
                    <input type="email" value={profileForm.email} onChange={(event) => setProfileForm((current) => ({ ...current, email: event.target.value }))} required />
                  </label>
                  <label>
                    Telefon
                    <input type="tel" value={profileForm.phone} onChange={(event) => setProfileForm((current) => ({ ...current, phone: event.target.value }))} maxLength={20} placeholder="05xx xxx xx xx" />
                  </label>
                </div>

                <div className="profile-account-summary">
                  <div><span>Toplam puan</span><strong>{profile?.points ?? dashboardUser.points ?? 0}</strong></div>
                  <div><span>Mevcut seviye</span><strong>{profile?.level || dashboardUser.level || 'Başlangıç Çaylak'}</strong></div>
                </div>

                <div className="profile-actions">
                  <button className="dashboard-primary" type="submit" disabled={busy}>{busy ? 'Kaydediliyor…' : 'Bilgilerimi kaydet'}</button>
                </div>
              </form>
            )}
          </section>
        </div>
      ) : activePage === 'complaints' ? (
        <div className="dashboard-container section-container">
          <section className="dashboard-panel profile-panel">
            <div className="section-title">
              <span className="card-kicker">BİZE ULAŞ</span>
              <h2>Şikâyet ve Geri Bildirim</h2>
              <p>
                Görüşlerin, önerilerin veya yaşadığın sorunlar bizim için önemli.
                Mesajını doğrudan yöneticiye iletebilirsin.
              </p>
            </div>

            <div style={{
              background: '#f1f6ee',
              borderRadius: '14px',
              padding: '20px',
              marginBottom: '25px'
            }}>
              <strong style={{ color: '#476b43' }}>
                ✉ Geri bildirimin bizim için değerli.
              </strong>
              <p style={{
                color: '#71806d',
                fontSize: '13px',
                margin: '8px 0 0'
              }}>
                Gönderdiğin mesaj yönetici panelindeki şikâyetler
                bölümüne kaydedilecektir.
              </p>
            </div>

            {complaintNotice && (
              <div className="dashboard-message message-success" role="status">
                {complaintNotice}
              </div>
            )}

            {complaintError && (
              <div className="dashboard-message message-error" role="alert">
                {complaintError}
              </div>
            )}

            <form onSubmit={sendComplaint}>
              <div style={{ marginBottom: '22px' }}>
                <label
                  htmlFor="complaintMessage"
                  style={{
                    display: 'block',
                    fontWeight: 700,
                    fontSize: '13px',
                    marginBottom: '10px'
                  }}
                >
                  Şikâyet veya öneri mesajın
                </label>

                <textarea
                  id="complaintMessage"
                  value={complaintMessage}
                  onChange={(event) => {
                    setComplaintMessage(event.target.value);
                    setComplaintError('');
                  }}
                  placeholder="Yaşadığın sorunu veya önerini buraya yazabilirsin..."
                  rows={7}
                  maxLength={2000}
                  required
                  style={{
                    width: '100%',
                    padding: '16px',
                    border: '1px solid #dce5d7',
                    borderRadius: '12px',
                    background: '#fbfcfa',
                    fontSize: '14px',
                    resize: 'vertical',
                    outlineColor: '#648b5d',
                    fontFamily: 'inherit'
                  }}
                />

                <div style={{
                  textAlign: 'right',
                  fontSize: '11px',
                  color: '#929d8c',
                  marginTop: '7px'
                }}>
                  {complaintMessage.length} / 2000 karakter
                </div>
              </div>

              <button
                type="submit"
                className="dashboard-primary"
                disabled={complaintBusy || complaintMessage.trim().length < 10}
              >
                {complaintBusy ? 'Gönderiliyor…' : 'Şikâyeti Gönder ↗'}
              </button>
            </form>
          </section>
        </div>
      ) : (
        <div className="dashboard-container section-container">
          <section className="dashboard-panel badges-panel">
            <div className="section-title">
              <span className="card-kicker">BAŞARILARINI KEŞFET</span>
              <h2>Rozetlerim</h2>
              <p>Alışkanlıklarını tamamladıkça yeni rozetler kazan.</p>
            </div>

            {sectionLoading ? <div className="section-loading">Rozetlerin yükleniyor…</div> : (
              <>
                <div className="badge-summary">
                  <div><strong>{badgesSummary.earned}</strong><span>Kazanılan rozet</span></div>
                  <div><strong>{Math.max(0, badgesSummary.total - badgesSummary.earned)}</strong><span>Kilitli rozet</span></div>
                  <div><strong>{badgesSummary.total}</strong><span>Toplam rozet</span></div>
                </div>
                {badges.length === 0 ? (
                  <div className="empty-state"><span>🏅</span><strong>Henüz rozet tanımlanmamış.</strong><p>Rozet kuralları eklendiğinde burada görünecek.</p></div>
                ) : (
                  <div className="badges-grid">
                    {badges.map((badge, index) => (
                      <article className={`badge-card ${badge.completed ? 'badge-earned' : 'badge-locked'}`} key={`${badge.category}-${index}`}>
                        <div className="badge-icon">{badge.completed ? '🏆' : '🔒'}</div>
                        <div className="badge-copy">
                          <strong>{badge.name}</strong>
                          <p>{badge.description}</p>
                        </div>
                        <div className="badge-progress">
                          <div><span>{badge.current} / {badge.target}</span><strong>%{badge.progress}</strong></div>
                          <div className="badge-progress-track"><span style={{ width: `${badge.progress}%` }} /></div>
                        </div>
                        <small>{badge.completed ? 'Kazanıldı' : 'Henüz kazanılmadı'}</small>
                      </article>
                    ))}
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      )}

      {modal && (
        <div className="dashboard-modal-backdrop" onMouseDown={(event) => {
          if (event.target === event.currentTarget && !busy) setModal(null);
        }}>
          <section className="dashboard-modal" role="dialog" aria-modal="true" aria-labelledby="habit-modal-title">
            <div className="modal-heading">
              <div>
                <span className="card-kicker">{modal.type === 'edit' ? 'RUTİNİNİ GÜNCELLE' : 'YENİ BİR BAŞLANGIÇ'}</span>
                <h2 id="habit-modal-title">{modal.type === 'edit' ? 'Alışkanlığı düzenle' : 'Yeni alışkanlık'}</h2>
              </div>
              <button className="modal-close" onClick={() => setModal(null)} disabled={busy}>×</button>
            </div>
            <HabitForm
              initialValue={modal.type === 'edit' ? {
                name: modal.habit.name,
                category: modal.habit.category,
                frequency: modal.habit.frequency,
                date: modal.habit.date || getToday(),
                time: modal.habit.time || '09:00',
              } : undefined}
              onSave={saveHabit}
              onCancel={() => setModal(null)}
              saving={busy}
            />
          </section>
        </div>
      )}
    </main>
  );
}

export default Dashboard;
