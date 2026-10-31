/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)', surface: 'var(--surface)', ink: 'var(--text)', muted: 'var(--text-muted)',
        primary: 'var(--primary)', 'primary-hover': 'var(--primary-hover)', 'primary-text': 'var(--primary-text)',
        line: 'var(--border)', success: 'var(--success)', danger: 'var(--danger)',
      },
      fontFamily: {
        sans: ['"Inter Tight Variable"', 'system-ui', 'sans-serif'],
        logo: ['"Bodoni Moda"', 'Didot', 'serif'],
      },
      letterSpacing: { label: '0.1em', wide2: '0.12em' },
      minHeight: { cta: '56px', tap: '48px' },
    },
  },
  plugins: [],
};
