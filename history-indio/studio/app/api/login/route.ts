import {NextRequest, NextResponse} from 'next/server';
import {COOKIE, safeEqual, sessionToken} from '@/lib/auth';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  const pass = process.env.STUDIO_PASSCODE;
  if (!pass) {
    return NextResponse.json({error: 'The studio is locked: STUDIO_PASSCODE is not set in the project settings.'}, {status: 503});
  }
  let given = '';
  try {
    given = String((await req.json()).passcode || '');
  } catch {
    return NextResponse.json({error: 'bad request'}, {status: 400});
  }
  await new Promise((r) => setTimeout(r, 400)); // slow down guessing
  if (!safeEqual(await sessionToken(given), await sessionToken(pass))) {
    return NextResponse.json({error: 'Wrong passcode.'}, {status: 401});
  }
  const res = NextResponse.json({ok: true});
  res.cookies.set(COOKIE, await sessionToken(pass), {
    httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax', path: '/', maxAge: 60 * 60 * 24 * 30,
  });
  return res;
}
