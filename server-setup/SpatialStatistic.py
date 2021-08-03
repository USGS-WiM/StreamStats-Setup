#------------------------------------------------------------------------------
#----- SpatialStatistics ------------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:    2014 WiM - USGS
#Disclaimer:    Not approved by USGS. (Provisional, subject to revision.)
#
#   authors:    Jeremy K. Newson USGS Wisconsin Internet Mapping           
# 
#   purpose:    Joins attributes from one feature to another based on the spatial relationship,
#               Also uses the Merge rules to calculate the value;
#          
#discussion:    spatial relationship
#               http://resources.arcgis.com/en/help/main/10.1/index.html#//00080000000q000000
#               Merge rules
#               http://resources.arcgis.com/en/help/main/10.1/index.html#//00210000000s000000
#               MakeTable
#               http://resources.arcgis.com/en/help/main/10.1/index.html#//00170000006v000000
#               
#               ? Not sure the diff between this method and summary statistics
#               http://resources.arcgis.com/en/help/main/10.1/index.html#//00080000001z000000
#


#region "Comments"
#06.03.2014 jkn - Created
#endregion

#region "Imports"
import arcpy
import os
#endregion

def sm(msg):
    mymsg=msg
    #print msg

def getFieldMap(mappedFields,FieldIndex, newName, mergeRule):
    "Maps the field"
    try:
        fieldmap = mappedFields.getFieldMap(FieldIndex)
        # Get the output field's properties as a field object
        field = fieldmap.outputField

        # Rename the field and pass the updated field object back into the field map
        field.name = newName
        field.aliasName = newName

        fieldmap.outputField = field
        fieldmap.mergeRule = mergeRule

        return fieldmap
    except:
        sm("Failed to map "+ newName)
        return None

#Main
try:
    targetFeatures = arcpy.GetParameterAsText(0)
    if targetFeatures == '#' or not targetFeatures:
        targetFeatures = r"D:\users\jknewson\Documents\ArcGIS\ND\DelineatedBasin.gdb\delineatedBasin" # provide a default value if unspecified

    joinFeatures = arcpy.GetParameterAsText(1)
    if joinFeatures == '#' or not joinFeatures:
        joinFeatures = "D:\users\jknewson\Documents\ArcGIS\ND\IsoLakes\global.gdb\isolakes" # provide a default value if unspecified

    outTable = arcpy.GetParameterAsText(2)
    if outTable == '#' or not outTable:
	outTable = "isoLakeTable"
    #end if
    
    parDir = os.path.dirname(targetFeatures)
    outTable = os.path.join(parDir,outTable)
    #check if exists
    if arcpy.Exists(outTable):
        #sm("outfc exists, deleting ...")
        arcpy.Delete_management(outTable)
    else:
        #check if gdb exists
        parDir = os.path.dirname(outTable)
        if not arcpy.Exists(parDir):  
            sm("outFc parent directory doesn't exist, creating ...")
            arcpy.CreateFileGDB_management(os.path.dirname(parDir),os.path.basename(parDir))
    #endif
    

    methodStr = arcpy.GetParameterAsText(3)
    if methodStr == '#' or not methodStr:
        methodStr = "sum; mean" # provide a default value if unspecified

    fieldStr = arcpy.GetParameterAsText(4)
    if fieldStr == '#' or not fieldStr:
        fieldStr = "lakearea; lakeda" # provide a default value if unspecified

    # Create a new fieldmappings and add the two input feature classes.
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)

    #for each field + method
    methods = [x.strip() for x in methodStr.split(';')]
    Fields = [x.strip() for x in fieldStr.split(';')]
    #sm(Fields.count + " Fields & " + methods.count + " Methods")
    for field in Fields:
        lakeAreaFieldIndex = fieldmappings.findFieldMapIndex(field)
        for method in methods:  
            map = getFieldMap(fieldmappings,lakeAreaFieldIndex,method+field,method)
            if map is not None:
                fieldmappings.addFieldMap(map)
        #next method
    #next Field

    sm("performing spatial join ...")
    spjoinfeatures = arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outTable + "tmp", "", "", fieldmappings)
    arcpy.CopyRows_management(spjoinfeatures ,outTable)
    sm("Finished")
except Exception, e:
    sm(e.message)

