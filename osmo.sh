# Aliases
# Establishing custom commands below -vf scale=1920:-2  -preset slower -crf 28
# for i in *.MP4; do ffmpeg -n -i "$i" -c:v libx265 -tag:v hvc1 -crf 24 "/Volumes/VIDS/OsmoPocket/${i%.*}.mp4"; done
cd /Volumes/OSMO_SD1/DCIM/100MEDIA
clear
pwd
# for i in *.MP4 *.MOV; do ffmpeg -n -i "$i" -c:v hevc_videotoolbox -quality highest -b:v 3M -bufsize 16M -maxrate 6M -tag:v hvc1 "/Volumes/VIDS/OsmoPocket/${i%.*}.mp4"; done
#for i in *.MP4 *.MOV; do ffmpeg -n -i "$i" -c:v hevc_videotoolbox -b:v 6000k -tag:v hvc1 "/Volumes/VIDS/OsmoPocket/${i%.*}.mp4"; done
for i in *.MP4 *.MOV; do ffmpeg -n -i "$i" -c:v libx265 -tag:v hvc1 -crf 24 "/Volumes/VIDS/OsmoPocket/${i%.*}.mp4"; done
#-vf "lut=val*1.04, eq=brightness=0.04, eq=gamma=0.8, unsharp=luma_msize_x=7:luma_msize_y=7:luma_amount=1.50" \


