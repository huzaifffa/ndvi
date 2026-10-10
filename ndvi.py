import rasterio
import numpy as np

def ndvi(red, nir, output):
    with rasterio.open(red) as red_src:
        red = red_src.read(1).astype("float32")
        profile = red_src.profile

    with rasterio.open(nir) as nir_src:
        nir = nir_src.read(1, masked=True).astype("float32")

    ndvi = (nir - red) / (nir + red)

    profile.update(dtype="float32", count=1)

    with rasterio.open(output, "w", **profile) as dst:
        dst.write(ndvi, 1)

