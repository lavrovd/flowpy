""" flowpy
"""

import numpy as np
import matplotlib.pyplot as plt
from struct import unpack


def flow_write(filename, u, v):
    assert u.shape == v.shape
    with open(filename, "wb") as f:
        f.write(b'PIEH')
        np.flip(u.shape).astype("uint32").tofile(f)
        np.stack((u,v), axis=-1).flatten().astype("float32").tofile(f)


def flow_read(filename):
    with open(filename, 'rb') as f:
        assert f.read(4) == b'PIEH', filename + " does not seem to be a flo file."
        ny, nx = unpack("II", f.read(8))
        result = np.fromfile(f, dtype="float32").reshape((nx, ny, 2))
    return result[:,:,0], result[:,:,1]


def make_colorwheel():
    """ make_colorwheel
    """
    RY = 15
    YG = 6
    GC = 4
    CB = 11
    BM = 13
    MR = 6
    ncols = RY+YG+GC+CB+BM+MR

    colorwheel = np.zeros((ncols, 3), dtype="uint8")
    col = 0

    colorwheel[col:col+RY, 0] = 255
    colorwheel[col:col+RY, 1] = np.linspace(0, 255, RY, True)
    col += RY

    colorwheel[col:col+YG, 0] = np.linspace(255, 0, YG, True)
    colorwheel[col:col+YG, 1] = 255
    col += YG

    colorwheel[col:col+GC, 1] = 255
    colorwheel[col:col+GC, 2] = np.linspace(0, 255, GC, True)
    col += GC

    colorwheel[col:col+CB, 1] = np.linspace(255, 0, CB, True)
    colorwheel[col:col+CB, 2] = 255
    col += CB

    colorwheel[col:col+BM, 0] = np.linspace(0, 255, BM, True)
    colorwheel[col:col+BM, 2] = 255
    col += BM

    colorwheel[col:col+MR, 0] = 255
    colorwheel[col:col+MR, 2] = np.linspace(255, 0, MR, True)

    return colorwheel, ncols


def __get_polar(u, v):
    nan_mask = np.isnan(u) | np.isnan(v)
    u[nan_mask] = 0
    v[nan_mask] = 0

    radius = np.sqrt(u**2 + v**2)
    angle = np.arctan2(v, u)

    return radius, angle


def flow_to_color(u, v, min_is_black=True, max_norm=None):
    """ flow_to_color
    """
    radius, angle = __get_polar(u, v)
    if max_norm is None:
        max_norm = np.max(radius)
    radius *= (1/max_norm)

    wheel, ncols = make_colorwheel()

    hue_float = (-angle * (1 / np.pi) + 1) / 2 * (ncols - 1)
    hue_fraction, hue_floor = np.modf(hue_float)

    hue_floor = hue_floor.astype(int)
    hue_ceil = (hue_floor + 1) % ncols

    img = np.zeros(u.shape + (3,), dtype="uint8")

    # get color interpolation between values
    for i in range(3):
        col_floor = wheel[hue_floor, i] / 255
        col_ceil = wheel[hue_ceil, i] / 255
        col_interp = (1 - hue_fraction) * col_floor + hue_fraction * col_ceil
        mask = radius <= 1

        if min_is_black:
            col_interp[mask] = radius[mask] * col_interp[mask]
        else:
            col_interp[mask] = 1 - radius[mask] * (1 - col_interp[mask])

        col_interp[~mask] = 0.75 * col_interp[~mask]
        img[:, :, i] = 255 * col_interp


    return img


def show_flow_color(u, v, min_is_black=True, max_norm=None):
    flow_rgb = flow_to_color(u, v, min_is_black=min_is_black, max_norm=max_norm)

    plt.figure()
    plt.imshow(flow_rgb)
    plt.title("Color representation of the flow")
    plt.tight_layout()
    plt.show()


def show_flow_polar(u, v, max_norm=None):
    radius, angle = __get_polar(u, v)
    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(radius)
    plt.title("Flow radius in pixels")

    plt.subplot(1, 2, 2)
    plt.imshow(angle * (180 / np.pi))
    plt.title("Flow angle in degrees")

    plt.tight_layout()
    plt.show()


def show_flow_arrows(u, v, max_norm=None, min_is_black=True, sub_factors=None):
    h, w = u.shape
    y, x = np.mgrid[:h,:w]

    if sub_factors is None:
        sub_factor_x = int(w/25.5)
        sub_factor_y = int(h/25.5)
    elif isinstance(sub_factors, (tuple, list, np.ndarray)):
        sub_factor_x, sub_factor_y = sub_factors
    else:
        sub_factor_x = sub_factor_y = sub_factors

    plt.figure()

    flow_rgb = flow_to_color(u, v, min_is_black=min_is_black, max_norm=max_norm)
    plt.imshow(flow_rgb)

    plt.quiver(x[::sub_factor_x,::sub_factor_y],
               y[::sub_factor_x,::sub_factor_y],
               u[::sub_factor_x,::sub_factor_y],
               v[::sub_factor_x,::sub_factor_y],
               color="w" if min_is_black else "k")
    plt.ylim(h, 0)

    plt.title("Arrows (not true scale) over rgb representation")
    plt.tight_layout()
    plt.show()


def show_flow(u, v, max_norm=None, min_is_black=True, sub_factors=None):
    show_flow_arrows(u, v, max_norm=max_norm, min_is_black=min_is_black, sub_factors=sub_factors)
    show_flow_polar(u, v, max_norm=max_norm)


def test_pattern(width=151, min_is_black=True, show=True):
    """ test_pattern
    """
    truerange = 1
    extendedrange = truerange * 1.04

    hw = width // 2

    [x, y] = np.mgrid[:width, :width]

    u = x * extendedrange / hw - extendedrange
    v = y * extendedrange / hw - extendedrange

    img = flow_to_color(u / truerange, v / truerange, False, min_is_black)

    if show:
        plt.figure()
        plt.imshow(img)
        plt.hlines(hw, -.5, width-.5)
        plt.vlines(hw, -.5, width-.5)
        plt.title("test color pattern")
        plt.tight_layout()
        plt.show()

    return img
