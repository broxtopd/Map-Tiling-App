# Convert a qgis qml file to a clr file
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
import sys, os
from xml.dom import minidom
from optparse import OptionParser, OptionGroup

def qml2clr(qml):

    xmldoc = minidom.parse(qml)
    itemlist = xmldoc.getElementsByTagName('item') 

    file = open(qml[:-4] + '.clr','w')
    for s in itemlist :
        value = s.attributes['value'].value
        color = s.attributes['color'].value.lstrip('#')
        alpha = s.attributes['alpha'].value
        (r,g,b) = tuple(int(color[i:i+2], 16) for i in (0, 2 ,4))
        file.write(str(value) + ' ' + str(r) + ' ' + str(g) + ' ' + str(b) + ' ' + str(alpha) + '\n')

    file.close()

if __name__ == '__main__':
    if len(sys.argv) < 1 or len(sys.argv) > 1:
        print("Usage: qml2clr.py stylefile.qml")
        sys.exit(1)
    qml = sys.argv[1]
    try:
        qml2clr(qml)
        print('Successfully wrote ' + qml[:-4] + '.clr!')
    except:
        print('There was a problem creating the .clr file')