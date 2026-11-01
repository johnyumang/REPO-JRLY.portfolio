BLK="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"; SEMI="/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
DJ="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
Y="0xFFD60A"
# (text,font,size,color,border(0/1),box(None|color),x,y,start,end)
T=[("₱130 FOR",BLK,96,"white",1,None,"(w-tw)/2","h*0.60",0.05,1.0),("THIS?",BLK,130,Y,1,None,"(w-tw)/2","h*0.60+108",0.30,1.0),
   ("◀◀ REWIND",DJ,46,"white",1,None,"40","70",1.0,1.5),
   ("WALKED IN",BLK,90,"white",1,None,"(w-tw)/2","h*0.64",1.55,3.0),("LIKE THIS…",BLK,90,Y,1,None,"(w-tw)/2","h*0.64+100",1.85,3.0),
   ("CUT.",BLK,130,Y,1,None,"(w-tw)/2","h*0.66",3.02,4.0),("SHAPE.",BLK,130,Y,1,None,"(w-tw)/2","h*0.66",4.02,5.0),
   ("DETAIL.",BLK,130,Y,1,None,"(w-tw)/2","h*0.66",5.02,6.0),("FINISH.",BLK,130,Y,1,None,"(w-tw)/2","h*0.66",6.02,7.0),
   ("WALKED OUT",BLK,90,"white",1,None,"(w-tw)/2","h*0.66",7.1,9.0),("LIKE THIS.",BLK,110,Y,1,None,"(w-tw)/2","h*0.66+100",7.4,9.0),
   ("BEFORE",BLK,40,"black",0,"white","36","36",9.05,11.5),("AFTER",BLK,40,"black",0,Y,"36","676",9.3,11.5),
   ("STARTS @ ₱130",BLK,76,Y,1,None,"(w-tw)/2","h*0.86",9.6,11.5),
   ("PREMIUM HAIRCUT",BLK,60,"black",0,None,"(w-tw)/2","345",11.6,15),
   ("STARTS @",SEMI,40,"0x444444",0,None,"(w-tw)/2","440",11.85,15),
   ("₱130",BLK,170,"black",0,Y,"(w-tw)/2","505",12.1,15),
   ("HERRKUTZ BARBERSHOP",BLK,44,"black",0,None,"(w-tw)/2","740",12.4,15),
   ("1170 P. Jacinto St., Brgy. 165",SEMI,30,"0x333333",0,None,"(w-tw)/2","805",12.55,15),
   ("Bagbaguin, Caloocan City",SEMI,30,"0x333333",0,None,"(w-tw)/2","848",12.6,15),
   ("WE’RE OPEN",BLK,40,"white",0,"black","(w-tw)/2","912",12.9,15)]
f=[]
for i,(s,font,sz,col,bd,box,x,y,a,b) in enumerate(T):
    p=f"txt/t{i:02d}.txt"; open(p,"w").write(s)
    al=f"min(1\\,max(0\\,(t-{a})/0.07))" if b>=15 else f"if(lt(t\\,{b}-0.06)\\,min(1\\,max(0\\,(t-{a})/0.07))\\,max(0\\,({b}-t)/0.06))"
    bounce=f"22*max(0\\,1-(t-{a})/0.14)"
    st=f":borderw=7:bordercolor=black" if bd else ""
    bx=f":box=1:boxcolor={box}:boxborderw=12" if box else ""
    f.append(f"drawtext=fontfile={font}:textfile={p}:fontsize={sz}:fontcolor={col}{st}{bx}:x={x}:y={y}+{bounce}:alpha='{al}':enable='between(t,{a},{b})'")
# modern progress bar along the bottom (retention cue)
f.append("drawbox=x=0:y=ih-8:w=iw*t/15:h=8:color=0xFFD60A:t=fill")
open("vfm.txt","w").write("[0:v]"+",".join(f)+",format=yuv420p[v];[1:a]loudnorm=I=-11.5:TP=-1.0:LRA=7,aresample=44100,aformat=channel_layouts=stereo[a]")
