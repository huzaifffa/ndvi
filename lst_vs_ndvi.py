import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def read_band(band):
    # Accept either a file path or an array that is already in memory
    if isinstance(band, str):
        with rasterio.open(band) as src:
            return src.read(1).astype("float64")
    return np.asarray(band, dtype="float64")


def lst_vs_ndvi(ndvi, lst, output=None, ndvi_min=0):
    ndvi = read_band(ndvi).ravel()
    lst = read_band(lst).ravel()

    # Keep only pixels where both values are valid
    valid = np.isfinite(ndvi) & np.isfinite(lst) & (ndvi >= -1) & (ndvi <= 1)
    # Water has NDVI < 0 and is much cooler than land, which hides the land trend.
    # Set ndvi_min=None to keep every pixel.
    if ndvi_min is not None:
        valid &= ndvi >= ndvi_min
    ndvi = ndvi[valid]
    lst = lst[valid]

    # Pearson correlation and a straight-line fit: LST = slope * NDVI + intercept
    r = np.corrcoef(ndvi, lst)[0, 1]
    slope, intercept = np.polyfit(ndvi, lst, 1)

    # Millions of pixels are too many for a scatter plot, so show pixel density instead
    blues = LinearSegmentedColormap.from_list("blues", ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"])

    fig, ax = plt.subplots(figsize=(8, 6))
    hb = ax.hexbin(ndvi, lst, gridsize=120, bins="log", cmap=blues, mincnt=1)
    fig.colorbar(hb, ax=ax, label="Number of pixels")

    x = np.array([ndvi.min(), ndvi.max()])
    ax.plot(x, slope * x + intercept, color="#1a1a1a", linewidth=2)
    ax.text(0.02, 0.04,
            f"LST = {slope:.2f} × NDVI + {intercept:.2f}\nr = {r:.2f}   R² = {r ** 2:.2f}",
            transform=ax.transAxes, fontsize=10, color="#1a1a1a",
            bbox=dict(facecolor="white", edgecolor="#cccccc", boxstyle="round"))

    ax.set_title("LST vs NDVI")
    ax.set_xlabel("NDVI")
    ax.set_ylabel("LST (°C)")
    ax.grid(color="#e5e5e5", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)

    fig.tight_layout()
    if output:
        fig.savefig(output, dpi=150)
    plt.show()

    return r


if __name__ == "__main__":
    folder = "/Users/sadrealam/Desktop/uno/ndvi/data/"
    scene = "LC08_L1TP_040037_20260830_20260910_02_T1"

    red = read_band(folder + scene + "_B4.TIF")
    nir = read_band(folder + scene + "_B5.TIF")
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red)
    ndvi[(red == 0) | (nir == 0)] = np.nan

    r = lst_vs_ndvi(ndvi, folder + "lst_output.tif", output=folder + "lst_vs_ndvi.png")
    print("Correlation (r):", round(r, 3))
