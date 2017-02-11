#!/bin/bash
BitBarDarkMode=${BitBarDarkMode}
export BitBarDarkMode
if [ $# -gt 0 ]
  then
  	if [ $1 = "request" ]
  	then
  		curl -s $2 -H "Authorization: Bearer "$3
  		exit
    elif [ $1 = "open" ]
    then
        open $2 $3 $4 $5
        exit
	fi
fi
python `dirname $0`/ST/ST_Python_Logic.py $0
