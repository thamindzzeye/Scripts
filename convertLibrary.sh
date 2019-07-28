# Aliases
# Establishing custom commands below -vf scale=1920:-2  -preset slower -crf 28

for i in *.mp4 *.m4v *.mov *.MP4 *.M4V *.MOV *.mkv *.MKV *.avi *.AVI; do ffmpeg -i "$i" -c:v libx265 -tag:v hvc1 -preset slower -crf 23 "${i%_x265.*}.mp4"; done
