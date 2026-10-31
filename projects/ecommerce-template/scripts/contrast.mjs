// WCAG AA contrast check for every text/background token pair in both themes.
const L = (h) => { const c = h.match(/\w\w/g).map((x) => parseInt(x, 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
const ratio = (a, b) => { const [x, y] = [L(a), L(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
const T = {
  dark: { bg: '0b0f1a', surface: '121829', text: 'ffffff', muted: 'a7b0c5', primaryText: '8aa4ff', danger: 'f06363', success: '3cc47a' },
  light: { bg: 'ffffff', surface: 'f5f7fc', text: '0b0f1a', muted: '5a6378', primaryText: '2f54c9', danger: 'c42b2b', success: '157a41' },
};
let fail = 0;
for (const [name, t] of Object.entries(T)) for (const bg of ['bg', 'surface']) for (const fg of ['text', 'muted', 'primaryText', 'danger', 'success']) {
  const r = ratio(t[fg], t[bg]); const ok = r >= 4.5; if (!ok) fail++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name.padEnd(5)} ${fg.padEnd(11)} on ${bg.padEnd(7)} ${r.toFixed(2)}:1`);
}
for (const [label, fg, bg] of [['white on Royal Blue (CTA)', 'ffffff', '4169e1'], ['white on primary-hover light', 'ffffff', '2f54c9'], ['white on primary-hover dark', 'ffffff', '2f54c9']]) {
  const r = ratio(fg, bg); const ok = r >= 4.5; if (!ok) fail++; console.log(`${ok ? 'PASS' : 'FAIL'} ${label} ${r.toFixed(2)}:1`);
}
console.log(fail ? `${fail} failing pairs` : 'All pairs pass WCAG AA (4.5:1)'); process.exit(fail ? 1 : 0);
