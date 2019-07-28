# Aliases
# Establishing custom commands below
alias createSampleVideosWithWatermark='/Users/ricky/Library/Mobile\ Documents/com\~apple\~CloudDocs/pyscripts/createSampleVideosWithWatermark.sh'
alias createSampleVideos='/Users/ricky/Library/Mobile\ Documents/com\~apple\~CloudDocs/pyscripts/createSampleVideos.sh'

alias createVideoFromImages='function _func(){ ffmpeg -framerate $2 -i $1 -c:v libx264 -pix_fmt yuv420p /Users/ricky/Movies/renders/videosFromImages/output.mp4; };_func'
