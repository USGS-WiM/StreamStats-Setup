# --------------------------------------------------------------------------------------
# publishMapServices.py
# Created on: 08-22-2017
# Author: Martyn Smith USGS
# Usage: publishMapServices
# Description: Loops over set of input MXDs, checks to make sure data store is not 
#   already set, checks service definition draft for errors, and publishes to server
# --------------------------------------------------------------------------------------
"""Publish Map Services from an input python list"""

import arcpy
import os
import getpass
import glob
arcpy.env.overwriteOutput = True

try:
    import secrets
    print 'Secrets file successfully imported'
    username = secrets.USERNAME
    password = secrets.PASSWORD
except ImportError:
    print 'Secrets file not found'
    username = raw_input("Enter user name: ")
    password = getpass.getpass("Enter password: ")
    pass

SERVERNAME = 'localhost'
SERVERPORT = 6080
CONNECTIONFILE = os.path.join(os.path.dirname(sys.argv[0]), SERVERNAME + ".ags")
#SERVERURL = "http://" + SERVERNAME + ":" + str(SERVERPORT) + "/arcgis/admin"
SERVERURL = "http://" + SERVERNAME + "/arcgis/admin"

MAINDATAPATH = 'e:\\data'
SERVICELIST = [
    {'mxdPath':'e:/mapservices/nationalLayers.mxd', 'serviceName':'nationalLayers', 'folderName':'StreamStats'},
    {'mxdPath':'e:/mapservices/stateServices.mxd', 'serviceName':'stateServices', 'folderName':'StreamStats'},
    {'mxdPath':'e:/projects/data/INCoordinatedReachs/CoordinatedReaches.mxd', 'serviceName':'in', 'folderName':'coordinatedreaches'},
    {'mxdPath':'e:/projects/data/NSSRegions/nssRegions.mxd', 'serviceName':'regions', 'folderName':'nss'},  
    {'mxdPath':'e:/projects/data/Regulation/CoDam/codams.mxd', 'serviceName':'co', 'folderName':'regulations'},
    {'mxdPath':'e:/projects/data/Regulation/MTDam/mtdams.mxd', 'serviceName':'mt', 'folderName':'regulations'}
    ]

def analyze_map_service(service_draft=None):
    """analyze_map_service(service_draft=None)
        Analyzes service definition and returns messages, warnings, and errors
    """
    # Analyze the service definition draft
    analysis = arcpy.mapping.AnalyzeForSD(SDDRAFT)

    # Print errors, warnings, and messages returned from the analysis
    print "\nThe following information was returned during analysis of the MXD:"
    for key in ('messages', 'warnings', 'errors'):
        print '---- START ' + key.upper() + '---'
        vars = analysis[key]
        for ((message, code), layerlist) in vars.iteritems():
            print '    ', message, ' (CODE %i)' % code
            print '       applies to:',
            for layer in layerlist:
                print layer.name,
            print

        print '---- END ' + key.upper() + '---\n'
    if analysis['errors'] == {}:
        return True
    else:
        return False

def add_data_store_item(data_store_name=None,data_path=None):
    """add_data_store_item(data_store_name=None,data_path=None
        Checks if data store is already registered, if not registers it
    """
    if data_path not in [i[2] for i in arcpy.ListDataStoreItems(CONNECTIONFILE, 'FOLDER')]:
        print 'This path is not a registered data store:',data_path
        dsStatus = arcpy.AddDataStoreItem(CONNECTIONFILE, "FOLDER", data_store_name, data_path, data_path)
        print "Data store addition status : " + str(dsStatus)
        validity = arcpy.ValidateDataStoreItem(CONNECTIONFILE, "FOLDER", data_store_name)
        print("The data store item '{}' is {}".format(data_store_name, validity))
        return True
    else:
        print 'This path is already a registered data store:', data_path
        return False

if __name__ == "__main__":

    # Create a connection file to the server            
    try:
        arcpy.mapping.CreateGISServerConnectionFile("PUBLISH_GIS_SERVICES",os.curdir,SERVERNAME+".ags",SERVERURL,"ARCGIS_SERVER",username=username,password=password)
    except Exception, e:
            print e.message   
    if not os.path.isfile(CONNECTIONFILE):
        print("Unable to connect to ArcGIS Server -- exiting")
        sys.exit(1)

    #first register main data path
    print "\nProcessing:",MAINDATAPATH
    DATASTORENAME = os.path.normpath(MAINDATAPATH).split(os.sep)[1]
    add_data_store_item(DATASTORENAME,MAINDATAPATH)

    #main loop over service items and do the work
    for serviceItem in SERVICELIST:

        #variables
        SCRIPTPATH = os.path.dirname(sys.argv[0])
        MXDPATH = serviceItem['mxdPath']
        PATH = os.path.normpath(MXDPATH)
        PATHLIST = PATH.split(os.sep)
        WORKSPACE = "\\".join(PATHLIST[:2])
        DATASTORENAME = os.path.normpath(WORKSPACE).split(os.sep)[1]
        SERVICENAME = serviceItem['serviceName']
        FOLDERNAME = serviceItem['folderName']

        print "\nProcessing:",MXDPATH

        # make sure the folder is registered with the server, if not, add it to the datastore
        add_data_store_item(DATASTORENAME,WORKSPACE)
        
        # Provide other service details
        MAPDOCUMENT = arcpy.mapping.MapDocument(MXDPATH)
        SDDRAFT = os.path.join(SCRIPTPATH, SERVICENAME + '.sddraft')
        SD = os.path.join(SCRIPTPATH, SERVICENAME + '.sd')

        # Create service definition draft
        arcpy.mapping.CreateMapSDDraft(MAPDOCUMENT, SDDRAFT, SERVICENAME, 'ARCGIS_SERVER', CONNECTIONFILE, False, FOLDERNAME, SERVICENAME, SERVICENAME)

        # Analyze the service definition draft
        map_service_status = analyze_map_service(SDDRAFT)

        # Stage and upload the service if the analysis did not contain errors
        if map_service_status:
            # Execute StageService. This creates the service definition.
            arcpy.StageService_server(SDDRAFT, SD)

            # Execute UploadServiceDefinition. This uploads the service definition and publishes the service.
            arcpy.UploadServiceDefinition_server(SD, CONNECTIONFILE)
            print "Service successfully published:",MXDPATH
        else: 
            print "Service could not be published because errors were found during analysis:",MXDPATH

print arcpy.GetMessages()

#cleanup
print '\nCleaning up...'
types = ('*.sddraft', '*.sd', '*.ags') # the tuple of file types
for files in types:
    filelist = glob.glob(files)
    for f in filelist:
        print filelist
        os.remove(f)