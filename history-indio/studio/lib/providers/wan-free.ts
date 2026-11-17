'use client';
// The free provider runs in the browser: it talks to the public Hugging Face Space directly, so no server function
// waits on it (the Space cancels a job when its connection closes, which rules out create-then-poll on a server).
// It uses the viewer's own free GPU quota on the Space; no key is involved.

export const WAN_SPACE = 'https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space';
export const WAN_MAX_SECONDS = 5;
const NEG = 'static, frozen, camera cut, scene change, morphing face, extra fingers, extra limbs, duplicate person, '
  + 'hands only, text, subtitles, watermark, blurry, low quality, photorealistic, 3d render';

type Update = {status: 'queued' | 'running'; note?: string};

async function imageBlob(image: string): Promise<Blob> {
  const res = await fetch(image);
  if (!res.ok) throw new Error(`could not load the image (${res.status})`);
  return res.blob();
}

export async function runWanFree(
  opts: {image: string; prompt: string; negative?: string; duration: number},
  onUpdate: (u: Update) => void,
): Promise<{url: string; seed?: number}> {
  const {Client, handle_file} = await import('@gradio/client');
  onUpdate({status: 'queued', note: 'connecting'});
  const client = await Client.connect(WAN_SPACE, {events: ['data', 'status']});
  const blob = await imageBlob(opts.image);
  const job = client.submit('/generate_video', {
    input_image: handle_file(blob),
    prompt: opts.prompt,
    steps: 6,
    negative_prompt: opts.negative || NEG,
    duration_seconds: Math.max(0.5, Math.min(WAN_MAX_SECONDS, opts.duration)),
    guidance_scale: 1,
    guidance_scale_2: 1,
    seed: 42,
    randomize_seed: true,
  });
  for await (const ev of job as AsyncIterable<{type: string; stage?: string; position?: number; eta?: number;
    title?: string; message?: unknown; success?: boolean; data?: unknown[]}>) {
    if (ev.type === 'status') {
      if (ev.stage === 'error') {
        throw new Error([ev.title, ev.message].filter(Boolean).join(': ') || 'the Space returned an error (quota or queue)');
      }
      if (ev.stage === 'pending') {
        onUpdate({status: 'queued', note: ev.position != null ? `queue position ${ev.position}` : 'waiting for a GPU'});
      } else if (ev.stage === 'generating' || ev.stage === 'streaming') {
        onUpdate({status: 'running', note: ev.eta ? `about ${Math.round(ev.eta)}s` : 'generating'});
      }
    } else if (ev.type === 'data' && Array.isArray(ev.data)) {
      const first = ev.data[0] as {video?: {url?: string}; url?: string} | string | undefined;
      const url = typeof first === 'string' ? first : first?.video?.url ?? first?.url;
      if (!url) throw new Error('the Space finished without a video');
      return {url, seed: typeof ev.data[1] === 'number' ? (ev.data[1] as number) : undefined};
    }
  }
  throw new Error('the connection to the Space closed before the video was ready');
}
