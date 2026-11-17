// Passcode gate. The passcode lives only in the STUDIO_PASSCODE env var (set by the owner in Vercel).
// The cookie holds a hash of it, never the passcode itself. Works in both the edge (middleware) and node runtimes.
export const COOKIE = 'studio_session';

export async function sessionToken(passcode: string): Promise<string> {
  const data = new TextEncoder().encode('indio-studio-v1:' + passcode);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

export function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

/** True only when a passcode is configured and the cookie matches it. No passcode set = everything locked. */
export async function isAuthed(cookieValue: string | undefined): Promise<boolean> {
  const pass = process.env.STUDIO_PASSCODE;
  if (!pass || !cookieValue) return false;
  return safeEqual(cookieValue, await sessionToken(pass));
}
