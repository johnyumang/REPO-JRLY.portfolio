import {NextRequest, NextResponse} from 'next/server';
import {COOKIE, isAuthed} from './lib/auth';

// Everything is locked unless the visitor has the passcode cookie: the studio can spend the owner's credits.
const OPEN = ['/login', '/api/login'];

export async function middleware(req: NextRequest) {
  const {pathname} = req.nextUrl;
  if (OPEN.includes(pathname)) return NextResponse.next();
  if (await isAuthed(req.cookies.get(COOKIE)?.value)) return NextResponse.next();
  if (pathname.startsWith('/api/')) {
    return NextResponse.json({error: 'locked'}, {status: 401});
  }
  const url = req.nextUrl.clone();
  url.pathname = '/login';
  url.search = '';
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
