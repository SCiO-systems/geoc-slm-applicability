import numpy as np
import numpy.ma as ma
import gdal
import os
import sys
import pathlib
import boto3
import json
import copy

def lambda_handler(event, context):
    
    
    body = json.loads(event['body'])
    json_file = body
    # json_file = event['body']
    
    path_to_save_temp_files = "/tmp/"

    # get  input json and extract geojson
    try:
        slms = json_file["slms"]
        matching_target_area_file = json_file["filename"].split("/")[-1]
    except Exception as e:
        print(e)

    if bool(slms) == False:
        raise Exception("Empty target area")

    my_output = {
        "results": []
    }

    slm_block = {
        "id": None,
        "applicable": None
    }

    for slm_area in slms:
        gdal_warp_kwargs_target_area = {
            'format': 'GTiff',
            'cutlineDSName': json.dumps(slm_area["area"]),
            'cropToCutline': True,
            #     'srcNodata' : 255,
            #     'dstNodata' : -9999,
            # 'creationOptions': ['COMPRESS=DEFLATE']

        }
        input_path = '/vsis3/geoc-temp/' + matching_target_area_file
        output_path = path_to_save_temp_files + "common_area.tif"

        gdal.Warp(output_path, input_path, **gdal_warp_kwargs_target_area)

        slm_area_array = gdal.Open(path_to_save_temp_files + "common_area.tif").ReadAsArray()
        slm_area_array = ma.array(slm_area_array, mask=slm_area == -9999, fill_value=-9999)

        slm_block["id"] = slm_area["id"]

        if (slm_area_array == 1).any():
            slm_block["applicable"] = True
        else:
            slm_block["applicable"] = False

        my_output["results"] = copy.copy(slm_block)

    return {
        "statusCode": 200,
        "body": json.dumps(my_output),
    }
