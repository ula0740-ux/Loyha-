"""Kia Sonet slaydini bitta HTML faylga yig'ish (mashina rasmi base64 ichida)."""
import base64, pathlib
H = pathlib.Path(__file__).parent
src = (H / 'sonet.src.html').read_text(encoding='utf-8')
car = 'data:image/webp;base64,' + base64.b64encode((H / 'assets/sonet_cut.webp').read_bytes()).decode()
(H / 'Kia_Sonet_slayd.html').write_text(src.replace('{{CAR}}', car), encoding='utf-8')
print('ok', (H / 'Kia_Sonet_slayd.html').stat().st_size // 1024, 'KB')
