
#------------------------------------------------------------------------------
#----- DelineateWrapper.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  Wrapper to delineate watershed using split catchement methods
#          
#discussion:  https://github.com/GeoJSON-Net/GeoJSON.Net/blob/master/src/GeoJSON.Net/Feature/Feature.cs
#             http://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/watershed.htm
#             geojsonToShape: http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/asshape.htm
#       

#region "Comments"
#08.19.2015 jkn - Created
#endregion

#region "Imports"
import traceback
import datetime
import time
import os
import argparse
import arcpy
import json

#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
#http://stackoverflow.com/questions/13653991/passing-quotes-in-process-start-arguments
class SpatialRefWrapper(object):
    #region Constructor
    def __init__(self):
        self.tosr = None
        self.fromsrname = None
        self.availablespatialRef = set();
        try:
            parser = argparse.ArgumentParser()            
            parser.add_argument("-Directory", help="Parent directory", type=str, default="d:\data\ms")   
            parser.add_argument("-FromSR",type=str,help="Name of Spatial Reference to project from", default='NAD_1983_Mississippi_TM')#NAD_1983_Transverse_Mercator
            parser.add_argument("-ToSR",type=str,help="WKID or Name of Spatial Reference to project to", default=None)#'PROJCS["NAD_1983_Transverse_Mercator",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",1300000.0],PARAMETER["Central_Meridian",-89.75],PARAMETER["Scale_Factor",0.9998335],PARAMETER["Latitude_Of_Origin",32.5],UNIT["Meter",1.0]]') #3814 NAD_1983_Mississippi_TM'
            args = parser.parse_args()

            directory = args.Directory
            if directory == '#' or not directory:
                raise Exception('Directory is not supplied')
            if args.FromSR:
                self.fromsrname = args.FromSR
            if args.ToSR:
                self.tosr = arcpy.SpatialReference()
                self.tosr.loadFromString(args.ToSR)#os.path.join(directory,args.ToSR))

            walk = arcpy.da.Walk(directory, datatype=['FeatureClass','RasterDataset','FeatureDataset' ])
            
            for dirpath, dirnames, filenames in walk:
                dirtype = arcpy.Describe(dirpath).datatype
                if(dirtype == 'Coverage' or dirtype == 'FeatureDataset'):
                    self.__defineProjection(dirpath)
                    continue;               
                else:
                    for filename in filenames:
                        item =os.path.join(dirpath, filename); 
                        self.__defineProjection(item)
                    #next filename
            #next directory
            
            print(self.availablespatialRef)

            
        except:
             tb = traceback.format_exc()
             print(tb)

    def __defineProjection(self, item):
        try:

            try:
                sr = arcpy.Describe(item).spatialReference.name
            except:
                print("error getting spatialReference", item)
                return

            if not self.fromsrname: 
                self.availablespatialRef.add(sr)
                return

            if (sr.lower() == self.fromsrname.lower()):
                if(self.tosr != None):
                    try:
                        print("DefineProj to", self.tosr.name)
                        print("BEFORE",arcpy.Describe(item).spatialReference.name)
                        arcpy.DefineProjection_management(item,self.tosr)
                        print("AFTER",arcpy.Describe(item).spatialReference.name)
                        print ("sucessfully Defined", item)
                    except:
                        print("error Defining spatialReference", item)
                else:
                    print (item, sr)
        except :
            tb = traceback.format_exc()
            print(tb)

    
if __name__ == '__main__':
    SpatialRefWrapper()
