// Usage: node scripts/hash-password.mjs '<password>'  → prints a PBKDF2 hash for content/seed.ts
const pw = process.argv[2];
if (!pw) { console.error('usage: node scripts/hash-password.mjs <password>'); process.exit(1); }
const salt = crypto.getRandomValues(new Uint8Array(16));
const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveBits']);
const bits = new Uint8Array(await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: 210000 }, key, 256));
const b64 = (u) => Buffer.from(u).toString('base64');
console.log(`pbkdf2$sha256$210000$${b64(salt)}$${b64(bits)}`);
