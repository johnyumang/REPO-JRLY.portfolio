'use client';
import { useEffect, useState } from 'react';
import { MoonIcon, SunIcon } from './Icons';

export default function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  useEffect(() => { setTheme((document.documentElement.dataset.theme as 'dark' | 'light') || 'dark'); }, []);
  const flip = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('tpl.theme', next); } catch {}
    setTheme(next);
  };
  return (
    <button className="icon-btn" onClick={flip} aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
      {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}

/** Runs before paint: stored choice → OS preference → dark default. */
export const themeScript = `(function(){try{var t=localStorage.getItem('tpl.theme');if(!t){t=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'}document.documentElement.dataset.theme=t}catch(e){document.documentElement.dataset.theme='dark'}})();`;
