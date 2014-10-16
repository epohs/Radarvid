Radarvid
========

Download and archive images from a remote server, then compile them into a video and upload to YouTube.


## File summary

* **weather.config** – Contains all login credentials and paths... sensitive info.
* **weather.py** – This file downloads the image, converts it to a PNG (ffmpeg doesn't like GIF) and saves it.
* **make_vid.sh** – Grabs downloaded images by date range, converts them into a webm video, and calls the YouTube upload python script.
* **post_to_youtube.py** – Creates title & description for a video and uploads it to YouTube.
* **weather.db** – Sqlite3 database. Stores information about every video uploaded to YouTube.




## System Requirements

*I'm not too sure, to be honest. This has been tested on Debian Linux 7 (wheezy). But, I haven't taken time to test on various versions of software. If you do test for yourself, and have feedback for me, please by all means let me know.*

* Bash
* Python
* ImageMagick
* ffmpeg





### To-do

**make_vid.sh**
[ ] Allow for true custom date ranges, instead of the *last-x-days* style that is currently used.

**post_to_youtube.py**
[ ] Support for a custom title.