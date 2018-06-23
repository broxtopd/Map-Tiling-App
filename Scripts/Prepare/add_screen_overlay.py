# Add a screen overlay to a kml file
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
import shutil

def add_screen_overlay(kml_path,image_path,overlay_folder_name,OverlayName):

    if os.path.isdir(overlay_folder_name) == False:
        os.makedirs(overlay_folder_name)

    shutil.copy(image_path, overlay_folder_name + os.path.sep + OverlayName)

    f = open(kml_path)
    kml_str = f.read()
    f.close()


    kml_rep = '''<ScreenOverlay>
        <Icon>
          <href>%s</href>
        </Icon>
        <overlayXY x="0" y="0.05" xunits="fraction" yunits="fraction"/>
        <screenXY x="0" y="0.05" xunits="fraction" yunits="fraction"/>
        <rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>
        <size x="0" y="0" xunits="fraction" yunits="fraction"/>
    </ScreenOverlay>
    </Document>''' %(OverlayName)

    kml_str = kml_str.replace('</Document>',kml_rep)

    fid_out = open(kml_path,'w')
    fid_out.write(kml_str);
    fid_out.close()
    
if __name__ == '__main__':
    kml_path = sys.argv[1]
    image_path = sys.argv[2]
    overlay_folder_name,OverlayName = os.path.split(sys.argv[3])
    add_screen_overlay(kml_path,image_path,overlay_folder_name,OverlayName)
