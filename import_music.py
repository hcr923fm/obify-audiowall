import os, os.path
import pprint
import ConfigParser
import subprocess
import re

IGNORE_CHRISTMAS = True
IGNORE_TEMPS = True
IGNORE_ADS = True

root_path = os.path.join("C:\\", "Users", "hcrob", "AudioWall")
song_destination_path = os.path.join("C:\\", "Users", "hcrob", "Desktop", "OB Music")
jingle_destination_path = os.path.join("C:\\", "Users", "hcrob", "Desktop", "OB Music", "Jingles")
song_entries = []
dirs_to_check = [root_path]

while dirs_to_check:
    current_dir = dirs_to_check.pop()
    for f in os.listdir(current_dir):
        fullpath = os.path.join(current_dir, f)

        # If the folder contains directories, add them to the list of
        # dirs to iterate over
        if os.path.isdir(fullpath): dirs_to_check.append(fullpath)
        else:
            if "~syncthing~" in fullpath: continue
            inf_path = fullpath.replace(".wav", ".inf")

            if re.match(".*MYR4[5-9]", fullpath) and IGNORE_CHRISTMAS: continue
            if re.match(".*MYR01[5-9]", fullpath) and IGNORE_TEMPS: continue
            if re.match(".*MYR001[0-9]", fullpath) and IGNORE_TEMPS: continue
            if re.match(".*MYR01[0-4]", fullpath) and IGNORE_ADS: continue
            
            
            if fullpath.endswith(".wav") and os.path.isfile(inf_path):
                song_entries.append((fullpath, inf_path))

cp = ConfigParser.SafeConfigParser()
if not os.path.exists(song_destination_path): os.mkdir(song_destination_path)
if not os.path.exists(jingle_destination_path): os.mkdir(jingle_destination_path)
devnull = open(os.devnull, "w")

for song in song_entries:
    try:
        cp.read(song[1])
        song_title = cp.get("Copyright", "MusicTitle")
        song_artist = cp.get("Copyright", "Performer")
        if not song_artist:
            copyright_type = cp.get("Copyright", "CopyrightCode")
            if copyright_type == "S":
                song_artist = "!JINGLE"
    except ConfigParser.NoOptionError:
        print "No title available for", song[1]
        continue
    except:
        print "Failed to parse INF for", song[1]
        continue


    if (not song_artist) or (not song_title):
        print "Data missing for", song[1]
        print "Title:", song_title, "Artist:", song_artist
        continue

    mp3_name = "{0} - {1}.mp3".format(song_artist, song_title)
    mp3_name=re.sub('[^\w\-_\. ]', '_', mp3_name)
    if song_artist == "!JINGLE":
        mp3_path = os.path.join(jingle_destination_path, mp3_name)
    else:
        mp3_path = os.path.join(song_destination_path, mp3_name)

    if os.path.exists(mp3_path):
        print "File exists:", mp3_path
        continue

    print "Converting", song[0]
    subprocess.check_call(["ffmpeg.exe", "-i", song[0], "-c:a", "libmp3lame", "-q:a", "2", mp3_path], stdout=devnull, stderr=devnull)
