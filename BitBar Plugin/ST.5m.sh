#!/bin/bash
BitBarDarkMode=${BitBarDarkMode}
export BitBarDarkMode
if [ $# -gt 0 ]
  then
  	if [ $1 = "request" ]
  	then
  		curl -s $2 -H "Authorization: Bearer "$3
  		exit
	fi
fi
python `dirname $0`/ST/ST_Python_Logic.py $0