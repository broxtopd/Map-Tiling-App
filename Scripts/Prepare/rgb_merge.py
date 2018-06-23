#!/usr/bin/env python
#******************************************************************************
#  $Id$
#
#  Project:  GDAL Python Interface
#  Purpose:  Script to merge greyscale as intensity into an RGB(A) image, for
#            instance to apply hillshading to a dem colour relief.
#  Author:   Frank Warmerdam, warmerdam@pobox.com
#            Trent Hare (USGS)
#
#******************************************************************************
#  Copyright (c) 2009, Frank Warmerdam
#  Copyright (c) 2010, Even Rouault <even dot rouault at mines-paris dot org>
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
#******************************************************************************

import sys

import numpy
from osgeo import gdal

# =============================================================================
# Usage()

def Usage():
    print("""Usage: rgb_merge.py [-q] [-of format] src_color src_greyscale blend_pct dst_color

where src_color is a RGB or RGBA dataset,
      src_greyscale is a greyscale dataset (e.g. the result of gdaldem hillshade)
      dst_color will be a RGB or RGBA dataset using the greyscale as the
      intensity for the color dataset.
""")
    sys.exit(1)

# =============================================================================
# 	Mainline
# =============================================================================

argv = gdal.GeneralCmdLineProcessor( sys.argv )
if argv is None:
    sys.exit( 0 )

format = 'GTiff'
src_color_filename = None
src_greyscale_filename = None
dst_color_filename = None
blend_pct = None
quiet = False

# Parse command line arguments.
i = 1
while i < len(argv):
    arg = argv[i]

    if arg == '-of':
        i = i + 1
        format = argv[i]

    elif arg == '-q' or arg == '-quiet':
        quiet = True

    elif src_color_filename is None:
        src_color_filename = argv[i]

    elif src_greyscale_filename is None:
        src_greyscale_filename = argv[i]
        
    elif blend_pct is None:
        blend_pct = argv[i]

    elif dst_color_filename is None:
        dst_color_filename = argv[i]
    else:
        Usage()

    i = i + 1

if dst_color_filename is None:
    Usage()

datatype = gdal.GDT_Byte

hilldataset = gdal.Open( src_greyscale_filename, gdal.GA_ReadOnly )
colordataset = gdal.Open( src_color_filename, gdal.GA_ReadOnly )

#check for 3 or 4 bands in the color file
if (colordataset.RasterCount != 3 and colordataset.RasterCount != 4):
    print('Source image does not appear to have three or four bands as required.')
    sys.exit(1)

#define output format, name, size, type and set projection
out_driver = gdal.GetDriverByName(format)
outdataset = out_driver.Create(dst_color_filename, colordataset.RasterXSize, \
                   colordataset.RasterYSize, colordataset.RasterCount, datatype)
outdataset.SetProjection(hilldataset.GetProjection())
outdataset.SetGeoTransform(hilldataset.GetGeoTransform())

#assign RGB and hillshade bands
rBand = colordataset.GetRasterBand(1)
gBand = colordataset.GetRasterBand(2)
bBand = colordataset.GetRasterBand(3)
if colordataset.RasterCount == 4:
    aBand = colordataset.GetRasterBand(4)
else:
    aBand = None

hillband = hilldataset.GetRasterBand(1)
hillbandnodatavalue = hillband.GetNoDataValue()

#check for same file size
if ((rBand.YSize != hillband.YSize) or (rBand.XSize != hillband.XSize)):
    print('Color and hillshade must be the same size in pixels.')
    sys.exit(1)

#loop over lines to apply hillshade
for i in range(hillband.YSize):
    #load RGB and Hillshade arrays
    rScanline = rBand.ReadAsArray(0, i, hillband.XSize, 1, hillband.XSize, 1)
    gScanline = gBand.ReadAsArray(0, i, hillband.XSize, 1, hillband.XSize, 1)
    bScanline = bBand.ReadAsArray(0, i, hillband.XSize, 1, hillband.XSize, 1)
    hillScanline = hillband.ReadAsArray(0, i, hillband.XSize, 1, hillband.XSize, 1)

    r = float(blend_pct) * rScanline + (1-float(blend_pct)) * hillScanline
    g = float(blend_pct) * gScanline + (1-float(blend_pct)) * hillScanline
    b = float(blend_pct) * bScanline + (1-float(blend_pct)) * hillScanline
    dst_color = numpy.asarray([r,g,b]).astype(numpy.uint8)

    # if there's nodata on the hillband, use the v value from the color
    # dataset instead of the hillshade value.
    if hillbandnodatavalue is not None:
        equal_to_nodata = numpy.equal(hillScanline, hillbandnodatavalue)
        v = numpy.choose(equal_to_nodata,(hillScanline,rScanline))
    else:
        v = hillScanline

    #write out new RGB bands to output one band at a time
    outband = outdataset.GetRasterBand(1)
    outband.WriteArray(dst_color[0], 0, i)
    outband = outdataset.GetRasterBand(2)
    outband.WriteArray(dst_color[1], 0, i)
    outband = outdataset.GetRasterBand(3)
    outband.WriteArray(dst_color[2], 0, i)
    if aBand is not None:
        aScanline = aBand.ReadAsArray(0, i, hillband.XSize, 1, hillband.XSize, 1)
        outband = outdataset.GetRasterBand(4)
        outband.WriteArray(aScanline, 0, i)

    #update progress line
    if not quiet:
        gdal.TermProgress_nocb( (float(i+1) / hillband.YSize) )