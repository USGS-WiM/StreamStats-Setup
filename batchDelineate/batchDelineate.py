# --------------------------------------------------------------------------------------
# batchDelineate.py
# Created on: 11-21-2016
# Updated on: 10-14-2017
# Author: Martyn Smith USGS
# Usage: batchDelineate
# Description: Download basins for snapped points using streamstats web services
# Pre-requirements: ArcGIS 10.5+
# Requirements:
#   (1)Input points feature class must contain points pre-snapped streamstats stream
#   grid cells available here:
#   http://streamstatsags.cr.usgs.gov/WebServices/StreamGrids/directoryBrowsing.asp
#   (2) Each feature must have a "siteID" and "state" field with 2 digit state abbrv
#   (3) Projection of input point shapefile should be NAD 83 (WKID 4269)
#   (4) Streamstats must be available for the attempted state
# --------------------------------------------------------------------------------------
"""Download basins for snapped points using streamstats web services"""

# Import modules
import os
import json
import urllib2
import zipfile
import time
import shutil
import arcpy
import arcpy.da
import argparse
import logging

def delineate_basin(state_code=None, x_coord=None, y_coord=None):
    """delineate_basin(state_code=None, x_coord=None, y_coord=None)
        Delineates streamstats basin based on state, x and y
    """
    url = args.server + 'watershed.json?rcode=' + state_code + '&xlocation=' + str(x_coord) + '&ylocation=' + str(y_coord) + '&crs=4326&includeparameters=' + args.parameters + '&includefeatures=false'
    log.debug('Requesting watershed for [%s, %s] in %s', x_coord, y_coord, state_code)
    log.debug('Request URL: %s', url)
    try:
        response = urllib2.urlopen(url)
        hostname = response.info().getheader('usgswim-hostname')
        data = json.load(response)
        workspace_id = data["workspaceID"]
        log.debug('Watershed delineation successful for: %s Using hostname: %s', workspace_id, hostname)
        return workspace_id,hostname
        
    except urllib2.HTTPError, err:
        log.error('HTTP Error code %s during delineation of points [%s, %s] in %s on server: %s', err.code, x_coord, y_coord, state_code, hostname)

        #recursive retry
        delineate_basin(state_code, x_coord, y_coord)
        return False

def download_basin(workspace_id=None,hostname=None):
    """download_basin(workspace_id=None,hostname=None)
        Downloads streamstats basin using workspace_id and hostname
    """
    #make sure we rewrite the hostname
    url = args.server[:8] + hostname.lower() + '.' + args.server[8:] + 'download?workspaceID=' + workspace_id + '&format=SHAPE'
    log.debug('Requesting shapefile download for workspaceID: %s on server: %s', workspace_id, hostname)
    try:
        request = urllib2.urlopen(url)
        zipfilename = os.path.join(outfolder, 'b' + siteID + '.zip')
        if os.path.exists(zipfilename):
            os.remove(zipfilename)
        with open(zipfilename, "wb") as local_file:
            local_file.write(request.read())

    except urllib2.HTTPError, err:
        log.error('HTTP Error code %s during shapefile download for workspace: %s on server %s', workspace_id, hostname)
        '  FAIL: HTTP error during download:', err.code

        #recursive retry
        download_basin(workspace_id,hostname)
        return False
    
    return zipfilename

def download_and_extract(state_code=None, x_coord=None, y_coord=None, site_id=None, basin_time=None, attempts=None):
    """download_and_extract(state_code=None, x_coord=None, y_coord=None, site_id=None, basin_time=None, attempts=None)
        Delineates, downloads and extracts the streamstats shapefile zip
    """
    attempts += 1  
    if attempts <= 4:
        log.debug('Delineation attempt #: %s', attempts)
        workspace_id,hostname = delineate_basin(state_code, x_coord, y_coord)
        input_zip = download_basin(workspace_id,hostname)
        with zipfile.ZipFile(input_zip, "r") as the_zip:
            zipfiles = the_zip.namelist()

            #make sure there are some files
            if len(zipfiles) > 1:
                the_zip.extractall(outfolder)

                #create paths
                dirpath = os.path.join(outfolder,workspace_id)
                dirpath = os.path.join(dirpath,'Layers')
                filename = 'GlobalWatershed.shp'
                shapefilename = os.path.join(dirpath, filename)

                #check to make sure we have a global watershed shapefile
                if os.path.exists(shapefilename):
                    log.debug('SUCCESS, basin delineation complete for: %s', site_id)

                    #add the unique ID field back in to shapefile, Name field should already exist
                    arcpy.CalculateField_management(shapefilename, "Name", "'" + site_id + "'", "PYTHON_9.3")

                    log.debug('Appending to basinlist: %s', shapefilename)
                    basinlist.append(shapefilename)

                    log.debug('Time elapsed: %s seconds', round((time.time()- basinTime)/60 * 100, 2))

                #otherwise something failed, add to fail list
                else:
                    log.error('FAIL: No workspace folder for: %s. Attempt #: %s', site_id, attempts)

                    #close the zip
                    the_zip.close()
                    
                    #recursively call this function again
                    download_and_extract(state_code, x_coord, y_coord, site_id, basin_time, attempts)

            else:
                log.error('FAIL: Incomplete download for: %s. Attempt #: %s', site_id, attempts)

                #close the zip
                the_zip.close()
                
                #recursively call this function again
                download_and_extract(state_code, x_coord, y_coord, site_id, basin_time, attempts)

    else:
        log.error('FAIL: SKIPPING THIS POINT: %s (TOO MANY FAILURES -- Make sure your input point is good)', site_id)
        faillist.append([state_code, x_coord, y_coord, site_id])
        return False

if __name__ == "__main__":

    #env
    arcpy.env.overwriteOutput = True

    #folders
    workfolder = os.path.dirname(os.path.abspath(__file__))
    outfolder = os.path.join(workfolder, 'output')
    projectedsnappedpointsfc = os.path.join(outfolder, 'projectedPoints.shp')
    outfc = os.path.join(outfolder, 'results.shp')

    #cleanup
    if os.path.exists(outfolder):
        shutil.rmtree(outfolder)
    os.makedirs(outfolder)

    # create logger
    log = logging.getLogger('StreamStats Batch Processor')
    log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create file handler which logs even debug messages
    fh = logging.FileHandler(time.strftime(outfolder + "/log%Y%m%d-%H%M%S.log"))
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    #SET ARGUMENTS HERE
    parser = argparse.ArgumentParser(description='Batch delineation script using StreamStats services')

    parser.add_argument('--server', type=str, default='https://streamstats.usgs.gov/streamstatsservices/', help='server for streamstats services')
    parser.add_argument('--snappedpoints', type=str, default='C:/NYBackup/GitHub/StreamStats-Setup/batchDelineate/input/sample.shp', help='input shapefile of snapped points')
    parser.add_argument('--idfield', type=str, default='siteidfina', help='unique ID field')
    parser.add_argument('--statefield', type=str, default='state', help='state field')
    parser.add_argument('--parameters', type=str, default='false', help='comma seperated parameter list to be computed, "false" if none required, "true" for all')

    args = parser.parse_args()

    # Start time recording
    starttime = time.time()
    starttimestr = time.strftime("%m-%d-%Y %H:%M:%S")

    log.info('Starting program')
    log.info('Using server: ' + args.server)

    # project input FC to geographic to get lat/longs
    outcs = arcpy.SpatialReference(4269)
    arcpy.Project_management(args.snappedpoints, projectedsnappedpointsfc, outcs)

    #initialize basinlist for merge
    basinlist = []
    faillist = []

    #get total count
    totalpoints = arcpy.GetCount_management(projectedsnappedpointsfc)

    #project input to geographic to enable getting x and y in DD
    for row in arcpy.da.SearchCursor(projectedsnappedpointsfc, ["SHAPE@X", "SHAPE@Y", args.idfield, args.statefield]):

        #make sure we have all fields
        if len(row) < 4:
            log.error('ERROR: make sure you have "SiteID" and "State" fields')
            break
        try:
            x, y, siteID, state = row
        except:
            log.error('ERROR: make sure you have "SiteID" and "State" fields')

        #skip processing if we already have a zip for this basin
        zipfilename = os.path.join(outfolder, 'b' + siteID + '.zip')
        if not os.path.exists(zipfilename):

            #reset timer
            basinTime = time.time()

            log.debug('Processing: %s siteID ( %s of %s)', siteID, len(basinlist)+1, totalpoints)

            #start work
            download_and_extract(state, x, y, siteID, basinTime, 0)

    #created merged output shapefile
    arcpy.Merge_management(basinlist, outfc)
    log.info('Processed successfully: ( %s of %s ) points', len(basinlist), totalpoints)
    log.info('Merged basin shapefile:  %s', outfc)
    if len(faillist) > 0:
        log.info('Number of failures/retries:  %s', len(faillist))
        log.info('List of failures:  %s', faillist)
    log.info('Finished.  Total time elapsed: %s minutes', round((time.time()- starttime)/60, 2))
