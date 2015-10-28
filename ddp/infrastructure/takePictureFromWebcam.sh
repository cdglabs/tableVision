# ffmpeg -f v4l2 -list_formats all -i /dev/video1

devNo=0
shotsNo=9 # up to 9
[[ "$1" =~ ^[0-9]$ ]] && devNo=$1
dev=/dev/video$devNo
[[ ! -c "$dev" ]] && echo "$dev is not a character device" && exit;

#,white_balance_temperature_auto=1
v4l2-ctl --device=$devNo --set-fmt-video=width=1920,height=1080,pixelformat=1
# you want to take multiple pictures because the first may turn out to be crappy/black/not brightness-adjusted
ffmpeg -f v4l2 -i $dev -framerate 3 -vframes $shotsNo out%3d.png
for (( i=1; i<$shotsNo; i++ ))
do
	rm out00$i.png
done
