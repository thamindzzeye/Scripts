# Aliases
# Establishing custom commands below

for i in *.mp4 *.m4v *.mov; do ffmpeg -i "$i" -i /Users/ricky/Movies/renders/watermark/watermark.png \
-filter_complex "[0:v]scale=1280:-2[bg];[bg][1:v]overlay=0:0" -c:v libx264 "/Users/ricky/Movies/renders/samples/${i%.*}_sample.mp4"; done
