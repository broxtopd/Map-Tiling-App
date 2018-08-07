# GUI for the map tiling application
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

import sys
import os
(major,minor,micro,releaselevel,serial) = sys.version_info
if major == 2:
    import Tkinter as tk
    import tkMessageBox as tkmb
    import tkFileDialog as tkfd
elif major == 3:
    import tkinter as tk
    from tkinter import messagebox as tkmb
    from tkinter import filedialog as tkfd
import subprocess
import time
import datetime
import random
import string
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/Prepare')
import get_bounds
import qml2clr

raster_file_types = "*.vrt *.tif* *.asc *.txt *.img"
vector_file_types = "*.shp *.gpx *.kml"
image_file_types = "*.png* *.jpg* *.jpeg* *.gif *.bmp"

class Tiler():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Map Tiling Application")

        self.canvas = tk.Canvas(self.root, width=500, height=500)
        self.canvas.pack()

        self.canvas.grid(row=1, column=0, rowspan=2, sticky="nsew")
        
        self.initialdir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
        
        # Inputs text
        self.inputs_frame = tk.Frame(self.canvas)
        self.inputs_frame.grid(sticky="w",row=0, column=0, columnspan=2)
        self.inputs = tk.Label(self.inputs_frame, text="Inputs:")
        self.inputs.grid(sticky='w', row=0, column=0)
                                
        # Input file
        self.input_check = tk.IntVar()
        self.input_checkbox = tk.Checkbutton(self.inputs_frame, text="Input Dataset: ", variable=self.input_check,state=tk.DISABLED)
        self.input_checkbox.grid(sticky='w', row=1, column=0)
        self.input_check.set(1)
        self.input_frame = tk.Canvas(self.inputs_frame)
        self.input_frame.grid(sticky="w",row=1, column=1)
        self.input_filename_var = tk.StringVar()
        self.input_filename_var.set('')
        self.input_dialog_button = tk.Button(self.input_frame, text='Choose a file...', command=self.open_input_dialog)
        self.input_dialog_button.grid(sticky="w",row=0, column=1)
        self.input_filename = tk.Entry(self.input_frame, textvariable=self.input_filename_var, width=35)
        self.input_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.input_filename_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.input_filename.grid(sticky="w",row=0, column=2)
        
        # Clr file
        self.clr_check = tk.IntVar()
        self.clr_checkbox = tk.Checkbutton(self.inputs_frame, text="Colorize the Input File: ", variable=self.clr_check)
        self.clr_checkbox.grid(sticky='w', row=2, column=0)
        self.clr_frame = tk.Canvas(self.inputs_frame)
        self.clr_frame.grid(sticky="w",row=2, column=1)
        self.clr_filename_var = tk.StringVar()
        self.clr_filename_var.set('')
        self.clr_dialog_button = tk.Button(self.clr_frame, text='Choose a file...', command=self.open_clr_dialog)
        self.clr_dialog_button.grid(sticky="w",row=0, column=0)
        self.clr_filename = tk.Entry(self.clr_frame, textvariable=self.clr_filename_var, width=35)
        self.clr_filename.grid(sticky="w",row=0, column=1)
        self.clr_check.trace("w", lambda name, index, mode, object=self.clr_frame,check=self.clr_check: self.check_show(object,check))
        self.clr_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.clr_filename_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.clr_frame.grid_remove()
        
        # Clr file options
        self.qml2clr_button = tk.Button(self.inputs_frame, text='Create CLR from QML', command=self.qml2clr)
        self.qml2clr_button.grid(sticky="w",row=3, column=0)
        self.colormode_frame = tk.Frame(self.inputs_frame)
        self.colormode_frame.grid(sticky="w",row=3, column=1,columnspan=3)
        self.colormode_txt = tk.Label(self.colormode_frame, text="Color Interpolation Mode:")
        self.colormode_txt.grid(sticky='w',row=0, column=0)
        MODES = [
            ("Interpolated", "interp"),
            ("Exact", "exact"),
            ("Nearest", "nearest"),
        ]
        self.colormode_var = tk.StringVar()
        self.colormode_var.set('interp')
        i = 0;
        for text, mode in MODES:
            i = i+1
            self.colormode = tk.Radiobutton(self.colormode_frame, text=text, variable=self.colormode_var, value=mode)
            self.colormode.grid(sticky="w",row=0, column=i)
        self.colormode_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.colormode_frame.grid_remove()
        
        # Shapefile
        self.shp_check = tk.IntVar()
        self.shp_checkbox = tk.Checkbutton(self.inputs_frame, text="Mask with a Shapefile: ", variable=self.shp_check)
        self.shp_checkbox.grid(sticky='w', row=4, column=0)
        self.shp_frame = tk.Canvas(self.inputs_frame)
        self.shp_frame.grid(sticky="w",row=4, column=1)
        self.shp_filename_var = tk.StringVar()
        self.shp_filename_var.set('')
        self.shp_dialog_button = tk.Button(self.shp_frame, text='Choose a file...', command=self.open_shp_dialog)
        self.shp_dialog_button.grid(sticky="w",row=0, column=0)
        self.shp_filename = tk.Entry(self.shp_frame, textvariable=self.shp_filename_var, width=35)
        self.shp_filename.grid(sticky="w",row=0, column=1)
        self.shp_invert_check = tk.IntVar()
        self.shp_invert_checkbox = tk.Checkbutton(self.shp_frame, text="Invert Mask ", variable=self.shp_invert_check)
        self.shp_invert_checkbox.grid(sticky="e",row=0, column=2)
        self.shp_check.trace("w", lambda name, index, mode, object=self.shp_frame,check=self.shp_check: self.check_show(object,check))
        self.shp_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.shp_filename_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.shp_invert_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.shp_frame.grid_remove()
        
        # Background file
        self.bg_check = tk.IntVar()
        self.bg_checkbox = tk.Checkbutton(self.inputs_frame, text="Include Background File: ", variable=self.bg_check)
        self.bg_checkbox.grid(sticky='w', row=5, column=0)
        self.bg_frame = tk.Canvas(self.inputs_frame)
        self.bg_frame.grid(sticky="w",row=5, column=1)
        self.bg_filename_var = tk.StringVar()
        self.bg_filename_var.set('')
        self.bg_dialog_button = tk.Button(self.bg_frame, text='Choose a file...', command=self.open_bg_dialog)
        self.bg_dialog_button.grid(sticky="w",row=0, column=0)
        self.bg_filename = tk.Entry(self.bg_frame, textvariable=self.bg_filename_var, width=35)
        self.bg_filename.grid(sticky="w",row=0, column=1)
        self.bg_blend_label = tk.Label(self.bg_frame, text="Blend (%):")
        self.bg_blend_label.grid(sticky="e",row=0, column=2)
        self.bg_blend_var = tk.StringVar() # Reprojection String
        self.bg_blend = tk.Entry(self.bg_frame, textvariable=self.bg_blend_var, width=5)
        self.bg_blend.grid(sticky="w",row=0, column=3)
        self.bg_blend_var.set(50)
        self.bg_check.trace("w", lambda name, index, mode, object=self.bg_frame,check=self.bg_check: self.check_show(object,check))
        self.bg_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bg_filename_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bg_blend_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bg_frame.grid_remove()
        
        # OUTPUTS

        self.spacer1 = tk.Label(self.canvas, text="")
        self.spacer1.grid(sticky="w",row=1, column=0)
        
        # Outputs text
        self.outputs_frame = tk.Frame(self.canvas)
        self.outputs_frame.grid(sticky="w",row=2, column=0,columnspan=2)
        self.outputs = tk.Label(self.outputs_frame, text="Outputs:")
        self.outputs.grid(sticky="w",row=0, column=0)
        
        # Outputs
        MODES = [
            ("Create JPEG-Compressed Tiff", "RGB-JPEG"),
            ("Create LZW-Compressed Tiff", "RGB-GIS"),
            ("Create MBTiles file", "MBTiles"),
            ("Create Google Earth KMZ file", "KMZ"),
        ]
        self.outputs_var = tk.StringVar()
        i = 0
        for text, mode in MODES:
            i = i+1
            out_opts = tk.Radiobutton(self.outputs_frame, text=text,
                            variable=self.outputs_var, value=mode)
            out_opts.grid(sticky="w",row=i, column=0)
        self.outputs_var.set("RGB-GIS") # initialize
        
        self.mbtiles_frame = tk.Frame(self.outputs_frame)
        self.mbtiles_frame.grid(sticky="w",row=3, column=1)
        
        # Include Base Tiff File
        self.basetiff_mbtiles_check = tk.IntVar()  # Basetiff Checkbox Variable
        self.basetiff_mbtiles_checkbox = tk.Checkbutton(self.mbtiles_frame, text="Keep Base Tiff File ", variable=self.basetiff_mbtiles_check)
        self.basetiff_mbtiles_checkbox.grid(sticky="w",row=0, column=0)
        
        # Output Tile Type
        self.tiletype_txt = tk.Label(self.mbtiles_frame, text="Tile Type:")
        self.tiletype_txt.grid(sticky="w",row=0, column=1)
        MODES = [
            ("PNG", "png"),
            ("JPEG", "jpeg")
        ]
        self.tiletype_mbtiles = tk.StringVar()
        i = 1;
        for text, mode in MODES:
            i = i+1
            resample = tk.Radiobutton(self.mbtiles_frame, text=text,
                            variable=self.tiletype_mbtiles, value=mode)
            resample.grid(sticky="w",row=0, column=i)
        self.tiletype_mbtiles.set("png") # initialize
        
        self.kmz_frame = tk.Frame(self.outputs_frame)
        self.kmz_frame.grid(sticky="w",row=4, column=1)
        
        # Include Base Tiff File
        self.basetiff_kmz_check = tk.IntVar()  # Basetiff Checkbox Variable
        self.basetiff_kmz_checkbox = tk.Checkbutton(self.kmz_frame, text="Keep Base Tiff File ", variable=self.basetiff_kmz_check)
        self.basetiff_kmz_checkbox.grid(sticky="w",row=0, column=0)
        self.kmz_overlay_filename_var = tk.StringVar()
        self.kmz_overlay_filename_var.set('')
        self.kmz_overlay_dialog_button = tk.Button(self.kmz_frame, text='Choose Overlay...', command=self.open_kmz_overlay_dialog)
        self.kmz_overlay_dialog_button.grid(sticky="w",row=0, column=1)
        self.kmz_overlay_filename = tk.Entry(self.kmz_frame, textvariable=self.kmz_overlay_filename_var, width=22)
        self.kmz_overlay_filename.grid(sticky="w",row=0, column=2)
        
        self.outputs_var.trace("w", lambda name, index, mode, :self.outputs_show())
        self.outputs_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.basetiff_kmz_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.basetiff_mbtiles_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.tiletype_mbtiles.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.basetiff_kmz_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.kmz_overlay_filename_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.mbtiles_frame.grid_remove()
        self.kmz_frame.grid_remove()
        
        # Output File
        self.output_check = tk.IntVar()
        self.output_checkbox = tk.Checkbutton(self.canvas, text="Output File: ", variable=self.output_check,state=tk.DISABLED)
        self.output_checkbox.grid(sticky='w', row=3, column=0)
        self.output_check.set(1)
        self.output_frame = tk.Canvas(self.canvas)
        self.output_frame.grid(sticky="w",row=4, column=0)
        self.output_dirname_var = tk.StringVar()
        self.output_dirname_var.set('')
        self.output_dialog_button = tk.Button(self.output_frame, text='Choose directory...', command=self.open_output_directory_dialog)
        self.output_dialog_button.grid(sticky="w",row=0, column=0)
        self.output_dirname = tk.Entry(self.output_frame, textvariable=self.output_dirname_var, width=35)
        self.output_dirname.grid(sticky="w",row=0, column=1)
        self.output_filename_label = tk.Label(self.output_frame, text="Filename:")
        self.output_filename_label.grid(sticky="e",row=0, column=2)
        self.output_filename_var = tk.StringVar() # Reprojection String
        self.output_filename = tk.Entry(self.output_frame, textvariable=self.output_filename_var, width=12)
        self.output_filename.grid(sticky="w",row=0, column=3)
        self.output_filename_var.set('')
        self.output_check.trace("w", lambda name, index, mode, object=self.output_frame,check=self.output_check: self.check_show(object,check))
        self.output_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.output_dirname_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.output_filename_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        
        
        # OPTIONS
        
        self.spacer1 = tk.Label(self.canvas, text="")
        self.spacer1.grid(sticky="w",row=5, column=0)
        
        # Options text
        self.options_frame = tk.Frame(self.canvas)
        self.options_frame.grid(sticky="w",row=6, column=0, columnspan=2)
        self.options = tk.Label(self.options_frame, text="Options:")
        self.options.grid(sticky='w',row=0, column=0)
        self.options_raster_button = tk.Button(self.options_frame, text='Get Info from Georeferenced File', command=self.get_geo_info)
        self.options_raster_button.grid(sticky="w",row=0, column=1)
        
        # Reproject Map
        self.t_srs_check = tk.IntVar()  # Checkbox Variable
        self.t_srs_checkbox = tk.Checkbutton(self.options_frame, text="Reproject Map: ", variable=self.t_srs_check)
        self.t_srs_checkbox.grid(sticky='w',row=2, column=0)
        self.t_srs_frame = tk.Canvas(self.options_frame)
        self.t_srs_frame.grid(sticky="w",row=2, column=1)
        self.t_srs_txt = tk.Label(self.t_srs_frame, text="Target SRS:")
        self.t_srs_txt.grid(sticky='w',row=0, column=0)
        self.t_srs_var = tk.StringVar() # Reprojection String
        self.t_srs = tk.Entry(self.t_srs_frame, textvariable=self.t_srs_var, width=40)
        self.t_srs.grid(sticky='w',row=0, column=1)
        self.t_srs_check.trace("w", lambda name, index, mode, object=self.t_srs_frame,check=self.t_srs_check: self.check_show(object,check))
        self.t_srs_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.t_srs_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.t_srs_frame.grid_remove()
        
        # Adjust Bounds
        self.bounds_check = tk.IntVar()  # Bounds Checkbox Variable
        self.bounds_checkbox = tk.Checkbutton(self.options_frame, text="Adjust Bounds: ", variable=self.bounds_check)
        self.bounds_checkbox.grid(sticky="w",row=3, column=0)
        self.bounds_frame = tk.Canvas(self.options_frame)
        self.bounds_frame.grid(sticky="w",row=3, column=1)
        self.bounds_xmin_txt = tk.Label(self.bounds_frame, text="XMin:")
        self.bounds_xmin_txt.grid(sticky='w',row=0, column=1)
        self.bounds_xmin_var = tk.StringVar() # Bounds XMin String
        self.bounds = tk.Entry(self.bounds_frame, textvariable=self.bounds_xmin_var, width=8)
        self.bounds.grid(sticky="w",row=0, column=2)
        self.bounds_xmax_txt = tk.Label(self.bounds_frame, text="XMax:")
        self.bounds_xmax_txt.grid(sticky="w",row=0, column=3)
        self.bounds_xmax_var = tk.StringVar() # Bounds XMax String
        self.bounds = tk.Entry(self.bounds_frame, textvariable=self.bounds_xmax_var, width=8)
        self.bounds.grid(sticky="w",row=0, column=4)
        self.bounds_ymin_txt = tk.Label(self.bounds_frame, text="YMin:")
        self.bounds_ymin_txt.grid(sticky="w",row=0, column=5)
        self.bounds_ymin_var = tk.StringVar() # Bounds YMin String
        self.bounds = tk.Entry(self.bounds_frame, textvariable=self.bounds_ymin_var, width=8)
        self.bounds.grid(sticky="w",row=0, column=6)
        self.bounds_xmax_txt = tk.Label(self.bounds_frame, text="XMax:")
        self.bounds_xmax_txt.grid(sticky="w",row=0, column=7)
        self.bounds_ymax_var = tk.StringVar() # Bounds YMax String
        self.bounds = tk.Entry(self.bounds_frame, textvariable=self.bounds_ymax_var, width=8)
        self.bounds.grid(sticky="w",row=0, column=8)
        self.bounds_check.trace("w", lambda name, index, mode, object=self.bounds_frame,check=self.bounds_check: self.check_show(object,check))
        self.bounds_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bounds_xmin_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bounds_xmax_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bounds_ymin_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bounds_ymax_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.bounds_frame.grid_remove()
        
        # Adjust Resolution
        self.res_check = tk.IntVar()  # Adjust Resolution Checkbox Variable
        self.res_checkbox = tk.Checkbutton(self.options_frame, text="Adjust Resolution: ", variable=self.res_check)
        self.res_checkbox.grid(sticky="w",row=4, column=0)
        self.res_frame = tk.Canvas(self.options_frame)
        self.res_frame.grid(sticky="w",row=4, column=1)
        self.res_xres_txt = tk.Label(self.res_frame, text="X-Resolution:")
        self.res_xres_txt.grid(sticky="w",row=0, column=0)
        self.res_xres_var = tk.StringVar() # Reolution XRes String
        self.res = tk.Entry(self.res_frame, textvariable=self.res_xres_var, width=8)
        self.res.grid(sticky="w",row=0, column=1)
        self.res_yres_txt = tk.Label(self.res_frame, text="Y-Resolution:")
        self.res_yres_txt.grid(sticky="w",row=0, column=2)
        self.res_yres_var = tk.StringVar() # Resolution YRes String
        self.res = tk.Entry(self.res_frame, textvariable=self.res_yres_var, width=8)
        self.res.grid(sticky="w",row=0, column=3)
        self.res_check.trace("w", lambda name, index, mode, object=self.res_frame,check=self.res_check: self.check_show(object,check))
        self.res_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.res_xres_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.res_yres_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.res_frame.grid_remove()
        
        # Adjust Zoom Levels
        # self.zoom_frame_0 = tk.Canvas(self.options_frame)
        # self.zoom_frame_0.grid(sticky="w",row=5, column=0,columnspan=2)
        self.zoom_check = tk.IntVar()  # Zoom Levels Checkbox Variable
        self.zoom_checkbox = tk.Checkbutton(self.options_frame, text="Adjust Zoom: ", variable=self.zoom_check)
        self.zoom_checkbox.grid(sticky="w",row=5, column=0)
        self.zoom_frame = tk.Canvas(self.options_frame)
        self.zoom_frame.grid(sticky="w",row=5, column=1)
        self.zoom_minz_txt = tk.Label(self.zoom_frame, text="MinZoom:")
        self.zoom_minz_txt.grid(sticky="w",row=0, column=0)
        self.zoom_minz_var = tk.StringVar() # Min Zoom String Variable
        self.zoom = tk.Entry(self.zoom_frame, textvariable=self.zoom_minz_var, width=8)
        self.zoom.grid(sticky="w",row=0, column=1)
        self.zoom_maxz_txt = tk.Label(self.zoom_frame, text="MaxZoom:")
        self.zoom_maxz_txt.grid(sticky="w",row=0, column=2)
        self.zoom_maxz_var = tk.StringVar() # Max Zoom String Variable
        self.zoom = tk.Entry(self.zoom_frame, textvariable=self.zoom_maxz_var, width=8)
        self.zoom.grid(sticky="w",row=0, column=3)
        self.zoom_check.trace("w", lambda name, index, mode, object=self.zoom_frame,check=self.zoom_check: self.check_show(object,check))
        self.zoom_check.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.zoom_minz_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.zoom_maxz_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        self.zoom_frame.grid_remove()
        
        # Resampling Method
        self.resample_frame = tk.Frame(self.options_frame)
        self.resample_frame.grid(sticky="w",row=6, column=0,columnspan=8)
        self.resample_txt = tk.Label(self.resample_frame, text="Resampling Method:")
        self.resample_txt.grid(sticky='w',row=0, column=0)
        MODES = [
            ("Average", "average"),
            ("Nearest", "near"),
            ("Bilinear", "bilinear"),
            ("CubicSpline", "cubicspline"),
            ("Lanczos", "lanczos"),
            ("AntiAlias", "antiAlias")
        ]
        self.resample_var = tk.StringVar()
        self.resample_var.set('average')
        i = 0;
        for text, mode in MODES:
            i = i+1
            self.resample = tk.Radiobutton(self.resample_frame, text=text, variable=self.resample_var, value=mode)
            self.resample.grid(sticky="w",row=0, column=i)
        self.resample_var.trace("w", lambda name, index, mode, :self.update_preprocess_cmd())
        
        self.spacer3 = tk.Label(self.canvas, text="")
        self.spacer3.grid(sticky="w",row=7, column=0)
        
        self.command_frame = tk.Frame(self.canvas)
        self.command_frame.grid(sticky="w",row=8, column=0, columnspan=2)
        self.command_txt = tk.Label(self.command_frame, text="Command:")
        self.command_txt.grid(sticky='w',row=0, column=0)
        self.command_var = tk.StringVar() # Layers String
        self.command = tk.Text(self.command_frame, width=60, height=5)
        self.command.grid(sticky="w",row=1, column=0)
        self.command.bind("<1>", lambda event: self.command.focus_set())
        self.command_button = tk.Button(self.command_frame, text='Start!', command=self.execute_prepare)
        self.command_button.grid(sticky="w",row=1, column=1)
        
        self.update_preprocess_cmd()
        self.root.mainloop()
        
    def outputs_show(self):
        if self.outputs_var.get() == 'MBTiles':
            self.mbtiles_frame.grid()
            self.kmz_frame.grid_remove()
        elif self.outputs_var.get() == 'KMZ':
            self.mbtiles_frame.grid_remove()
            self.kmz_frame.grid()    
        else:
            self.mbtiles_frame.grid_remove()
            self.kmz_frame.grid_remove()    
        
    def check_show(self,event,check):
        if check.get() == 0:
            event.grid_remove()
        else:
            event.grid()
            
        if self.clr_check.get() == 0:
            self.colormode_frame.grid_remove()
        else:
            self.colormode_frame.grid()
   
    def qml2clr(self):
        filename = tkfd.askopenfilename(initialdir=self.initialdir,title = "Select qml file")
        try: 
            qml2clr.qml2clr(filename)
            tkmb.showinfo("Success", "Created " + filename.replace('.qml','.clr')) 
        except:
            tkmb.showinfo("Georeference Error", "There was a problem converting " + filename) 
                
    def get_geo_info(self):
        filename = tkfd.askopenfilename(initialdir=self.initialdir,title = "Select file")
        if '.tif' in filename: 
            try:
                (ulx,uly,lrx,lry,pixelWidth,pixelHeight,epsg,epsg_success,proj4) = get_bounds.get_raster_info(filename)
                if epsg_success == True:
                    t_srs = 'EPSG:' + epsg
                else:
                    t_srs = proj4
                self.t_srs_check.set(1)
                self.t_srs_var.set(t_srs)
                self.bounds_check.set(1)
                self.bounds_xmin_var.set(ulx)
                self.bounds_xmax_var.set(lrx)
                self.bounds_ymin_var.set(lry)
                self.bounds_ymax_var.set(uly)
                self.res_check.set(1)
                self.res_xres_var.set(pixelWidth)
                self.res_yres_var.set(pixelHeight)
            except:
                tkmb.showinfo("Georeference Error", "There was a problem reading the georeferencing information on the specified file") 
        if '.shp' in filename:
            try:
                (ulx,uly,lrx,lry,epsg,epsg_success,proj4) = get_bounds.get_shape_info(filename)
                if epsg_success == True:
                    t_srs = 'EPSG:' + epsg
                else:
                    t_srs = proj4
                self.t_srs_check.set(1)
                self.t_srs_var.set(proj4)
                self.bounds_check.set(1)
                self.bounds_xmin_var.set(ulx)
                self.bounds_xmax_var.set(lrx)
                self.bounds_ymin_var.set(lry)
                self.bounds_ymax_var.set(uly)
            except:
                tkmb.showinfo("Georeference Error", "There was a problem reading the georeferencing information on the specified file") 
        
    def execute_prepare(self):
        output_filename_var = self.output_filename_var.get()
        if (self.outputs_var.get() == 'RGB-JPEG' or self.outputs_var.get() == 'RGB-GIS') and not (output_filename_var[-4:].lower() == '.tif'):
            output_filename_var += '.tif'
        if self.outputs_var.get() == 'MBTiles' and not (output_filename_var[-8:].lower() == '.mbtiles'):
            output_filename_var += '.mbtiles'
        if self.outputs_var.get() == 'KMZ' and not (output_filename_var[-4:].lower() == '.kmz'):
            output_filename_var += '.kmz'
            
        execute = 'yes'
        outdir = self.output_dirname_var.get()
        if os.path.exists(self.output_dirname_var.get() + '/' + os.path.splitext(output_filename_var)[0]):
            tkmb.showinfo('File Exists', 'The folder ' + os.path.splitext(output_filename_var)[0] + ' exists in this location.  Please specify a different name.')
            execute='no'
        elif os.path.exists(self.output_dirname_var.get() + '/' + output_filename_var):
            execute = tkmb.askquestion('File Exists', 'The file ' + output_filename_var + ' exists in this location.  Do you want to continue?', icon='warning', default='no')
        elif os.path.exists(self.output_dirname_var.get() + '/' + os.path.splitext(output_filename_var)[0] + '.tif'):
            execute = tkmb.askquestion("File Exists", 'The file ' + os.path.splitext(output_filename_var)[0] + '.tif exists in this location (this file will be overwritten!).  Do you want to continue?', icon='warning',default='no')
        
        if execute == 'yes':
            if sys.platform == "win32" or sys.platform == "win64":                # If windows
                if not os.path.exists(os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Commands'):
                    os.makedirs(os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Commands')
                fname = os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Commands/' + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + '.bat'
                f1=open(fname, 'w+')
                f1.write(self.command.get(1.0,tk.END))
                f1.write('pause')
                f1.close()
                subprocess.Popen(fname, creationflags = subprocess.CREATE_NEW_CONSOLE)
                time.sleep(1)
                #os.remove(fname)
            elif sys.platform == "darwin":      # If mac
                if not os.path.exists(os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Commands'):
                    os.makedirs(os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Commands')
                fname = os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Commands/' + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + '.sh'
                f1=open(fname, 'w+')
                f1.write('cd "$(dirname "$0")"\n')
                f1.write(self.command.get(1.0,tk.END))
                f1.close()
                print 'osascript -e \'tell application "Terminal" to do script "sh ' + fname + '"\''
                os.system('osascript -e \'tell application "Terminal" to do script "sh ' + fname + '"\'')
                time.sleep(1)
            elif sys.platform == "linux" or sys.platform == "linux2":   # If linux
                cmd = "xterm -hold -e '" + self.command.get(1.0,tk.END) + "'"
                print(cmd)
                subprocess.Popen(cmd,shell=True)
          
    def t_srs_set(self,sv):
        self.t_srs_check.set(1)
        
    def bounds_set(self,sv):
        self.bounds_check.set(1)
        
    def scale_set(self,sv):
        self.scale_check.set(1)
        
    def res_set(self,sv):
        self.res_check.set(1)
        
    def open_input_dialog(self):
        filename = tkfd.askopenfilename(initialdir=self.initialdir,title = "Select file")
        if filename != '':
            self.initialdir = os.path.dirname(filename)
        self.input_filename_var.set(filename)
        
    def open_output_directory_dialog(self):
        filename = tkfd.askdirectory(initialdir=self.initialdir,title = "Select directory")
        if filename != '':
            self.initialdir = filename
        self.output_dirname_var.set(filename)
        
    def open_clr_dialog(self):
        filename = tkfd.askopenfilename(initialdir=self.initialdir,title = "Select file")
        if filename != '':
            self.initialdir = os.path.dirname(filename)
        self.clr_filename_var.set(filename)
        self.clr_check.set(1)
        
    def open_shp_dialog(self):
        filename = tkfd.askopenfilename(initialdir=self.initialdir,title = "Select file")
        if filename != '':
            self.initialdir = os.path.dirname(filename)
        self.shp_filename_var.set(filename)
        self.shp_check.set(1)
        
    def open_bg_dialog(self):
        filename = tkfd.askopenfilename(initialdir=self.initialdir,title = "Select file")
        if filename != '':
            self.initialdir = os.path.dirname(filename)
        self.bg_filename_var.set(filename)
        self.bg_check.set(1)
        
    def open_kmz_overlay_dialog(self):
        filename = tkfd.askopenfilename(initialdir=self.initialdir,title = "Select file")
        if filename != '':
            self.initialdir = os.path.dirname(filename)
        self.kmz_overlay_filename_var.set(filename)
    
    def open_kml_server_preview_directory_dialog(self):
        filename = tkfd.askdirectory(initialdir=self.initialdir,title = "Select directory")
        if filename != '':
            self.initialdir = filename
        self.kml_server_preview_directory_var.set(filename)
                           
    def update_preprocess_cmd(self): 
    
        if not self.input_filename_var.get() == '' and not self.output_dirname_var.get() == '' and not self.output_filename_var.get() == '':
        
            if self.outputs_var.get() == 'RGB-JPEG' or self.outputs_var.get() == 'RGB-GIS':
                cmd = 'python "' + os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Prepare/generate_tif.py"'
            else:
                cmd = 'python "' + os.path.dirname(os.path.realpath(__file__).replace('\\','/')) + '/Prepare/generate_static_tiles.py"'
                
            if self.clr_check.get() == 1:
                if not self.clr_filename_var.get() == '':
                    cmd += ' --clrfile "' + self.clr_filename_var.get().replace('\\','/') + '"'
                    if self.colormode_var.get() == 'exact':
                        cmd += ' --ExactColorEntry'
                    elif self.colormode_var.get() == 'nearest':
                        cmd += ' --NearestColorEntry'
                        
            if self.shp_check.get() == 1:
                if not self.shp_filename_var.get() == '':
                    cmd += ' --shpfile "' + self.shp_filename_var.get().replace('\\','/') + '"'
                    if self.shp_invert_check.get():
                        cmd += ' --outsideMask'
                        
            if self.bg_check.get() == 1:
                if not self.bg_filename_var.get() == '':
                    cmd += ' --bgfile "' + self.bg_filename_var.get().replace('\\','/') + '"'
                    cmd += ' --blend ' + str(float(self.bg_blend_var.get())/100)
                        
            if self.outputs_var.get() == 'MBTiles':
                if self.basetiff_mbtiles_check.get() == 1:
                    cmd += ' --SaveTiff'
                cmd += ' --FType ' + self.tiletype_mbtiles.get()
                
            if self.outputs_var.get() == 'KMZ':
                if self.basetiff_kmz_check.get() == 1:
                    cmd += ' --SaveTiff'
                   
            if self.t_srs_check.get() == 1:
                if not self.t_srs_var.get() == '':
                    cmd += ' --t_srs "' + self.t_srs_var.get() + '"'
            if self.bounds_check.get() == 1:
                if not self.bounds_xmin_var.get() == '' and not self.bounds_xmin_var.get() == '' and not self.bounds_xmax_var.get() == '' and not self.bounds_ymin_var.get() == '' and not self.bounds_ymax_var.get() == '': 
                    cmd += ' --te "' + self.bounds_xmin_var.get() + ' ' + self.bounds_ymin_var.get() + ' ' + self.bounds_xmax_var.get() + ' ' + self.bounds_ymax_var.get() + '"'
            if self.res_check.get() == 1:
                    if not self.res_xres_var.get() == '' and not self.res_yres_var.get() == '':
                        cmd += ' --tr "' + self.res_xres_var.get() + ' ' + self.res_yres_var.get() + '"'
                
            if self.zoom_check.get() == 1:
                    if not self.zoom_minz_var.get() == '' and not self.zoom_maxz_var.get() == '':
                        cmd += ' --Zoom "' + self.zoom_minz_var.get() + ' ' + self.zoom_maxz_var.get() + '"'
            cmd += ' --resample ' + self.resample_var.get()
                
            if self.outputs_var.get() == 'RGB-GIS':
                cmd += ' --GISOptimizedImage'
            
            if self.outputs_var.get() == 'KMZ':
                if not self.kmz_overlay_filename_var.get() == '':
                    cmd += ' --overlayName "' + self.kmz_overlay_filename_var.get() + '"'
            
            output_filename_var = self.output_filename_var.get()
            if (self.outputs_var.get() == 'RGB-JPEG' or self.outputs_var.get() == 'RGB-GIS') and not (output_filename_var[-4:].lower() == '.tif'):
                output_filename_var += '.tif'
            if self.outputs_var.get() == 'MBTiles' and not (output_filename_var[-4:].lower() == '.mbtiles'):
                output_filename_var += '.mbtiles'
            if self.outputs_var.get() == 'KMZ' and not (output_filename_var[-4:].lower() == '.kmz'):
                output_filename_var += '.kmz'
                
            cmd += ' "' + self.input_filename_var.get().replace('\\','/') + '"'
            cmd += ' "' + self.output_dirname_var.get().replace('\\','/') + '/' + output_filename_var + '"'
           
        else:
            cmd = 'Must specify at least an input file and an output folder!'
            
        self.command.config(state="normal")
        self.command_var = cmd
        self.command.delete('1.0', tk.END)
        self.command.insert(tk.INSERT,self.command_var)
        self.command.config(state="disabled")
        
        if cmd == 'Must specify at least an input file and an output folder!' or cmd == 'For QGIS Files, must specify Layer Names and all fields related to projection, bounds, and resolution!':
            self.command_button.config(state="disabled")
        else:
            self.command_button.config(state="normal")
        
        
Tiler()
