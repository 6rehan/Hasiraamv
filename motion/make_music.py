import numpy as np, wave
SR=44100; D=20.0; N=int(SR*D); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7); B=0.5  # beat seconds @120bpm
def n2f(n): return 440*2**((n-69)/12)
def add(sig,t,pan=0.0,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); 
    if i>=N: return
    s=sig[:j-i]*g; L[i:j]+=s*np.sqrt((1-pan)/2); R[i:j]+=s*np.sqrt((1+pan)/2)
def env(n,a,d): t=np.arange(n)/SR; return np.minimum(1,t/max(a,1e-4))*np.exp(-t/d)
def saw(f,dur,det=0.0):
    t=np.arange(int(dur*SR))/SR; o=0
    for dv in (-det,0,det): o=o+2*((t*f*(1+dv))%1)-1
    return o/3
def lp(x,a):  # one-pole lowpass, a in (0,1]
    y=np.empty_like(x); z=0.0
    for k in range(len(x)): z+=a*(x[k]-z); y[k]=z
    return y
def kick(g=1):
    n=int(.45*SR); t=np.arange(n)/SR; f=45+110*np.exp(-t/.035)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.16)*g+ rng.standard_normal(n)*np.exp(-t/.003)*.3
def hat(d=.04): n=int(.15*SR); x=rng.standard_normal(n); x=x-np.concatenate([[0],x[:-1]]); return x*env(n,.001,d)
def clap():
    n=int(.35*SR); x=rng.standard_normal(n); e=np.zeros(n); t=np.arange(n)/SR
    for o in (0,.011,.022): e+=np.where(t>=o,np.exp(-(t-o)/.012),0)
    e+=np.exp(-t/.09)*.6; x=x-lp(x,.15); return x*e*.5
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]   # Am F C G
roots=[45,41,48,43]
# --- intro 0-3: pad swell + noise riser + reverse swell
for c in range(2):
    for n in chords[0]+[69]:
        s=saw(n2f(n),3.0,.006); s=lp(s,.04); tt=np.arange(len(s))/SR; add(s*(tt/3)**2*.18,0,pan=rng.uniform(-.6,.6))
nz=rng.standard_normal(int(3*SR)); tt=np.arange(len(nz))/SR
ris=np.zeros_like(nz); z=0; 
for k in range(len(nz)): a=.01+.5*(tt[k]/3)**3; z+=a*(nz[k]-z); ris[k]=z
add(ris*(tt/3)**3*.5,0)
for i,t in enumerate([.25,.5,.75,1.0]):  # word hits
    s=np.sin(2*np.pi*n2f(76+[0,3,7,12][i])*np.arange(int(.6*SR))/SR)*env(int(.6*SR),.002,.18); add(s,t,pan=(i-1.5)/2,g=.22)
# sub drop into 3s
n=int(1.6*SR); t=np.arange(n)/SR; add(np.sin(2*np.pi*np.cumsum(55*np.exp(-t/1.2)+30)/SR)*np.exp(-t/.7)*.7,3.0)
crash=rng.standard_normal(int(2.5*SR)); crash=(crash-lp(crash,.3))*env(len(crash),.001,.6); add(crash,3.0,g=.35); add(crash,17.5,g=.45)
# --- main groove 3 -> 17.5
end_groove=17.5
t=3.0; bar=0
while t<end_groove-1e-6:
    b=int(round((t-3)/B))
    build = t>=15.5
    if not build or b%2==0: add(kick(),t,g=.95)
    add(hat(.03),t+B/2,pan=.3,g=.22); add(hat(.015),t+B*.25,pan=-.3,g=.08); add(hat(.015),t+B*.75,pan=-.3,g=.08)
    if b%2==1 and not build: add(clap(),t,pan=.05,g=.55)
    t+=B
# bass + pad + arp per 2s bar
for k,bt in enumerate(np.arange(3.0,end_groove,2.0)):
    ci=(k)%4; dur=min(2.0,end_groove-bt)
    for e in range(int(dur/ .25)):
        s=saw(n2f(roots[ci]-12 if e%2==0 else roots[ci]),.24,.003); s=lp(s,.08)*env(len(s),.003,.12)
        tt=np.arange(len(s))/SR; add(s*(1-np.exp(-tt/.01)),bt+e*.25+.0,g=.55)   # offbeat pump feel
    for n in chords[ci]:
        s=lp(saw(n2f(n+12),dur,.008),.05); tt=np.arange(len(s))/SR
        duck=1-.7*np.exp(-((tt)%B)/.12); add(s*duck*np.minimum(1,tt/.05)*.07,bt,pan=rng.uniform(-.7,.7))
    arp=chords[ci]+[chords[ci][0]+12]
    for e in range(int(dur/.125)):
        if 9.5<=bt+e*.125<12 or bt>=12 or e%2==0:
            n=arp[e%4]+24; s=saw(n2f(n),.12,.004); s=lp(s,.25)*env(len(s),.001,.05)
            add(s,bt+e*.125,pan=np.sin(e*.7)*.6,g=.10)
# code scene: terminal line blips at 3.25 + j*0.5
for j in range(6): 
    s=np.sin(2*np.pi*1800*np.arange(int(.05*SR))/SR)*env(int(.05*SR),.001,.012); add(s,3.25+j*.5,pan=.4,g=.25)
    for q in range(6): add(hat(.006),3.25+j*.5+q*.04,pan=-.2,g=.05)  # typing clicks
# chart bars: rising plucks
scale=[69,72,74,76,79,81,84,86]
for j in range(8):
    s=saw(n2f(scale[j]),.4,.002); s=lp(s,.2)*env(len(s),.001,.12); add(s,9.75+j*.25,pan=(j-3.5)/5,g=.2)
# tiles: 12 bell pops
pent=[69,72,74,76,79,81,84,86,88,91,93,96]
for j in range(12):
    n=int(.7*SR); tt=np.arange(n)/SR; f=n2f(pent[j])
    s=(np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt/.05))*env(n,.001,.25)
    add(s,12.25+j*.25,pan=((j%4)-1.5)/2,g=.17)
# create build 15.5-17.5: accelerating snare roll + riser
tt=15.5
while tt<17.45:
    p=(tt-15.5)/2; add(clap(),tt,g=.15+.35*p); tt+= .25 if p<.5 else (.125 if p<.8 else .0625)
nz=rng.standard_normal(int(2*SR)); x=nz-lp(nz,.05); ttt=np.arange(len(x))/SR; add(x*(ttt/2)**2*.25,15.5)
for i,t in enumerate([15.75,16.0,16.25]):
    add(np.sin(2*np.pi*n2f(81+[0,3,7][i])*np.arange(int(.5*SR))/SR)*env(int(.5*SR),.002,.15),t,g=.2)
# final impact 17.5: big kick, chord, sub; tail to 20
add(kick(1.3),17.5)
for n in [45,57,64,69,72,76]:
    s=saw(n2f(n),2.5,.01); s=lp(s,.12); tt=np.arange(len(s))/SR; add(s*np.exp(-tt/.9)*np.minimum(1,tt/.005)*.12,17.5,pan=rng.uniform(-.8,.8))
n=int(2.5*SR); t=np.arange(n)/SR; add(np.sin(2*np.pi*41.2*t)*np.exp(-t/.8)*.6,17.5)
# reverb (stereo comb network) on everything
def verb(x,seed):
    out=np.zeros_like(x)
    for d,fb in zip([1557,1617,1491,1422,1277,1356],[.8,.79,.81,.78,.8,.77]):
        d+=seed; y=x.copy()
        for k in range(d,len(y),d): pass
        buf=np.zeros(len(x)+d)
        for s0 in range(0,len(x),d):
            e=min(len(x),s0+d); buf[s0+d:e+d]=x[s0:e]+buf[s0:e]*fb
        out+=buf[d:d+len(x)]
    return lp(out,.35)/6
wl,wr=verb(L,0),verb(R,23)
L=L+.28*wl; R=R+.28*wr
d=int(.013*SR); wr=np.concatenate([np.zeros(d),wr[:-d]]); L=L+.1*wl; R=R+.1*wr
M,Sd=(L+R)/2,(L-R)/2*2.2; L,R=M+Sd,M-Sd
m=np.stack([L,R],1); m=np.tanh(m*1.4/np.max(np.abs(m)))  # glue + soft clip
fade=np.ones(N); fn=int(.4*SR); fade[-fn:]=np.linspace(1,0,fn); m*=fade[:,None]; m/=np.max(np.abs(m))*1.05
w=wave.open('capabilities.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m*32767).astype('<i2').tobytes()); w.close()
print('ok')
