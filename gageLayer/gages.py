import requests, gdal, subprocess
from geojson import Point, Feature, FeatureCollection, dump

STATIONTYPEURL = 'https://test.streamstats.usgs.gov/gagestatsservices/stationtypes'
STATIONURL = 'https://test.streamstats.usgs.gov/gagestatsservices/stations?'
PAGECOUNT = '1000'
STARTPAGE = 1
PAGES = 50

params = { 'pageCount': PAGECOUNT, 'page': STARTPAGE }

#first get station type lookup
r = requests.get(STATIONTYPEURL)
station_types = r.json()

#print('station types:', station_types)

features = []

#loop over station pages
for x in range(PAGES):

    params['page'] = STARTPAGE + x

    #print(params)
    r = requests.get(STATIONURL, params=params)
    stations = r.json()

    #check if were done
    if len(stations) == 0:
        print('breaking')
        break

    for station in stations:
        print('station:',station)
        coords = station['location']['coordinates']
        name = station['name']
        siteid = station['code']
        stationtypeid = station['stationTypeID']
        sitetype = None

        #lookup site type
        for station_type in station_types:
            if station_type['id'] == stationtypeid:
                sitetype = station_type['name']
                break

        #print('site:', name,siteid,sitetype)

        point = Point((coords[0], coords[1]))
        features.append(Feature(geometry=point, properties={"name": name, "siteid": siteid, "type": sitetype}))

print('done', len(features))
feature_collection = FeatureCollection(features)

with open('sites.geojson', 'w') as f:
    dump(feature_collection, f)

args = ['ogr2ogr', '-f', 'ESRI Shapefile', 'sites.shp', 'sites.geojson']
subprocess.Popen(args)
