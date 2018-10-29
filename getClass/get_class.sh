#!/bin/bash

rdom () { local IFS=\> ; read -d \< E C ;}

V=$(gdallocationinfo -wgs84 mountain_binary.tif $1 $2 | sed -n '4p')
V=${V:11:6}
if [ "$V" = "-9999" ]; then 
    V=$(gdallocationinfo -wgs84 reclassed.tif $1 $2 | sed -n '4p')
    
else 
    V="MOUNTAIN"
fi

echo $V




