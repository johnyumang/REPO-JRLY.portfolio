import {NextResponse} from 'next/server';
import {minimaxConfigured} from '@/lib/providers/minimax';

export const dynamic = 'force-dynamic';

// Which providers this deployment can use. Never returns a key, only whether one is set.
export async function GET() {
  return NextResponse.json({
    'wan-free': {ready: true, free: true, note: 'Runs from your browser on a free shared GPU; may queue or hit a daily limit.'},
    minimax: {ready: minimaxConfigured(), free: false, note: 'Spends MiniMax credits on every take.'},
  });
}
