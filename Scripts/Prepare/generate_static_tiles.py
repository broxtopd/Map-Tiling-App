# Script to make a tiled map from GIS data
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
import subprocess
import shutil
prefix = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, prefix)

argv = sys.argv
arg_str = ''
overlay = 0
overlayname = ''
ftype = 0
ftype_name = 'png'
savetiff = 0
zoom = 0
resample = 0
zoomstr = ''
resamplestr = ''
for i in argv[1:-2]:
    if i[0:2] == '--':
        if i == '--overlayName':
            overlay = 1
        elif i == '--FType':
            ftype = 1
        elif i == '--SaveTiff':
            savetiff = 1
        elif i == '--Zoom':
            zoom = 1
        else:
            arg_str += i + ' '
        if i == '--resample':
            resample = 1
    else:
        if overlay == 1:
            overlayname = i
            overlay = 0
        elif ftype == 1:
            ftype_name = i
            ftype = 0  
        elif zoom == 1:
            zoomstr = i
            zoom = 0  
        else:
            arg_str += '"' + i + '" '
        if resample == 1:
            resamplestr = i
            resample = 0
          
ifname = argv[len(argv)-2]
ofname = argv[len(argv)-1]
arg_str = arg_str.strip()
outfolder,ofname = os.path.split(ofname)
workingfolder = outfolder

if not os.path.isdir(outfolder):
    os.makedirs(outfolder)
if os.path.isdir(ofname):
    shutil.rmtree(ofname)

if ofname.find('.kmz') > 0:    
    type = 'kmz'
    ofname = ofname.replace('.kmz','')
    if os.path.isfile(outfolder + os.path.sep + ofname + '.kmz'):
        os.remove(outfolder + os.path.sep + ofname + '.kmz')
elif ofname.find('.mbtiles') > 0:
    type = 'mbtiles'
    ofname = ofname.replace('.mbtiles','')
    if os.path.isfile(outfolder + os.path.sep + ofname + '.mbtiles'):
        os.remove(outfolder + os.path.sep + ofname + '.mbtiles')
elif ofname.find('.tif') > 0:
    type = 'tif'
    savetiff = 1
    ofname = ofname.replace('.tif','')
    if os.path.isfile(outfolder + os.path.sep + ofname + '.tif'):
        os.remove(outfolder + os.path.sep + ofname + '.tif')
        
kmzname = outfolder + os.path.sep + ofname + '.kmz'
mbtilesname = outfolder + os.path.sep + ofname + '.mbtiles'
ofname = workingfolder + os.path.sep + ofname

if savetiff:
    arg_str += ' --GISOptimizedImage'
    
command = 'python "' + prefix + '/generate_tif.py" "' + ifname + '" -g ' + arg_str + ' "' + ofname + '.tif"' 
print(command)
subprocess.call(command, shell=True)

zoomstr = zoomstr.replace(' ','-')
if resamplestr == '':
    resamplestr = 'near'
if type == 'kmz':
    if zoomstr == '':
        command = 'python "' + prefix + '/gdal2tiles-multiprocess.py" -r ' + resamplestr + ' --profile geodetic -w none -k "' + ofname + '.tif' + '" "' + ofname + '"'
    else:
        command = 'python "' + prefix + '/gdal2tiles-multiprocess.py" -r ' + resamplestr + ' --zoom "' + zoomstr + '" --profile geodetic -w none -k "' + ofname + '.tif' + '" "' + ofname + '"'
    print(command)
    subprocess.call(command, shell=True)
elif type == 'mbtiles':
    if zoomstr == '':
        command = 'python "' + prefix + '/gdal2tiles-multiprocess.py" -r ' + resamplestr + ' "' + ofname + '.tif' + '" "' + ofname + '"'
    else:
        command = 'python "' + prefix + '/gdal2tiles-multiprocess.py" -r ' + resamplestr + ' --zoom "' + zoomstr + '" "' + ofname + '.tif' + '" "' + ofname + '"'
    print(command)
    subprocess.call(command, shell=True)

if type == 'kmz':
    command = 'python "' + prefix + '/shrink_tiles.py" "' + ofname + '" mix'
    print(command)
    subprocess.call(command, shell=True)

    if overlayname != '':
        path,overlay = os.path.split(overlayname)
        overlay_folder_name = ofname + os.path.sep + overlay
        command = 'python "' + prefix + '/add_screen_overlay.py" "' + ofname + os.path.sep + 'doc.kml" "' + overlayname + '" "' + overlay_folder_name + '"'
        print(command)
        subprocess.call(command, shell=True)
        
    command = 'python "' + prefix + '/kmz_zip.py" "' + ofname + '" "' + kmzname + '"'
    print(command)
    subprocess.call(command, shell=True)

elif type == 'mbtiles':
    if ftype_name == 'jpg' or ftype_name == 'jpeg':
        command = 'python "' + prefix + '/shrink_tiles.py" "' + ofname + '" all'
        print(command)
        subprocess.call(command, shell=True)

        command = 'python "' + prefix + '/mb-util.py" --scheme=tms --image_format jpg "' + ofname + '" "' + mbtilesname + '"'
        print(command)
        subprocess.call(command, shell=True)
        
    else:
        command = 'python "' + prefix + '/mb-util.py" --scheme=tms --image_format png "' + ofname + '" "' + mbtilesname + '"'
        print(command)
        subprocess.call(command, shell=True)

if not savetiff:
    os.remove(ofname + '.tif') 

if type == 'kmz' or type == 'mbtiles':
    shutil.rmtree(ofname)

print('DONE CREATING TILES!')
