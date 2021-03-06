import arcpy
from simpledbf import Dbf5
import os
import functions

inFolder = r'L:\Workspace\ESA_Species\Step3\10417_Files\SETAC_results'
ws = r"L:\Workspace\ESA_Species\Step3\10417_Files\SETAC_results\Exported_results"
name_dir = "RawUse"
def createdirectory(DBF_dir):
    if not os.path.exists(DBF_dir):
        os.mkdir(DBF_dir)
        print "created directory {0}".format(DBF_dir)

File_dir = ws + os.sep + str(name_dir)
DBF_dir = File_dir + os.sep + 'DBF'
CSV_dir = File_dir + os.sep + 'CSV'
createdirectory(File_dir)
createdirectory(DBF_dir)
createdirectory(CSV_dir)

counter = 0

FolderList = os.listdir(inFolder)
print FolderList
FolderList =[gdb  for gdb in FolderList if gdb.endswith('gdb')]
for value in FolderList:
        folder,path =os.path.split(inFolder)
        value = value.replace('.gdb','')
        FinalGDB = inFolder + os.sep + value+ os.sep +value+'.gdb'
        print FinalGDB
        # print FinalGDB
        outfolder = DBF_dir + os.sep + value
        createdirectory(outfolder)

        arcpy.env.workspace=FinalGDB
        listtable = arcpy.ListTables()
        print listtable
        for table in listtable:
            try:
                print table
                counter += 1
                tableview = "tbl_view_" + str(counter)
                outtable = outfolder + os.sep + table+'.dbf'
                print outtable
                if not arcpy.Exists(outtable):
                    arcpy.MakeTableView_management(table, tableview)
                    arcpy.TableToTable_conversion(tableview, outfolder, table)
                else:
                    continue
            except:
                continue


        arcpy.env.workspace = outfolder
        files = arcpy.ListTables()
        outcsv = CSV_dir
        createdirectory(outcsv)
        outfoldercsv = CSV_dir + os.sep + value
        createdirectory(outfoldercsv)
        for f in files:
            if f[-3:].lower() == 'dbf':
                stripdbf = f.replace('.dbf','.csv')
                outtable = outfoldercsv + os.sep + stripdbf
                print outtable
                if os.path.exists(outtable):
                    continue
                intable = outfolder + os.sep + f
                dbf = Dbf5(intable)
                dbf.to_csv(outtable)
