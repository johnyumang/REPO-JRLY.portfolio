import re,sys,subprocess,wave,struct,statistics as st
V,cuts=sys.argv[1],[int(x) for x in sys.argv[2].split(',')]
subprocess.run(["ffmpeg","-v","error","-i",V,"-vf","signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=_y.txt","-f","null","-"])
subprocess.run(["ffmpeg","-v","error","-i",V,"-i",V,"-filter_complex","[1:v]trim=start_frame=1,setpts=PTS-STARTPTS[b];[0:v][b]ssim=stats_file=_s.txt","-f","null","-"])
subprocess.run(["ffmpeg","-v","error","-y","-i",V,"-ac","1","-ar","44100","_a.wav"])
y=[float(l.split('=')[1]) for l in open('_y.txt') if 'YAVG' in l]
s=[float(re.search(r'All:([\d.]+)',l).group(1)) for l in open('_s.txt')]
fl=[i for i in range(1,len(y)-1) if i not in cuts and i+1 not in cuts and abs(y[i]-y[i-1])>12]
print("frames",len(y))
print("non-cut luma jumps >12 (flash frames):",[(i,round(i/30,2)) for i in fl] or "none")
print("1-3 frame flash shots:",[ (cuts[k],cuts[k+1]-cuts[k]) for k in range(len(cuts)-1) if cuts[k+1]-cuts[k]<4] or "none")
print("cut ssim:",[(round(c/30,2),round(s[c-1],3)) for c in cuts])
w=wave.open('_a.wav');n=w.getnframes();a=struct.unpack(f"<{n}h",w.readframes(n))
d=[abs(a[i]-a[i-1]) for i in range(1,n)];med=st.median(d)
clicks=[(round(c/30,2),max(d[int(c/30*44100)-40:int(c/30*44100)+40])) for c in cuts]
print("median sample delta",med,"| max delta at cuts:",clicks)
