import os
THIN="/usr/share/fonts/opentype/inter/Inter-Light.otf"
SEMI="/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SERIF="/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
GOLD="0xD9B872"
# (text, font, size, color, y-expr, start, end)
T=[
 ("B E F O R E",SEMI,30,GOLD,"h*0.08",0.4,4.4),
 ("Some days, the hair wears you.",SERIF,46,"white","h*0.80",0.8,2.9),
 ("Today, that changes.",SERIF,50,"white","h*0.80",3.05,4.45),
 ("M E A S U R E D .",THIN,46,"white","h*0.80",5.55,7.45),
 ("S H A P E D .",THIN,46,"white","h*0.80",7.55,9.45),
 ("D E T A I L E D .",THIN,46,"white","h*0.80",9.55,11.7),
 ("Every line, by hand.",SERIF,50,"white","h*0.80",12.35,14.7),
 ("A F T E R",SEMI,30,GOLD,"h*0.08",15.45,17.7),
 ("Now you wear it.",SERIF,56,"white","h*0.80",15.7,17.7),
 ("B E F O R E",SEMI,26,GOLD,"40",17.9,21.95),
 ("A F T E R",SEMI,26,GOLD,"h/2+40",17.9,21.95),
 ("Walk in. Walk out sharper.",SERIF,44,"white","h*0.88",18.6,21.95),
 ("The door is open.",SERIF,50,"white","h*0.80",22.1,25.15),
 ("H E R R K U T Z",THIN,74,"white","h*0.40",25.6,30),
 ("B A R B E R S H O P",SEMI,28,GOLD,"h*0.40+112",26.0,30),
 ("Wear it well.",SERIF,46,"white","h*0.40+190",26.7,30),
]
f=["drawbox=x=0:y=ih*0.40-60:w=iw:h=330:color=black@0.62:t=fill:enable=\'between(t,25.4,30)\'"]
for i,(s,font,sz,col,y,a,b) in enumerate(T):
    p=f"txt/t{i:02d}.txt"; open(p,"w").write(s)
    alpha=f"if(lt(t\\,{a})\\,0\\,if(lt(t\\,{a+0.35})\\,(t-{a})/0.35\\,if(lt(t\\,{b-0.3})\\,1\\,max(0\\,({b}-t)/0.3))))"
    rise=f"(1-min(1\\,max(0\\,(t-{a})/0.5)))*14"
    f.append(f"drawtext=fontfile={font}:textfile={p}:fontsize={sz}:fontcolor={col}:shadowcolor=black@0.55:shadowx=0:shadowy=3:"
             f"x=(w-tw)/2:y={y}+{rise}:alpha='{alpha}':enable='between(t,{a},{b})'")
# end-card gold rule
f.append(f"drawbox=x=(iw-160)/2:y=ih*0.40+96:w=160:h=2:color={GOLD}:t=fill:enable='between(t,25.9,30)'")
f.append("fade=t=out:st=29.4:d=0.6")
open("vf.txt","w").write("[0:v]"+",".join(f)+"[v];"
 "[0:a]volume=0.5,highpass=f=100,lowpass=f=9000[o];[1:a]volume=0.9[m];"
 "[m][o]amix=inputs=2:weights=1 0.55:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=10,afade=t=out:st=29.0:d=1.0,aresample=44100,aformat=channel_layouts=stereo[a]")
