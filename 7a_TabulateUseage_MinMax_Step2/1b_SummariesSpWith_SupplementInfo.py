import pandas as pd
import arcpy
import datetime
import os

in_directory_csv = r'L:\ESA\Results_Usage\L48\Range\Agg_Layers'
out_path = r'L:\ESA\Tabulates_Usage\L48\Range\Agg_Layers'
in_directory_grids = r'L:\ESA\UnionFiles_Winter2018\Range\SpComp_UsageHUCAB_byProjection_2' \
                     r'\Grid_byProjections_Combined'
look_up_fc_ab = r'L:\ESA\UnionFiles_Winter2018\Range\R_Clipped_Union_CntyInter_HUC2ABInter_20180612.gdb'
look_up_fc = r'L:\ESA\UnionFiles_Winter2018\Range\R_Clipped_Union_20180110.gdb'


elevation_adjustments = r'L:\ESA\UnionFiles_Winter2018\input tables\Elevation_Summary_test.csv'
habitat_adjustment_path = r'L:\ESA\UnionFiles_Winter2018\input tables'

skip_species = [u'r_amphib', u'r_birds', u'r_clams', u'r_flower', u'r_fishes', u'r_mammal', u'r_conife']

habitat_dict = {'AK': 'AK_Species_habitat_classes_20180624_test.csv',
                'AS': 'AS_Species_habitat_classes_20180624_test.csv',
                'CNMI': 'CNMI_Species_habitat_classes_20180624_test.csv',
                'CONUS': 'CONUS_Species_habitat_classes_20180624_test.csv',
                'GU': 'GU_Species_habitat_classes_20180624_test.csv',
                'HI': 'HI_Species_habitat_classes_20180624_test.csv',
                'PR': 'PR_Species_habitat_classes_20180624_test.csv',
                'VI': 'VI_Species_habitat_classes_20180624_test.csv'}

arcpy.env.workspace = look_up_fc
list_fc = arcpy.ListFeatureClasses()
arcpy.env.workspace = look_up_fc_ab
list_fc_ab = arcpy.ListFeatureClasses()
list_dir = os.listdir(in_directory_csv)

grid_folder_lookup = {'AK': 'AK_WGS_1984_Albers',
                      'AS': 'AS_WGS_1984_UTM_Zone_2S',
                      'CNMI': 'CNMI_WGS_1984_UTM_Zone_55N',
                      'CONUS': 'CONUS_Albers_Conical_Equal_Area',
                      'GU': 'GU_WGS_1984_UTM_Zone_55N',
                      'HI': 'HI_NAD_1983_UTM_Zone_4N',
                      'PR': 'PR_Albers_Conical_Equal_Area',
                      'VI': 'VI_WGS_1984_UTM_Zone_20N'}


def melt_df(df_melt):
    cols = df_melt.columns.values.tolist()
    id_vars_melt = []  # other columns (non EntityID columns)
    val_vars = []  # columns with EntityID
    for k in cols:
        val_vars.append(k) if type(k) is long else id_vars_melt.append(k)
    df_melt_row = pd.melt(df_melt, id_vars=id_vars_melt, value_vars=val_vars, var_name='melt_var',
                          value_name='EntityID')
    df_melt_row['EntityID'].fillna('None', inplace=True)
    df_melt_row = df_melt_row.loc[df_melt_row['EntityID'] != 'None']
    df_melt_row.drop('melt_var', axis=1, inplace=True)

    numeric_cols = []
    group_cols = []

    for r in df_melt_row.columns.values.tolist():
        if r.startswith('VALUE'):
            numeric_cols.append(r)
        else:
            group_cols.append(r)

    df_melt_row.ix[:, numeric_cols] = df_melt_row.ix[:, numeric_cols].apply(pd.to_numeric)

    sum_by_ent = df_melt_row.groupby(group_cols).sum()
    df_out = sum_by_ent.reset_index()

    return df_out


def parse_tables(in_table, in_row_sp, col_pre):
    # Sets data type and replaces extra characters found in the ZoneSpecies field do they are just separated by a comma
    in_table['ZoneID'] = in_table['ZoneID'].map(lambda y: y.replace(',', '')).astype(str)
    in_row_sp['ZoneSpecies'] = in_row_sp['ZoneSpecies'].apply(
        lambda d: d.replace('[', '').replace(']', '').replace('u', '').replace(' ', '').replace("'", ""))

    # EntityIDs in ZoneSpecies are split into their own columns, headers for these fields are number and can be id
    # as type(col) is long
    spl = in_row_sp['ZoneSpecies'].str.split(',', expand=True)
    # Adds the ZoneID field to the spl dataframes
    spl['ZoneID'] = in_row_sp['ZoneID'].map(lambda u: u.replace(',', '')).astype(str)
    # merges table to the split dataframe, now it is in the format needed for the melt
    merged_df = pd.merge(in_table, spl, on='ZoneID', how='left')
    # drops extra columns from the merged tables

    for q in merged_df.columns.values.tolist():
        if type(q) is long or q in col_pre or q.startswith('VALUE'):
            pass
        else:
            merged_df.drop(q, axis=1, inplace=True)

    out_df = melt_df(merged_df)
    return out_df


def merge_to_hucid(table_lookup, spe_table, spe_cols, id_cols, join_col):
    for z in id_cols:
        table_lookup[z] = table_lookup[z].map(lambda t: str(t).split('.')[0]).astype(str)

    table_lookup = table_lookup[table_lookup[join_col].isin(spe_table[spe_cols].values.tolist())]
    merg_table = pd.merge(spe_table, table_lookup, on=join_col, how='left')
    zones_in_table = merg_table['ZoneID'].values.tolist()
    return merg_table, zones_in_table


def adjust_elevation (out_df, adjust_path, out_csv, next_csv):
    # Adjust for elevation based on elevation input files
    if not os.path.exists(out_csv):
        dem_col = [v for v in out_df.columns.values.tolist() if v.startswith('dem')]
        out_df[dem_col[0]] = out_df[dem_col[0]].map(lambda w: w).astype(int)
        adjust_df = pd.read_csv(adjust_path)
        adjust_df['EntityID'] = adjust_df['EntityID'].map(lambda r: r).astype(str)
        sp_to_adjust = adjust_df['EntityID'].values.tolist()
        e_working = out_df.loc[~out_df['EntityID'].isin(sp_to_adjust)]
        e_adjust = out_df.loc[out_df['EntityID'].isin(sp_to_adjust)]

        for v in sp_to_adjust:
            if v in e_adjust['EntityID'].values.tolist():
                min_v = adjust_df.loc[(adjust_df['EntityID'] == v, 'Min Elevation GIS')].iloc[0]
                max_v = adjust_df.loc[(adjust_df['EntityID'] == v, 'Max Elevation GIS')].iloc[0]
                w_df = e_adjust.loc[(e_adjust['EntityID'] == v) & (e_adjust[dem_col[0]] <= int(max_v)) & (
                    e_adjust[dem_col[0]] >= int(min_v))]
                e_working = pd.concat([e_working, w_df])
        e_h_working = e_working.copy()
        out_col = ['EntityID']
        [out_col.append(i) for i in out_df.columns.values.tolist() if i.startswith('VALUE')]
        out_col.remove('VALUE')
        out_ele = e_working[out_col]
        out_ele = (out_ele.groupby('EntityID').sum()).reset_index()
        out_ele.to_csv(out_folder + os.sep + csv.replace('.csv', '_adj_Ele.csv'))
        print ('  Created {0}'.format(out_folder + os.sep + csv.replace('.csv', '_adj_Ele.csv')))
        return e_h_working
    else:
        print ('  Already created {0}'.format(out_csv))

        dem_col = [v for v in out_df.columns.values.tolist() if v.startswith('dem')]
        out_df[dem_col[0]] = out_df[dem_col[0]].map(lambda w: w).astype(int)
        adjust_df = pd.read_csv(elevation_adjustments)
        adjust_df['EntityID'] = adjust_df['EntityID'].map(lambda r: r).astype(str)
        sp_to_adjust = adjust_df['EntityID'].values.tolist()
        e_working = out_df.loc[~out_df['EntityID'].isin(sp_to_adjust)]
        e_adjust = out_df.loc[out_df['EntityID'].isin(sp_to_adjust)]

        for v in sp_to_adjust:
            if v in e_adjust['EntityID'].values.tolist():
                min_v = adjust_df.loc[(adjust_df['EntityID'] == v, 'Min Elevation GIS')].iloc[0]
                max_v = adjust_df.loc[(adjust_df['EntityID'] == v, 'Max Elevation GIS')].iloc[0]
                w_df = e_adjust.loc[(e_adjust['EntityID'] == v) & (e_adjust[dem_col[0]] <= int(max_v)) & (
                    e_adjust[dem_col[0]] >= int(min_v))]
                e_working = pd.concat([e_working, w_df])
        e_h_working = e_working.copy()
        e_h_working['EntityID'] = e_h_working['EntityID'].map(lambda b: b).astype(str)
        return e_h_working


def adjust_habitat(out_csv, adjust_path, out_df):
    # Adjusts for habitat based on habitat input file

    if not os.path.exists(out_csv):
        habitat_adjustment = adjust_path
        habitat_df = pd.read_csv(habitat_adjustment, dtype=object)
        sp_to_adjust_h = habitat_df.columns.values.tolist()
        hab_col = [v for v in out_df.columns.values.tolist() if v.startswith('Habit') or v.startswith(
            'gap') or v.startswith('2011')]
        out_df[hab_col[0]] = out_df[hab_col[0]].map(lambda t: t).astype(str)
        h_working = out_df.loc[~out_df['EntityID'].isin(sp_to_adjust_h)]
        h_adjust = out_df.loc[out_df['EntityID'].isin(sp_to_adjust_h)]

        for v in sp_to_adjust_h:
            if v in h_adjust['EntityID'].values.tolist():
                hab_cat = habitat_df[v].values.tolist()
                w_df = h_adjust.loc[(h_adjust['EntityID'] == v) & (h_adjust[hab_col[0]].isin(hab_cat))]
                h_working = pd.concat([h_working, w_df])
        out_col = ['EntityID']
        [out_col.append(i) for i in out_df.columns.values.tolist() if i.startswith('VALUE')]
        out_col.remove('VALUE')
        out_hab = h_working[out_col]
        out_hab = (out_hab.groupby('EntityID').sum()).reset_index()
        out_hab.to_csv(out_folder + os.sep + csv.replace('.csv', '_adj_Hab.csv'))
        print ('  Created {0}'.format(out_folder + os.sep + csv.replace('.csv', '_adj_Hab.csv')))
        return sp_to_adjust_h, habitat_df
    else:
        print ('  Already created {0}'.format(out_folder + os.sep + csv.replace('.csv', '_adj_Hab.csv')))
        habitat_adjustment = habitat_adjustment_path + os.sep + habitat_dict[region]
        habitat_df = pd.read_csv(habitat_adjustment, dtype=object)
        sp_to_adjust_h = habitat_df.columns.values.tolist()
        return sp_to_adjust_h, habitat_df


def adjust_elv_habitat(out_csv,  e_h_working, out_df, hab_sp_adjust, hab_df):
    # Adjusts for elevation and habitat based on input file
    if not os.path.exists(out_csv):
        e_h_working = e_h_working.loc[~e_h_working['EntityID'].isin(hab_sp_adjust)]
        e_h_adjust = e_h_working.loc[e_h_working['EntityID'].isin(hab_sp_adjust)]
        hab_col = [v for v in out_df.columns.values.tolist() if v.startswith('Habit') or v.startswith(
            'gap') or v.startswith('2011')]
        out_df[hab_col[0]] = out_df[hab_col[0]].map(lambda t: t).astype(str)
        for v in hab_sp_adjust:
            if v in e_h_adjust['EntityID'].values.tolist():
                hab_cat = hab_df[v].values.tolist()
                w_eh_df = e_h_adjust.loc[(e_h_adjust['EntityID'] == v) & (e_h_adjust[hab_col[0]].isin(hab_cat))]
                e_h_working = pd.concat([e_h_working, w_eh_df])
        out_col = ['EntityID']
        [out_col.append(i) for i in out_df.columns.values.tolist() if i.startswith('VALUE')]
        out_col.remove('VALUE')
        out_hab_ele = e_h_working[out_col]
        out_hab_ele = (out_hab_ele.groupby('EntityID').sum()).reset_index()
        out_hab_ele.to_csv(out_folder + os.sep + csv.replace('.csv', '_adj_EleHab.csv'))
        print ('  Created {0}'.format(out_folder + os.sep + csv.replace('.csv', '_adj_EleHab.csv')))
    else:
        print ('  Already created {0}'.format(out_folder + os.sep + csv.replace('.csv', '_adj_EleHab.csv')))


def export_aquatics(out_csv, out_df):
    # Export information needed for aquatic tables
    if not os.path.exists(out_csv):
        if ['VALUE_0'] in out_df.columns.values.tolist():
            val_col = ['EntityID', 'HUC2_AB','GEOID','STUSPS','VALUE_0']
        else:
            val_col = ['EntityID', 'HUC2_AB', 'GEOID', 'STUSPS']
        # [val_col.append(i) for i in out_df.columns.values.tolist() if i.startswith('VALUE')]
        # val_col.remove('VALUE')
        out_aqu =  out_df[val_col].copy()
        out_aqu['GEOID'] = out_aqu['GEOID'].map(lambda (n): n).astype(str)
        out_aqu['STATEFP'] = out_aqu['GEOID'] .map(lambda (n): str(n)[:2] if len(n) == 5 else '0' + n[:1]).astype(str)
        out_aqu.drop('GEOID', axis =1, inplace = True)
        if ['VALUE_0'] not in out_df.columns.values.tolist():
            out_aqu['VALUE_0'].map(lambda (n): 0).astype(str)
        out_aqu = (out_aqu.groupby(['EntityID', 'HUC2_AB', 'STUSPS','STATEFP']).sum()).reset_index()
        out_aqu.to_csv(out_folder + os.sep + csv.replace('.csv', '_HUC2AB.csv'))
        print ('  Created {0}'.format(out_csv))

start_time = datetime.datetime.now()
print "Start Time: " + start_time.ctime()

# Get date
today = datetime.datetime.today()
date = today.strftime('%Y%m%d')

if not os.path.exists(os.path.dirname(out_path)):
    os.mkdir(os.path.dirname(out_path))

if not os.path.exists(out_path):
    os.mkdir(out_path)
for folder in list_dir:
    print folder
    out_folder = out_path + os.sep + folder
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    # empty df for regional output habitat table

    region = folder.split('_')[0]  # extracts regions from folder title
    in_directory_species_grids = in_directory_grids + os.sep + grid_folder_lookup[region]  # path to region combine fld
    list_csv = os.listdir(in_directory_csv + os.sep + folder)  # list of csv in folder
    list_csv = [csv for csv in list_csv if csv.endswith('.csv')]  # list of att csvs
    # loops on each csv added the HUCIDs and ZoneIDs from parent fc att table to working dfs, then transforms table
    # so it is entityID by elevation or habitat
    for csv in list_csv:
        if csv.split("_")[0] + "_" + csv.split("_")[1] in skip_species:
            continue
        else:
            if not os.path.exists(out_folder + os.sep + csv):
                print ("   Working on {0}...table {1} of {2}".format(csv, (list_csv.index(csv) + 1), len(list_csv)))
                # parent fc att table with all input ID field (list_fc_ab) and ZoneID and associated EntityID (list_fc)
                # for species listed in the csv title
                par_zone_fc = [j for j in list_fc_ab if
                               j.startswith(
                                   os.path.basename(look_up_fc).split("_")[0] + "_" + csv.split("_")[1].title())]
                zone_fc = [j for j in list_fc if
                           j.startswith(os.path.basename(look_up_fc).split("_")[0] + "_" + csv.split("_")[1].title())]
                # converts att from species fc with ZoneID and association entityID  to dfs
                zone_array = arcpy.da.TableToNumPyArray(look_up_fc + os.sep + zone_fc[0], ['ZoneID', 'ZoneSpecies'])
                sp_zone_df = pd.DataFrame(data=zone_array, dtype=object)
                sp_zone_df['ZoneID'] = sp_zone_df['ZoneID'].map(lambda f: str(f).split('.')[0]).astype(str)

                # reads in csv to df for species and the parent raster attribute table for species
                spe_att = pd.read_csv(
                    in_directory_species_grids + os.sep + csv.split("_")[0] + "_" +
                    csv.split("_")[1] + '_att.csv')
                spe_att['VALUE'] = spe_att['VALUE'].map(lambda n: str(n).split('.')[0]).astype(str)
                c_csv = pd.read_csv(in_directory_csv + os.sep + folder + os.sep + csv)
                c_csv['VALUE'] = c_csv['VALUE'].map(lambda k: str(k).split('.')[0]).astype(str)

                # reads in the desire col headers from the look up raster df (raster col header have a limited number
                # of characters) for the parent attribute table
                col_header = pd.read_csv(in_directory_species_grids + os.sep + csv.split("_")[0] + "_" +
                                         csv.split("_")[1] + '_lookup_rasters.csv')
                # makes a list of the current col headers, and if they need be updated based on the look up table
                # then makes the update
                spe_col = spe_att.columns.values.tolist()
                update_col = []

                for col in spe_col:
                    if col in col_header['Default output header'].values.tolist():
                        new_col = \
                            col_header.loc[col_header['Default output header'] == col, 'Desired output header'].iloc[
                                0]
                        update_col.append(new_col)
                    else:
                        update_col.append(col)
                spe_att.columns = update_col

                # merges the current output file to the parent raster attribute table : HUCID value that can
                # then be joined back to extract state/cnties and species information
                merge_combine = pd.merge(c_csv, spe_att, on='VALUE', how='left')

                # find HUCID parent column ds), col header will be species raster name from parent raster att,
                # set dtype to str
                parent_id_col = [v for v in merge_combine.columns.values.tolist() if
                                 v.startswith('ch_') or v.startswith('r_')]
                merge_combine[parent_id_col[0]] = merge_combine[parent_id_col[0]].map(
                    lambda g: str(g).split('.')[0]).astype(str)
                col_prefix = []

                for i in update_col:
                    if i in ['OID', 'VALUE', 'COUNT', parent_id_col[0]]:
                        pass
                    else:
                        col_prefix.append(i)

                # add col HUCID mirror from the species parent column in table needed for join
                merge_combine['HUCID'] = merge_combine[parent_id_col[0]].map(lambda z: str(z).split('.')[0]).astype(str)

                # converts att from species input intersect fc, with all ID field, into df, captures the
                # ZoneID, InterID and HUCID to be joined to working table
                par_zone_array = arcpy.da.TableToNumPyArray(look_up_fc_ab + os.sep + par_zone_fc[0],
                                                            ['ZoneID', 'InterID', 'HUCID', 'GEOID', 'STUSPS', 'Region',
                                                             'HUC2_AB'])
                par_zone_df = pd.DataFrame(data=par_zone_array, dtype=object)
                for x in ['GEOID', 'STUSPS', 'Region', 'HUC2_AB']:
                    col_prefix.append(x)
                # merges working table with HUCID field
                merge_par, sp_zones = merge_to_hucid(par_zone_df, merge_combine, 'HUCID', ['ZoneID', 'HUCID'], 'HUCID')
                try:
                    # Filter so on the zone from the current use table is in the working df
                    # filters parent species lookup table from FC to just the zones in current table
                    c_sp_zone_df = sp_zone_df[sp_zone_df['ZoneID'].isin(sp_zones)]
                    # merges working table with the EntityID from parent lookup table based on the ZoneID
                    out_sp_table = parse_tables(merge_par, c_sp_zone_df, col_prefix)
                    out_sp_table.to_csv(out_folder + os.sep + csv)
                    print ('  Created {0}'.format(out_folder + os.sep + csv))
                except:
                    print 'Failed on {0}'.format(csv)
                    continue
            else:
                print ('  Already created {0}'.format(out_folder + os.sep + csv))
                out_sp_table = pd.read_csv(out_folder + os.sep + csv)
                out_sp_table['EntityID'] = out_sp_table['EntityID'].map(lambda b: b).astype(str)
            # if not os.path.exists(out_folder + os.sep + csv.replace('.csv', '_HUC2AB.csv')):
            export_aquatics(out_folder + os.sep + csv.replace('.csv', '_HUC2AB.csv'), out_sp_table)
            if region != 'AK':
                if not os.path.exists( out_folder + os.sep + csv.replace('.csv', '_adj_Ele.csv')):
                    elev_hab_working = adjust_elevation(out_sp_table, elevation_adjustments, out_folder + os.sep +
                                                        csv.replace('.csv', '_adj_Ele.csv'), out_folder + os.sep +
                                                        csv.replace('.csv', '_adj_Hab.csv'))
                if not os.path.exists(out_folder + os.sep + csv.replace('.csv', '_adj_EleHab.csv')):
                    elev_hab_working = adjust_elevation(out_sp_table, elevation_adjustments, out_folder + os.sep +
                                                        csv.replace('.csv', '_adj_Ele.csv'), out_folder + os.sep +
                                                        csv.replace('.csv', '_adj_Hab.csv'))
                if not os.path.exists(out_folder + os.sep + csv.replace('.csv', '_adj_Hab.csv')) :
                    hab_sp_adjust, hab_df = adjust_habitat(out_folder + os.sep + csv.replace('.csv', '_adj_Hab.csv'),
                                                            habitat_adjustment_path + os.sep + habitat_dict[region], out_sp_table)
                if not os.path.exists(out_folder + os.sep + csv.replace('.csv', '_adj_EleHab.csv')):
                    hab_sp_adjust, hab_df = adjust_habitat(out_folder + os.sep + csv.replace('.csv', '_adj_Hab.csv'),
                                                           habitat_adjustment_path + os.sep + habitat_dict[region], out_sp_table)
                if not os.path.exists(out_folder + os.sep + csv.replace('.csv', '_adj_EleHab.csv')):
                    adjust_elv_habitat(out_folder + os.sep + csv.replace('.csv', '_adj_EleHab.csv'),
                                       elev_hab_working, out_sp_table, hab_sp_adjust, hab_df)




end = datetime.datetime.now()
print "End Time: " + end.ctime()
elapsed = end - start_time
print "Elapsed  Time: " + str(elapsed)

# # except Exception as error:

#             # try:
#             #     print('Error was {0} for {1}'.format(error.args[0], csv))
#             # except:
#             #     pass