# Asl musiqadan uzluksiz fon: gapsiz bo'laklar O'Z TARTIBIDA ketma-ket ulanadi (musiqa oldinga oqadi, orqaga sakramaydi),
# har bo'lak bir xil balandlikka keltiriladi, ulanishlar ritmga moslab 0.6 s crossfade bilan. Kerakli uzunlikka yetguncha davom etadi.
import json, numpy as np, subprocess, sys
from scipy.signal import fftconvolve
SR=44100; TOTAL=float(sys.argv[1]) if len(sys.argv)>1 else 296
O=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','orig.wav','-f','f32le','-ac','2','-'],capture_output=True).stdout,np.float32).reshape(-1,2).copy()
N=len(O)
w=[x for x in json.load(open('stt.json'))['words'] if x.get('type')=='word']
sp=np.zeros(N,bool)
for x in w: sp[max(0,int((x['start']-.5)*SR)):min(N,int((x['end']+.7)*SR))]=True
# gapsiz bo'laklar (>= 4 s)
reg=[]; i=0
while i<N:
    if not sp[i]:
        j=i
        while j<N and not sp[j]: j+=1
        if (j-i)/SR>=4: reg.append((i,j))
        i=j
    else: i+=1
print('bo\'laklar:',[(round(a/SR,1),round(b/SR,1)) for a,b in reg], 'jami %.1fs'%(sum(b-a for a,b in reg)/SR))
def rms(x): return np.sqrt((x**2).mean())+1e-9
target=np.median([rms(O[a:b]) for a,b in reg])
parts=[O[a:b]*(target/rms(O[a:b])) for a,b in reg]
outro=parts.pop()            # asl musiqaning yakuni — faqat eng oxirida
BODY=TOTAL-len(outro)/SR+0.6
XF=int(.6*SR); D=4
def align(tail, head):
    """head boshidagi 2 s ichidan tail oxiriga eng mos (faza/ritm) nuqtani topadi."""
    t=tail[-int(.8*SR):].mean(1)[::D]; h=head[:int(2.8*SR)].mean(1)[::D]
    c=fftconvolve(h,t[::-1],'valid'); e=np.sqrt(fftconvolve(h*h,np.ones(len(t)),'valid'))+1e-9
    k=int(np.argmax(c/e)); return (k+len(t))*D   # head ichida tail tugagan joyga mos keladigan nuqta
out=parts[0].copy(); k=1
while len(out)<BODY*SR+XF:
    nxt=parts[k%len(parts)]; k+=1
    j=align(out, nxt)
    j=max(XF, min(j, len(nxt)//3))
    seg=nxt[j-XF:]
    f=np.linspace(0,1,XF)[:,None]
    out[-XF:]=out[-XF:]*(1-f)+seg[:XF]*f
    out=np.concatenate([out, seg[XF:]])
out=out[:int(BODY*SR)]
j=align(out, outro); j=max(XF, min(j, len(outro)//3)); seg=outro[j-XF:]
f=np.linspace(0,1,XF)[:,None]; out[-XF:]=out[-XF:]*(1-f)+seg[:XF]*f; out=np.concatenate([out, seg[XF:]])
# yakuniy yumshoq tekislash: qisqa muddatli balandlik o'zgarishini kamaytirish
out.astype(np.float32).tofile('bed2.f32')
print('fon %.1fs, %d bo\'lak ulandi'%(len(out)/SR, k))
