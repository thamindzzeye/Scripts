# Aliases
# Establishing custom commands below

for i in *.mp4 *.m4v *.mov *.MP4 *.M4V *.MOV; do ffmpeg -i "$i" -vf scale=720:-2 -c:v libx264 "/Users/ricky/Movies/renders/samples/${i%.*}.mp4"; done
