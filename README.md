# Land Surface Temperature (LST) from Landsat 8

LST is the temperature of the ground surface (not the air). We calculate it from
Landsat 8's **thermal band (Band 10)**, corrected using **NDVI** to estimate how
well each surface emits heat (emissivity).

## Inputs

| Input | File | Used for |
|-------|------|----------|
| Band 4 (Red) | `..._B4.TIF` | NDVI |
| Band 5 (NIR) | `..._B5.TIF` | NDVI |
| Band 10 (Thermal IR) | `..._B10.TIF` | Temperature |
| Metadata | `..._MTL.txt` | Conversion constants for Band 10 |

All files come from the same Landsat 8 **Level-1** scene (`LC08_L1TP_...`).

### Constants for Band 10 (read from the MTL file)

| Name | MTL key | Typical value |
|------|---------|---------------|
| `ML` | `RADIANCE_MULT_BAND_10` | 3.342e-4 |
| `AL` | `RADIANCE_ADD_BAND_10` | 0.1 |
| `K1` | `K1_CONSTANT_BAND_10` | 774.8853 |
| `K2` | `K2_CONSTANT_BAND_10` | 1321.0789 |

## Process (6 steps)

```
B10 ──► 1. Radiance ──► 2. Brightness Temp ─────────────┐
                                                         ├──► 6. LST
B4, B5 ──► 3. NDVI ──► 4. Veg. Proportion ──► 5. Emissivity ┘
```

### 1. Digital Number → TOA Radiance
Convert the raw pixel values (DN) of Band 10 to radiance.

```
Lλ = ML × DN + AL
```

### 2. Radiance → Brightness Temperature (BT)
Temperature the satellite "sees", assuming the surface is a perfect emitter.

```
BT = K2 / ln(K1 / Lλ + 1)        # Kelvin
```

### 3. NDVI
How green / vegetated each pixel is (−1 to 1).

```
NDVI = (B5 − B4) / (B5 + B4)
```

### 4. Proportion of Vegetation (Pv)
Fraction of each pixel covered by vegetation (0 to 1).

```
Pv = ((NDVI − NDVImin) / (NDVImax − NDVImin))²
```

### 5. Land Surface Emissivity (ε)
How efficiently the surface emits heat (soil ≈ 0.986, vegetation ≈ 0.99).

```
ε = 0.004 × Pv + 0.986
```

### 6. Land Surface Temperature
Correct BT for emissivity, then convert to Celsius.

```
LST = BT / (1 + (λ × BT / ρ) × ln(ε))     # Kelvin
LST_C = LST − 273.15                       # Celsius
```

- `λ` = 10.895 µm (centre wavelength of Band 10)
- `ρ` = h·c/σ = 14388 µm·K

## Output

A single-band GeoTIFF of LST in °C, with the same size and georeference as the input bands.

## Note: Level-2 shortcut
If you download a Landsat 8 **Level-2** product (`LC08_L2SP_...`), surface temperature
is already provided in `ST_B10.TIF`:

```
LST_C = ST_B10 × 0.00341802 + 149.0 − 273.15
```
