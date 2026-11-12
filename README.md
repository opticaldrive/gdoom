Reverse engineering google docs 

as of current state, most of the data is in browser-exports

we have data for several commands:
"ibi":"is" - insert
"ibi":"ds" - delete

We have successfully tested:
- replaying requests in firefox - simply update the revision id
- replaying requests via curl - same thing (this means that google didn't care to fingerprint so hard that I was using a ssl cert mismatch, good news as that would have been annoying.)

What I'm doing next:
- make it work in python so I don't have to keep editing the raw curl requests.
- insert (is) at specific locations.
- bad apple

Much is to be done :)