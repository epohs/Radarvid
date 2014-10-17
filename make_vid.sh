#! /bin/bash


# Get the current directory
my_dir="$(dirname "$0")"


# Load config values
source "${my_dir}/weather.config"







# Default values for command line options
NUMDAYS=1     # One day
FRAMERATE=9   # 9 frames per second

while getopts "d:f:" opts; do
   case ${opts} in
      d) NUMDAYS=${OPTARG} ;;
      f) FRAMERATE=${OPTARG} ;;
   esac
done






# Empty temporary directory
# and wait until the process is completed
# before we refill it with links to new
# batch of images.
$(rm ${TEMPDIR}/*.png) & my_pid=$!
wait $my_pid



# Grab all weather images from our image directory
# that fall within our date range.
# Sort them by date and then trim off the timestamp.
x=1
for f in `find  ${IMGDIR} -newermt "$(date --date "$NUMDAYS day ago" "+%Y-%m-%d %H:%M")" -type f -name "*.png" -printf "%T+\t%p\n" | sort -k 1nr | cut -f 2`
do
  counter=$(printf %05d $x)

  if [ "$x" -eq "1" ]; then
      oldest_img=$f
  fi

  ln -s $f ${TEMPDIR}/"${counter}".png
  ((x++))

  newest_img=$f
done



# Capture timestamps for the oldest and the newest image
oldest_img_date=$(stat -c%y $oldest_img)
newest_img_date=$(stat -c%y $newest_img)





# Build the save path

SPTH+="${VIDDIR}/"
SPTH+="$(date +%Y)/"
#SPTH+='/'
SPTH+="$(date +%m)/"
#SPTH+='/'
SPTH+=$(date +%d)

TIMESTMP=$(date +%H:%M:%S)

mkdir -p $SPTH # Create the directory if it doesn't exits

# Change ownership
# This is important when the script is run by cron
chown ${LOCALUSER}:${LOCALGROUP} $SPTH


$(/usr/local/bin/ffmpeg -f image2 -r ${FRAMERATE} -i ${TEMPDIR}/%05d.png -c:v libvpx -crf 4 -b:v 25M ${SPTH}/out-${TIMESTMP}.webm) & my_pid=$!

wait $my_pid

chown ${LOCALUSER}:${LOCALGROUP} ${SPTH}/out-${TIMESTMP}.webm

$(python ${SCRIPTDIR}/post_to_youtube.py -f ${SPTH}/out-${TIMESTMP}.webm -s "${oldest_img_date}" -e "${newest_img_date}" > ${LOGDIR}/last_youtube.log) & my_pid=$!

wait $my_pid

chown ${LOCALUSER}:${LOCALGROUP} ${LOGDIR}/last_youtube.log


ln -sf ${SPTH}/out-${TIMESTMP}.webm ${PUBDIR}/latest.webm


