# Script to go through all images in quadtree hierarchy and convert images that
# do not have any transparency to jpegs to save space
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
from PIL import Image

def shrink_tiles(outdir,mode):
    pwd = os.getcwd()
    path = outdir

    for root, dirs, files in os.walk(path):
        for file in files:
            if  file.find('.png') != -1:
                im = Image.open(root + os.path.sep + file)
                extrema = im.getextrema()
                pngfile = root + os.path.sep + file
                jpgfile = root + os.path.sep + file.replace('.png','.jpg')
                kmlfile = root + os.path.sep + file.replace('.png','.kml') 
                if len(extrema) == 4:
                    if extrema[3][1] == 0:
                        # Remove the image and kml file
                        os.remove(pngfile)
                        os.remove(kmlfile)
                    elif (mode == 'mix' and extrema[3][0] == 255) or (mode == 'all'):
                        # Convert the image to a jpeg
                        im = Image.open(pngfile)
                        im = im.convert('RGB')
                        im.save(jpgfile)
                        os.remove(pngfile)
                        f = open(kmlfile);
                        kml = f.read()
                        kml = kml
                        f.close()
                        f = open(kmlfile,'w')
                        f.write(kml.replace('.png','.jpg'))
                        f.close()
                else:
                    im = Image.open(pngfile)
                    im = im.convert('RGB')
                    im.save(jpgfile)
                    os.remove(pngfile)
                    f = open(kmlfile);
                    kml = f.read()
                    kml = kml
                    f.close()
                    f = open(kmlfile,'w')
                    f.write(kml.replace('.png','.jpg'))
                    f.close()
                del im
                
    if mode == 'all':
        jsonfile = outdir + os.path.sep + 'metadata.json'
        f = open(jsonfile);
        txt = f.read()
        txt = txt
        f.close()
        f = open(jsonfile,'w')
        f.write(txt.replace('png','jpg'))
        f.close()
    
if __name__ == '__main__':
    outdir = sys.argv[1]
    mode = sys.argv[2]
    shrink_tiles(outdir,mode)

