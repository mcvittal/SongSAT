# SongSAT
Hackathon entry for NASA Space Apps 2018. http://songsat.ca

Converts image data to music given the theme. 

## A note to users

This project currently requires two very large TIF files for the automatic land cover detection - one of mountain ranges supplied by the UNEP, and the other of a global land use dataset created by NASA from MODIS imagery. They are too large to host on Github - a V2 of this project will involve them being hosted on a cloud provider and having a REST API returning the values currently being generated locally. 

## Using and how it works

To use this, simply invoke the `songSAT` method and provide a path to a GeoTIFF (Ideally, landsat or a clipped landsat image). It will attempt to assess the geographic contents of the image by getting the center coordinates, and finding what land cover is there using the `getclass` shell script. If a supported land type is discovered, it will then pass that information along with the data to the `generate_song` method, and produce a MIDI file (by default `/tmp/OUT.mid`). Simply open the MIDI file in your media player of choice, or in your notation software of choice to listen! 
