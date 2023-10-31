#!/bin/bash

# add histograms per era to histograms per year.
# all histograms in one-level subfolders of input folder are added.
# a python script for plotting is invoked on the result.
# command-line arguments:
# - target folder
# - which plotter (assumed to be in ~/Kshort/python)
# - input folders (note that the histograms are one level more down e.g. inputfolder/histn?/hist.root)

targetfolder=$1
plotter=$2
inputfolders=${@:3}

if [[ -d "$targetfolder" ]]
then
	echo "target folder already exists"
	echo "overwrite? (y/n)"
	read go
	if [[ $go != "y" ]]
	then
		exit
	else
		echo "overwriting"
        rm -r $targetfolder
	fi
fi

# find number of histograms per input folder
arr=($inputfolders)
firstinputfolder=${arr[0]}
i=0
subdirectory="histn$i"
while [[ -d "$firstinputfolder/$subdirectory" ]]
do
	i=$(($i+1))
	subdirectory="histn$i"
done
echo "found $i subdirectories"
i=$((i-1))

# make plot command as it is common to all instances
if [[ $plotter == "mcvsdata_plot.py" ]]
then
	cmd2='python ~/Kshort/python/mcvsdata_plot.py'
elif [[ $plotter == "mcvsdata_plot2d.py" ]]
then 
	cmd2='python ~/Kshort/python/mcvsdata_plot2d.py'
else
	echo "plot command not found"
	exit
fi
cmd2=$cmd2' histfile=test.root histtitle="K^{0}_{S} data to simulation ratio" xaxistitle="radial distance (cm)" yaxistitle="transverse momentum (GeV)" outfile="figure.png"'

# make hadd commands and run them
echo "making subdirectories and hadd commands"
mkdir "$targetfolder"
cd "$targetfolder"
# (manually set range of histograms here)
j=0
#i=9
while [ $j -le $i ]; do
	mkdir "histn$j"
	cd "histn$j"
	cmd="hadd test.root"
	for inputfolder in $inputfolders
	do
		cmd="$cmd $inputfolder/histn$j/test.root"
	done
	eval $cmd
	eval $cmd2
	cd ".."
    j=$(($j+1))
done
