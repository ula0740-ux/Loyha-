import { createApp } from './app.ts';
import { getBundle } from './pipeline.ts';

const PORT = Number(process.env.PORT || 3000);
const app = createApp(() => PORT);
app.listen(PORT, () => {
  console.log(`Studio: http://localhost:${PORT}`);
  getBundle().then(() => console.log('Remotion bundle tayyor.'));
});
