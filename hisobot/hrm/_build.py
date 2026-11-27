import base64,json,html,glob
t=json.load(open('titles.json',encoding='utf-8')); t[0]='HRM Ҳисоботи 2026'
fs=sorted(glob.glob('s-*.webp')); assert len(fs)==29
imgs='\n'.join(f'    <img src="data:image/webp;base64,{base64.b64encode(open(f,"rb").read()).decode()}" alt="{html.escape(t[i])}" decoding="async" draggable="false">' for i,f in enumerate(fs))
s=open('template.html',encoding='utf-8').read().replace('__IMGS__',imgs)
open('/home/user/Loyha-/hisobot/hrm/HRM_2026_taqdimot.html','w',encoding='utf-8').write(s)
print(len(s)//1024,'KB')
