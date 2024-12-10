
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('lidar_map.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

from os import path

from onecode import checkbox, dropdown, file_input, file_output, Logger, slider

from .map_isolines import create_map_png, draw_colored_map, draw_isocontours, grid_lidar


def run():
    lidar_file = file_input(
        key="lid_file",
        value="",
        label="LIDAR file :",
        types=[("LAZ", ".laz")],
        multiple=False,
    )

    resolution = slider(
        key="res_slider",
        value=1.0,
        label="Grid resolution :",
        min=0.5,
        max=5.0,
        step=0.5,
    )

    grid = grid_lidar(lidar_file=lidar_file, resolution=resolution)

    min_level = slider(
        key="min_level",
        value=-40.,
        label="Elevation min level :",
        min=-40.,
        max=4000.,
        step=1.,
    )

    max_level = slider(
        key="max_level",
        value=4000.,
        label="Elevation min level :",
        min=-40.,
        max=4000.,
        step=1.,
    )

    color_map = dropdown(
        key="cmap_dropdown",
        value="gist_earth",
        options=["gist_earth", "terrain"],
        label="Terrain colormap :",
        multiple=False,
    )

    log_scale_color = checkbox(
        key="scale_color_checkbox",
        value=True,
        label="Logarithmic color scaling",
    )

    shadding = checkbox(
        key="shadding_checkbox",
        value=True,
        label="Hill shadding",
    )

    map_img = draw_colored_map(
        m=grid,
        min_level=min_level,
        max_level=max_level,
        cmap=color_map,
        log_scale_color=log_scale_color,
        shadding=shadding,
    )

    isocontours = checkbox(
        key="isocontours_checkbox",
        value=True,
        label="Isocontours",
    )

    alpha_isolines = slider(
        key="isolines_slider",
        value=128,
        label="Alpha isolines :",
        min=0.0,
        max=255.0,
        step=1.0,
    )

    iso_img = None
    if isocontours:
        iso_img = draw_isocontours(
            m=grid,
            alpha_isolines=int(alpha_isolines),
        )

    create_map_png(
        name=file_output(
            key="png_output",
            value="map",
            # make_path=True,
        ),
        map=map_img,
        isocontours=iso_img
    )

    Logger.info("=== map created! ===")
