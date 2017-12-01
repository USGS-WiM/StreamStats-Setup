# ---------------------------------------------------------------------------
# Name: groupLayersToMXDs.py
# Description: Parses map document, breaks out group layers to individual
#   new MXDs
#
# Author: Martyn Smith
# last modified: 8/25/2017
# ---------------------------------------------------------------------------

import arcpy, os

#main
if __name__ == "__main__":
	print 'Starting script'

	#paths
	scriptPath = os.path.dirname(os.path.realpath(__file__))
	stateServicesMXD = 'E:/mapServices/stateServices.mxd'
        templateMXD = scriptPath + '/template.mxd'
        stateMXDpath = scriptPath + '/state_mxd/'
	if not os.path.exists(stateMXDpath):
		os.makedirs(stateMXDpath)
	
	all_mxd = arcpy.mapping.MapDocument(stateServicesMXD)
	for lyr in arcpy.mapping.ListLayers(all_mxd):
		if lyr.isGroupLayer: 
			template_mxd = arcpy.mapping.MapDocument(templateMXD)
			df = arcpy.mapping.ListDataFrames(template_mxd, 'Layers')[0]
			for subLayer in lyr:
				print 'This layer is in a group layer: ',lyr ,str(subLayer.name)
				arcpy.mapping.AddLayer(df, subLayer)
			new_mxd = stateMXDpath + str(lyr.name) + '.mxd'
			print 'new mxd:',new_mxd
			template_mxd.saveACopy(new_mxd)
			del template_mxd

			#paise the loop
			#raw_input("Press Enter to continue...")
	del all_mxd
