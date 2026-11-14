#!/bin/bash
# contact sheet of every 4th frame: sheet.sh in.mp4 out.jpg
ffmpeg -v error -y -i "$1" -vf "select='not(mod(n\,4))',scale=160:-1,drawtext=text='%{n}':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black,tile=6x3" -frames:v 1 "$2"
