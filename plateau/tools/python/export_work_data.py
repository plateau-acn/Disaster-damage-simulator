#!/usr/bin/env python
# coding: utf-8

# export_lod0_lod1.py

import os

import arcpy
from_fc = arcpy.GetParameter(0)
dest_fc = arcpy.GetParameter(1)

def main():

    arcpy.conversion.ExportFeatures(
        in_features=from_fc,
        out_features=dest_fc
    )

if __name__ == "__main__":
    main()

