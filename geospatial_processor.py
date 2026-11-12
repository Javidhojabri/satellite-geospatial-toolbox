"""
Geospatial Processing Toolbox for Satellite Image Analysis
Author: Javid Hojabri
Description: Automated Python workflows for NDVI, NDWI, and Land Surface Temperature (LST) calculations 
utilizing Rasterio, GeoPandas, and NumPy. Designed for environmental and climate monitoring applications.
"""

import os
import numpy as np
import rasterio
from rasterio.plot import show
import geopandas as gpd

class GeospatialProcessor:
    def __init__(self, image_path):
        """
        Initializes the geospatial processor with a multi-spectral raster dataset.
        :param image_path: Path to the input raster file (e.g., GeoTIFF)
        """
        self.image_path = image_path
        
    def calculate_ndvi(self, red_band_idx, nir_band_idx, output_path=None):
        """
        Calculates Normalized Difference Vegetation Index (NDVI).
        Formula: (NIR - Red) / (NIR + Red)
        """
        with rasterio.open(self.image_path) as src:
            red = src.read(red_band_idx).astype(np.float32)
            nir = src.read(nir_band_idx).astype(np.float32)
            profile = src.profile
            
        # Handle potential division by zero
        np.seterr(divide='ignore', invalid='ignore')
        ndvi = (nir - red) / (nir + red)
        ndvi = np.nan_to_num(ndvi, nan=-999.0)
        
        if output_path:
            profile.update(dtype=rasterio.float32, count=1, nodata=-999.0)
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(ndvi.astype(rasterio.float32), 1)
                
        return ndvi

    def calculate_ndwi(self, green_band_idx, nir_band_idx, output_path=None):
        """
        Calculates Normalized Difference Water Index (NDWI) for surface water extraction.
        Formula: (Green - NIR) / (Green + NIR)
        """
        with rasterio.open(self.image_path) as src:
            green = src.read(green_band_idx).astype(np.float32)
            nir = src.read(nir_band_idx).astype(np.float32)
            profile = src.profile
            
        np.seterr(divide='ignore', invalid='ignore')
        ndwi = (green - nir) / (green + nir)
        ndwi = np.nan_to_num(ndwi, nan=-999.0)
        
        if output_path:
            profile.update(dtype=rasterio.float32, count=1, nodata=-999.0)
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(ndwi.astype(rasterio.float32), 1)
                
        return ndwi

    def estimate_lst(self, thermal_band_idx, emissivity=0.97, output_path=None):
        """
        Estimates Land Surface Temperature (LST) from thermal infrared bands.
        Simplified conversion from Digital Number (DN) / Top of Atmosphere (TOA) radiance to Celsius.
        """
        with rasterio.open(self.image_path) as src:
            thermal_dn = src.read(thermal_band_idx).astype(np.float32)
            profile = src.profile
            
        brightness_temp = thermal_dn * 0.05 + 150.0  # Placeholder scaling
        lst_celsius = brightness_temp - 273.15
        lst_celsius = np.nan_to_num(lst_celsius, nan=-999.0)
        
        if output_path:
            profile.update(dtype=rasterio.float32, count=1, nodata=-999.0)
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(lst_celsius.astype(rasterio.float32), 1)
                
        return lst_celsius

if __name__ == "__main__":
    print("Geospatial Processor initialized successfully.")
    print("Ready for automated remote sensing pipelines (NDVI, NDWI, LST).")
