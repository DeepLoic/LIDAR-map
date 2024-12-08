import math

import laspy
from matplotlib import cm, colors, colormaps
import numpy as np
from PIL import Image
from scipy.interpolate import griddata
from skimage.filters import gaussian
from skimage.measure import find_contours


def grid_lidar(lidar_file: str, resolution: float = 1.0) -> np.ndarray:
    las = laspy.read(lidar_file)

    x = np.asarray(las.x[las.classification == 2])
    y = np.asarray(las.y[las.classification == 2])
    z = np.asarray(las.z[las.classification == 2])

    grid_x, grid_y = np.mgrid[x.min():x.max():resolution, y.min():y.max():resolution]

    return np.rot90(griddata((x, y), z, (grid_x, grid_y), method="nearest"))


def draw_isocontours(
    m: np.ndarray,
    sigma: float = 1.0,
    num_level: int = 200,
    alpha_isolines: int = 128
) -> Image:
    m = gaussian(m, sigma=sigma, preserve_range=True)

    levels = np.logspace(0, 1, num=num_level) * np.linspace(
        m.min(),
        m.max() / 10,
        num_level
    )

    cts = []
    for level in levels:
        cts += find_contours(
            m,
            level=level,
            fully_connected="high",
            positive_orientation="high"
        )

    isolines = np.full([m.shape[1], m.shape[0], 4], (255, 255, 255, 0), np.uint8)
    for p in cts:
        a = np.asarray(p).astype(np.int32)

        filtx = a[:, 0] == (0.0 or isolines.shape[0] or isolines.shape[0])
        filty = a[:, 1] == (0.0 or isolines.shape[1] or isolines.shape[1])

        cx, cy = np.count_nonzero(filtx), np.count_nonzero(filty)

        if (cx and cy) != 0:
            if cx >= cy:
                a = a[np.invert(filtx)]
            elif cy > cx:
                a = a[np.invert(filty)]

        isolines[a[:, 0], a[:, 1]] = (0, 0, 0, alpha_isolines)

    return Image.fromarray(isolines).convert("RGBA")


def hill_shade(m: np.ndarray, az: float = 30.0, alt: float = 30.0) -> np.ndarray:
    x, y = np.gradient(m)

    if az <= 360.0:
        az = 360.0 - az
        az_rad = math.radians(az)
    else:
        raise ValueError()

    if alt <= 90.0:
        alt_rad = math.radians(alt)
    else:
        raise ValueError()

    slope = np.pi / 2.0 - np.arctan(np.sqrt(x**2, y**2))
    aspect = np.arctan2(-x, y)
    shaded = np.sin(alt_rad) * np.sin(slope) + np.cos(alt_rad) * np.cos(slope) * np.cos(
        (az_rad - np.pi / 2.0) - aspect
    )

    return 255.0 * (shaded + 1.0) / 2.0


def draw_colored_map(
    m: np.ndarray,
    min_level: float,
    max_level: float,
    cmap: str = "gist_earth",
    log_scale_color: bool = True,
    shadding: bool = True,
    blend_shadding: float = 0.2
) -> Image:
    if log_scale_color:
        norm = colors.SymLogNorm(linthresh=100, vmin=min_level, vmax=max_level)
    else:
        norm = colors.Normalize(vmin=min_level, vmax=max_level)
    scale = cm.ScalarMappable(norm=norm, cmap=colormaps[cmap])

    img1 = Image.fromarray(np.uint8(scale.to_rgba(m) * 255))

    if shadding:
        shade = hill_shade(m)

        img2 = Image.fromarray(
            np.uint8(colormaps["Greys"](shade / np.nanmax(shade)) * 255)
        ).convert("RGBA")

        return Image.blend(img1, img2, blend_shadding)

    else:
        return img1


def create_map_png(name: str, map: Image, isocontours: Image = None):
    if isocontours is not None:
        map.paste(isocontours, (0, 0), isocontours)

    map.save(f"./{name}.png")


if __name__ == "__main__":
    grid = grid_lidar("LHD_FXX_0919_6601_PTS_C_LAMB93_IGN69.copc.laz", resolution=0.5)

    # min_level, max_level = -40., 4000.
    min_level, max_level = grid.min(), grid.max()

    iso = draw_isocontours(grid, sigma=5.0, alpha_isolines=160)
    map = draw_colored_map(grid, min_level, max_level, shadding=True)

    map.paste(iso, (0, 0), iso)
    map.save("./map.png")
    iso.convert("RGB").save("./contours.png")
