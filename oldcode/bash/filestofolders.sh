#!/bin/bash

# move each noskim_x.root file into a job(x-1) folder

filenames=`ls $1/*.root`
for rootfile in $filenames
do
	TMP=$(echo $rootfile| rev | cut -d'_' -f 1 | rev)
	TMP2=$(echo $TMP| cut -d'.' -f 1)
	INDEX=$(($TMP2-1))
	NEWDIR="job$INDEX"
	mkdir "$1/$NEWDIR"
	mv $rootfile "$1/$NEWDIR/job$INDEX.root"
done
	

