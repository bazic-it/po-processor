from pathlib import Path
import json

def readConfigJson():
    configs = {
        "assets_base_directory": "",
        "uom_master_filename": "",
        "inventory_master_filename": "",
        "logs_filename": "",
        "local_logs_filepath": "",
        "input_file_location": "",
        "output_file_location": ""
    }

    jsonFilepath = "./assets/config.json"

    with open(jsonFilepath, 'r') as file:
        data = json.load(file)
        configs["assets_base_directory"] = data["assets_base_directory"]
        configs["uom_master_filename"] = data["uom_master_filename"]
        configs["inventory_master_filename"] = data["inventory_master_filename"]
        configs["logs_filename"] = data["logs_filename"]
        configs["local_logs_filepath"] = data["local_logs_filepath"]
        configs["input_file_location"] = data["input_file_location"]
        configs["output_file_location"] = data["output_file_location"]

    return configs

configs = readConfigJson()

APP_VERSION = '1.1.0'

ASSETS_BASE_DIR = configs["assets_base_directory"]
# ASSETS_BASE_DIR = './'
UOM_MASTER_FILENAME = configs["uom_master_filename"]
QTY_PRICE_MASTER_FILENAME = configs["inventory_master_filename"]
LOGS_FILENAME = configs["logs_filename"]
USER_DOWNLOADS = str(Path.home() / configs["input_file_location"]) + '/'
OUTPUT_DIR = configs["output_file_location"]