playing with google docs \

raw data data is in browser-exports and in curl-headers-extractor.py\ 
those have my cookies. \

we have data for several commands: \
"ibi":"is" - insert \ 
"ibi":"ds" - delete \ 

There's also a multi-command thing where you can send multiple commands in one requests \ 
We use that for bad apple.

We have successfully tested:
- replaying requests in firefox - simply update the revision id
- replaying requests via curl - same thing (this means that google didn't care to fingerprint so hard that I was using a ssl cert mismatch, good news as that would have been annoying.)

What I'm doing next:
- make it work in python so I don't have to keep editing the raw curl requests.
- insert (is) at specific locations.
- bad apple

Much is to be done :)

is incomplete, \ 

Bad apple \
- frames made into braille
- frame data has note of what color is in the background - black or white
- when we play it, we set the background of the page to black or white
- then, we ad the braille text
- the we set the text's color to the inverse of the background
- then we try to do that several more times per second
- download the yt video yourself with yt-dlp - i'm not getting dmcaed for that.
