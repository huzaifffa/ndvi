from email.mime import image

import rasterio
import matplotlib.pyplot as plt
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
        image = input('press y to get image of the result')
        if image == "y":
            import matplotlib.pyplot as plt
            plt.imshow(ndvi, cmap='RdYlGn')
            plt.colorbar()
            plt.title('NDVI Image')
            plt.show()

    else:
        print("Continuing without calculating ndvi.")
        return

    profile.update(dtype="float32", count=1)

    with rasterio.open(output, "w", **profile) as dst:
        dst.write(ndvi, 1)

if __name__ == "__main__":
    red_band = "/Users/sadrealam/Desktop/uno/ndvi/data/LC08_L1TP_040037_20260830_20260910_02_T1_B4.TIF"
    nir_band = "/Users/sadrealam/Desktop/uno/ndvi/data/LC08_L1TP_040037_20260830_20260910_02_T1_B5.TIF"
    output_file = "/Users/sadrealam/Desktop/uno/ndvi/data/ndvi_output.tif"

    ndvi(red_band, nir_band, output_file)