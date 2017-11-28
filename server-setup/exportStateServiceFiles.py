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
        
            stateAbv = str(lyr)
        
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
                    print '   Exporting stream grid raster...'
                    rasterName = 'StreamGrid'
                    raster = os.path.join(statePath, rasterName)
                    print '      ',raster
                    arcpy.CopyRaster_management(in_raster=subLayer, out_rasterdataset=raster, config_keyword="", background_value="", nodata_value="-128", onebit_to_eightbit="NONE", colormap_to_RGB="NONE", pixel_type="1_BIT", scale_pixel_value="NONE", RGB_to_Colormap="NONE", format="Esri Grid", transform="NONE")

                    #delete pyramids
                    if os.path.exists(statePath + 'StreamGrid.rrd'):
                        print '      DELETING raster pyramids....'
                        os.remove(statePath + 'StreamGrid.rrd')
                    
                #check for other state layers
                else:
                    print '   Exporting other state layer...'
                    shapeName = layerName + '.shp'
                    shape = os.path.join(statePath, shapeName)
                    print '      ', shape
                    arcpy.management.CopyFeatures(subLayer, shape)

            #paise the loop
            #raw_input("Press Enter to continue...")
    del all_mxd
