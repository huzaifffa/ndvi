import numpy as np
import rasterio


def read_mtl(mtl):
    # Read the Band 10 constants (ML, AL, K1, K2) from the MTL metadata file
    keys = ["RADIANCE_MULT_BAND_10", "RADIANCE_ADD_BAND_10", "K1_CONSTANT_BAND_10", "K2_CONSTANT_BAND_10"]
    values = {}
    with open(mtl) as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                if key.strip() in keys:
                    values[key.strip()] = float(value)
    return [values[k] for k in keys]


def lst(red, nir, thermal, mtl, output=None):
    with rasterio.open(red) as red_src:
        red = red_src.read(1).astype("float32")

    with rasterio.open(nir) as nir_src:
        nir = nir_src.read(1).astype("float32")

    with rasterio.open(thermal) as b10_src:
        b10 = b10_src.read(1).astype("float32")
        profile = b10_src.profile

    # Pixels outside the scene have DN = 0
    nodata = (b10 == 0) | (red == 0) | (nir == 0)

    ML, AL, K1, K2 = read_mtl(mtl)

    # 1. DN -> TOA radiance
    radiance = ML * b10 + AL

    # 2. Radiance -> brightness temperature (Kelvin)
    bt = K2 / np.log(K1 / radiance + 1)

    # 3. NDVI
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red)
    ndvi[nodata] = np.nan

    # 4. Proportion of vegetation
    ndvi_min = np.nanmin(ndvi)
    ndvi_max = np.nanmax(ndvi)
    pv = ((ndvi - ndvi_min) / (ndvi_max - ndvi_min)) ** 2

    # 5. Emissivity
    emissivity = 0.004 * pv + 0.986

    # 6. LST (Kelvin -> Celsius)
    wavelength = 10.895  # µm, Band 10 centre
    rho = 14388          # µm·K, h*c/σ
    lst_k = bt / (1 + (wavelength * bt / rho) * np.log(emissivity))
    lst_c = (lst_k - 273.15).astype("float32")
    lst_c[nodata] = np.nan

    if output:
        profile.update(dtype="float32", count=1, nodata=np.nan)
        with rasterio.open(output, "w", **profile) as dst:
            dst.write(lst_c, 1)

    return lst_c


if __name__ == "__main__":
    folder = "/Users/sadrealam/Desktop/uno/ndvi/data/"
    scene = "LC08_L1TP_040037_20260830_20260910_02_T1"

    result = lst(
        red=folder + scene + "_B4.TIF",
        nir=folder + scene + "_B5.TIF",
        thermal=folder + scene + "_B10.TIF",
        mtl=folder + scene + "_MTL.txt",
        output=folder + "lst_output.tif",
    )

    print("LST min:", np.nanmin(result), "°C")
    print("LST max:", np.nanmax(result), "°C")
    print("LST mean:", np.nanmean(result), "°C")
