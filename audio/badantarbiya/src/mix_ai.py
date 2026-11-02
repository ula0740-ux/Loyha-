# Barcha gaplar sun'iy intellekt ovozida (Sarah, eleven_v4 uz, STT tekshiruvi), asl gap vaqtlarida;
import os
# fon — asl musiqa (bed.wav, gapsiz tiklangan), hushtak yo'q, oxirida olqish.
import json, numpy as np, subprocess
SR=44100; Q='/home/user/Loyha-/audio/badantarbiya/qiz_ovozi/audio/'
# (asl boshlanish vaqti, fayl) — qiz (f*) va o'g'il bola (m*) gaplari, vaqt tartibida
LINES=[(1.54,'f0'),(22.82,'m0'),(24.94,'m1'),(51.62,'f1'),(76.20,'m2'),(81.88,'m3'),(111.16,'f2'),
       (141.66,'m4'),(148.61,'m5'),(166.62,'f3'),(198.10,'m6'),(225.70,'m7'),(253.46,'f4'),(279.78,'f5')]
def load(p,ch=1,af='anull'):
    a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-af',af,'-f','f32le','-ac',str(ch),'-ar',str(SR),'-'],capture_output=True).stdout,np.float32).reshape(-1,ch).copy()
    return a[:,0] if ch==1 else a
def lufs(x):
    x.astype(np.float32).tofile('t.f32')
    r=subprocess.run(['ffmpeg','-hide_banner','-f','f32le','-ar',str(SR),'-ac','1','-i','t.f32','-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])
CHAIN='silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,highpass=f=90,highshelf=f=4000:g=-2.5,acompressor=threshold=-24dB:ratio=2.5:attack=6:release=120'
import sys
BEDF=sys.argv[1] if len(sys.argv)>1 else 'bed.wav'
music=load(BEDF,2)*10**(float(os.environ.get('MUSIC_DB','0'))/20); T=len(music); vo=np.zeros(T,np.float32); prev=0
for at,fid in LINES:
    a=load(Q+fid+'.mp3',1,CHAIN); a=a*10**((-16.5-lufs(a))/20)
    st=max(at, prev+0.6); i=int(st*SR); e=min(T,i+len(a)); vo[i:e]+=a[:e-i]; prev=st+len(a)/SR
    print(fid,'%.2f-%.2f'%(st,prev))
vo.astype(np.float32).tofile('v.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','v.f32','-af','aecho=0.9:0.6:35|60:0.08|0.05','v_ai.wav'],check=True)
vo=load('v_ai.wav')[:T]; vo=np.pad(vo,(0,T-len(vo)))
act=(np.convolve(np.abs(vo),np.ones(2205)/2205,'same')>0.003).astype(np.float32)
env=np.clip(np.convolve(act,np.ones(int(.35*SR))/int(.35*SR),'same')*1.5,0,1)
fade=np.ones(T,np.float32); fe=int((T/SR-1.0)*SR); fade[fe:]=np.linspace(1,0,T-fe)
out=music*((1-env*(1-10**(-9/20)))*fade)[:,None]+vo[:,None]
ap=load('applause.mp3',2); i=int((prev+0.3)*SR); e=min(T,i+len(ap)); out[i:e]+=ap[:e-i]*0.45
np.clip(out,-1,1).astype(np.float32).tofile('mix.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','mix.f32','mix_ai.wav'],check=True)
