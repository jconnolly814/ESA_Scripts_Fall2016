import pandas as pd
import os
import datetime

inFolder = r'L:\Workspace\ESA_Species\Step3\ToolDevelopment\TerrestrialGIS\Using_BE_Compfiles\Range\YearlyCDL_results\Collapse'
final_folder = r'L:\Workspace\ESA_Species\Step3\ToolDevelopment\TerrestrialGIS\Using_BE_Compfiles\Range\YearlyCDL_results\Final_Conus_Yearly'

species_nonconus = ['15', '16', '19', '23', '26', '78', '6522', '65', '4136', '93', '122', '74', '4237', '91', '5170',
                    '119', '121', '4889', '97', '112', '68', '69', '8386', '76', '108', '73', '82', '77', '64', '100',
                    '105', '70', '71', '10582', '118', '120', '148', '98', '11333', '81', '87', '109', '106', '114',
                    '1222', '72', '75', '99', '150', '79', '113', '127', '111', '80', '101', '128', '156', '162', '163',
                    '164', '165', '174', '177', '191', '193', '195', '196', '418', '446', '463', '485', '497', '499',
                    '518', '533', '535', '536', '537', '538', '545', '549', '560', '561', '563', '564', '565', '567',
                    '572', '575', '577', '581', '584', '589', '590', '591', '597', '598', '601', '602', '603', '604',
                    '605', '606', '616', '617', '618', '619', '621', '622', '623', '634', '635', '645', '646', '648',
                    '649', '650', '654', '659', '662', '664', '665', '671', '672', '673', '674', '684', '685', '686',
                    '687', '688', '690', '691', '692', '693', '697', '715', '717', '719', '720', '721', '722', '724',
                    '725', '726', '727', '728', '729', '731', '732', '733', '735', '736', '737', '738', '741', '745',
                    '746', '747', '755', '756', '757', '758', '759', '765', '766', '767', '768', '769', '770', '771',
                    '772', '773', '774', '775', '778', '779', '780', '781', '782', '788', '795', '799', '800', '801',
                    '806', '808', '810', '814', '815', '820', '821', '822', '829', '830', '832', '833', '838', '839',
                    '845', '846', '847', '848', '849', '850', '851', '860', '861', '862', '863', '864', '865', '866',
                    '867', '868', '869', '874', '882', '883', '890', '893', '894', '895', '896', '900', '908', '909',
                    '912', '915', '916', '917', '918', '919', '921', '936', '938', '939', '942', '947', '948', '951',
                    '952', '954', '955', '956', '961', '962', '963', '964', '965', '968', '970', '971', '975', '980',
                    '981', '983', '985', '986', '987', '993', '999', '1001', '1002', '1005', '1006', '1007', '1012',
                    '1016', '1018', '1032', '1033', '1038', '1040', '1049', '1050', '1051', '1052', '1054', '1057',
                    '1060', '1062', '1063', '1065', '1066', '1067', '1068', '1069', '1070', '1071', '1072', '1075',
                    '1083', '1084', '1085', '1091', '1092', '1093', '1094', '1097', '1098', '1099', '1100', '1101',
                    '1102', '1103', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113',
                    '1114', '1116', '1117', '1118', '1121', '1124', '1127', '1128', '1129', '1131', '1132', '1133',
                    '1135', '1136', '1137', '1138', '1139', '1140', '1141', '1142', '1143', '1144', '1146', '1147',
                    '1148', '1151', '1152', '1154', '1155', '1156', '1157', '1158', '1159', '1160', '1162', '1163',
                    '1169', '1175', '1176', '1177', '1178', '1179', '1180', '1181', '1182', '1183', '1184', '1185',
                    '1186', '1187', '1188', '1193', '1194', '1196', '1197', '1198', '1200', '1201', '1202', '1205',
                    '1206', '1207', '1208', '1210', '1211', '1212', '1213', '1214', '1215', '1216', '1217', '1218',
                    '1223', '1224', '1226', '1230', '1231', '1232', '1248', '1249', '1250', '1251', '1252', '1253',
                    '1254', '1255', '1256', '1257', '1258', '1259', '1264', '1265', '1266', '1278', '1302', '1311',
                    '1349', '1361', '1407', '1497', '1502', '1521', '1607', '1609', '1623', '1636', '1645', '1693',
                    '1709', '1241', '1760', '1840', '1862', '1953', '1968', '1989', '2036', '2085', '2118', '2144',
                    '2154', '2265', '2268', '2273', '2278', '2364', '2404', '2517', '2619', '2682', '2683', '2727',
                    '2758', '2778', '2782', '2860', '2891', '2929', '2934', '2970', '3020', '3049', '3054', '3084',
                    '3116', '3133', '3154', '3175', '3224', '3267', '3292', '3385', '3387', '3388', '3472', '3540',
                    '3592', '3653', '3671', '3728', '3737', '3753', '3784', '3832', '3871', '3876', '3990', '3999',
                    '4000', '4007', '4030', '4201', '86', '4238', '4297', '4308', '4326', '4377', '4413', '4487',
                    '4533', '4551', '4564', '4589', '4630', '146', '4680', '4740', '4754', '4858', '147', '4961',
                    '5104', '5168', '6345', '5186', '5232', '5333', '5334', '5449', '5580', '5709', '5763', '5956',
                    '5991', '6019', '6176', '6231', '6257', '6303', '141', '6536', '6632', '6654', '6679', '6747',
                    '6845', '6867', '6870', '6969', '7046', '7067', '7116', '7170', '7229', '7254', '7261', '7280',
                    '7367', '10729', '7529', '7617', '7731', '7805', '7840', '7886', '7892', '7907', '7918', '7955',
                    '7979', '8166', '8254', '8277', '8303', '8338', '8347', '8357', '8861', '8962', '9282', '9378',
                    '9395', '9397', '9399', '9401', '9403', '9405', '9407', '9409', '9411', '9413', '9415', '9417',
                    '9419', '9421', '9423', '9433', '9435', '9437', '9439', '9441', '9443', '9445', '9447', '9449',
                    '9451', '9453', '9455', '9457', '9459', '9461', '9463', '9465', '9467', '9469', '9471', '9473',
                    '9475', '9477', '9479', '9481', '9483', '9709', '9951', '9952', '9953', '9954', '9955', '9956',
                    '9957', '9958', '9959', '9960', '9961', '9962', '9963', '10007', '10008', '10009', '117', '10144',
                    '10222', '10223', '10224', '10225', '10226', '10227', '10228', '10229', '10230', '10231', '10232',
                    '10233', '10234', '10235', '10319', '10323', '10326', '10332', '10340', '10341', '10370', '10381',
                    '10479', '10480', '10481', '10483', '10583', '10584', '10585', '10586', '10587', '10588', '10590',
                    '10591', '10592', '10593', '10594', '10599', '10719', '10720', '10721', '10722', '10723', '10724',
                    '10725', '10726', '10727', '10728', '10903', 'FWS001', '11340', '10732', ]


csv_list = os.listdir(inFolder)

for csv in csv_list:
     print csv


     out_csv = final_folder + os.sep + csv
     current_csv = inFolder + os.sep + csv
     in_df = pd.read_csv(current_csv)
     in_df.drop('Unnamed: 0', axis=1, inplace=True)

     removed_entries = in_df[in_df['EntityID'].isin(species_nonconus) == False]
     removed_entries.to_csv(out_csv)