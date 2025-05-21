"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
# Import packages
import arcpy
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection

def script_tool(checkout_lyr):
    """Script code goes below"""
    
    # Authenticate API using Pro license
    target_gis = GIS("Pro")

    with arcpy.da.SearchCursor(checkout_lyr, 'TeamTMU') as cursor:
        for row in cursor:
            team_tmu = row[0]
            break
    
    project = team_tmu.strip()

    ######### DEFINE TABLE FIELDS AND PROPERTIES #######
    # Create list of fields for Editor Tracking Table
    fields_ett = [{
        "name": "OBJECTID",
        "type": "esriFieldTypeOID",
        "alias": "OBJECTID",
        "sqlType": "sqlTypeOther",
        "nullable": False,
        "editable": False,
        "domain": None,
        "defaultValue": None},
        {
            "name": "Editor",
            "type": "esriFieldTypeString",
            "alias": "Editor",
            "sqlType": "sqlTypeOther",
            "length": 255,
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Ct",
            "type": "esriFieldTypeInteger",
            "alias": "Poly_Ct",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Length_KM",
            "type": "esriFieldTypeDouble",
            "alias": "Poly_Length_KM",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Area_Acres",
            "type": "esriFieldTypeDouble",
            "alias": "Poly_Area_Acres",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Map_Hrs",
            "type": "esriFieldTypeDouble",
            "alias": "Map_Hrs",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Per_Hr",
            "type": "esriFieldTypeDouble",
            "alias": "Poly_Per_Hr",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Acres_Per_Hr",
            "type": "esriFieldTypeDouble",
            "alias": "Acres_Per_Hr",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "KM_Per_Hr",
            "type": "esriFieldTypeDouble",
            "alias": "KM_Per_Hr",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None}
    ]

    #Define Editor Tracking Table properties
    properties_ett = {
        "name": f"{project}_Editor_Tracking_Table",
        "type": "Table",
        "displayField": "Editor",
        "description": "Editor Tracking Table used track editors creation speeds",
        "fields": fields_ett,
        "capabilities": "Create,Delete,Query,Update,Editing",
        "spatialReference": None,
        "indexes": [{"name": "Editor_unique_index", "fields": "Editor", "isUnique": True, "description": "Unique index on"
                                                                                                        "editor field to support append"}]
    }

    # Create list of fields for Team Edit Tracking Table
    fields_tet = [{
        "name": "OBJECTID",
        "type": "esriFieldTypeOID",
        "alias": "OBJECTID",
        "sqlType": "sqlTypeOther",
        "nullable": False,
        "editable": False,
        "domain": None,
        "defaultValue": None},
        {
            "name": "Team",
            "type": "esriFieldTypeString",
            "alias": "Team",
            "sqlType": "sqlTypeOther",
            "length": 255,
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Ct",
            "type": "esriFieldTypeInteger",
            "alias": "Poly_Ct",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Length_KM",
            "type": "esriFieldTypeDouble",
            "alias": "Poly_Length_KM",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Area_Acres",
            "type": "esriFieldTypeDouble",
            "alias": "Poly_Area_Acres",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Map_Hrs",
            "type": "esriFieldTypeDouble",
            "alias": "Map_Hrs",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Poly_Per_Hr",
            "type": "esriFieldTypeDouble",
            "alias": "Poly_Per_Hr",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Acres_Per_Hr",
            "type": "esriFieldTypeDouble",
            "alias": "Acres_Per_Hr",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "KM_Per_Hr",
            "type": "esriFieldTypeDouble",
            "alias": "KM_Per_Hr",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None}
    ]

    #Define Team Edit Tracking Table properties
    properties_tet = {
        "name": f"{project}_Team_Edit_Tracking_Table",
        "type": "Table",
        "displayField": "Team",
        "description": "Team Edit Tracking Table used track team creation speeds",
        "fields": fields_tet,
        "capabilities": "Create,Delete,Query,Update,Editing",
        "spatialReference": None,
        "indexes": [{"name": "Team_unique_index", "fields": "Team", "isUnique": True, "description": "Unique index on"
                                                                                                    "Team field to support append"}]
    }

    # Create list of fields for Team Tracking Table
    fields_ttt = [{
        "name": "OBJECTID",
        "type": "esriFieldTypeOID",
        "alias": "OBJECTID",
        "sqlType": "sqlTypeOther",
        "nullable": False,
        "editable": False,
        "domain": None,
        "defaultValue": None},
        {
            "name": "Team",
            "type": "esriFieldTypeString",
            "alias": "Team",
            "sqlType": "sqlTypeOther",
            "length": 255,
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Sum_Map_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Sum_Map_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Sum_QA_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Sum_QA_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Sum_Finalize_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Sum_Finalize_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Sum_Total_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Sum_Total_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None}
    ]

    #Define Editor Tracking Table properties
    properties_ttt = {
        "name": f"{project}_Team_Tracking_Table",
        "type": "Table",
        "displayField": "Team",
        "description": "Team Tracking Table used track team time spent of select project processes",
        "fields": fields_ttt,
        "capabilities": "Create,Delete,Query,Update,Editing",
        "spatialReference": None,
        "indexes": [{"name": "Team_unique_index", "fields": "Team", "isUnique": True, "description": "Unique index on"
                                                                                                    "Team field to support append"}]
    }

    # Create list of fields for Project Tracking Table
    fields_ptt = [{
        "name": "OBJECTID",
        "type": "esriFieldTypeOID",
        "alias": "OBJECTID",
        "sqlType": "sqlTypeOther",
        "nullable": False,
        "editable": False,
        "domain": None,
        "defaultValue": None},
        {
            "name": "Team",
            "type": "esriFieldTypeString",
            "alias": "Team",
            "sqlType": "sqlTypeOther",
            "length": 255,
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Total_HUCs",
            "type": "esriFieldTypeInteger",
            "alias": "Total_HUCs",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "HUCs_Not_Started",
            "type": "esriFieldTypeInteger",
            "alias": "HUCs_Not_Started",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "HUCs_Mapping_IP",
            "type": "esriFieldTypeInteger",
            "alias": "HUCs_Mapping_IP",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "HUCs_Mapped",
            "type": "esriFieldTypeInteger",
            "alias": "HUCs_Mapped",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "HUCs_QA_IP",
            "type": "esriFieldTypeInteger",
            "alias": "HUCs_QA_IP",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "HUCs_QA_Done",
            "type": "esriFieldTypeInteger",
            "alias": "HUCs_QA_Done",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "HUCs_Finalize_IP",
            "type": "esriFieldTypeInteger",
            "alias": "HUCs_Finalize_IP",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "HUCs_Finalized",
            "type": "esriFieldTypeInteger",
            "alias": "HUCs_Finalized",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Mean_Map_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Mean_Map_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Mean_QA_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Mean_QA_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Mean_Finalize_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Mean_Finalize_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
        {
            "name": "Mean_Total_Time",
            "type": "esriFieldTypeDouble",
            "alias": "Mean_Total_Time",
            "sqlType": "sqlTypeOther",
            "nullable": False,
            "editable": True,
            "domain": None,
            "defaultValue": None},
    ]

    #Define Project Tracking Table properties
    properties_ptt = {
        "name": f"{project}_Project_Tracking_Table",
        "type": "Table",
        "displayField": "Team",
        "description": "Project Tracking Table used track project progress and mean speeds",
        "fields": fields_ptt,
        "capabilities": "Create,Delete,Query,Update,Editing",
        "spatialReference": None,
        "indexes": [{"name": "Team_unique_index", "fields": "Team", "isUnique": True, "description": "Unique index on"
                                                                                                    "Team field to support append"}]
    }


    ###### CREATING SERVICE LAYER TO HOST TABLES ######

    # Set up create an Empty feature service
    service_name = f"{project}_Tracking_Table_Service"
    service_desc = "Feature service with multiple tables to track project progress"
    service_params = {
        "name": service_name,
        "serviceDescription": service_desc,
        "hasStaticData": False,
        "maxRecordCount": 500,
        "supportedQueryFormats": "JSON, CSV",
        "capabilities": "Create,Delete,Query,Update,Editing",
        "spatialReference": None
    }

    #Create the empty feature service
    try:
        # Create the empty feature service
        service_item = target_gis.content.create_service(name=service_name, service_type='featureService', create_params=service_params)

        # Access feature service
        service_collection = FeatureLayerCollection.fromitem(service_item)

        # Add tables to service
        add_tables = service_collection.manager.add_to_definition({"tables": [properties_ett, properties_tet, properties_ttt, properties_ptt]})
    except Exception as e:
        arcpy.AddError('Failed to create Online Service Layer. Ivalid Credentials or Service Layer already exists. Ensure ArcGIS online portal is signed in and set to primary and ensure web portal does not already contain the Service Layer.')
        return
    
    try:
        # Create new folder for tracking items
        folder_name = f"{project}_Tracking"
        target_gis.content.folders.create(folder=folder_name)

        # Move fs to folder
        service_item.move(folder=folder_name)
    except Exception as e:
        arcpy.AddError(f'Error creating folder {folder_name} in ArcGIS Online. Ensure this folder does not already exist.')
        return
    
    arcpy.AddMessage(str(folder_name))
    
    #Clone and rename Experience
    try:
        source_gis = GIS("https://smumn.maps.arcgis.com/home/index.html", "GSS_Workspace", "GSSWorkspaceAccount#666!")

        eb_id = "554d527ed8f341168c1f9466a83748e3"

        tracking_item = source_gis.content.get(eb_id)

        item_mapping = {
            "a8ef3a6e9e24455780fa5bac194f806b" : service_item.id
        }

        cloned_eb = target_gis.content.clone_items(items=[tracking_item], search_existing_items=False, item_mapping=item_mapping, folder=folder_name)
    except Exception as e:
        arcpy.AddError('Error cloning the Web Experience to new project.')
        return
    
    try:
        properties_dict = {
            "title" : f"{project}_Tracking_EB"
        }

        cloned_eb[0].update(item_properties=properties_dict)
    except Exception as e:
        arcpy.AddError('Error renaming web experience.')
        return

    return


if __name__ == "__main__":

    checkout_lyr = arcpy.GetParameterAsText(0)

    script_tool(checkout_lyr)