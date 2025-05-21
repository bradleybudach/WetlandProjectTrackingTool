"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import csv
import datetime as dt
from arcgis.gis import GIS
import os


def script_tool(param0):
    CO_table_path = param0

    # Iterates over CO table and creates dictionaries to hold stats values
    def generate_stats_dicts(co_path):
        # Create empty arrays to hold the unique Editors and TeamTMU in CO layer
        editors = []
        teams = []

        # Iterate over CO table and add editors and teams to array
        with arcpy.da.SearchCursor(co_path, ['Editor', 'TeamTMU']) as cursor:
            for row in cursor:
                editor_name = row[0]
                team_name = row[1]

                if editor_name is not None:
                    editor_name = editor_name.strip()
                if editor_name is not None and editor_name not in editors:
                    editors.append(editor_name)
                if team_name is not None and team_name not in teams:
                    teams.append(team_name)
        editor_stats_lp = {editor: [0] * 7 for editor in editors}
        team_edit_stats_lp = {team: [0] * 7 for team in teams}
        team_prog_track_lp = {team: [0] * 4 for team in teams}
        proj_prog_track_lp = {team: [0] * 12 for team in teams}

        return editor_stats_lp, team_edit_stats_lp, team_prog_track_lp, proj_prog_track_lp, teams


    # Call create dict function and save returned dicts
    try:
        editor_stats, team_estats, team_prog_track, proj_prog_track, proj_array = generate_stats_dicts(CO_table_path)
    except Exception as e:
        arcpy.AddError('The selected Feature Class does not have the required fields Editor or TeamTMU. Choose a different Feature Class')
        return
    
    # Function to iterate over CO table and populate dicts with editing stats
    def populate_edit_dicts(co_path, editor_stats_lp, team_edit_stats_lp):
        # Iterate over table and pull needed values into appropriate dicts
        with arcpy.da.SearchCursor(co_path, ['Editor', 'TeamTMU', 'POLY_CT', 'POLY_AREA_ACRES', 'POLY_LENGTH_KM',
                                            'MAPPING_HRS']) as cursor:
            for row in cursor:
                editor = row[0]
                team = row[1]
                poly_ct = row[2]
                poly_area = row[3]
                poly_length = row[4]
                map_hrs = row[5]

                if editor in editor_stats_lp:
                    editor_stats_lp[editor][0] += int(poly_ct)
                    editor_stats_lp[editor][1] += float(poly_length)
                    editor_stats_lp[editor][2] += float(poly_area)

                if editor in editor_stats and map_hrs > 1:
                    editor_stats_lp[editor][3] += float(map_hrs)

                if team in team_edit_stats_lp:
                    team_edit_stats_lp[team][0] += int(poly_ct)
                    team_edit_stats_lp[team][1] += float(poly_length)
                    team_edit_stats_lp[team][2] += float(poly_area)

                if team in team_edit_stats_lp and map_hrs > 1:
                    team_edit_stats_lp[team][3] += float(map_hrs)

        # loop calculates Poly per hr, Acres per hr, km per hr for each editor
        for editor in editor_stats_lp:
            if editor_stats_lp[editor][3] > 1:
                editor_stats_lp[editor][4] = round(editor_stats_lp[editor][0] / editor_stats_lp[editor][3], 2)
                editor_stats_lp[editor][5] = round(editor_stats_lp[editor][2] / editor_stats_lp[editor][3], 2)
                editor_stats_lp[editor][6] = round(editor_stats_lp[editor][1] / editor_stats_lp[editor][3], 2)

        # loop calculates Poly per hr, Acres per hr, km per hr for the team
        for team in team_edit_stats_lp:
            if team_edit_stats_lp[team][3] > 1:
                team_edit_stats_lp[team][4] = round(team_edit_stats_lp[team][0] / team_edit_stats_lp[team][3], 2)
                team_edit_stats_lp[team][5] = round(team_edit_stats_lp[team][2] / team_edit_stats_lp[team][3], 2)
                team_edit_stats_lp[team][6] = round(team_edit_stats_lp[team][1] / team_edit_stats_lp[team][3], 2)

        return editor_stats_lp, team_edit_stats_lp


    # Call populate_edit_dicts and save the results to the appropriate dict
    try:
        editor_stats, team_estats = populate_edit_dicts(co_path=CO_table_path, editor_stats_lp=editor_stats,
                                                    team_edit_stats_lp=team_estats)
    except Exception as e:
        arcpy.AddError('The selected Feature Class does not have the required fields POLY_CT, POLY_AREA_ACRES, POLY_LENGTH_KM, or MAPPING_HRS. Choose a different Feature Class')
        return
    
    # Function to iterate over CO table and populate dicts with project progress stats
    def populate_prog_dicts(co_path, team_prog_track_lp, proj_prog_track_lp):
        # Iterate over CO layer and do sums and counts
        with arcpy.da.SearchCursor(co_path,
                                ['HUC12', 'TeamTMU', 'Editor', 'MAPPING_HRS', 'QA_REVIEW_HRS', 'QA_REVISION_HRS',
                                    'QA_TOTAL_HRS', 'FINALIZATION_HRS', 'TOTAL_HRS']) as cursor:
            for row in cursor:
                huc = row[0]
                team = row[1]
                editor = row[2]
                map_hr = row[3]
                qa_review = row[4]
                qa_revision = row[5]
                qa_total = row[6]
                final = row[7]
                total = row[8]

                # Counts total number of HUCs
                if team in proj_prog_track_lp and huc is not None:
                    proj_prog_track_lp[team][0] += 1

                # Counts HUCs not checked out yet
                if editor is None and map_hr == 1:
                    proj_prog_track_lp[team][1] += 1

                # Counts HUCs checked out but not finished with initial mapping
                if editor is not None and map_hr == 1:
                    proj_prog_track_lp[team][2] += 1

                # Counts Hucs through initial mapping and total time of initial mapping
                if map_hr > 1:
                    proj_prog_track_lp[team][3] += 1
                    team_prog_track_lp[team][0] += float(map_hr)

                # Count HUCs currently in QA
                if map_hr > 1 and (qa_review is None or qa_revision is None):
                    proj_prog_track_lp[team][4] += 1

                # Count HUCs through QA and sum QA time
                if qa_review is not None and qa_revision is not None:
                    proj_prog_track_lp[team][5] += 1
                    team_prog_track_lp[team][1] += float(qa_total)

                # Count Hucs currently in finalization
                if qa_revision is not None and final is None:
                    proj_prog_track_lp[team][6] += 1

                # Count Hucs finalized and sum finalization time and total time
                if final is not None:
                    proj_prog_track_lp[team][7] += 1
                    team_prog_track_lp[team][2] += float(final)
                    team_prog_track_lp[team][3] += float(total)

        for team in proj_prog_track_lp:
            if proj_prog_track_lp[team][3] > 0:
                proj_prog_track_lp[team][8] = round(team_prog_track_lp[team][0] / proj_prog_track_lp[team][3], 2)
            if proj_prog_track_lp[team][5] > 0:
                proj_prog_track_lp[team][9] = round(team_prog_track[team][1] / proj_prog_track_lp[team][5], 2)
            if proj_prog_track_lp[team][7] > 0:
                proj_prog_track_lp[team][10] = round(team_prog_track_lp[team][2] / proj_prog_track_lp[team][7], 2)
                proj_prog_track_lp[team][11] = round(team_prog_track_lp[team][3] / proj_prog_track_lp[team][7], 2)

        return team_prog_track_lp, proj_prog_track_lp


    # Call populate_por_dicts and update values in dictionaries
    try:
        team_prog_track, proj_prog_track = populate_prog_dicts(co_path=CO_table_path, team_prog_track_lp=team_prog_track,
                                                        proj_prog_track_lp=proj_prog_track)
    except Exception as e:
        arcpy.AddError('The selected Feature Class does not have the required fields. Choose a different Feature Class')
        return
    
    ### Set up for writing csv and appened hosted tables ###
    CO_path_split = CO_table_path.split("\\")
    root_path = "\\".join(CO_path_split[:-2])
    proj_name = proj_array[0].strip()

    # Create directory to store output
    # Get current date as string for file naming
    current_date = dt.datetime.now().strftime("%Y_%m_%d")

    tracking_folder_path = root_path + f"\\{proj_name}_Project_Tracking"

    # create Project_Tracking folder if it doesn't exist yet
    if not os.path.exists(tracking_folder_path):
        os.makedirs(tracking_folder_path)

    #Folder for current year/month
    output_path = tracking_folder_path + f"\\{current_date[:-3]}"

    #create date folder if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Set up Editor tracking table to be written
    ett_columns = ["Editor", "Poly_Ct", "Poly_Length_KM", "Poly_Area_Acres", "Map_Hrs", "Poly_Per_Hr", "Acres_Per_Hr",
                "KM_Per_Hr"]
    ett_date_name = f"{proj_name}_Editor_Tracking_{current_date}.csv"
    ett_date_out = os.path.join(output_path, ett_date_name)
    ett_intermediate_prop = {"title": ett_date_name, "type": "CSV",
                            "description": "Intermediate table used to update table linked to EB",
                            "spatialReference": None}
    ett_write_array = [ett_columns, ett_date_name, ett_date_out, ett_intermediate_prop]

    # Set up team edit tracking table to be written
    tet_columns = ["Team", "Poly_Ct", "Poly_Length_KM", "Poly_Area_Acres", "Map_Hrs", "Poly_Per_Hr", "Acres_Per_Hr",
                "KM_Per_Hr"]
    tet_date_name = f"{proj_name}_Team_Edit_Tracking_{current_date}.csv"
    tet_date_out = os.path.join(output_path, tet_date_name)
    tet_intermediate_prop = {"title": tet_date_name, "type": "CSV",
                            "description": "Intermediate table used to update table linked to EB",
                            "spatialReference": None}
    tet_write_array = [tet_columns, tet_date_name, tet_date_out, tet_intermediate_prop]

    # set up team tracking table to be written
    ttt_columns = ["Team", "Sum_Map_Time", "Sum_QA_Time", "Sum_Finalize_Time", "Sum_Total_Time"]
    ttt_date_name = f"{proj_name}_Team_Tracking_{current_date}.csv"
    ttt_date_out = os.path.join(output_path, ttt_date_name)
    ttt_intermediate_prop = {"title": ttt_date_name, "type": "CSV",
                            "description": "Intermediate table used to update table linked to EB",
                            "spatialReference": None}
    ttt_write_array = [ttt_columns, ttt_date_name, ttt_date_out, ttt_intermediate_prop]

    # set up project tracking table to be written
    ptt_columns = ["Team", "Total_HUCs", "HUCs_Not_Started", "HUCs_Mapping_IP", "HUCs_Mapped", "HUCs_QA_IP", "HUCs_QA_Done",
                "HUCs_Finalize_IP", "HUCs_Finalized", "Mean_Map_Time", "Mean_QA_Time", "Mean_Finalize_Time",
                "Mean_Total_Time"]
    ptt_date_name = f"{proj_name}_Project_Tracking_{current_date}.csv"
    ptt_date_out = os.path.join(output_path, ptt_date_name)
    ptt_intermediate_prop = {"title": ptt_date_name, "type": "CSV",
                            "description": "Intermediate table used to update table linked to EB",
                            "spatialReference": None}
    ptt_write_array = [ptt_columns, ptt_date_name, ptt_date_out, ptt_intermediate_prop]


    # function writes the csv tables to be uploded and appened to EB tables
    def write_csv_for_tables(ett_write_array_lp, editor_stats_lp, tet_write_array_lp, team_estats_lp, ttt_write_array_lp,
                            team_proglp, ptt_write_array_lp, proj_tracklp):
        # write ett csv
        with open(ett_write_array_lp[2], mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(ett_write_array_lp[0])
            for editor, stats in editor_stats_lp.items():
                writer.writerow([editor] + [int(stats[0])] + [float(stat) for stat in stats[1:]])

        # write tet csv
        with open(tet_write_array_lp[2], mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(tet_write_array_lp[0])
            for team, stats in team_estats_lp.items():
                writer.writerow([team] + stats)

        # write ttt csv
        with open(ttt_write_array_lp[2], mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(ttt_write_array_lp[0])
            for team, prog in team_proglp.items():
                writer.writerow([team] + prog)

        # write ptt csv
        with open(ptt_write_array_lp[2], mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(ptt_write_array_lp[0])
            for proj, tracklp in proj_tracklp.items():
                writer.writerow([proj] + tracklp)


    # Call write_csv_for_tables
    write_csv_for_tables(ett_write_array_lp=ett_write_array, editor_stats_lp=editor_stats,
                        tet_write_array_lp=tet_write_array,
                        team_estats_lp=team_estats, ttt_write_array_lp=ttt_write_array, team_proglp=team_prog_track,
                        ptt_write_array_lp=ptt_write_array, proj_tracklp=proj_prog_track)

    #### Retrive hosted tables from online ####
    # Authenicate API
    try:
        gis = GIS('Pro')


        # Add csvs to arcOnline and return intermediate table items
        def add_csv_arconline(api_token, ett_write_array_fn, tet_write_array_fn, ttt_write_array_fn, ptt_write_array_fn):
            ett_int_item_fn = api_token.content.add(item_properties=ett_write_array_fn[3], data=ett_write_array_fn[2])
            ett_source_info_fn = api_token.content.analyze(item=ett_int_item_fn.id)

            tet_int_item_fn = api_token.content.add(item_properties=tet_write_array_fn[3], data=tet_write_array_fn[2])
            tet_source_info_fn = api_token.content.analyze(item=tet_int_item_fn.id)

            ttt_int_item_fn = api_token.content.add(item_properties=ttt_write_array_fn[3], data=ttt_write_array_fn[2])
            ttt_source_info_fn = api_token.content.analyze(item=ttt_int_item_fn.id)

            ptt_int_item_fn = api_token.content.add(item_properties=ptt_write_array_fn[3], data=ptt_write_array_fn[2])
            ptt_source_info_fn = api_token.content.analyze(item=ptt_int_item_fn.id)

            return (ett_int_item_fn, ett_source_info_fn, tet_int_item_fn, tet_source_info_fn, ttt_int_item_fn,
                    ttt_source_info_fn, ptt_int_item_fn, ptt_source_info_fn)


        # Call add_csv_arcOnline to publish the intermediate tables
        try:
            (ett_int_item, ett_source_info, tet_int_item, tet_source_info, ttt_int_item, ttt_source_info,
            ptt_int_item, ptt_source_info) = add_csv_arconline(api_token=gis, ett_write_array_fn=ett_write_array,
                                                                tet_write_array_fn=tet_write_array, ttt_write_array_fn=ttt_write_array,
                                                                ptt_write_array_fn=ptt_write_array)
        except Exception as e:
            arcpy.AddError('Failed to add tracking CSV files to ArcGIS Online. Ensure that these CSVs do not already exist on Arcgis Online for this script to run.')
            return



        # Accesses feature service and returns tables
        def get_host_tables(api_token):
            fs = api_token.content.search(f"title:{proj_name}_Tracking_Table_Service", item_type='Feature Service')[0]
            ett_fs_table_fn = fs.tables[0]
            tet_fs_table_fn = fs.tables[1]
            ttt_fs_table_fn = fs.tables[2]
            ptt_fs_table_fn = fs.tables[3]

            return ett_fs_table_fn, tet_fs_table_fn, ttt_fs_table_fn, ptt_fs_table_fn


        # Call get_host_tables and store returned tables]
        try:
            ett_fs_table, tet_fs_table, ttt_fs_table, ptt_fs_table = get_host_tables(api_token=gis)
        except Exception as e:
            arcpy.AddError(f'Unable to find {proj_name}_Tracking_Table_Service on ArcGIS online. If this table has not been created, use the CreateOnlineProjectTracking tool and ensure the name matches the project folder.')
            return


        # Appends EB Tables and deletes intermediate tables
        def append_fs_tables(ett_write_array_fn, ett_fs_fn, ett_int_item_fn, ett_si_fn, tet_write_array_fn, tet_fs_fn,
                            tet_int_item_fn, tet_si_fn, ttt_write_array_fn, ttt_fs_fn, ttt_int_item_fn, ttt_si_fn,
                            ptt_write_array_fn, ptt_fs_fn, ptt_int_item_fn, ptt_si_fn):
            ett_fs_fn.append(source_table_name=ett_write_array_fn[1], item_id=ett_int_item_fn.id, upload_format='csv',
                            source_info=ett_si_fn['publishParameters'], upsert=True, update_geometry=False,
                            append_fields=ett_write_array_fn[0], skip_inserts=False, upsert_matching_field='Editor')

            tet_fs_fn.append(source_table_name=tet_write_array_fn[1], item_id=tet_int_item_fn.id, upload_format='csv',
                            source_info=tet_si_fn['publishParameters'], upsert=True, update_geometry=False,
                            append_fields=tet_write_array_fn[0], skip_inserts=False, upsert_matching_field='Team')

            ttt_fs_fn.append(source_table_name=ttt_write_array_fn[1], item_id=ttt_int_item_fn.id, upload_format='csv',
                            source_info=ttt_si_fn['publishParameters'], upsert=True, update_geometry=False,
                            append_fields=ttt_write_array_fn[0], skip_inserts=False, upsert_matching_field='Team')

            ptt_fs_fn.append(source_table_name=ptt_write_array_fn[1], item_id=ptt_int_item_fn.id, upload_format='csv',
                            source_info=ptt_si_fn['publishParameters'], upsert=True, update_geometry=False,
                            append_fields=ptt_write_array_fn[0], skip_inserts=False, upsert_matching_field='Team')

            ett_int_item_fn.delete()
            tet_int_item_fn.delete()
            ttt_int_item_fn.delete()
            ptt_int_item_fn.delete()


        # Call function to append
        try:
            append_fs_tables(ett_write_array_fn=ett_write_array, ett_fs_fn=ett_fs_table, ett_int_item_fn=ett_int_item, ett_si_fn=ett_source_info,
                        tet_write_array_fn=tet_write_array, tet_fs_fn=tet_fs_table, tet_int_item_fn=tet_int_item, tet_si_fn=tet_source_info,
                        ttt_write_array_fn=ttt_write_array, ttt_fs_fn=ttt_fs_table, ttt_int_item_fn=ttt_int_item, ttt_si_fn=ttt_source_info,
                        ptt_write_array_fn=ptt_write_array, ptt_fs_fn=ptt_fs_table, ptt_int_item_fn=ptt_int_item, ptt_si_fn=ptt_source_info)
        except Exception as e:
            arcpy.AddError("Error with adding CSV data to service.")
    except Exception as e:
        arcpy.AddError('Ivalid Credentials for uploading to ArcGIS Online. Ensure ArcGIS online portal is signed in and set to primary.')
        return
    return


if __name__ == "__main__":

    param0 = arcpy.GetParameterAsText(0)

    script_tool(param0)
    #arcpy.SetParameterAsText(1, param0)
