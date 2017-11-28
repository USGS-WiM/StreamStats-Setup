# ---------------------------------------------------------------------------
# batchCalcinRasterStats.py
# Created on: 11-21-2016
# Author: Martyn Smith USGS
# Usage: batchCalcinRasterStats [gridFolder] [inputFeatures] [outTable]
# Description: Caclulate categorical raster percent area for input polygons
# ---------------------------------------------------------------------------

# Import modules
print 'Importing arcpy...\n'
import arcpy
from arcpy.sa import ExtractByMask
from os import path
from time import time,strftime
from traceback import format_exc
from shutil import rmtree
from tempfile import mkdtemp

#input args
#example string:
# python batchCalcRasterStats.py C:/NYBackup/NYFF2016/results.gdb/inputBasinsAlb D:/gages2grids/prism-nov06-800m/ppt7100_800a pptavg_basin continuous
inputFeatures = arcpy.GetParameterAsText(0)
inRaster = arcpy.GetParameterAsText(1)
outTableName = arcpy.GetParameterAsText(2)
analysisType = arcpy.GetParameterAsText(3)

#MAIN ARGS
#-----------------------------------------------------------------------------------------------------------------------
#check for input arguments
#inVector = 'D:/gages2grids/nhdplusv1/nhdflowline_strahler_alb.shp'  
if not inputFeatures: inputFeatures = 'C:/NYBackup/NYFF2016/LGSS_sites/sites_originalUTM50m.shp' #input polygon features
if not inRaster: inRaster = 'D:/gages2grids/nlcd2011lu/nlcd_2011_landcover_2011_edition_2014_10_10.img'
if not outTableName: outTableName = 'slope'
if not analysisType: analysisType = 'test' #'other' #'continuous'
#-----------------------------------------------------------------------------------------------------------------------

print 'Input arguments:\n----------------\ninputFeatures:',inputFeatures,'\ninRaster:     ',inRaster,'\noutTableName: ',outTableName,'\nanalysisType: ',analysisType,'\n'

#other arguments
uniqueFeatureIDfield = 'SiteID' #unique ID field in input polygon feature classs
uniqueRasterIDfield = 'Value' #unique ID field for Raster
rasterValueField = 'COUNT'
fieldPrefix = 'cat'
calculateStat = 'MEAN' #raster stat to calculate in output table
outTableLocation = 'C:/NYBackup/NYFF2016/LGSS_sites/results.gdb'
outTable = path.join(outTableLocation,outTableName)

#folders
tempFolder = mkdtemp()

#arcpy setup
arcpy.CheckOutExtension('Spatial')
arcpy.env.overwriteOutput = True
arcpy.env.workspace = tempFolder
arcpy.env.scratchWorkspace = tempFolder

def findField(fc, field):
	lst = arcpy.ListFields(fc)
	for f in lst:
		if f.name == field:
			return True
	else:
		return False

def findRow(fc, fieldName, fieldValue):
	with arcpy.da.SearchCursor(fc, fieldName) as cursor:
		for row in cursor:
			if row[0] == fieldValue:
				return True
		else:
			return False

def rasterStatistics2(feature, featureID, inRaster, calculateStat):
	#https://pypi.python.org/pypi/rasterstats/0.3.2
	#http://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio

	from rasterstats import zonal_stats

	try:
		#convert feature to temp shapefile
		arcpy.FeatureClassToFeatureClass_conversion(feature, tempFolder, 'temp.shp')

		#get values
		stats = zonal_stats(tempFolder + '/temp.shp', inRaster, nodata=0, stats=[calculateStat.lower()])
		data = ResultObj(featureID, stats[0])
		return data

	except:
		tb = format_exc()
		raise Exception(tb)

#where feature=geometry,featureID=siteID, inRaster=inRaster,calculateState='mean'
#returns {ID: '01312000', results: {'mean':3.22}}
def rasterStatistics(feature, featureID, inRaster, calculateStat):
	try:
		#create results obj
		results = {}

		#get values
		outExtractByMask = ExtractByMask(inRaster, feature)
		value = arcpy.GetRasterProperties_management(outExtractByMask, calculateStat).getOutput(0)

		value = round(float(value),5)
		results[calculateStat] = value
		data = ResultObj(featureID, results)
		return data

	except:
		try:
			#check raster cell size against input       
			cellsize = float(arcpy.GetRasterProperties_management(inRaster, 'CELLSIZEX').getOutput(0))
			print 'in Except block, area check:',feature.area, cellsize ** 2

			#get centroid value if first method failed
			value = arcpy.GetCellValue_management(inRaster, str(feature.centroid.X) + ' ' + str(feature.centroid.Y)).getOutput(0)
			value = round(float(value),5)
			results[calculateStat] = value
			data = ResultObj(featureID, results)
			return data

		except:
			tb = format_exc()
			raise Exception(tb)

#where feature=geometry,featureID=siteID,inRaster=inRaster,uniquieRasterIDfield='VALUE',rasterValueField='COUNT',fieldPrefix='cat'
def rasterPercentAreas(feature, featureID, inRaster, uniqueRasterIDfield,  rasterValueField, fieldPrefix):
	try:
		#create results obj
		results = {}

		#define land use key value dictionary with all possible values
		for row in arcpy.da.SearchCursor(inRaster, uniqueRasterIDfield):
			results[fieldPrefix + str(row[0])] = 0

		#mask raster
		outExtractByMask = ExtractByMask(inRaster, feature)
		outExtractByMask.save('in_memory/mask.img')

		#get total cell count for percent area computation
		field = arcpy.da.TableToNumPyArray('in_memory/mask.img', rasterValueField, skip_nulls=True)
		sum = field[rasterValueField].sum() 

		#loop over masked raster rows
		for row in arcpy.da.SearchCursor('in_memory/mask.img', [uniqueRasterIDfield, rasterValueField]):

			#get values
			value, count = row
			percentArea = round((float(count) / sum) * 100,5)
			results[fieldPrefix + str(row[0])] = percentArea

		data = ResultObj(featureID, results)
		return data

	except:
		tb = format_exc().split('\n')
		raise Exception(tb)

def vectorStatistics(feature, featureID, uniqueFeatureIDfield, inVector):
	try:
		results = {}

		#clip inVector with feature
		arcpy.Clip_analysis(inVector, feature, 'in_memory/clip', '')

		#accumlate total length of clip features
		sumLength = 0
		maxStrahler = 0
		for row in arcpy.da.SearchCursor('in_memory/clip', ['SHAPE@LENGTH', 'sosc_SO']):
			length,so = row
			sumLength += length
			if so > maxStrahler:
				maxStrahler = so

		#write output
		results['STREAMS_KM_SQ_KM'] = (sumLength/1000)/(feature.area/1000000)
		results['STRAHLER_MAX'] = maxStrahler
		data = ResultObj(featureID, results)
		return data

	except:
		tb = format_exc().split('\n')
		raise Exception(tb)

def testStatistics(feature, featureID, calculateStat):

	str900_all = "D:\\StreamStats\\ny_strgrid\\str900_all" 
	ned10sl = "D:\\ned10\\output\\ned10sl_utm.img"

	#create results obj
	results = {}

	#arcpy.CopyFeatures_management(feature, "C:\\NYBackup\\NYFF2016\\LGSS_sites\\output\\sh_" + featureID + ".shp")

	# Process: Extract by Mask
	strExtractByMask = ExtractByMask(str900_all, feature)
	strExtractByMask.save("C:\\NYBackup\\NYFF2016\\LGSS_sites\\output\\str_" + featureID + ".img")
	slExtractByMask = ExtractByMask(ned10sl, strExtractByMask)
	slExtractByMask.save("C:\\NYBackup\\NYFF2016\\LGSS_sites\\output\\sl_" + featureID + ".img")
	value = arcpy.GetRasterProperties_management(slExtractByMask, calculateStat).getOutput(0)
	value = round(float(value),5)
	results[calculateStat] = value
	data = ResultObj(featureID, results)
	return data



class ResultObj(object):
	def __init__(self,featureID,data):
		self.ID = featureID
		self.data = data

if __name__ == '__main__':

	try:

		# Start time recording
		startTime = time()
		startTimeStr  = strftime('%m-%d-%Y %H:%M:%S')
		print 'Starting program: ', startTimeStr, '\n'

		#create output table 
		if arcpy.Exists(outTable):
			arcpy.Delete_management(outTable)
		arcpy.CreateTable_management(outTableLocation, outTableName)

		#add featureID field
		if not findField(outTable, uniqueFeatureIDfield):
			arcpy.AddField_management(outTable, uniqueFeatureIDfield, 'TEXT', '','',20)

		#add fields for each possible value in categorical raster
		if analysisType == 'categorical':
			arcpy.AddField_management(outTable, fieldPrefix + '0', 'DOUBLE', '','',20)
			for row in arcpy.da.SearchCursor(inRaster, uniqueRasterIDfield):
				if not findField(outTable, fieldPrefix + str(row[0])):
					arcpy.AddField_management(outTable, fieldPrefix + str(row[0]), 'DOUBLE', '','',20)

		#add fields for each possible value in continuous raster
		if analysisType == 'continuous':
			if not findField(outTable, calculateStat):
				arcpy.AddField_management(outTable, calculateStat, 'DOUBLE', '','',20)    

		if analysisType == 'other':
			if not findField(outTable, 'STREAMS_KM_SQ_KM'):
				arcpy.AddField_management(outTable, 'STREAMS_KM_SQ_KM', 'DOUBLE', '','',20)    
			if not findField(outTable, 'STRAHLER_MAX'):
				arcpy.AddField_management(outTable, 'STRAHLER_MAX', 'DOUBLE', '','',20)   

		if analysisType == 'test':
			if not findField(outTable, calculateStat):
				arcpy.AddField_management(outTable, calculateStat, 'DOUBLE', '','',20)    				

		#get feature count
		totalInputFeatures = arcpy.GetCount_management(inputFeatures)
		featureCounter = 0

		#loop over features
		for row in arcpy.da.SearchCursor(inputFeatures, ['SHAPE@', uniqueFeatureIDfield]):

			#get feature info
			feature, featureID = row

			#get raster mean value for feature
			if analysisType == 'categorical':
				results =  rasterPercentAreas(feature, featureID, inRaster, uniqueRasterIDfield, rasterValueField, fieldPrefix)
			if analysisType == 'continuous':
				results =  rasterStatistics(feature, featureID, inRaster, calculateStat)
				#results =  rasterStatistics2(feature, featureID, inRaster, calculateStat)
			if analysisType == 'other':
				results =  vectorStatistics(feature, featureID, uniqueFeatureIDfield, inVector)
			if analysisType == 'test':
				results =  testStatistics(feature, featureID, calculateStat)	

			#build lists for insert cursor
			resultFieldList = results.data.keys()
			resultFieldList.insert(0,uniqueFeatureIDfield)
			resultList = results.data.values()
			resultList.insert(0,results.ID)

			#write data to output table
			if not findRow(outTable, uniqueFeatureIDfield, featureID):
				with arcpy.da.InsertCursor(outTable, resultFieldList) as cursor:
					cursor.insertRow(resultList)

			#increment counter
			featureCounter +=1

			#print progress
			print 'processed:',featureCounter,'of',totalInputFeatures,results.ID,results.data

			#pause for debugging
			#raw_input('Press Enter to continue...')

	except:
		tb = format_exc()
		raise Exception(tb)
	finally:
		arcpy.CheckInExtension('Spatial')
		#rmtree(tempFolder)
		print 'Finished.  Total time elapsed:', round((time()- startTime)/60, 2), 'minutes'
		# name =''
		# if row: del row
		# if cursor: del cursor