#!/usr/bin/env python
# coding: utf-8

# export_lod0_lod1.py

import os

import arcpy
import pandas as pd


def main():

    # 対象データ
    target_fc = r"C:\plateau\work\sims.gdb\sim_landslide_tmp_SpatialJoin"

    out_put_field = ["Join_Count", "landslide_height", "LandslideSurface"]
    expression = '"Join_Count"=1'

    with arcpy.da.SearchCursor(target_fc, out_put_field, where_clause=expression) as s_cursor:
        for row in s_cursor:
            center_landslide_height = row[1]
            center_LandslideSurface = row[2]

            break
            

    # 土砂堆積深の標高値から堆積深を減算し、中心地点の標高値を取得する
    center_elevation_tp = center_LandslideSurface - center_landslide_height

    # この値をフィールド演算で中心地点の標高値として付与する
    arcpy.management.CalculateField(
        target_fc,
        "elevation_tp",
        center_elevation_tp,
        field_type="DOUBLE"
    )
    


if __name__ == "__main__":
    main()

