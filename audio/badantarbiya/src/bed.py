# Asl musiqadan ovozsiz fon tiklash: gapirilgan joylar musiqaning gapsiz bo'laklari bilan to'ldiriladi.
# Ulanish nuqtasi to'lqin shakli bo'yicha eng o'xshash joydan tanlanadi (ritm va faza saqlanadi), 120 ms crossfade.
import numpy as np, subprocess, json
from scipy.signal import fftconvolve
SR=44100
O=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','orig.wav','-f','f32le','-ac','2','-'],capture_output=True).stdout,np.float32).reshape(-1,2).copy()
N=len(O)
w=[x for x in json.load(open('stt.json'))['words'] if x.get('type')=='word']
speech=np.zeros(N,bool)
for x in w: speech[max(0,int((x['start']-.35)*SR)):min(N,int((x['end']+.45)*SR))]=True
# bo'shliqlarni (gap ichidagi < 1.2 s) ham nutq deb hisoblaymiz
idx=np.flatnonzero(np.diff(speech.astype(int)))
runs=[]; st=None; v=speech[0]; s=0
for i in list(idx)+[N-1]:
    runs.append((s,i+1,speech[s])); s=i+1
spans=[]
for s,e,isS in runs:
    if isS:
        if spans and s-spans[-1][1]<1.2*SR: spans[-1][1]=e
        else: spans.append([s,e])
free=np.ones(N,bool)
for s,e in spans: free[s:e]=False
mono=O.mean(1); D=4; m=mono[::D]; sr=SR//D
okd=free[::D]
bed=O.copy(); XF=int(.25*SR); CTX=int(.6*sr)
def best_src(ctx, need, ctx2=None):
    """ctx: oxirgi 0.6 s (downsampled); topilgan joydan keyin need namuna bo'sh (gapsiz) bo'lishi kerak."""
    c=fftconvolve(m, ctx[::-1], 'valid'); e=np.sqrt(fftconvolve(m*m, np.ones(len(ctx)), 'valid'))+1e-9
    score=c/e
    L=len(score); valid=np.zeros(L,bool)
    # manba oynasi + davomi butunlay bo'sh bo'lsin
    cs=np.concatenate([[0],np.cumsum(~okd)])
    endr=np.arange(L)+len(ctx)+need; endi=np.minimum(endr, len(okd))
    valid=((cs[endi]-cs[np.arange(L)])==0) & (endr<=len(okd))
    if ctx2 is not None:   # oxirgi bo'lak: ulanishning chiqish tomoni ham asl musiqaga mos kelsin
        c2=fftconvolve(m, ctx2[::-1], 'valid'); e2=np.sqrt(fftconvolve(m*m, np.ones(len(ctx2)), 'valid'))+1e-9
        s2=np.full(L,-9.0); off=len(ctx)+need-len(ctx2)//2
        idx=np.arange(L)+off; ok=idx<len(c2); s2[ok]=(c2/e2)[idx[ok]]
        score=score+s2
    score[~valid]=-99
    k=int(np.argmax(score)); return (k+len(ctx))*D, score[k]
for s,e in spans:
    p=s
    while p<e:
        ctx=bed[max(0,p-CTX*D):p].mean(1)[::D]
        need=min(e-p+XF, int(20*SR))
        while True:   # gapsiz bo'lak topilmasa, uzunlikni qisqartiramiz
            last = e-p+XF <= need
            ctx2 = O[e:e+int(.6*SR)].mean(1)[::D] if last and e+int(.6*SR)<=N else None
            src,sc=best_src(ctx, (e-p+XF)//D+1 if last else need//D+1, ctx2)
            if sc>-90 or need<int(1.5*SR): break
            need=int(need*0.75)
        assert sc>-90, 'gapsiz manba topilmadi'
        L=min(e-p, need-XF) if e-p>need-XF else e-p
        seg=O[src:src+L+XF]
        fi=np.linspace(0,1,XF)[:,None]
        bed[p:p+XF]=bed[p:p+XF]*(1-fi)+seg[:XF]*fi
        bed[p+XF:p+L]=seg[XF:L]
        # chiqishda asl musiqaga qaytish crossfade
        if p+L>=e and e+XF<=N:
            fo=np.linspace(1,0,XF)[:,None]; bed[e:e+XF]=seg[L:L+XF]*fo+O[e:e+XF]*(1-fo)
        print('span %.1f-%.1f  chunk@%.1f <- src %.1f (%.2fs, score %.2f)'%(s/SR,e/SR,p/SR,src/SR,L/SR,sc))
        p+=L
bed.astype(np.float32).tofile('bed.f32')
