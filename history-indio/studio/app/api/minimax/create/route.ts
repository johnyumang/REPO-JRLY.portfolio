import {NextRequest, NextResponse} from 'next/server';
import {createTask, minimaxConfigured} from '@/lib/providers/minimax';

export const dynamic = 'force-dynamic';
export const maxDuration = 30; // creating a task is one short request

export async function POST(req: NextRequest) {
  if (!minimaxConfigured()) return NextResponse.json({error: 'MiniMax is not set up on this deployment.'}, {status: 503});
  let body: {image?: string; prompt?: string; duration?: number};
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({error: 'bad request'}, {status: 400});
  }
  const image = String(body.image || '');
  if (!/^(https:\/\/|data:image\/(jpeg|png|webp);base64,)/.test(image)) {
    return NextResponse.json({error: 'image must be an https URL or an uploaded picture'}, {status: 400});
  }
  if (!body.prompt) return NextResponse.json({error: 'prompt is empty'}, {status: 400});
  try {
    const taskId = await createTask({image, prompt: String(body.prompt), duration: Number(body.duration) || 6});
    return NextResponse.json({taskId});
  } catch (e) {
    return NextResponse.json({error: (e as Error).message}, {status: 502});
  }
}
