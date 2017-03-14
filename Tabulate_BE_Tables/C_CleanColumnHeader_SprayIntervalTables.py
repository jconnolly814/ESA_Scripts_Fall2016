import pandas as pd
import datetime
import os

in_table = r'L:\Workspace\ESA_Species\Step3\ToolDevelopment\TerrestrialGIS\Tabulated_NewComps\NL48\Range\R_NL48_SprayInterval_20170209_All.csv'
outlocation = 'L:\Workspace\ESA_Species\Step3\ToolDevelopment\TerrestrialGIS\Tabulated_NewComps\L48\FinalTables_Range\MagTool'
out_csv = outlocation + os.sep + 'R_NL48_MagTool_SprayDrift_20170209_clean.csv'

master_list = 'C:\Users\JConno02\Documents\Projects\ESA\MasterLists\MasterListESA_June2016_20170216.xlsx'

master_col = ['EntityID', 'Group', 'comname', 'sciname', 'status_text', 'Des_CH', 'CH_GIS',
              'Source of Call final BE-Range', 'WoE Summary Group', 'Source of Call final BE-CriticalHabitat']

regions = ['AK', 'GU', 'HI', 'AS', 'PR', 'VI', 'CNMI', 'AS', 'CONUS']

useLookup = {
    'Ag': 'Ag',
    'CattleEarTag': 'Cattle Eartag',
    'Developed': 'Developed',
    'ManagedForests': 'Managed Forests',
    'Nurseries': 'Nurseries',
    'OSD': 'Open Space Developed',
    'ROW': 'Right of Way',
    'Rangeland': 'Cattle Eartag',
    'NonCultivated': 'Non Cultivated',
    'OrchardsVineyards': 'Orchards and vineyards',
    'OtherCrops': 'Other Crops',
    'OtherGrains': 'Other Grains',
    'VegetablesGroundFruit': 'Vegetables and Ground Fruit',
    'Diazinon': 'Diazinon',
    'Carbaryl': 'Carbaryl',
    'Chlorpyrifos': 'Chlorpyrifos',
    'Methomyl': 'Methomyl',
    'Malathion': 'Malathion',
    'usa': 'Golf Courses',
    'CCAP': 'Non Cultivated',
    'NLCD': 'Non Cultivated',
    'Alley Cropping': 'Alley Cropping',
    'Methomyl wheat': 'Methomyl wheat',
    'Vegetables and Ground Fruit': 'Vegetables and Ground Fruit',
    'Orchards and Vineyards': 'Orchards and Vineyards',
    'Other Grains': 'Other Grains',
    'Other RowCrops': 'Other RowCrops',
    'Other Crops': 'Other Crops',
    'Pasture': 'Pasture',
    'Corn': 'Corn',
    'Cotton': 'Cotton',
    'Rice': 'Rice',
    'Soybeans': 'Soybeans',
    'Wheat': 'Wheat',
    'Bermuda Grass': 'Bermuda Grass',
    'Cattle Eartag': 'Cattle Eartag',
    'Cull Piles': 'Cull Piles',
    'Cultivated': 'Cultivated',
    'Managed Forest': 'Managed Forests',
    'Golfcourses': 'Golfcourses',
    'Non Cultivated': 'Non Cultivated',
    'Open Space Developed': 'Open Space Developed',
    'Right of Way': 'Right of Way',
    'Pine seed orchards': 'Pine seed orchards',
    'Christmas Trees': 'Christmas Trees',
    'Managed Forests': 'Managed Forests',
    'usa':'Golfcourses',
    'Golf Courses':'Golfcourses',
    'zMethomylWheat':'zMethomylWheat',
    'Methomyl_footprint': 'Methomyl',
    'Chlorpyrifos_footprint': 'Chlorpyrifos',
    'Carbaryl_footprint':'Carbaryl',
    'Diazinon_footprint':'Diazinon',
    'Malathion_footprint':'Malathion'
}

start_time = datetime.datetime.now()
print "Start Time: " + start_time.ctime()

# master_list_df =  pd.read_csv(master_list)
master_list_df = pd.read_excel(master_list)
master_list_df = master_list_df.ix[:, master_col]
master_list_df ['EntityID'] = master_list_df ['EntityID'].map(lambda x: x).astype(str)
print master_list_df

in_df = pd.read_csv(in_table, dtype=object)
in_df['EntityID'] = in_df['EntityID'].map(lambda x: x).astype(str)
in_df_col = in_df.columns.values.tolist()

for col in in_df_col:
    if col.startswith('Acres'):
        in_df.drop(col, axis=1, inplace=True)
        print 'dropped: ' + col
    else:
        pass
in_df_col = in_df.columns.values.tolist()

col_reindex = ['EntityID']

for col in in_df_col:
    region = col.split("_")[0]
    if col in col_reindex:
        pass

    elif region in regions:
        split_col = col.split("_")
        use_value = col.split("_")[1]
        distance = col.split("_")[(len(split_col) - 1)]
        use = useLookup[use_value]
        new_col = region + '_' + use + "_" + distance
        col_reindex.append(new_col)
    else:
        in_df.drop(col, axis=1, inplace=True)
        print 'dropped: ' + col

in_df.columns = col_reindex
out_df = pd.merge( master_list_df ,in_df, on='EntityID', how='inner')
out_df.to_csv(out_csv)

end = datetime.datetime.now()
print "End Time: " + end.ctime()
elapsed = end - start_time
print "Elapsed  Time: " + str(elapsed)
