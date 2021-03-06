import arcpy
import os
import datetime

# Tile: Checks for species with duplicate files in spatial library; this indicated that files has been updated, or a
# species has two files that need to be merged

### Make sure all commas are removed the get accurate results!
# User input variable
# input table
masterlist = 'J:\Workspace\ESA_Species\ForCoOccur\Documents_FinalBE\MasterListESA_June2016_20160725.csv'
# in spatial library
infolder = 'J:\Workspace\ESA_Species\Range\NAD83'


# #########Functions
# recursively checks workspaces found within the inFileLocation and makes list of all feature class
def fcs_in_workspace(workspace):
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses():
        yield (fc)
    for ws in arcpy.ListWorkspaces():
        for fc in fcs_in_workspace(ws):
            yield fc

# generates a list of sp groups from masterlist
def get_group_list(master_list):
    grouplist = []
    with open(master_list, 'rU') as inputFile:
        header = next(inputFile)
        for line in inputFile:
            line = line.split(',')
            group = line[7]
            grouplist.append(group)
    inputFile.close()

    unq_grps = set(grouplist)
    sorted_group = sorted(unq_grps)
    print sorted_group
    del header, grouplist
    return sorted_group
start_time = datetime.datetime.now()
print "Start Time: " + start_time.ctime()


alpha_group = get_group_list(masterlist)

duplicate_files =[]
for group in alpha_group:

    print "\nWorking on {0}".format(group)
    group_gdb = infolder + os.sep + str(group) + '.gdb'

    arcpy.env.workspace = group_gdb
    fclist = arcpy.ListFeatureClasses()
    entlist_fc = []

    for fc in fclist:
        entid = fc.split('_')
        entid = str(entid[1])
        counter = 0
        if entid not in entlist_fc:
            entlist_fc.append(entid)
            counter += 1
            continue
        else:
            print 'Species {0} has a duplicate file'.format(entid)
            duplicate_files.append(entid)

print 'Species {0} has a duplicate file'.format(duplicate_files)

end = datetime.datetime.now()
print "End Time: " + end.ctime()

elapsed = end - start_time
print "Elapsed  Time: " + str(elapsed)

