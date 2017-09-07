# ---------------------------------------------------------------------------
# Name: 1_groupLayersToMXDs.py
# Description: Parses map document, breaks out group layers to individual
#   new MXDs
#
# Author: Martyn Smith
# last modified: 8/25/2017
# ---------------------------------------------------------------------------

import arcpy

#main
if __name__ == "__main__":
	print 'hello'
	all_mxd = arcpy.mapping.MapDocument("E:/mapServices/stateServices.mxd")

	for lyr in arcpy.mapping.ListLayers(all_mxd):
		if lyr.isGroupLayer: 
			template_mxd = arcpy.mapping.MapDocument("E:/tile_scripts/template.mxd")
			df = arcpy.mapping.ListDataFrames(template_mxd, "Layers")[0]
			for subLayer in lyr:
				print "This layer is in a group layer: ",lyr ,str(subLayer.name)
				arcpy.mapping.AddLayer(df, subLayer)
			new_mxd = "E:/tile_scripts/state_mxd/" + str(lyr.name) + ".mxd"
			print 'new mxd:',new_mxd
			template_mxd.saveACopy(new_mxd)
			del template_mxd

			#paise the loop
			#raw_input("Press Enter to continue...")
	del all_mxd
