"""Synthesize royalty-free dark ambient beds (own work, no copyright issues).
Usage: python3 make_music.py <out_dir>  -> writes dark_1.m4a ... dark_4.m4a (~32 s each)"""
import sys, os, subprocess, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
SR=44100; DUR=32
def env_adsr(n,a,r):
    e=np.ones(n); a=int(a*SR); r=int(r*SR)
    e[:a]=np.linspace(0,1,a); e[-r:]=np.linspace(1,0,r); return e
def reverb(x,t=3.5,mix=.35,seed=0):
    rng=np.random.default_rng(seed); n=int(t*SR)
    ir=rng.standard_normal(n)*np.exp(-np.linspace(0,7,n)); ir/=np.abs(ir).sum()**.5*8
    return (1-mix)*x+mix*fftconvolve(x,ir)[:len(x)]
def lp(x,f): return sosfilt(butter(4,f,fs=SR,output="sos"),x)
def track(root,bpm,chord,seed):
    rng=np.random.default_rng(seed); n=SR*DUR; t=np.arange(n)/SR; out=np.zeros(n)
    # drone: detuned root + fifth, slow swell
    lfo=.6+.4*np.sin(2*np.pi*t/9)
    for f,d in [(root,0),(root*1.003,0),(root*1.5,0.002)]:
        out+=.22*np.sin(2*np.pi*f*t+d)*lfo
    out+=.05*np.sign(np.sin(2*np.pi*root*t))*lfo   # grit
    out=lp(out,600)
    # noise wash
    out+=lp(rng.standard_normal(n),900)*.04*(.5+.5*np.sin(2*np.pi*t/13))
    # eerie pad (minor chord, tremolo), enters after 4 s
    pad=sum(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t) for f in chord)
    pad*=.05*(.7+.3*np.sin(2*np.pi*.25*t))*np.clip((t-4)/4,0,1)
    out+=lp(pad,2500)
    # heartbeat kicks
    beat=60/bpm; k=np.zeros(n); kl=int(.35*SR); kt=np.arange(kl)/SR
    kick=np.sin(2*np.pi*(55*kt-25*kt**2/.35))*np.exp(-kt*9)
    tt=2.0
    while tt<DUR-1:
        for off,g in [(0,1),(.22,.6)]:
            i=int((tt+off)*SR)
            if i+kl<n: k[i:i+kl]+=kick*g
        tt+=beat*2
    out+=.55*k*np.clip((t-2)/6,0,1)
    out=reverb(out,seed=seed)*env_adsr(n,2.5,3)
    st=np.stack([out,np.roll(out,int(.012*SR))],1)
    return st/np.abs(st).max()*.85
def main(od):
    os.makedirs(od,exist_ok=True)
    specs=[(55,62,[220,261.63,329.63]),(49,58,[196,233.08,293.66]),(61.7,68,[246.94,293.66,369.99]),(43.65,54,[174.61,207.65,261.63])]
    for i,(r,b,c) in enumerate(specs,1):
        x=(track(r,b,c,i)*32767).astype(np.int16); wav=os.path.join(od,f"dark_{i}.wav")
        import wave
        with wave.open(wav,"wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",wav,"-c:a","aac","-b:a","160k",wav[:-4]+".m4a"],check=True); os.remove(wav)
if __name__=="__main__": main(sys.argv[1])
