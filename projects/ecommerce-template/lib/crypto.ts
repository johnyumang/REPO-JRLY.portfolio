// PBKDF2-SHA256 via WebCrypto: works in the browser (offline mode) and in Node 20+.
// Format: pbkdf2$sha256$<iterations>$<salt b64>$<hash b64>
const ITERATIONS = 210_000; // OWASP 2023 minimum for PBKDF2-HMAC-SHA256
const enc = new TextEncoder();
const b64 = (u: Uint8Array) => btoa(String.fromCharCode(...u));
const unb64 = (s: string) => Uint8Array.from(atob(s), (ch) => ch.charCodeAt(0));

async function derive(password: string, salt: Uint8Array, iterations: number) {
  const key = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations }, key, 256);
  return new Uint8Array(bits);
}

export async function hashPassword(password: string, iterations = ITERATIONS) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  return `pbkdf2$sha256$${iterations}$${b64(salt)}$${b64(await derive(password, salt, iterations))}`;
}

export async function verifyPassword(password: string, stored: string) {
  const [scheme, algo, iter, salt, hash] = stored.split('$');
  if (scheme !== 'pbkdf2' || algo !== 'sha256') return false;
  const actual = await derive(password, unb64(salt), Number(iter));
  const expected = unb64(hash);
  // Constant-time compare
  let diff = actual.length ^ expected.length;
  for (let i = 0; i < Math.min(actual.length, expected.length); i++) diff |= actual[i] ^ expected[i];
  return diff === 0;
}

export const uuid = () => crypto.randomUUID();
