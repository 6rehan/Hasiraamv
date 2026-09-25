# Full arrangement as MIDI, rendered with FluidSynth + FluidR3 GM soundfont
import mido
BPM=92; T=480; mid=mido.MidiFile(ticks_per_beat=T)
def track(ch,prog,name):
    tr=mido.MidiTrack(); mid.tracks.append(tr); tr.name=name
    if ch!=9: tr.append(mido.Message('program_change',channel=ch,program=prog))
    return tr
ev={}
def note(tr,ch,n,start,dur,v=90): ev.setdefault(id(tr),(tr,[]))[1].extend([(start,'on',ch,n,v),(start+dur,'off',ch,n,0)])
meta=mido.MidiTrack(); mid.tracks.append(meta); meta.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM)))
pno=track(0,0,'Piano'); pad=track(1,89,'Pad'); bass=track(2,38,'Bass'); vox=track(3,52,'Vocal guide'); drm=track(9,0,'Drums')
chords=[[53,56,60,63],[49,53,56,60],[56,60,63,67],[51,55,58,62]]; roots=[29,25,32,27]
hook=[(0,72,1),(1.5,75,.5),(2,77,1),(3,75,1),(4,72,1.5),(5.5,70,.5),(6,68,1),(7,70,1)]
verse=[(0,65,.5),(.5,65,.5),(1,68,.5),(1.5,65,1),(3,63,.5),(3.5,65,.5),(4,68,1),(5,70,.5),(5.5,68,1.5)]
B=4*T; BARS=40
for b in range(BARS):
    s=b*B; c=chords[b%4]; sec=['intro','verse','hook','verse','hook'][b//8]
    for n in c: note(pad,1,n,s,B,55)
    for i,n in enumerate(c+[c[2]+12,c[1]+12]): note(pno,0,n+12,s+i*T//2,T,62 if sec=='intro' else 52)
    if sec!='intro':
        note(bass,2,roots[b%4],s,int(2.4*T),110); note(bass,2,roots[b%4],s+int(2.5*T),T,100)
        for k in(0,1.75,2.5): note(drm,9,36,s+int(k*T),T//4,115)
        for k in(1,3): note(drm,9,38,s+k*T,T//4,100); note(drm,9,39,s+k*T,T//4,70)
        div=4 if sec=='hook' else 2
        for h in range(4*div): note(drm,9,42,s+h*T//div,T//8,70 if h%2 else 90)
        if sec=='hook' and b%2: [note(drm,9,42,s+3*T+j*T//6,T//12,60) for j in range(6)]
    if b%2==0 and sec!='intro':
        for st,n,d in (hook if sec=='hook' else verse): note(vox,3,n,s+int(st*T),int(d*T),100)
for tr,evs in ev.values():
    evs.sort(key=lambda e:(e[0],e[1]=='on')); last=0
    for t,k,ch,n,v in evs:
        tr.append(mido.Message('note_on' if k=='on' else 'note_off',channel=ch,note=n,velocity=v,time=t-last)); last=t
mid.save('late_night_scroll.mid'); print('midi ok')
