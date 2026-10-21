# python3 mix.py BED OFFSET OUT.wav   — toza ovozlar (vf.wav/vm.wav) + fon, ovozlar tenglashtirilgan, keraksiz so'zlar olib tashlangan
import json, sys, numpy as np, subprocess
SR=44100; BED, OFF, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
def load(p,ch=1):
    a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-f','f32le','-ac',str(ch),'-ar',str(SR),'-'],capture_output=True).stdout,np.float32).reshape(-1,ch).copy()
    return a[:,0] if ch==1 else a
vf,vm=load('vf.wav'),load('vm.wav'); n=min(len(vf),len(vm)); vf,vm=vf[:n],vm[:n]
w=[x for x in json.load(open('stt.json'))['words'] if x.get('type')=='word']
CUTS=[(63.0,74.9),      # erkakning sanashi "bir, ikki, uch, to'rt" x3
      (93.50,94.70),    # "Qani bo'shashmaymiz"
      (152.75,153.95),  # "Qani bo'shashmaymiz"
      (210.95,212.55)]  # "Qani, ADM, bo'shashmaymiz"
inside=lambda x: any(x['start']>=a and x['end']<=b for a,b in CUTS)
words=[x for x in w if not inside(x)]
def lufs(x):
    x.astype(np.float32).tofile('t.f32')
    r=subprocess.run(['ffmpeg','-hide_banner','-f','f32le','-ar',str(SR),'-ac','1','-i','t.f32','-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])
seg=lambda spk,sig: np.concatenate([sig[int(x['start']*SR):int(x['end']*SR)] for x in words if x['speaker_id']==spk])
gF=10**((-16.8-lufs(seg('speaker_0',vf)))/20); gM=10**((-16.0-lufs(seg('speaker_1',vm)))/20)
mf=np.zeros(n,np.float32); mm=np.zeros(n,np.float32)
for x in words:
    i,e=max(0,int((x['start']-.15)*SR)),min(n,int((x['end']+.25)*SR))
    (mf if x['speaker_id']=='speaker_0' else mm)[i:e]=1
for a,b in CUTS: mf[int(a*SR):int(b*SR)]=0; mm[int(a*SR):int(b*SR)]=0
k=np.ones(int(.06*SR))/int(.06*SR); mf=np.convolve(mf,k,'same'); mm=np.minimum(np.convolve(mm,k,'same'),1-mf)
vox=vf*gF*mf+vm*gM*mm
vox.astype(np.float32).tofile('v.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','v.f32','-af','aecho=0.9:0.6:35|60:0.10|0.06','v_rev.wav'],check=True)
vox=load('v_rev.wav')[:n]
music=load(BED,2); T=max(len(music), int((n/SR+OFF+1)*SR)); music=np.pad(music,((0,T-len(music)),(0,0)))
out=np.zeros((T,2),np.float32); vo=np.zeros(T,np.float32); i0=int(OFF*SR); vo[i0:i0+n]=vox[:T-i0]
act=(np.convolve(np.abs(vo),np.ones(2205)/2205,'same')>0.003).astype(np.float32)
env=np.clip(np.convolve(act,np.ones(int(.35*SR))/int(.35*SR),'same')*1.5,0,1)
duck=1-env*(1-10**(-9/20))
fade=np.ones(T,np.float32); fe=int((T/SR-2.5)*SR); fade[fe:]=np.linspace(1,0,T-fe)
out=music*(duck*fade)[:,None]*float(sys.argv[4] if len(sys.argv)>4 else 1)+vo[:,None]
def sfx(p,at,g):
    a=load(p,2); i=int(at*SR); e=min(T,i+len(a)); out[i:e]+=a[:e-i]*g
sfx('whistle.mp3', max(0.2, OFF-1.7), 0.5)
sfx('applause.mp3', max(x['end'] for x in words)+OFF+0.3, 0.45)
np.clip(out,-1,1).astype(np.float32).tofile('mix.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','mix.f32',OUT],check=True)
print(OUT, 'female %.1f male %.1f, %.1fs'%(lufs(seg('speaker_0',vf*gF)),lufs(seg('speaker_1',vm*gM)),T/SR))
