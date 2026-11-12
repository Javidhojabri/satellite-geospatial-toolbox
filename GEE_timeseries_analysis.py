import ee

# Initialize Google Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

print("Google Earth Engine initialized successfully.")

# 1. Define the Study Area (e.g., Lake Urmia Basin - approximate coordinates)
roi = ee.Geometry.Polygon([
    [[44.5, 38.5], [46.5, 38.5], [46.5, 37.0], [44.5, 37.0], [44.5, 38.5]]
])

# 2. Load Sentinel-2 Surface Reflectance Collection for NDVI calculation
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi) \
    .filterDate('2023-05-01', '2023-10-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) # Filter clouds

# 3. Define function to calculate Normalized Difference Vegetation Index (NDVI)
def calculate_ndvi(image):
    # NIR is Band 8, Red is Band 4 in Sentinel-2
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi).copyProperties(image, ['system:time_start'])

# Map the NDVI function across the image collection
ndvi_series = s2.map(calculate_ndvi).select('NDVI')

# 4. Extract mean NDVI time-series statistics over the Region of Interest (ROI)
def get_mean_ndvi(image):
    mean_val = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=30,
        maxPixels=1e9
    )
    return ee.Feature(None, {
        'date': image.date().format('YYYY-MM-dd'),
        'NDVI': mean_val.get('NDVI')
    })

ndvi_chart_data = ndvi_series.map(get_mean_ndvi)
print("GEE Time-Series NDVI processing pipeline defined successfully.")
