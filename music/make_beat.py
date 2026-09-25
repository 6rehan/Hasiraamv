# Original dreamy hip-hop beat ("late-night Tumblr" vibe) - 92 BPM, F minor
import numpy as np, wave
SR=44100; BPM=92; BEAT=60/BPM; BAR=4*BEAT
def n2f(n): return 440*2**((n-69)/12)
def env(t,a,d): return np.minimum(t/a,1)*np.exp(-t/d)
def piano(f,dur,v=.3):
    t=np.arange(int(dur*SR))/SR
    s=sum(np.sin(2*np.pi*f*k*t)/k**1.6 for k in range(1,6))
    return v*s*env(t,.005,.9)
def pad(f,dur,v=.08):
    t=np.arange(int(dur*SR))/SR
    s=sum(np.sin(2*np.pi*f*(1+d)*t+np.sin(2*np.pi*.3*t)) for d in(-.004,0,.004))
    return v*s*np.minimum(t/.6,1)*np.minimum((dur-t)/.5,1)
def b808(f,dur,v=.7):
    t=np.arange(int(dur*SR))/SR
    fr=f*(1+2*np.exp(-t*30)); ph=2*np.cumsum(fr)/SR*np.pi
    return v*np.tanh(1.5*np.sin(ph))*np.exp(-t/1.2)
def kick():
    t=np.arange(int(.35*SR))/SR; ph=2*np.pi*np.cumsum(50+120*np.exp(-t*40))/SR
    return .9*np.sin(ph)*np.exp(-t*9)
def snare():
    t=np.arange(int(.3*SR))/SR; r=np.random.default_rng(1)
    return .45*(r.standard_normal(len(t))*np.exp(-t*18)+.5*np.sin(2*np.pi*190*t)*np.exp(-t*25))
def hat(o=False):
    t=np.arange(int((.25 if o else .05)*SR))/SR; r=np.random.default_rng(2)
    n=r.standard_normal(len(t)); n=np.diff(n,prepend=0)
    return .12*n*np.exp(-t*(12 if o else 90))
BARS=32; out=np.zeros(int((BARS*BAR+3)*SR))
def put(x,sec):
    i=int(sec*SR); out[i:i+len(x)]+=x[:len(out)-i]
# F minor progression: Fm - Db - Ab - Eb (original voicings)
chords=[[53,56,60,63],[49,53,56,60],[56,60,63,67],[51,55,58,62]]
roots=[41,37,44,39]
# original lead motif (per 2 bars, 8th-note grid index, midi)
motif=[(0,72),(3,75),(4,77),(6,75),(8,72),(11,70),(12,68),(14,70)]
for b in range(BARS):
    t0=b*BAR; c=chords[b%4]; sec=b//8   # sections: intro, verse, hook, outro
    for n in c: put(pad(n2f(n),BAR),t0)
    for i,n in enumerate(c+[c[2]+12]): put(piano(n2f(n+12),1.5,.07),t0+i*BEAT*.5)
    if sec in(1,2,3):
        put(b808(n2f(roots[b%4]-12),BAR*.9),t0); put(b808(n2f(roots[b%4]-12),BEAT*1.2,.5),t0+2.5*BEAT)
        for k in(0,1.75,2.5): put(kick(),t0+k*BEAT)
        for k in(1,3): put(snare(),t0+k*BEAT)
        for h in range(16 if sec==2 else 8):
            step=BAR/(16 if sec==2 else 8); put(hat(h%8==6),t0+h*step)
        if sec==2 and b%2==1: [put(hat(),t0+3.5*BEAT+j*BEAT/12) for j in range(6)]  # hat roll
    if sec in(2,3) and b%2==0:
        for idx,n in motif: put(piano(n2f(n),.8,.16),t0+idx*BEAT/2)
out/=np.max(np.abs(out))*1.1
# tiny reverb
d=int(.09*SR); wet=out.copy()
for k in range(1,6): wet[d*k:]+=out[:-d*k]*.35**k
wet/=np.max(np.abs(wet))*1.05
pcm=(np.stack([wet,np.roll(wet,300)],1)*32767).astype(np.int16)
with wave.open('late_night_scroll_beat.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('done', BARS*BAR, 'sec')
