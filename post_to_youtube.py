#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import string
import time
import gdata.youtube
import gdata.youtube.service
from datetime import datetime
from dateutil.parser import parse
import sqlite3

import pprint









# Get our configuration options
# from weather.config
# and add them to a dictionary
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

f = open(os.path.join(__location__, 'weather.config'), 'r')
conf_opt = {}

for line in f:
    listedline = line.strip().split('=') # split around the = sign
    if len(listedline) > 1: # we have the = sign in there
        conf_opt[listedline[0]] = listedline[1]








print '- -- ----{ S C R I P T   B E G I N N I N G }---- -- -'


# Get command line arguments
# and place them into an array
parser = argparse.ArgumentParser(description='Upload a video file to YouTube')
parser.add_argument('-f','--file', help='Full path to the video being uploaded', required=True)
parser.add_argument('-s','--start', help='Time of the first frame of the video', required=False)
parser.add_argument('-e','--end', help='Time of the last frame of the video', required=False)
args = vars(parser.parse_args())



video_file = args['file']


start_time = parse(args['start'])
end_time = parse(args['end'])



pprint.pprint(start_time) # Only need this for debugging




# Longer human readable versions of start and end times.
# Use this in the YouTube description.
start_time_long = datetime.strftime(start_time, '%a. %b %d, %Y')
end_time_long = datetime.strftime(end_time, '%a. %b %d, %Y')

# Get timestamps to store in the database
start_timestamp = time.mktime(start_time.timetuple())
end_timestamp = time.mktime(end_time.timetuple())

# Gotta round off the hours, minutes and seconds
# because Aug. 12 3:00 thru Aug. 13 2:45 isn't quite 
# 1 full day, technically... which sucks.
end_time_rounded = end_time.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
start_time_rounded = start_time.replace(hour = 0, minute = 0, second = 0, microsecond = 0)

day_range = (end_time_rounded-start_time_rounded).days

day_range_word = 'day' if (day_range == 1) else 'days'

hour_range = (start_time-end_time).seconds

# Build the start and stop TIME portion of 
# the YouTube description for our video.
day_range_desc = 'Video starts and ends at around {0}'.format( datetime.strftime(end_time, '%I:%M%p') ) if (hour_range <= 3600) else 'Video starts at {0} and ends at {1}'.format( datetime.strftime(start_time, '%I:%M%p'), datetime.strftime(end_time, '%I:%M%p') )


# Put together YouTube Titles and Descriptions
video_title = "{0} Day Weather Radar – {1} thru {2}".format(day_range, datetime.strftime(start_time, '%b. %d'), datetime.strftime(end_time, '%b. %d'))
video_desc = "US weather radar covering {0} {1} between {2} and {3}. {4}".format(day_range, day_range_word, start_time_long, end_time_long, day_range_desc )


print 'TITLE: ', video_title
print 'DESC: ', video_desc

print 'uploading file: ', args['file'] 
print 'Start time: ', start_time
print 'End time: ', end_time

print 'Start time long: ', start_time_long
print 'End time long: ', end_time_long

print 'Start timestamp: ', start_timestamp
print 'End timestamp: ', end_timestamp

print 'covering num days: ', day_range, day_range_word
print 'hour range: ', hour_range




yt_service = gdata.youtube.service.YouTubeService()

# Turn on HTTPS/SSL access.
# Note: SSL is not available at this time for uploads.
yt_service.ssl = False





# Setting developer key and client ID
# And complete client login request
yt_service.email = conf_opt["YT_EMAIL"]
yt_service.password = conf_opt["YT_PASS"]
yt_service.source = conf_opt["YT_SOURCE"]
yt_service.developer_key = conf_opt["YT_DEV_KEY"]
yt_service.client_id = conf_opt["YT_CLIENT_ID"]
yt_service.ProgrammaticLogin()






weather_db = conf_opt["SCRIPTDIR"] + "/weather.db"





## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
##
## HERE'S THE ACTUAL UPLOAD CONFIG
##
## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def UploadVideo(video_file):
  print 'Uploading {0}...'.format(video_file)
  # prepare a media group object to hold our video's meta-data
  my_media_group = gdata.media.Group(
    title=gdata.media.Title(text=video_title),
    description=gdata.media.Description(description_type='plain',
                                        text=video_desc),
    keywords=gdata.media.Keywords(text='weather, radar'),
    category=[gdata.media.Category(
        text='Tech',
        scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
        label='Tech')],
    player=None,
    #private=gdata.media.Private()
  )

  # create the gdata.youtube.YouTubeVideoEntry to be uploaded
  video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)

  # Attach developer tags for easier filtering
  developer_tags = ['radarvid_com', 'radarvid_dev']
  video_entry.AddDeveloperTags(developer_tags)

  # assuming that video_file_location points to a valid path
  new_entry = yt_service.InsertVideoEntry(video_entry, video_file)

  return new_entry


## - - - - - - - - - -
## END UPLOAD PROCESS
## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #








# Trigger the upload process
# And get the actual video_id
# For storage in the Sqlite database
new_youtube_video = UploadVideo(video_file)

new_youtube_video_id = new_youtube_video.id.text.rsplit('/',1)[1] # Returned in some really dumb atom format







upload_status = yt_service.CheckUploadStatus(new_youtube_video)

if upload_status is not None:


  conn = sqlite3.connect(weather_db)

  c = conn.cursor()

  sql_str = "INSERT INTO uploads ('youtube_id', 'start_time', 'end_time', 'orig_file_path') VALUES ('{0}', '{1}', '{2}', '{3}');".format(new_youtube_video_id, start_timestamp, end_timestamp, args['file'])

  print 'sql_str: ', sql_str

  c.execute(sql_str)

  conn.commit()

  conn.close()




print '- -- ----{ S C R I P T   E N D I N G }---- -- -'

