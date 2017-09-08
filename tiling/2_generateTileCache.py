# ---------------------------------------------------------------------------
# Name: 2_generateTileCache.py
# Description: Generates tiles cache, then cleans up redudant files 
# and optionally converts to TMS tile cache
#    
# Requirements:  ArcGIS 10.5
#
# Notes: pass in desired output cache location as sole argument:
#
# USAGE:
# python 2_generateTileCache.py
#
# Author: Martyn Smith
# last modified: 4/20/2016
# ---------------------------------------------------------------------------

import arcpy, time, glob, os, subprocess
arcpy.env.parallelProcessingFactor = "75%"

#main
if __name__ == "__main__":

	# Start time recording
	startTime = time.time()
	startTimeStr  = time.strftime("%Y%m%d-%H%M%S")
	print "\nStarting program: ", startTimeStr, "\n"

	#paths
	scriptPath = os.path.dirname(os.path.realpath(__file__))
	dataPath = scriptPath + '/state_mxd'
	cachePath = scriptPath + '/cache'
	if not os.path.exists(cachePath):
		os.makedirs(cachePath)

	#need tiling scheme file to explicitly define 'exploded' tile format for inidividual PNGs
	tilingScheme = scriptPath + '/PredefinedTilingScheme_levels_ALL.xml'
	webMapScaleList = ["591657527.591555","295828763.795777","147914381.897889","73957190.948944","36978595.474472","18489297.737236","9244648.868618","4622324.434309","2311162.217155","1155581.108577","577790.554289","288895.277144","144447.638572","72223.819286","36111.909643","18055.954822","9027.977411","4513.988705","2256.994353","1128.497176"]

	#SET VARIABLES HERE
	scaleList = webMapScaleList [15:18]  #cache levels
	stateList = ['AK'] #states to process

	#overwrite outputs
	arcpy.env.overwriteOutput = True

	for state in stateList:
		mxd = dataPath + '/' + state + '.mxd'
		print 'Currently proccesing:',mxd

		siteCachePath = cachePath + '/' + state + "/Layers/_alllayers/"

		print(state + '\n----------------------')    

		print "Step 1 -- Creating tile cache..."
		arcpy.ManageTileCache_management(in_cache_location=cachePath, manage_mode="RECREATE_ALL_TILES", in_cache_name=state, in_datasource=mxd, tiling_scheme="IMPORT_SCHEME", import_tiling_scheme=tilingScheme, scales=scaleList, area_of_interest="", max_cell_size="", min_cached_scale=scaleList[0], max_cached_scale=scaleList[-1])        
		print "       ...Done..."

		print "Step 2 -- Removing empty PNG files from cache..."
		subprocess.call(["python",scriptPath + "/2a_removeEmptyPNG.py", siteCachePath])
		print "       ...Done..."

		print "Step 3 -- Removing empty folders from cache..."
		subprocess.call(["python",scriptPath + "/2b_removeEmptyDirs.py", siteCachePath])
		print "       ...Done..."

		print "Step 4 -- Converting to TMS cache..."
		subprocess.call(["python",scriptPath + "/2c_esri2tms.py", "--cache", siteCachePath, "--ext", "png"])
		print "       ...Done..."

		print('----------------------')   

		#pause loop for testing
		raw_input("Press Enter to continue...")

	#button it up
	print "Finished generating tile cache"
	endTime = time.time()
	elapsed = (endTime - startTime)/60
	endTimeStr = time.strftime("%Y%m%d-%H%M%S")
	print "ending recording time: ", endTimeStr
	print "total time elapsed(minutes): ", elapsed
