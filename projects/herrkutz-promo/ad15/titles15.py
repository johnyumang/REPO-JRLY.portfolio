THIN="/usr/share/fonts/opentype/inter/Inter-Light.otf"; SEMI="/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SERIF="/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"; SERIFR="/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
GOLD="0xD9B872"
T=[("B E F O R E",SEMI,30,GOLD,"h*0.08",0.05,1.45,0.15),
   ("From this…",SERIF,58,"white","h*0.80",0.10,1.45,0.2),
   ("H E R R K U T Z",THIN,48,"white","h*0.80",1.62,2.45,0.25),
   ("M E A S U R E D .",THIN,46,"white","h*0.80",2.55,3.45,0.2),
   ("S H A P E D .",THIN,46,"white","h*0.80",3.55,4.45,0.2),
   ("D E T A I L E D .",THIN,46,"white","h*0.80",4.55,5.45,0.2),
   ("A F T E R",SEMI,30,GOLD,"h*0.08",6.2,8.45,0.3),
   ("…to this.",SERIF,62,"white","h*0.13",6.4,8.45,0.3),
   ("B E F O R E",SEMI,26,GOLD,"40",8.6,11.95,0.25),
   ("A F T E R",SEMI,26,GOLD,"h/2+40",8.6,11.95,0.25),
   ("Walk in. Walk out sharper.",SERIF,44,"white","h*0.88",8.9,11.95,0.3),
   ("H E R R K U T Z",THIN,74,"white","461",12.25,15,0.35),
   ("B A R B E R S H O P",SEMI,28,GOLD,"573",12.45,15,0.35),
   ("1170 P. Jacinto St., Brgy. 165",SERIFR,38,"white","640",12.75,15,0.35),
   ("Bagbaguin, Caloocan City",SERIFR,38,"white","690",12.85,15,0.35),
   ("W E ’ R E   O P E N",SEMI,24,GOLD,"758",13.1,15,0.35)]
f=["drawbox=x=0:y=401:w=iw:h=420:color=black@0.62:t=fill:enable='between(t,12.15,15)'"]
for i,(s,font,sz,col,y,a,b,fi) in enumerate(T):
    p=f"txt/t{i:02d}.txt"; open(p,"w").write(s)
    al=f"if(lt(t\\,{a})\\,0\\,if(lt(t\\,{a+fi})\\,(t-{a})/{fi}\\,if(lt(t\\,{b-0.2})\\,1\\,max(0\\,({b}-t)/0.2))))"
    if b>=15: al=f"min(1\\,max(0\\,(t-{a})/{fi}))"
    rise=f"(1-min(1\\,max(0\\,(t-{a})/0.45)))*12"
    f.append(f"drawtext=fontfile={font}:textfile={p}:fontsize={sz}:fontcolor={col}:shadowcolor=black@0.55:shadowx=0:shadowy=3:x=(w-tw)/2:y={y}+{rise}:alpha='{al}':enable='between(t,{a},{b})'")
f.append(f"drawbox=x=(iw-160)/2:y=557:w=160:h=2:color={GOLD}:t=fill:enable='gte(t,12.4)'")
f.append("fade=t=out:st=14.6:d=0.4")
open("vf15.txt","w").write(
 "[1:v]split[l1][l2];[l1]tpad=start_duration=6.0:color=black,format=gbrp[L1];[l2]tpad=start_duration=12.0:color=black,format=gbrp[L2];"
 "[2:v]tpad=start_duration=12.55:color=black,format=gbrp[SW];"
 "[0:v]format=gbrp[m];[m][L1]blend=all_mode=screen:all_opacity=0.55[m1];[m1][L2]blend=all_mode=screen:all_opacity=0.45[m2];"
 "[m2][SW]blend=all_mode=screen:all_opacity=0.35,format=yuv420p,"+",".join(f)+"[v];"
 "[3:a]loudnorm=I=-14:TP=-1.0:LRA=8,aresample=44100,aformat=channel_layouts=stereo[a]")
