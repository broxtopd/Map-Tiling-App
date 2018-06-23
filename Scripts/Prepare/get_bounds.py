# Get georeferencing information from a GIS datasource (called directly from the GUI program)
#
###############################################################################
# Copyright (c) 2018, Patrick Broxton
# 
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
###############################################################################
import sys,os
from osgeo import gdal,osr,ogr
from gdalconst import *
    
def get_raster_info(clipsrc):

    ds = gdal.Open(clipsrc, GA_ReadOnly)
    if ds is None:
        print('Content-Type: text/html\n')
        print('Could not open ' + clipsrc)
        sys.exit(1)
        
    # Read the georeferecing info on the raster_to_match
    transform = ds.GetGeoTransform()
    wkt = ds.GetProjection()
    rows = ds.RasterYSize
    cols = ds.RasterXSize
    ulx = transform[0]
    uly = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    lrx = ulx + (cols * pixelWidth)
    lry = uly + (rows * pixelHeight)
    te = str(ulx) + ' ' + str(lry) + ' ' + str(lrx) + ' ' + str(uly)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    
    epsg = srs.GetAttrValue("AUTHORITY",1)
    if epsg == None:
        epsg_success = False
        epsg = ''
    else:
        epsg_success = True
    proj4 = srs.ExportToProj4()
        
    return(ulx,uly,lrx,lry,pixelWidth,-pixelHeight,epsg,epsg_success,proj4)
        
def get_shape_info(clipsrc):

    shape = ogr.Open(clipsrc)
    if shape is None:
        print('Could not open ' + clipsrc)
        sys.exit(1) 

    layer = shape.GetLayer()
    ulx = 180
    uly = -90
    lrx = -180
    lry = 90
    for i in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(i)
        geom = feature.GetGeometryRef()
        srs = geom.GetSpatialReference()
        (ulx2, lrx2, lry2, uly2) = geom.GetEnvelope()
        ulx = min(ulx,ulx2)
        lrx = max(lrx,lrx2)
        lry = min(lry,lry2)
        uly = max(uly,uly2)
 
    epsg = srs.GetAttrValue("AUTHORITY",1)
    if epsg == None:
        epsg_success = False
        epsg = ''
    else:
        epsg_success = True
    proj4 = srs.ExportToProj4()
    
    return(ulx,uly,lrx,lry,epsg,epsg_success,proj4)
    