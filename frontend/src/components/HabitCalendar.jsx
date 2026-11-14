import { useEffect, useState } from 'react';
import { apiRequest } from '../lib/api';

const weekdays = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];
const formatDate = (year, month, day) => `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

export default function HabitCalendar({ refreshKey }) {
  const [month, setMonth] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  const [selected, setSelected] = useState(() => formatDate(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()));
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const year = month.getFullYear();
  const monthIndex = month.getMonth();
  const monthKey = `${year}-${String(monthIndex + 1).padStart(2, '0')}`;

  useEffect(() => {
    let alive = true;
    setLoading(true);
    setError('');
    apiRequest(`/api/calendar?month=${monthKey}`)
      .then((result) => { if (alive) setEntries(result.days || []); })
      .catch((err) => { if (alive) setError(err.message || 'Takvim yüklenemedi.'); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [monthKey, refreshKey]);

  const byDate = new Map(entries.map((item) => [item.date, item]));
  const firstOffset = (new Date(year, monthIndex, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
  const selectedEntry = byDate.get(selected);

  function changeMonth(offset) {
    const next = new Date(year, monthIndex + offset, 1);
    setMonth(next);
    setSelected(formatDate(next.getFullYear(), next.getMonth(), 1));
  }

  return (
    <section className="dashboard-panel calendar-panel">
      <div className="calendar-heading">
        <div><span className="card-kicker">ALIŞKANLIK GEÇMİŞİN</span><h2>Takvim</h2></div>
        <div className="calendar-navigation">
          <button type="button" aria-label="Önceki ay" onClick={() => changeMonth(-1)}>‹</button>
          <strong>{month.toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' })}</strong>
          <button type="button" aria-label="Sonraki ay" onClick={() => changeMonth(1)}>›</button>
        </div>
      </div>
      {error && <p className="calendar-error" role="alert">{error}</p>}
      <div className="calendar-grid" aria-label="Aylık alışkanlık takvimi">
        {weekdays.map((day) => <span className="calendar-weekday" key={day}>{day}</span>)}
        {Array.from({ length: firstOffset }, (_, index) => <span key={`blank-${index}`} />)}
        {Array.from({ length: daysInMonth }, (_, index) => {
          const date = formatDate(year, monthIndex, index + 1);
          const entry = byDate.get(date);
          const done = entry?.completed_count || 0;
          const planned = entry?.planned_count || 0;
          return (
            <button key={date} type="button" onClick={() => setSelected(date)}
              className={`calendar-day ${done > 0 ? 'has-completion' : ''} ${planned > 0 && done === planned ? 'fully-completed' : ''} ${selected === date ? 'selected' : ''}`}
              aria-pressed={selected === date} title={`${done} / ${planned} tamamlandı`}>
              <span>{index + 1}</span>{planned > 0 && <small>{done}/{planned}</small>}
            </button>
          );
        })}
      </div>
      <div className="calendar-details">
        <h3>{new Date(`${selected}T12:00:00`).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' })}</h3>
        {loading ? <p>Yükleniyor…</p> : !selectedEntry?.habits?.length ? <p>Bu tarihte planlanmış alışkanlık bulunmuyor.</p> : (
          <ul>{selectedEntry.habits.map((habit) => <li key={habit.id}><span>{habit.completed ? '✓' : '○'}</span><span>{habit.name}</span><small>{habit.completed ? 'Tamamlandı' : 'Tamamlanmadı'}</small></li>)}</ul>
        )}
      </div>
    </section>
  );
}
