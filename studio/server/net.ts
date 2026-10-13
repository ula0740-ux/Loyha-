// Load .env and make fetch() honour HTTPS_PROXY / NO_PROXY (Node's built-in fetch ignores them).
import 'dotenv/config';
import { EnvHttpProxyAgent, setGlobalDispatcher } from 'undici';

process.removeAllListeners('warning'); // hide undici's 'experimental' notice
if (process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY) {
  setGlobalDispatcher(new EnvHttpProxyAgent());
}

export async function fetchOk(url: string, init?: RequestInit): Promise<Response> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`HTTP ${res.status} ${new URL(url).host}: ${body}`);
  }
  return res;
}
