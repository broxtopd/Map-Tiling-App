# Script create an image (tif) file from GIS data
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
import zipfile
import gdal, osr
import subprocess
from PIL import Image
import tempfile
import shutil
import urllib
(major,minor,micro,releaselevel,serial) = sys.version_info
if major == 2:
    from cStringIO import StringIO
elif major == 3:
    from io import StringIO
from cgi import parse_qs, escape
import numpy as np
import multiprocessing
from itertools import repeat

resampling_list = ('average','near','bilinear','cubic','cubicspline','lanczos','antialias')
__version__ = "0.1"
scriptdir = os.path.dirname(os.path.realpath(__file__))

def optparse_init():
        """Prepare the option parser for input (argv)"""

        from optparse import OptionParser, OptionGroup
        usage = 'Usage: %prog [options] input_file(s) [output]'
        p = OptionParser(usage, version='%prog '+ __version__)
        p.add_option('-r', '--resample', dest='resample', type='choice', choices=resampling_list,
                        help='Resampling method (%s) - default "average"' % ','.join(resampling_list))
        p.add_option('-s', '--shpfile', dest='shpfilename',
                          help='Shapefile used to clip the raster')
        p.add_option('-o', '--outsideMask', dest='outsideMask', action='store_true',
                          help='If specified, specifies that everything outside of shape is masked')
        p.add_option('-c', '--clrfile', dest='clrfilename', 
                          help='Color file to be used to make the file into a color file')
        p.add_option('-f', '--bgfile', dest='bgfilename',
                          help='Background data to be blended with foreground data')
        p.add_option('-b', '--blend', dest='blend',
                          help='Fractional blend between background and foreground file (0-1)')
        p.add_option('-p', '--pct', dest='pct', action='store_true',
                          help='If speficied, creates a pct file from an rgb file')     
        p.add_option('-a', '--s_srs', dest='s_srs',
                          help='Coordinate System')  
        p.add_option('-d', '--t_srs', dest='t_srs',
                          help='Coordinate System')  
        p.add_option('-e', '--te', dest='te',
                          help='Map Bounds')  
        p.add_option('-q', '--tr', dest='tr',
                          help='Map Resolution') 
        p.add_option('-t', '--ts', dest='ts',
                          help='Map Scale') 
        p.add_option('-x', '--ExactColorEntry', dest='ExactColorEntry', action='store_true',
                          help='Exact Color Entry') 
        p.add_option('-n', '--NearestColorEntry', dest='NearestColorEntry', action='store_true',
                          help='Nearest Color Entry')  
        p.add_option('-g', '--GISOptimizedImage', dest='GISOptimizedImage', action='store_true',
                          help='Tiled image, GIS Optimized')
        p.set_defaults(resample='near', blend='0.5', shpfilename='', s_srs = '', t_srs = '', te = '', tr = '', ts = '', overlayName = '', FType='', outsideMask=False, clrfilename='', bgfilename='', pct=False,ExactColorEntry=False,NearestColorEntry=False,GISOptimizedImage=False)

        return p
    
if __name__ == '__main__':
    # Parse the command line arguments      
    argv = gdal.GeneralCmdLineProcessor( sys.argv )
    parser = optparse_init()
    options,args = parser.parse_args(args=argv[1:])
    inraster = args[0]
    inpath, infile = os.path.split(inraster)

    outraster = args[1]
    resample = options.resample
    shpfilename = options.shpfilename
    outsideMask = options.outsideMask
    clrfilename = options.clrfilename
    bgfilename = options.bgfilename
    blend = options.blend
    pct = options.pct
    GISOptimizedImage = options.GISOptimizedImage
    s_srs = options.s_srs
    te = options.te
    ts = options.ts
    tr = options.tr
    t_srs = options.t_srs
    ExactColorEntry = options.ExactColorEntry
    NearestColorEntry = options.NearestColorEntry
    
    working_dir = outraster.replace('.tif','_' + os.path.basename(tempfile.mktemp()))
    if ~os.path.exists(working_dir):
        os.makedirs(working_dir)
        
    tempfilename_web = working_dir + '/prepare_web'
    tempfilename_vrt = working_dir + '/prepare_vrt'
    tempfilename_raster = working_dir + '/prepare_raster' + infile[-4:] 
    tempfilename_a = working_dir + '/prepare_a.tif'
    tempfilename_clr = working_dir + '/prepare_clr.vrt'
    tempfilename_shp = working_dir + '/prepare_shp.tif'
    tempfilename_bg = working_dir + '/prepare_bg.tif'
    tempfilename_bg2 = working_dir + '/prepare_bg2.tif'
    tempfilename_pct = working_dir + '/prepare_pct.vrt'

    ifname = inraster

    if '.zip' in inraster:
        zf,zp = inraster.split('.zip')
        fh = open(zf + '.zip', 'rb')
        z = zipfile.ZipFile(fh)
        outfile = open(tempfilename_raster, 'wb')
        outfile.write(z.read(zp[1:]))
        outfile.close()
        fh.close()
        ifname = tempfilename_raster

    if clrfilename != '':    
        command = 'gdaldem color-relief -alpha -of vrt'
        if NearestColorEntry == True:
            command += ' -nearest_color_entry'
        elif ExactColorEntry == True:
            commmand += ' -exact_color_entry'
        command += ' "' + ifname + '" "' + clrfilename + '" "' + tempfilename_clr + '"'
        print(command)
        subprocess.call(command, shell=True)  
        ifname = tempfilename_clr
    else:
        in_ds = gdal.Open(ifname)
        bands = in_ds.RasterCount
        del in_ds
        if bands == 1:
            command = 'gdal_translate -of vrt "' + ifname + '" "' + tempfilename_clr + '"'
            subprocess.call(command, shell=True)  
            ifname = tempfilename_clr

    args = ''
    if s_srs != '':
        args += ' -s_srs "' + s_srs + '"'
    if te != '':
        args += ' -te ' + te 
    if ts != '':
        args += ' -ts ' + ts
    if tr!= '':
        args += ' -tr ' + tr
    if t_srs!= '':
        args += ' -t_srs "' + t_srs + '"'
        
    in_ds = gdal.Open(ifname)
    bands = in_ds.RasterCount
    del in_ds
    if bands == 3 or bands == 1:
        args += ' -dstalpha'
        
    command = 'gdalwarp' + args + ' -multi -r ' + resample + ' -overwrite "' + ifname + '" "' + tempfilename_a + '"'
    print(command)
    subprocess.call(command, shell=True) 
    ifname = tempfilename_a

    if shpfilename != '':
        path, shpfile = os.path.split(shpfilename)
        shplayer = shpfile.replace('.shp','')
        os.rename(ifname,tempfilename_shp)
        if outsideMask == True: 
            command = 'gdal_rasterize -b 4 -burn 0 -l "' + shplayer + '" "' + shpfilename + '" "' + tempfilename_shp + '"'
            print(command)
            subprocess.call(command, shell=True)
            ifname = tempfilename_shp
        else:                
            command = 'gdal_rasterize -i -b 4 -burn 0 -l "' + shplayer + '" "' + shpfilename + '" "' + tempfilename_shp + '"'
            print(command)
            subprocess.call(command, shell=True)
            ifname = tempfilename_shp

    if bgfilename != '':
        in_ds = gdal.Open(ifname)
        projection   = in_ds.GetProjection()
        geotransform = in_ds.GetGeoTransform()
        minx = geotransform[0]
        maxy = geotransform[3]
        maxx = minx + geotransform[1]*in_ds.RasterXSize
        miny = maxy + geotransform[5]*in_ds.RasterYSize
        te_str = str(minx) + ' ' + str(miny) + ' ' + str(maxx) + ' ' + str(maxy)
        ts_str = str(in_ds.RasterXSize) + ' ' + str(in_ds.RasterYSize)
        srs = osr.SpatialReference()
        srs.ImportFromWkt(projection)
        t_srs = srs.ExportToProj4()
        del in_ds
        
        command = 'gdalwarp -multi -r ' + resample + ' -overwrite -te ' + te_str + ' -ts ' + ts_str + ' -t_srs "' + t_srs + '" "' + bgfilename + '" "' + tempfilename_bg + '"'
        print(command)
        subprocess.call(command, shell=True)
        
        command = 'python "' + scriptdir + os.path.sep + 'rgb_merge.py" "' + ifname + '" "' + tempfilename_bg + '" ' + blend + ' "' + tempfilename_bg2 + '"'
        print(command)
        subprocess.call(command, shell=True)
        ifname = tempfilename_bg2
        
    if pct == True:
        command = 'python "' + scriptdir + os.path.sep + 'rgb2pct.py" -of VRT "' + ifname + '" "' + tempfilename_pct + '"'
        print(command)
        subprocess.call(command, shell=True)
        ifname = tempfilename_pct

    if GISOptimizedImage == True:
        command = 'gdalwarp -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=IF_SAFER -multi -overwrite "' + ifname + '" "' + outraster + '"'
        print(command)
        subprocess.call(command, shell=True) 
        command = 'gdaladdo --config COMPRESS_OVERVIEW LZW --config INTERLEAVE_OVERVIEW PIXEL -r average "' + outraster + '" 2 4 8 16 32 64'
        print(command)
        subprocess.call(command, shell=True)
    else:
        command = 'gdalwarp -co COMPRESS=JPEG -multi -overwrite "' + ifname + '" "' + outraster + '"'
        print(command)
        subprocess.call(command, shell=True) 
        
        
    # Remove temporary files 
    shutil.rmtree(working_dir)
    
    print('DONE CREATING MAP!')

