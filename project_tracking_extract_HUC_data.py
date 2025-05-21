import arcpy

def script_tool(selecting_feature, polys_feature):
    """Script code goes below"""
    # Get the directory for the polygons
    poly_path_split = polys_feature.split('\\') # split up path

    feature_layer = poly_path_split[-1] # get feature class name
    database_path = "\\".join(poly_path_split[:-1]) # database path
    arcpy.env.workspace = database_path #set working directory

    if arcpy.Exists(feature_layer): # ensure feature class exists in database and create a feature layer to work with
        working_feature_set = "working_set"
        arcpy.MakeFeatureLayer_management(feature_layer, working_feature_set)
    else:
        arcpy.AddError("The selected feature class does not exist.")
        return

    selecting_feature_class = selecting_feature.split("\\")[-1] # get selecting feature class name

    desc = arcpy.Describe(selecting_feature_class)
    if desc.FIDSet == "": #check for selected features
        arcpy.AddError("HUC Layer has no selection. Select the HUCS to analyze.")
        return
    
    selected_ids = [int(fid) for fid in desc.FIDSet.split(';')] #split out each object ID for the HUCS

    for fid in selected_ids: #analyze each HUC
        query = f"\"OBJECTID\" = {fid}"
        arcpy.AddMessage(query)
        select_lyr = arcpy.MakeFeatureLayer_management(selecting_feature_class, "in_memory\\selected_features_lyr", query) # create a layer of the currently selected HUC in memory
        arcpy.SelectLayerByLocation_management(working_feature_set, "INTERSECT", select_lyr, "", "NEW_SELECTION") # select polygons inside HUC for analysis
        
        clipped_features = 'in_memory\\clipped_features' # store clipped features in memory

        # Use the Clip tool
        arcpy.Clip_analysis(working_feature_set, select_lyr, clipped_features)

        arcpy.Delete_management(select_lyr) # delete selected polys from memory

        polygon_count = arcpy.GetCount_management(clipped_features) # get polygon count

        # Sum the area and length
        total_area = 0
        total_length = 0

        with arcpy.da.SearchCursor(clipped_features, ["SHAPE@AREA", "SHAPE@LENGTH"]) as cursor: #get summation of area and length in the HUC
            for row in cursor: 
                total_area += row[0]
                total_length += row[1]

        total_area = round((total_area / 4046.85642), 2) # convert to acers and round
        total_length = round((total_length / 1000), 2) # convert to km and round

        #Print outputs as messages in the tool (optional):
        arcpy.AddMessage(f'Count: {polygon_count}')
        arcpy.AddMessage(f"Total Area (acres): {total_area}")
        arcpy.AddMessage(f"Total Length (km): {total_length}")

        arcpy.Delete_management(clipped_features) #delete clipped features from memory

        with arcpy.da.UpdateCursor(selecting_feature_class, ['OBJECTID', 'POLY_CT', 'POLY_AREA_ACRES', 'POLY_LENGTH_KM'], query) as cursor: # update fields in attribute table for HUCs
            for row in cursor:
                row[1] = int(str(polygon_count)) # weird shenanagins to convert from Result to int
                row[2] = total_area
                row[3] = total_length
                cursor.updateRow(row)
                break
    return


if __name__ == "__main__":
    # get params
    selecting_feature = arcpy.GetParameterAsText(0)
    polys_feature = arcpy.GetParameterAsText(1)

    script_tool(selecting_feature, polys_feature)