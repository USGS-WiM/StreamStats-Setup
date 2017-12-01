# ------------------------------------------------------------------------------
# Name: updateS3Bucket.py
# Description: upload files to s3 bucket
#   
# Requirements:  (1) Amazon AWS CLI tools https://aws.amazon.com/cli/
# (2) AWS CLI profile configured using
# access ID and secret key, see:
# https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
#
#
# Author: Martyn Smith
# last modified: 11/30/2017
# ------------------------------------------------------------------------------

import time, glob, os, sys, subprocess

states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

#excludeList = ["ak","al","ar","az","ny"]
excludeList = []
includeList = ["drb"]
folderList = ["archydro","bc_layers"]

sourcePath = 'c:/temp/ss-data'
destinationBucket = 's3://streamstats-staged-data'
dataType = 'data'

print os.path.abspath(__file__)
scriptPath = os.path.dirname(os.path.abspath(__file__))

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

                #create AWS CLI command
                cmd="aws s3 cp " + sourcePath + "/" + state + "/" + folder + " " + destinationBucket + "/" + dataType + "/" + state + "/" + folder +  " --recursive --dryrun"

                print cmd
                print "   Started copying:", state + "/" + folder

                try:
                    output = subprocess.check_output(cmd, shell=True)
                except subprocess.CalledProcessError as e:
                    print 'ERROR: Make sure AWS CLI has been installed, and you have run "aws configure" to store credentials'
                    #print "Oops... returncode: ", e.returncode,", output:\n", e
                    sys.exit()
                else:
                    print "   Finished copying:", state + "/" + folder

                

    #button it up
    print "Finished"
    endTime = time.time()
    elapsed = (endTime - startTime)/60
    endTimeStr = time.strftime("%Y%m%d-%H%M%S")
    print "ending recording time: ", endTimeStr
    print "total time elapsed(minutes): ", elapsed
