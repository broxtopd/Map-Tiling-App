# Map-Tiling-App
This application automates GIS workflows (using a combination of python-gdal scripts and gdal utility programs) to create 
tiled maps from raster data.  It accepts as input any GDAL supported raster dataset, and has limited ability to process the 
data for display (e.g. colorizing the data with a colorfile, masking the data using a shapefile, or blending with a second 
dataset).  As output, it can create both jpeg-compressed tiff images (ideal for image processing), LZW-compressed tiff images 
(ideal for use with GIS), MBTiles file (can be used with a web tile image server, or as an offline map on a mobile device), 
or a KMZ (superoverlay) for Google Earth.

These functions require that GDAL and a python distribution with GDAL bindings are installed and accessable via the command line.  


Once the dependencies are installed, double click the 'start_program.bat' (Windows) or 'start_program.sh' (Linux)

Example 1 (Simplest Usage): 
- Next to "Input Dataset", click "Choose a file...", and choose "DEMO/Geology/Geology.tif"
- Under "Outputs", select "Create Google Earth KMZ file"
- Finally, under "Output File", click "Choose a directory", navigate to a directory where you will put the output file, 
  (suggest 'DEMO/Output') and next to "Filename", give it a name.
  Note that in the output directory, a working directory with the same name as "Filename" will be created, so make sure this 
  doesn't conflict with anything already there.  Here, call the output file "Geology"
- Click "Start!".  This will open a command window that executes the workflow.  Note that when enough information has been entered, 
  a python command will be generated.  This command can be used as a template to be used in another script.  To close the command 
  window, simply hit return (it should say "DONE CREATING TILES")  

This will open up a new terminal window and a bunch of commands will be executed to build the resulting map.  Be patient with large datasets
because this process involves many steps (including reprojection, tiling, and optionally coloring the maps, merging with other maps, and 
clipping the map data with shapefiles, etc

- Find the output file, double click it to open in "Google Earth", and inspect the result

Alternative 1 (Add a background file):
- Go back to the map tiling application
- Click "Include Background File", and choose "DEMO/Geology/Hillshade.tif"
- Click Start.  For now, we can overwrite the previous file that we created, but you can give the file a new name if you want
- Inspect the map

Alternative 2 (Get bounds from another file):
- In the map tiling application, click 'Get Info from Georeferenced File'.  
- Under the 'Files of Type' dropdown, select 'Vector File Types', and choose "DEMO/Geology/VCNP_Boundary.shp".  This will populate the 
  projection and bounds fields.  Note that if you had selected a raster file instead, it would have also populated the resolution field
- Click Start and Inspect the map

Alternative 3 (Mask with a Shapefile):
- Go back to the map tiling application
- Click "Mask with a Shapefile", and choose "DEMO/Geology/VCNP_Boundary.shp", - note that by default, everything outside
  of a shapefile feature is masked, inverting the mask causes everything inside of the feature to be masked.  For now, we want
  the default behavior (don't check 'Invert Mask')
- Click Start.
- Inspect the map

Example 2 (Colorized Snow Raster Map):
- For "Input Dataset", choose "DEMO/Snow/Snow_Depth.tif"
- For "Colorize the Input File", choose "DEMO/Cragin_Snow/snow.clr".  Note that ArcGIS .clr files must be used to provide the colormap.
  They can be created from QGIS style files by clicking on "Create CLR from QML", and navigating to a .qgs file (the .clr file will be 
  created in the same directory).  You will have to indicate the color interpolation mode manually (choose either interpolated - for a smooth
  color ramp, exact, or nearest.
- Uncheck "Mask with a Shapefile"
- For "Include Background File", choose "DEMO/Snow/Canopy_Hillshade.tif"
- Call the output file "Snow"
- Also, next to "Create Google Earth KMZ, we want to add a legend.  Click "Choose overlay..." and choose "DEMO/Snow/Snow_Depth_Colorbar.png"
- For now, uncheck "Reproject Map" and "Adjust Bounds" as we don't want to subset or reproject the data
- Click Start and Inspect the map

Alternative 1 (Add Overzoom)

Note that the maps appear fuzzy when zoomed in.  This is because map tiles for higher zoom levels than specified by a datasets resolution are not
created by default.  We can override this behavior by specifying zoom levels to create.

- In the Map Tiling Application, check "Adjust Zoom" and enter 12 for "MinZoom" and 19 for "MaxZoom"
- Click Start and Inspect the map.  Note that the tiling portion of the workflow will take much longer as we are creating many more map tiles.

Now, the map displays the same data, but the pixel boundaries appear to be more defined

Alternative 2 (create a mbtiles file):

So far, we have created files that are viewable in Google Earth.  This is useful for learning the process involved in the creation of the tiled maps
but we can also create geotiffs to be viewed in GIS applications ("LZW-compressed tiff"), image processing applications ("JPEG-compressed tiff"), 
or as tiled maps for web map viewers or for mobile devices.  Here, we will create a .mbtiles file.

- In the Map Tiling Application, select "Create mbtiles file".  Also, check "Keep Base Tiff" file.  This will keep a copy of the geotiff from which the tiles
  are generated

The .mbtiles file can be viewed using a computer application that can view this file type (e.g. QGIS), or it can be uploaded to a mobile device and viewed with
and offline map viewer such as Galileo.  Note that the .mbtiles and .tif files can also be used for a web map image server.





 
