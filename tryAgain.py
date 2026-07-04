import pygpod
import os
database = os.listdir("/Volumes/EYEPOD NANO/db/")
iPod = pygpod.Database("/Volumes/EYEPOD NANO/")
myTracks = iPod.tracks
tracksThere = []

for i in database:
    for j in myTracks:
        if i in j.composer:
            tracksThere.append(j.composer)
for i in tracksThere:
    database.remove(i)
for i in database:
    print(i)
    os.rmdir("/Volumes/EYEPOD NANO/db/"+i)