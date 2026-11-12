"""
Time-Series Geospatial Analyzer
Author: Javid Hojabri
Description: Module for analyzing multi-temporal raster time-series data 
             (e.g., historical NDVI/NDWI trends for environmental monitoring).
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio


class TimeSeriesAnalyzer:
    """Handles multi-temporal raster stacking and trend analysis."""

    def __init__(self, raster_dir: str):
        self.raster_dir = Path(raster_dir)

    def load_raster_stack(self, file_pattern: str = "*.tif") -> tuple:
        """
        Loads a stack of raster files matching the pattern from the directory.
        Returns the data array (time, height, width) and spatial metadata.
        """
        raster_files = sorted(list(self.raster_dir.glob(file_pattern)))
        
        if not raster_files:
            raise FileNotFoundError(f"No matching rasters found in {self.raster_dir}")

        stack_data = []
        meta = None

        for file_path in raster_files:
            with rasterio.open(file_path) as src:
                if meta is None:
                    meta = src.meta.copy()
                # Read the first band
                band = src.read(1)
                stack_data.append(band)

        # Convert list to a 3D NumPy array: (time, height, width)
        stack_array = np.array(stack_data, dtype=np.float32)
        
        # Update metadata count for the stack if needed
        meta.update(count=stack_array.shape[0])
        
        return stack_array, meta

    @staticmethod
    def calculate_temporal_mean(stack_array: np.ndarray, nodata_val: float = -9999.0) -> np.ndarray:
        """
        Calculates the pixel-wise temporal mean across the time-series stack,
        ignoring NoData values.
        """
        # Mask out nodata values to avoid skewing calculations
        masked_stack = np.ma.masked_equal(stack_array, nodata_val)
        mean_image = masked_stack.mean(axis=0)
        
        return mean_image.filled(nodata_val)


if __name__ == "__main__":
    # Example usage structure (update path with your actual directory)
    print("TimeSeriesAnalyzer module loaded successfully.")
