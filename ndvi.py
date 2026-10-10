import rasterio
# import numpy as np

def ndvi(red, nir, output):
    with rasterio.open(red) as red_src:
        red = red_src.read(1).astype("float32")
        profile = red_src.profile
        print(type(red))
        print(red_src.height, red_src.width)

    with rasterio.open(nir) as nir_src:
        nir = nir_src.read(1, masked=True).astype("float32")
        print(type(nir))
        print(nir_src.height, nir_src.width)

    x = input("Enter the value y if you want to calculate ndvi or pass to continue: ")
    if x == "y":
        ndvi = (nir - red) / (nir + red)
    else:
        print("Continuing without calculating ndvi.")
        return

    profile.update(dtype="float32", count=1)

    with rasterio.open(output, "w", **profile) as dst:
        dst.write(ndvi, 1)

