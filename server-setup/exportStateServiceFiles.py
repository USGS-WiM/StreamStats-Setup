# ---------------------------------------------------------------------------
# Name: exportStateServiceFiles.py
# Description: Parses map document, exports stream grid,exclude polys, and
#              other feature classes from state group layers
#
# Author: Martyn Smith
# last modified: 11/28/2017
#
# c:\Python27\ArcGISx6410.5\python.exe exportStateServiceFiles.py
#
# ---------------------------------------------------------------------------

import arcpy, os, shutil
from arcpy.sa import *

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

#main
if __name__ == "__main__":
    print 'Starting script'

    arcpy.env.overwriteOutput = True

    #paths
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    stateServicesMXD = scriptPath + '/stateServices.mxd'

    #main state mxd
    all_mxd = arcpy.mapping.MapDocument(stateServicesMXD)
    
    for lyr in arcpy.mapping.ListLayers(all_mxd):
    
        #find state based group layers
        if lyr.isGroupLayer: 
        
            stateAbv = str(lyr).lower()
        
            #set state path
            statePath = scriptPath + '/State/' + stateAbv + '/'
            
            #remove state folder if it exists
            if os.path.exists(statePath):
                shutil.rmtree(statePath)
            os.makedirs(statePath)
            
            #loop over single state layers inside of group
            for subLayer in lyr:
            
                layerName = str(subLayer.name)
                print 'This layer is in a group layer: ',stateAbv ,layerName

                if layerName == 'StreamGrid':
                
                    #turn off pyramids
                    arcpy.env.pyramid = "PYRAMIDS 0"
                    
                    #set raster compression
                    #arcpy.env.compression = "CCITT_1D"
                    
                    raster = os.path.join(statePath, 'streamgrid.tif')
                    
                    print '   Reclassifying stream grid raster...', raster
                    
                    # Reclassiffy
                    #using a tiff allows for 1 bit unsigned pixel depth, reducing file size
                    arcpy.gp.Reclassify_sa(subLayer, "VALUE", "1 1", raster, "DATA")
                                    
                    #print '   Exporting stream grid raster...',raster
                    #arcpy.CopyRaster_management(in_raster=tempRaster, out_rasterdataset=raster, config_keyword="", background_value="", nodata_value="-128", onebit_to_eightbit="NONE", colormap_to_RGB="NONE", pixel_type="1_BIT", scale_pixel_value="NONE", RGB_to_Colormap="NONE", format="TIFF", transform="NONE")

                    #delete tempRaster
                    #arcpy.Delete_management(tempRaster)
                    
                    #delete pyramids
                    #if os.path.exists(statePath + 'StreamGrid.rrd'):
                    #    print '      DELETING raster pyramids....'
                    #    os.remove(statePath + 'StreamGrid.rrd')
                    
                #check for other state layers
                else:
                    shape = os.path.join(statePath, layerName.lower() + '.shp')
                    print '   Exporting other state layer:', shape
                    arcpy.management.CopyFeatures(subLayer, shape)

            #paise the loop
            #raw_input("Press Enter to continue...")
    del all_mxd
