import {NextRequest, NextResponse} from 'next/server';
import {queryTask} from '@/lib/providers/minimax';

export const dynamic = 'force-dynamic';
export const maxDuration = 30;

export async function GET(req: NextRequest) {
  const id = req.nextUrl.searchParams.get('taskId');
  if (!id || !/^[\w-]{1,64}$/.test(id)) return NextResponse.json({error: 'taskId missing'}, {status: 400});
  try {
    return NextResponse.json(await queryTask(id));
  } catch (e) {
    return NextResponse.json({status: 'running', error: (e as Error).message}, {status: 200}); // transient: keep polling
  }
}
