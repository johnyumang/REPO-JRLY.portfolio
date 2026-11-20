'use client';
import {useState} from 'react';

export default function Login() {
  const [pass, setPass] = useState('');
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg('');
    const r = await fetch('/api/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({passcode: pass})});
    setBusy(false);
    if (r.ok) window.location.href = '/';
    else setMsg((await r.json().catch(() => ({}))).error || 'Locked.');
  }
  return (
    <main className="login">
      <form onSubmit={submit}>
        <div className="brand"><i />INDIO <b>STUDIO</b></div>
        <input type="password" placeholder="Passcode" value={pass} onChange={(e) => setPass(e.target.value)} autoFocus />
        <button className="primary" disabled={busy || !pass}>{busy ? 'Checking…' : 'Enter'}</button>
        {msg ? <div className="warn small">{msg}</div> : null}
      </form>
    </main>
  );
}
