import datetime
import urllib
import os

from datetime import datetime



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





now = datetime.now()


this_year = now.year
this_month = datetime.strftime(now, '%m')
this_week = now.isocalendar()[1]
this_day = datetime.strftime(now, '%d')
this_hour = datetime.strftime(now, '%H')
this_min = datetime.strftime(now, '%M')

remote_img = conf_opt["REMOTEIMG"]




local_img_path = conf_opt["IMGDIR"]

local_dir_img_home = "{0}/{1}/{2}".format(local_img_path, str(this_year), str(this_week))




if not os.path.isdir(local_dir_img_home):
  os.makedirs(local_dir_img_home)


this_file_gif = "{0}{1}-{2}{3}.gif".format(this_month, this_day, this_hour, this_min)
this_file_png = "{0}{1}-{2}{3}.png".format(this_month, this_day, this_hour, this_min)



f = urllib.urlopen(remote_img)
with open(local_dir_img_home + '/' + this_file_gif, "wb") as imgFile:
    imgFile.write(f.read())


imagemagick_cmd = "convert ephemeral:" + local_dir_img_home + '/' + this_file_gif + " " + local_dir_img_home + '/' + this_file_png

p = os.popen(imagemagick_cmd,"r")
while 1:
    line = p.readline()
    if not line: break
    print line