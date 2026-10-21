# Barcha gaplar qiz ovozida: qizning o'z gaplari (toza, tenglashtirilgan) + o'g'il bola gaplari Sarah (eleven_v4, uz) ovozida,
# o'g'il bola gapirgan vaqtlarga qo'yiladi. Fon: asl musiqa (bed.wav), hushtak yo'q, oxirida olqish.
import json, numpy as np, subprocess
SR=44100; Q='/home/user/Loyha-/audio/badantarbiya/qiz_ovozi/audio/'
def load(p,ch=1,af='anull'):
    a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-af',af,'-f','f32le','-ac',str(ch),'-ar',str(SR),'-'],capture_output=True).stdout,np.float32).reshape(-1,ch).copy()
    return a[:,0] if ch==1 else a
def lufs(x):
    x.astype(np.float32).tofile('t.f32')
    r=subprocess.run(['ffmpeg','-hide_banner','-f','f32le','-ar',str(SR),'-ac','1','-i','t.f32','-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])
vf=load('vf.wav'); n=len(vf)
w=[x for x in json.load(open('stt.json'))['words'] if x.get('type')=='word' and x['speaker_id']=='speaker_0']
fw=np.concatenate([vf[int(x['start']*SR):int(x['end']*SR)] for x in w])
TARGET=-16.8; vf=vf*10**((TARGET-lufs(fw))/20)
mf=np.zeros(n,np.float32)
for x in w: mf[max(0,int((x['start']-.15)*SR)):min(n,int((x['end']+.25)*SR))]=1
mf=np.convolve(mf,np.ones(int(.06*SR))/int(.06*SR),'same'); vox=vf*mf
# o'g'il bola gaplari -> qiz (Sarah) ovozi; qizning mikrofon rangiga yaqinlashtirish: o'sha EQ zanjiri + yengil yuqori kesish
CHAIN='silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,highpass=f=90,lowpass=f=11000,highshelf=f=3000:g=-5,equalizer=f=5500:t=q:w=1.5:g=-3,acompressor=threshold=-24dB:ratio=3:attack=6:release=120'
spans=json.load(open('conv/spans.json')); prev=0
for sp in spans:
    a=load(Q+f"m{sp['i']}.mp3",1,CHAIN); a=a*10**((TARGET-lufs(a))/20)
    st=max(sp['s']+0.08, prev+0.15); i=int(st*SR); e=min(n,i+len(a))
    vox[i:e]+=a[:e-i]; prev=st+len(a)/SR
    print('m%d %.2f-%.2f (asl %.2f-%.2f)'%(sp['i'],st,prev,sp['s'],sp['e']))
vox.astype(np.float32).tofile('v.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','v.f32','-af','aecho=0.9:0.6:35|60:0.10|0.06','v_rev.wav'],check=True)
vox=load('v_rev.wav')[:n]
music=load('bed.wav',2); T=len(music); vo=np.zeros(T,np.float32); vo[:min(n,T)]=vox[:min(n,T)]
act=(np.convolve(np.abs(vo),np.ones(2205)/2205,'same')>0.003).astype(np.float32)
env=np.clip(np.convolve(act,np.ones(int(.35*SR))/int(.35*SR),'same')*1.5,0,1)
fade=np.ones(T,np.float32); fe=int((T/SR-2.5)*SR); fade[fe:]=np.linspace(1,0,T-fe)
out=music*((1-env*(1-10**(-9/20)))*fade)[:,None]+vo[:,None]
ap=load('applause.mp3',2); i=int(288.2*SR); e=min(T,i+len(ap)); out[i:e]+=ap[:e-i]*0.45
np.clip(out,-1,1).astype(np.float32).tofile('mix.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','mix.f32','mix_qiz.wav'],check=True)
