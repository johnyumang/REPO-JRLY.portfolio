BI="/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"; BLK="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
SEMI="/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"; DJ="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PINK="0xFF2D8C"; PURP="0x4A145E"; YEL="0xFFE45C"
# (text,font,size,color,x-mode,y,start,end,shadow,border)
T=[("BAGBAGUIN",BI,104,"white","slide","h*0.70",0.15,1.5,PINK,0),("C A L O O C A N   C I T Y",SEMI,30,YEL,"slide","h*0.70+118",0.30,1.5,PURP,0),
   ("THE CLIENT",BI,92,"white","slide","h*0.72",2.25,3.5,PINK,4),("Status: overdue for a cut",SEMI,34,YEL,"slide","h*0.72+108",2.40,3.5,PURP,3),
   ("OBJECTIVE:  GET FRESH",SEMI,30,"white","fixed:40","60",3.5,10.5,PURP,3),
   ("FRESHNESS",SEMI,26,"white","fixed:40","h-150",3.5,10.5,PURP,3),
   ("THE BARBER",BI,92,"white","slide","h*0.72",6.55,8.0,PINK,4),("Herrkutz Barbershop",SEMI,34,YEL,"slide","h*0.72+108",6.70,8.0,PURP,3),
   ("★★★★★",DJ,64,YEL,"center","130",8.3,10.5,PURP,3),("+ FRESH",BI,84,"white","center","h*0.66",8.6,10.5,PINK,4),
   ("BEFORE",BI,48,"white","fixed:56","70",10.5,12.0,PINK,3),("AFTER",BI,48,"white","fixed:56","670",10.6,12.0,PINK,3),
   ("HERRKUTZ",BI,110,"white","center","560",12.15,15,PINK,5),("B A R B E R S H O P",SEMI,34,"white","center","700",12.3,15,PURP,3),
   ("PREMIUM HAIRCUT  ·  STARTS @ ₱130",BLK,38,"white","center","790",12.6,15,PURP,4),
   ("1170 P. Jacinto St., Brgy. 165",SEMI,32,"white","center","870",12.85,15,PURP,3),("Bagbaguin, Caloocan City",SEMI,32,"white","center","915",12.9,15,PURP,3),
   ("NOW OPEN",BI,80,YEL,"center","1010",13.2,15,PINK,5)]
f=[]
for i,(s,font,sz,col,xm,y,a,b,sh,bd) in enumerate(T):
    p=f"txt/t{i:02d}.txt"; open(p,"w").write(s)
    if xm=="slide": x=f"-tw+(tw+48)*min(1\\,(t-{a})/0.28)*(2-min(1\\,(t-{a})/0.28))"
    elif xm=="center": x="(w-tw)/2"
    else: x=xm.split(":")[1]
    al=f"min(1\\,max(0\\,(t-{a})/0.12))" if b>=15 else f"if(lt(t\\,{b}-0.1)\\,min(1\\,max(0\\,(t-{a})/0.12))\\,max(0\\,({b}-t)/0.1))"
    brd=f":borderw={bd}:bordercolor={PURP}" if bd else ""
    f.append(f"drawtext=fontfile={font}:textfile={p}:fontsize={sz}:fontcolor={col}:shadowcolor={sh}:shadowx=6:shadowy=6{brd}:x={x}:y={y}:alpha='{al}':enable='between(t,{a},{b})'")
# FRESHNESS meter: track + pink fill growing 3.5s -> 10.0s
f.insert(0,"drawbox=x=40:y=ih-110:w=400:h=26:color=white@0.55:t=fill:enable='between(t,3.5,10.5)'")
f.insert(1,"drawbox=x=40:y=ih-110:w='400*min(1,max(0,(t-3.5)/6.5))':h=26:color=0xFF2D8C:t=fill:enable='between(t,3.5,10.5)'")
open("vfg.txt","w").write("[0:v]"+",".join(f)+",format=yuv420p[v];[1:a]volume=9dB,alimiter=limit=0.7:attack=1:release=40:level=0,aresample=44100,aformat=channel_layouts=stereo[a]")
