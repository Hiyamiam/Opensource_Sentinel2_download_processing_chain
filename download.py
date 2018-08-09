'''
Created on Mon Jul 02 10:55:17 2018
@author: Hiyam
'''
import snappy as sp
import os
import sys
import shutil
import tempfile
import pandas as pd
import numpy as np
import subprocess
import multiprocessing
from datetime import date
import easygui as eg
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
import re

# Define path to the grass7x.bat file
grass7bin_win = 'C:\\Program Files\\GRASS GIS 7.4.0\\grass74.bat'

## Define GRASS GIS environment variables
os.environ['GISBASE'] = 'C:\\Program Files\\GRASS GIS 7.4.0'
os.environ['PATH'] = 'C:\\Program Files\\GRASS GIS 7.4.0\\lib;C:\\Program Files\\GRASS GIS 7.4.0\\bin;C:\\Program Files\\GRASS GIS 7.4.0\\extrabin' + os.pathsep + os.environ['PATH']
os.environ['PATH'] = 'C:\\Program Files\\GRASS GIS 7.4.0\\etc;C:\\Program Files\\GRASS GIS 7.4.0\\etc\\python;C:\\Python27' + os.pathsep + os.environ['PATH']
os.environ['PATH'] = 'C:\\Program Files\\GRASS GIS 7.4.0\\Python27;C:\\Users\\hel-badri\\AppData\\Roaming\\GRASS7\\addons\\scripts' + os.pathsep + os.environ['PATH']
os.environ['PATH'] = 'C:\\Python27\\Lib' + os.pathsep + os.environ['PATH']
os.environ['PYTHONLIB'] = 'C:\\Python27'
os.environ['PYTHONPATH'] = 'C:\\Program Files\\GRASS GIS 7.4.0\\etc\\python'
os.environ['GIS_LOCK'] = '$$'
os.environ['GISRC'] = 'C:\\Users\\hel-badri\\AppData\\Roaming\\GRASS7\\rc'
os.environ['GDAL_DATA'] = 'C:\\Program Files\\GRASS GIS 7.4.0\\share\\gdal'

## Define the Grass-Python environment
sys.path.append(os.path.join(os.environ['GISBASE'], 'etc', 'python'))

## Add the R software directory to the general PATH
os.environ['PATH'] = 'C:\\Program Files\\R\\R-3.4.3\\bin' + os.pathsep + os.environ['PATH']

## Set R software specific environment variables
os.environ['R_HOME'] = 'C:\Program Files\R\R-3.3.0'
os.environ['R_ENVIRON'] = 'C:\Program Files\R\R-3.3.0\etc\x64'
os.environ['R_DOC_DIR'] = 'C:\Program Files\R\R-3.3.0\doc'
os.environ['R_LIBS'] = 'C:\Program Files\R\R-3.3.0\library'

# os.environ['R_LIBS'] ='C:\Users\hel-badri\Documents\R\win-library\3.4'
os.environ['R_LIBS_USER'] = 'C:\Users\hel-badri\Documents\R\win-library\\3.3'

# Display current enviroment variables of your computer
for key in os.environ.keys():
    print '%s = %s \t' % (key, os.environ[key])
import grass.script as grass
import grass.script.setup as gsetup

# Define functions
## Import library for managing time in python
import time

## Function "print_processing_time()" compute processing time and print it.
# The argument "begintime" wait for a variable containing the begintime (result of time.time()) of the process for which to compute processing time.
# The argument "printmessage" wait for a string format with information about the process.
def print_processing_time(begintime, printmessage):
    endtime = time.time()
    processtime = endtime - begintime
    remainingtime = processtime
    days = int((remainingtime) / 86400)
    remainingtime -= (days * 86400)
    hours = int((remainingtime) / 3600)
    remainingtime -= (hours * 3600)
    minutes = int((remainingtime) / 60)
    remainingtime -= (minutes * 60)
    seconds = round((remainingtime) % 60, 1)
    if processtime < 60:
        finalprintmessage = str(printmessage) + str(seconds) + " seconds"
    elif processtime < 3600:
        finalprintmessage = str(printmessage) + str(minutes) + " minutes and " + str(seconds) + " seconds"
    elif processtime < 86400:
        finalprintmessage = str(printmessage) + str(hours) + " hours and " + str(minutes) + " minutes and " + str(
            seconds) + " seconds"
    elif processtime >= 86400:
        finalprintmessage = str(printmessage) + str(days) + " days, " + str(hours) + " hours and " + str(
            minutes) + " minutes and " + str(seconds) + " seconds"
    return finalprintmessage


# # Download i.sentinel if not yet installed
# if "i.sentinel" not in grass.parse_command('g.extension', flags='a'):
#     grass.run_command('g.extension', extension='i.sentinel')
#     print 'i.sentinel have been installed on your computer'
# else:
#     print 'i.sentinel is already installed on your computer'

# Defining global variables
folder = 'F:\\snap\\sentinel'

# Choice of method
message_study = 'Which analysis do you wish to pursue ?'
choices_study = ['One image analysis', 'Time-series analysis']
title_study = "Choice of study"
choice_study = eg.choicebox(message_study, title_study, choices_study)
print choice_study

if choice_study == 'One image analysis':

    # Choice of cloud coverage and dates of acquisition
    msg = 'Which percentage of cloud coverage do you wish to acquire ?'
    choices = ['0', '5', '10', '15', '20', '25', '30']
    title = "Cloud coverage percentage"
    choice = eg.choicebox(msg, title, choices)
    date_begin = raw_input("Please enter the start date under the following form : year-month-day ")
    date_end = raw_input("Please enter the end date under the following form : year-month-day ")

    ## Saving current time for processing time management
    begintime_importingdata = time.time()
    print ("Importing sentinel data at " + time.ctime())

    grass.run_command('i.sentinel.download', flags='l', overwrite=True, settings='F:\\snap\\user.txt', clouds=choice,
                       output='F:\\snap\\sentinel', map='region_uspo@uspo', start=date_begin, end=date_end)

    print("Data downloading at " + time.ctime())
    print_processing_time(begintime_importingdata, "Data download achieved in ")

    # Deleting zip files
    for item in os.listdir(folder):
        if item.endswith(".zip"):
            os.remove(os.path.join(folder, item))

    msg = 'Which file do you wish to use for the processing chain ?'
    choices = os.listdir(folder)
    title = "Processing chain"
    choice = eg.choicebox(msg, title, choices)
    eg.msgbox("You chose: " + str(choice), "File")

    HashMap = sp.jpy.get_type('java.util.HashMap')
    sp.GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    source = sp.ProductIO.readProduct('F:\\snap\\sentinel\\' + choice)

    ## SEN2COR ATMOSPHERIC CORRECTIONS

    ## Saving current time for processing time management
    begintime_sen2cor = time.time()
    print ("Executing atmospheric corrections at " + time.ctime())

    # parameters = HashMap()
    # parameters.put('resolution', '10')
    # parameters.put('cirrusCorrection', 'TRUE')
    # correction = sp.GPF.createProduct("Sen2Cor", parameters, source)
    correction = sp.ProductIO.readProduct("F:\\snap\\sentinel\\S2B_MSIL2A_20180204T080119_N0206_R035_T36NVF_20180204T114614.SAFE")

    print("Sen2Cor finished processing at " + time.ctime())
    print_processing_time(begintime_sen2cor, "Data processing achieved in ")

    # If precedent step not working, uncomment following lines
    # cmd = 'L2A_Process' + choice + '--resolution=10'
    # os.system(cmd)

    # Moving Sen2Cor processed images to new folder for future time series use
    for item in os.listdir(folder):
        if item.find('MSIL2A') != -1:
            shutil.move("F:\\snap\\sentinel\\" + item,"F:\\snap\\preprocessed\\" + item)

    ## RESAMPLING

    ## Saving current time for processing time management
    begintime_resample = time.time()
    print ("Executing resampling at " + time.ctime())

    parameters = HashMap()
    parameters.put('targetResolution', '10')
    resample = sp.GPF.createProduct("Resample", parameters, correction)

    print("Image resampled at " + time.ctime())
    print_processing_time(begintime_resample, "Image resampling achieved in ")

    ## SUBSETTING
    # Extracting all interesting bands amongst the 12 Sentinel-2 bands
    bands = ''
    L = list(correction.getBandNames())
    bands_extracted = [i for i in L if i.startswith('B')]
    for i in range(len(bands_extracted)):
        bands += bands_extracted[i]
        bands += ','
    bands = bands[:-1]
    print bands

    begintime_subset = time.time()
    print ("Executing subset at " + time.ctime())

    parameters = HashMap()
    parameters.put('bandNames', bands)
    subset = sp.GPF.createProduct("Subset", parameters, resample)
    "Available bands for " + choice[11:19] + " are: " + list(subset.getBandNames())

    print("Image subsetting at " + time.ctime())
    print_processing_time(begintime_subset, "Image subset achieved in ")

    ## EXPORT

    begintime_export = time.time()
    print ("Executing export at " + time.ctime() + " for data from " + choice[11:19])

    export = sp.ProductIO.writeProduct(subset,'F:\\snap\\images\\' + choice[11:19], 'GeoTIFF')

    print("Image exporting finishing at " + time.ctime())
    print_processing_time(begintime_export, "Image from " + choice[11:19] + " export achieved in ")

else:

    """Supposing all "MSIL2A" files preprocessed are already stored in "preprocessed" file"""

    date_begin = raw_input("Please enter the start date under the following form : year-month-day ")
    date_end = raw_input("Please enter the end date under the following form : year-month-day ")

    ## Downloading Sentinel data without any cloud coverage specifications

    begintime_importingdata = time.time()
    print ("Importing sentinel data at " + time.ctime())

    grass.run_command('i.sentinel.download', flags='l', overwrite=True, settings='F:\\snap\\user.txt',output='F:\\snap\\sentinel', map='region_uspo@uspo', start=date_begin, end=date_end)

    print("Data downloading at " + time.ctime())
    print_processing_time(begintime_importingdata, "Data download achieved in ")

    # Deleting zip files
    for item in os.listdir(folder):
        if item.endswith(".zip"):
            os.remove(os.path.join(folder, item))

    HashMap = sp.jpy.get_type('java.util.HashMap')
    sp.GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    input_directory = 'F:\\snap\\preprocessed\\'

    # Sen2Cor processing for all images

    parameters = HashMap()
    parameters.put('resolution', '10')
    parameters.put('cirrusCorrection', 'TRUE')

    files_to_correct = 'F:\snap\sentinel'
    for i in os.listdir(files_to_correct):
        source = sp.ProductIO.readProduct('F:\\snap\\sentinel\\' + i)
        correction = sp.GPF.createProduct("Sen2Cor", parameters, source)

    # Moving Sen2Cor processed images to new folder
    for item in os.listdir(folder):
        if item.find('MSIL2A') != -1:
            shutil.move("F:\\snap\\sentinel\\" + item,"F:\\snap\\preprocessed\\" + item)

    # source = ''
    # for i in os.listdir(input_directory):
    #     item = str(sp.ProductIO.readProduct(input_directory + i))
    #     source += item
    #     source += ','
    # source = source[:-1]

    ## SEN2THREE

    ## Saving current time for processing time management
    begintime_resample = time.time()
    print ("Executing Sen2Three at " + time.ctime())

    parameters = HashMap()
    parameters.put('resolution', '10')
    parameters.put('targetProductFile', 'F:\\snap\\preprocessed')
    parameters.put('postExecuteTemplate', 'True')
    image = sp.GPF.createProduct('Sen2Three', parameters)

    print("Sen2Three executing at " + time.ctime())
    print_processing_time(begintime_resample, "Sen2Three processing achieved in ")

    ## Sen2Three stand-alone needs to be already installed in order for this line to execute correctly
    # import os
    # os.system('L3_Process F:\\snap\\preprocessed --resolution=10')

    # Moving Sen2Three processed image to new folder
    for item in os.listdir(input_directory):
        if item.find('MSIL03') != -1:
            shutil.move("F:\\snap\\preprocessed\\" + item,"F:\\snap\\sen2three\\" + item)

    """

    from snappy import GPF

    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    op_spi = GPF.getDefaultInstance().getOperatorSpiRegistry().getOperatorSpi('Sen2Three')
    print('Op name:', op_spi.getOperatorDescriptor().getName())
    print('Op alias:', op_spi.getOperatorDescriptor().getAlias())
    param_Desc = op_spi.getOperatorDescriptor().getParameterDescriptors()
    for param in param_Desc:
        print(param.getName(), "or", param.getAlias())
    """