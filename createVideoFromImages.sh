# Aliases
# Establishing custom commands below

#for i in *.mp4 *.m4v *.mov; do ffmpeg -i "$i" -vf scale=720:-1 -c:v libx264 "/Users/ricky/Movies/renders/samples/${i%.*}.mp4"; done
#echo "First: $1"; echo "Second: $2";
alias createVideoFromImages='function _func(){ ffmpeg -framerate $2 -i $1 -c:v libx264 -pix_fmt yuv420p /Users/ricky/Movies/renders/videosFromImages/$3.mp4; };_func'
