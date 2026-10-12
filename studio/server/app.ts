import './net.ts';
import express from 'express';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { allVoices, readStatus } from './tts/index.ts';
import { MEDIA_DIR, OUT_DIR, ROOT, narrate, renderVideo, type JobInput } from './pipeline.ts';
import { detectScript, toScript } from '../src/lib/uzbek.ts';

interface Job {
  id: string;
  state: 'queued' | 'running' | 'done' | 'error';
  stage: string;
  progress: number;
  error?: string;
  file?: string;
  timing?: string[];
}

export function createApp(getPort: () => number) {
  const app = express();
  const jobs = new Map<string, Job>();
  app.use(express.json({ limit: '1mb' }));
  app.use(express.static(fileURLToPath(new URL('../ui', import.meta.url))));
  app.use('/media', express.static(MEDIA_DIR));
  app.use('/verify', express.static(join(ROOT, 'public/verify')));
  app.use('/out', express.static(OUT_DIR));

  // Voices grouped by provider, each with its real verification result (never assumed).
  app.get('/api/voices', async (_req, res) => {
    const status = await readStatus();
    const groups = await allVoices();
    res.json(
      groups.map((g) => ({
        id: g.provider.id,
        label: g.provider.label,
        kind: g.provider.kind,
        env: g.provider.env,
        hosts: g.provider.hosts,
        ok: g.ok,
        reason: g.reason,
        voices: g.voices.map((v) => ({ ...v, status: status[v.key] ?? null })),
      })),
    );
  });

  app.post('/api/transliterate', (req, res) => {
    const { text, to } = req.body as { text: string; to: 'latin' | 'cyrillic' };
    res.json({ text: toScript(text, to), from: detectScript(text) });
  });

  app.post('/api/render', async (req, res) => {
    const input = req.body as JobInput;
    const scenes = (input.scenes || []).map((s) => String(s).trim()).filter(Boolean);
    if (!scenes.length) return res.status(400).json({ error: 'Kamida bitta sahna matnini kiriting.' });
    if (!input.voice) return res.status(400).json({ error: 'Ovozni tanlang.' });
    const job: Job = { id: randomUUID().slice(0, 8), state: 'queued', stage: 'Navbatda', progress: 0 };
    jobs.set(job.id, job);
    res.json({ id: job.id });
    const progress = (stage: string, p: number) => Object.assign(job, { state: 'running', stage, progress: p });
    try {
      const { props, timing } = await narrate(job.id, { ...input, scenes }, `http://localhost:${getPort()}/media`, progress);
      job.timing = timing;
      const file = await renderVideo(job.id, props, progress);
      Object.assign(job, { state: 'done', stage: 'Tayyor', progress: 1, file: '/out/' + file.split('/').pop() });
    } catch (e) {
      Object.assign(job, { state: 'error', stage: 'Xato', error: String((e as Error).message).slice(0, 500) });
    }
  });

  app.get('/api/jobs/:id', (req, res) => {
    const job = jobs.get(req.params.id);
    if (!job) return res.status(404).json({ error: 'Topilmadi' });
    res.json(job);
  });

  return app;
}
