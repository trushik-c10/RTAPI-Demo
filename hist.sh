#!/bin/bash
#echo "Script starting"
##new code
POSITIONAL=()
VERBOSE="False"
MAC="ALL"
while [[ $# -gt 0 ]]
do
key="$1"

case $key in

    -h|--help)
    HELP="TRUE"
    echo 
    echo
    echo
    echo "-v    Verbose mode (Not used at this time)"
    echo "-h    print this help file"
    echo "-s    Start time of historical data: \"MM/DD/YYYY HH:MM:SS\""
    echo "-e    End time of historical data:   \"MM/DD/YYYY HH:MM:SS\""
    echo "-m    filter final output (CSV file) on a single MAC address \"XX:XX:XX:XX:XX:XX\""
    echo "-n    Warehouse IP address of IPv6 subnet when available"
    echo "-o    Name of output files <name>.log - raw data <name>.csv- csv format (filtered by MAC if -m selected)"
    echo
    echo
    echo
    exit 1
#    shift # past argument
#    shift # past value
    ;;
 
    -v|--verbose)
    VERBOSE="TRUE"
    shift # past argument
#    shift # past value
    ;;
    -e|--endtime)
    ENDTIME="$2"
    shift # past argument
    shift # past value
    ;;
    -s|--starttime)
    STARTTIME="$2"
    shift # past argument
    shift # past value
    ;;

    -m|--mac)
    MAC="$2"
    shift # past argument
    shift # past value
    ;;


    -n|--network)
    NETWORK="$2"
    shift # past argument
    shift # past value
    ;;

    -o|--output)
    OUTPUT="$2"
    shift # past argument
    shift # past value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

echo "Verbose = ${VERBOSE}"
echo "End Time  = ${ENDTIME}"
echo "Start Time     = ${STARTTIME}"
echo "Output File    = ${OUTPUT}"
echo "MAC Filter     = ${MAC}"
echo "DEFAULT         = ${DEFAULT}"

strt=$STARTTIME
end=$ENDTIME
#read -p "Please enter Earliest date: (MM/DD/YYYY HH:MM:SS)" strt
#read -p "Please enter Latest date: (MM/DD/YYYY HH:MM:SS)"  end

#########################################
loopval=1
#strt=$1
ht=$(date -d "$strt" +"%s%N" )
ht2=$(date -d "$end" +"%s%N")
ht=$(echo $ht | cut -b1-13) 
ht2=$(echo $ht2 | cut -b1-13) 
net=\"$NETWORK\"
echo $ht
echo $ht2
echo $net	
while [ $loopval != 0 ]
do
strHist=$(curl -X POST \
  https://wxre-rest-api.xre.aws.r53.xcal.tv/v1/historical \
  -H 'Authorization: Basic eec82673100ecf6d01fd53a7565d8e9f0c6f56883974088b5c059c0e93a4be4d' \
  -H 'Content-Type: application/json'\
  -d "$(cat <<EOF
{
	"subnet": $net,
        "start": $ht,
	"end": $ht2
}
EOF
)")

	echo "DONE_____________________",$strt,"  ",$2
	echo $strHist >> "logs/"$OUTPUT.log
	#echo $strHist >> test.log
	#echo  ${strHist##*eventsCount}
	extractedNum=${strHist##*eventsCount\":}
	extractedNum2=${extractedNum%%\}}
	#echo $extractedNum2
	if [[ $extractedNum2 == *"6000"* ]]
	then
	#	echo "more data needed"
		extractedNum3=${extractedNum2##*LastStoppedEpochTime\":}
	#	echo "use "$extractedNum3" as start time"
	        ht=$extractedNum3
	else
		loopval=0 
	fi

done
#cat "logs/"$OUTPUT.log
#python3 ProcessHist.py "logs/"$OUTPUT.log $MAC 
python3 ProcessHist.py "logs/"$OUTPUT.log $MAC  >> "logs/"$OUTPUT.csv
#  -H 'Authorization: Basic 728d39959c5fab43bfee2481375b041aa4965005af92abcc4ea206f5a6abf307' \
#  -H 'Authorization: Basic 9d47627d549db5cccbb87ed4b33bdf79f5964480a001bb93f4dd3be9e0cc4d57' \
#  -H 'Authorization: Basic eec82673100ecf6d01fd53a7565d8e9f0c6f56883974088b5c059c0e93a4be4d' \

