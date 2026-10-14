import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from lst_vs_ndvi import read_band


def lst_vs_ndwi(ndwi, lst, output=None, ndwi_max=0):
    ndwi = read_band(ndwi).ravel()
    lst = read_band(lst).ravel()

    # Keep only pixels where both values are valid
    valid = np.isfinite(ndwi) & np.isfinite(lst) & (ndwi >= -1) & (ndwi <= 1)
    # Water has NDWI > 0 and is much cooler than land, which hides the land trend.
    # Set ndwi_max=None to keep every pixel.
    if ndwi_max is not None:
        valid &= ndwi <= ndwi_max
    ndwi = ndwi[valid]
    lst = lst[valid]

    # Pearson correlation and a straight-line fit: LST = slope * NDWI + intercept
    r = np.corrcoef(ndwi, lst)[0, 1]
    slope, intercept = np.polyfit(ndwi, lst, 1)

    # Millions of pixels are too many for a scatter plot, so show pixel density instead
    blues = LinearSegmentedColormap.from_list("blues", ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"])

    fig, ax = plt.subplots(figsize=(8, 6))
    hb = ax.hexbin(ndwi, lst, gridsize=120, bins="log", cmap=blues, mincnt=1)
    fig.colorbar(hb, ax=ax, label="Number of pixels")

    x = np.array([ndwi.min(), ndwi.max()])
    ax.plot(x, slope * x + intercept, color="#1a1a1a", linewidth=2)
    ax.text(0.02, 0.04,
            f"LST = {slope:.2f} × NDWI + {intercept:.2f}\nr = {r:.2f}   R² = {r ** 2:.2f}",
            transform=ax.transAxes, fontsize=10, color="#1a1a1a",
            bbox=dict(facecolor="white", edgecolor="#cccccc", boxstyle="round"))

    ax.set_title("LST vs NDWI")
    ax.set_xlabel("NDWI")
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

    # NDWI (McFeeters) uses Green (B3) and NIR (B5)
    green = read_band(folder + scene + "_B3.TIF")
    nir = read_band(folder + scene + "_B5.TIF")
    with np.errstate(divide="ignore", invalid="ignore"):
        ndwi = (green - nir) / (green + nir)
    ndwi[(green == 0) | (nir == 0)] = np.nan

    r = lst_vs_ndwi(ndwi, folder + "lst_output.tif", output=folder + "lst_vs_ndwi.png")
    print("Correlation (r):", round(r, 3))
