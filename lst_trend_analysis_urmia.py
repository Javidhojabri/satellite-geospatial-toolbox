"""
Author: Javid Hojabri
Repository: satellite-geospatial-toolbox
Description: Advanced Land Surface Temperature (LST) Time-Series and Trend Analysis 
             for the Urmia Lake Basin, integrating methodologies from published research.
"""

import ee

# Initialize Earth Engine API
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# 1. Define Study Area (Urmia Lake Basin Bounding Box / Region of Interest)
# Based on geographic parameters used in Hojabri & Aydin (2026)
urmia_basin = ee.Geometry.Polygon([
    [[44.5, 38.5], [47.5, 38.5], [47.5, 36.5], [44.5, 36.5], [44.5, 38.5]]
])

# 2. Define Time Frame for Long-term Analysis
START_DATE = '2018-01-01'
END_DATE = '2023-12-31'

# 3. Load Landsat 8 Collection 2 Tier 1 Surface Temperature (LST) Data
def mask_landsat_sr(image):
    # Bit 3 = Cloud, Bit 5 = Cloud Confidence
    qa = image.select('QA_PIXEL')
    cloud_shadow_mask = (1 << 4)
    clouds_mask = (1 << 3)
    mask = qa.bitwiseAnd(cloud_shadow_mask).eq(0).And(
           qa.bitwiseAnd(clouds_mask).eq(0))
    return image.updateMask(mask)

landsat_col = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
               .filterBounds(urmia_basin)
               .filterDate(START_DATE, END_DATE)
               .map(mask_landsat_sr))

# 4. Extract and Scale Land Surface Temperature (ST_B10 converted to Celsius)
def calculate_lst(image):
    # Scale factor for Landsat Collection 2 thermal band is 0.00341802, offset is 149.0
    thermal_band = image.select('ST_B10').multiply(0.00341802).add(149.0)
    # Convert Kelvin to Celsius
    lst_celsius = thermal_band.subtract(273.15).rename('LST_Celsius')
    return image.addBands(lst_celsius).copyProperties(image, ['system:time_start'])

lst_collection = landsat_col.map(calculate_lst).select('LST_Celsius')

# 5. Extract Regional Time-Series Statistics across the Basin
def extract_basin_stats(image):
    mean_val = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=urmia_basin,
        scale=30,
        maxPixels=1e9
    )
    date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
    return ee.Feature(None, {'date': date, 'LST_mean': mean_val.get('LST_Celsius')})

time_series_features = lst_collection.map(extract_basin_stats)

print("Script compiled successfully. Ready for export or local pandas integration.")
