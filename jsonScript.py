import pandas as pd

# Importing all 4 files
temp_data1 = pd.read_json("rawData\\planet_osm_point_202312122304.json")
temp_data2 = pd.read_json("rawData\\planet_osm_point_202312122304_2.json")
temp_data3 = pd.read_json("rawData\\planet_osm_point_202312122304_3.json")
temp_data4 = pd.read_json("rawData\\planet_osm_point_202312122304_4.json")

# Removing the key "planet_osm_point" at the beginning
temp_data1 = temp_data1.get("planet_osm_point")
temp_data2 = temp_data2.get("planet_osm_point")
temp_data3 = temp_data3.get("planet_osm_point")
temp_data4 = temp_data4.get("planet_osm_point")

# Saving them into new fully usable jsons

temp_data1.to_json("rawData\\Copies\\planet_osm_point_202312122304_1_copy.json", orient="records", lines=True)
temp_data2.to_json("rawData\\Copies\\planet_osm_point_202312122304_2_copy.json", orient="records", lines=True)
temp_data3.to_json("rawData\\Copies\\planet_osm_point_202312122304_3_copy.json", orient="records", lines=True)
temp_data4.to_json("rawData\\Copies\\planet_osm_point_202312122304_4_copy.json", orient="records", lines=True)
