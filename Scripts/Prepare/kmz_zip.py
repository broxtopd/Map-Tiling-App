# Zip a directory containing a hierarchy of kml files and convert to a kmz file
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

def zipdir(path, ziph):
	# ziph is zipfile handle
	for root, dirs, files in os.walk(path):
		for file in files:
			ziph.write(os.path.join(root, file))

def kmz_zip(tiledir,outfile):
    # Zip the kmz file
    pwd = os.getcwd()
    os.chdir(tiledir)
    ziph = zipfile.ZipFile(outfile, 'w',allowZip64 = True)
    for f in os.listdir(os.getcwd()):
        if os.path.isdir(f):
            zipdir(f, ziph)
        elif '.xml' not in f and '.html' not in f and '.json' not in f:
            ziph.write(f)
    ziph.close()
    os.chdir(pwd)

if __name__ == '__main__':
    tiledir = sys.argv[1]
    outfile = sys.argv[2]
    kmz_zip(tiledir,outfile)
