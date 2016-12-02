import os
import csv
import datetime

import arcpy

# #Tile: Copy shapefiles to a geodatabase and rename to a standard naming convention.

# NOTE prior to running the NmChange check the the concatenated specode and vipcode on the FWS file name and the
# sci names match the master list.  Files were sometime received with typos

# TODO update so that check against the sci name and Concat codes are scripted
# TODO create the NmChange Dict dynamically from masters using Pandas

# Variables to be set by user
# Input File Locations
# Set the workspace for the ListFeatureClass function
#

InGDB = r""
abb = "FWS"  # FWS or NMFS


# Workspace
ws = "L:\NewFWS_RangesStep_20161017\FinalShapes"
# Folder in workspace where outputs will be saved
name_dir = "NewRanges_Step3_FWS_20161031"

# in yyyymmdd received date
receivedDate = '20161017'

# NOTE prior to running the NmChange check the the concatenated specode and vipcode on the FWS file name and the
# sci names match the master list.  Files were sometime received with typos

# #DICT for name change original file to EPA Std


NmChangeDICT = {'odo_vir_wtdec': 'R_4_GAP_20161017',
                'pan_onc_r_18': 'R_18_GAP_20161017',
                'mupdox_r_20': 'R_20_GAP_20161017',
                'per_lon_r_51': 'R_51_GAP_20161017',
                'tym_cup_grpca': 'R_83_GAP_20161017',
                'amp_bel_r_116': 'R_116_GAP_20161017',
                'str_occ_spowl': 'R_129_GAP_20161017',
                'vir_atr_bcvix': 'R_138_GAP_20161017',
                'den_chr_gcwax': 'R_139_GAP_20161017',
                'aph_coe_flsjx': 'R_140_GAP_20161017',
                'str_occ_142_r': 'R_142_GAP_20161017',
                'gam_sil_151': 'R_151_GAP_20161017',
                'reisnx': 'R_173_GAP_20161017',
                'uma_r_175': 'R_175_GAP_20161017',
                'pha_hub_r_192': 'R_192_GAP_20161017',
                'ple_she_r_200': 'R_200_GAP_20161017',
                'E070_V01_Hypomesus_transpacificus_new': 'R_305_poly_20161017',
                'bra_id_py_aoi': 'R_1240_GAP_20161017',
                'CountyRange_11260_poly_20161031': 'R_11260_CountyRange_20161017',
                'E088_V01_Spirinchus_thaleichthys_new': 'R_11262_poly_20161017',

                }


# recursively checks workspaces found within the inFileLocation and makes list of all feature class
def fcs_in_workspace(workspace):
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses():
        yield (fc)
    for ws in arcpy.ListWorkspaces():
        for fc in fcs_in_workspace(ws):
            yield (fc)


# creates directories to save files
def create_directory(path_dir, outLocationCSV, OutFolderGDB):
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)
        print "created directory {0}".format(path_dir)
    if not os.path.exists(outLocationCSV):
        os.mkdir(outLocationCSV)
        print "created directory {0}".format(outLocationCSV)
    if not os.path.exists(OutFolderGDB):
        os.mkdir(OutFolderGDB)
        print "created directory {0}".format(OutFolderGDB)


# creates date stamped generic file
def create_flnm_timestamp(namefile, outlocation, date_list, file_extension):
    file_extension.replace('.', '')
    filename = str(namefile) + "_" + str(date_list[0]) + '.' + file_extension
    filepath = os.path.join(outlocation, filename)
    return filename, filepath


# outputs table from list generated in create FileList
def create_out_table(list_name, csv_name):
    with open(csv_name, "wb") as output:
        writer = csv.writer(output, lineterminator='\n')
        for val in list_name:
            writer.writerow([val])


# Create a new GDB
def create_gdb(out_folder, out_name, outpath):
    if not arcpy.Exists(outpath):
        arcpy.CreateFileGDB_management(out_folder, out_name, "CURRENT")


# loops through inGDB and makes a copy of each file applying the std filename from the dict in outGDB
def StandName(InGDB, outFilegdbpath, outFilefailgdbpath):
    for fc in fcs_in_workspace(InGDB):
        try:
            dsc = arcpy.Describe(fc)
            sr = dsc.spatialReference
            prj = sr.name.lower()
            NewName = NmChangeDICT[fc]
            addSRList = str(fc) + "," + "Name: " + sr.name + "," + "Type: " + sr.type + "," + str(NewName)
            print addSRList
            OrgSRList.append(addSRList)
            outFeatureClass = os.path.join(outFilegdbpath, NewName)
            # print outFeatureClass
            if not arcpy.Exists(outFeatureClass):
                # print "FC does not exist"
                arcpy.CopyFeatures_management(fc, outFeatureClass)
            else:
                print" FC already exists"

        except:
            print "Failed  " + str(fc)
            addFailed = str(fc)
            FailedList.append(addFailed)
            outFailedFC = os.path.join(outFilefailgdbpath, addFailed)
            arcpy.CopyFeatures_management(fc, outFailedFC)


# static variable no user input needed unless changing code structure
datelist = []
today = datetime.date.today()
datelist.append(today)

OrgSRList = []
FailedList = []
addSRList = "Filename Original (GDB)" + "," + "Original Projection" + "," + "Original Projection Type" + "," + \
            "Standardize Filename"
OrgSRList.append(addSRList)
addFailed = "Filename-Original (GDB)"
FailedList.append(addFailed)

path_dir = ws + os.sep + str(name_dir)
outLocationCSV = path_dir + os.sep + "CSV"
OutFolderGDB = path_dir + os.sep + "GDB"

# Output File Names
ReNmCSVCopied = 'ReNm' + str(abb) + "_" + str(receivedDate)
out_nameGDB = "ReNm_" + str(abb) + "_" + str(receivedDate)
FailedGDB = "Failed_" + str(out_nameGDB)
ReNmCSVFailed = "Failed_" + str(ReNmCSVCopied)

# CREATES FILE NAMES
# CSV out table succeed and faile
csvfile, csvpath = create_flnm_timestamp(ReNmCSVCopied, outLocationCSV, datelist, 'csv')
failedcsv, failedcsvpath = create_flnm_timestamp(ReNmCSVFailed, outLocationCSV, datelist, 'csv')
# GDB succeed and faile
OutGDB, outFilegdbpath = create_flnm_timestamp(out_nameGDB, OutFolderGDB, datelist, 'gdb')
FailGDB, outFilefailgdbpath = create_flnm_timestamp(FailedGDB, OutFolderGDB, datelist, 'gdb')

arcpy.env.scratchWorkspace = ""
# NOTE Change this to False if you don't want GDB to be overwritten
arcpy.env.overwriteOutput = True

# Start script

# Copy shapefiles to a file geodatabase and rename

# start clock on timing script

start_time = datetime.datetime.now()
print "Start Time: " + start_time.ctime()

create_directory(path_dir, outLocationCSV, OutFolderGDB)

create_gdb(OutFolderGDB, OutGDB, outFilegdbpath)
create_gdb(OutFolderGDB, FailGDB, outFilefailgdbpath)
StandName(InGDB, outFilegdbpath, outFilefailgdbpath)

# ##write data store in lists to out tables in csv format
create_out_table(OrgSRList, csvpath)
create_out_table(FailedList, failedcsvpath)
# #End clock time script
end = datetime.datetime.now()
print "End Time: " + end.ctime()

elapsed = end - start_time
print "Elapsed  Time: " + str(elapsed)
