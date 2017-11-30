python updateS3Bucket.py E:/ss_data s3://streamstats-staged-data

# ------------------------------------------------------------------------------
# Name: updateS3Bucket.py
# Description: upload files to s3 bucket
#   
# Requirements:  Amazon AWS CLI tools with a profile configured using
# access ID and secret key, in this case "WIM", see:
# https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
#
# USAGE: pass in tile cache path
# python updateS3Bucket.py D:/cache s3://nwismapper
#
# Author: Martyn Smith
# last modified: 11/17/2016
# ------------------------------------------------------------------------------

import arcpy, time, glob, os, sys, subprocess

if len(sys.argv) >= 3:
    sourcePath = sys.argv[1]
    destinationBucket = sys.argv[2]
else:
    print "Not enough arguments provided"
    sys.exit()

#excludeList = ["ak","al","ar","az","ny"]
excludeList = []
includeList = ["drb"]
folderList = ["archydro","bc_layers"]

#main
if __name__ == "__main__":
    # Start time recording
    startTime = time.time()
    startTimeStr  = time.strftime("%Y%m%d-%H%M%S")
    print "\nStarting program: ", startTimeStr, "\n"

    stateList = os.listdir(sourcePath)
    #reverse option
    stateList.sort(reverse=True)

    for state in stateList:
                if state in includeList:
                        for folder  in folderList:

                                print "Copying " + state + " " + folder + " to s3..."

                                #copy
                                #subprocess.call(["aws", "s3", "cp", sourcePath + "/" + state + "/" + folder, destinationBucket + "/" + state + "/" + folder, "--no-verify-ssl", "--recursive"])

                                #sync
                                subprocess.call(["aws", "s3", "sync", sourcePath + "/" + state + "/" + folder, destinationBucket + "/" + state + "/" + folder, "--no-verify-ssl", "--delete"])

                                #working
                                #aws s3 cp e:\ss_data\ca s3://streamstats/ca --exclude "*" --include "archydro/*" --include "bc_layers/*" --no-verify-ssl --recursive

                                print "   -- Done..."   

    #button it up
    print "Finished generating tile cache"
    endTime = time.time()
    elapsed = (endTime - startTime)/60
    endTimeStr = time.strftime("%Y%m%d-%H%M%S")
    print "ending recording time: ", endTimeStr
    print "total time elapsed(minutes): ", elapsed
