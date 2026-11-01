BLK="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
Y,P,W,K="0xFFE100","0xFF2D8C","white","black"
# (text, size, fontcolor, boxcolor, x, y, start, end)
T=[("BAD",92,K,Y,"70","h*0.56",0.03,1.0),("HAIR",92,W,P,"150","h*0.56+118",0.13,1.0),("DAY?",92,K,W,"110","h*0.56+236",0.23,1.0),
   ("HERRKUTZ",96,K,Y,"(w-tw)/2","h*0.62",1.36,2.33),("BARBERSHOP",44,W,P,"(w-tw)/2","h*0.62+128",1.46,2.33),
   ("SNIP.",110,K,Y,"(w-tw)/2","h*0.70",2.70,3.33),("SHAPE.",110,W,P,"(w-tw)/2","h*0.70",3.36,4.0),("BUZZ.",110,K,W,"(w-tw)/2","h*0.70",4.36,5.0),
   ("AFTER",60,K,Y,"(w-tw)/2","70",5.40,8.33),("FRESH.",150,W,P,"(w-tw)/2","h*0.70",5.75,8.33),
   ("BEFORE",48,K,W,"36","40",8.36,11.33),("AFTER",48,K,Y,"36","h/2+44",8.40,11.33),
   ("WALK IN.",58,K,W,"(w-tw)/2","h*0.80",8.9,11.33),("WALK OUT SHARPER.",58,W,P,"(w-tw)/2","h*0.80+82",9.2,11.33),
   ("HERRKUTZ",120,K,Y,"(w-tw)/2","250",11.70,15),("BARBERSHOP",52,Y,K,"(w-tw)/2","410",11.80,15),
   ("1170 P. JACINTO ST., BRGY. 165",38,K,W,"(w-tw)/2","560",12.10,15),("BAGBAGUIN, CALOOCAN CITY",38,K,W,"(w-tw)/2","626",12.20,15),
   ("WE’RE OPEN",70,W,P,"(w-tw)/2","760",12.60,15),("PULL UP.",64,K,Y,"(w-tw)/2","880",13.34,15)]
f=[]
for i,(s,sz,fc,bc,x,y,a,b) in enumerate(T):
    p=f"txt/t{i:02d}.txt"; open(p,"w").write(s)
    # slam-in: scales from 1.6x position offset -> stamp (jitter 2 frames)
    jit=f"if(lt(t-{a}\\,0.07)\\,9\\,0)"
    f.append(f"drawtext=fontfile={BLK}:textfile={p}:fontsize={sz}:fontcolor={fc}:box=1:boxcolor={bc}:boxborderw=14:"
             f"x={x}+{jit}:y={y}-{jit}:enable='between(t,{a},{b})'")
open("vfp.txt","w").write("[0:v]"+",".join(f)+",format=yuv420p[v];[1:a]loudnorm=I=-13:TP=-1.0:LRA=7,aresample=44100,aformat=channel_layouts=stereo[a]")
