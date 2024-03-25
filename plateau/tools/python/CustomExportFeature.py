#!/usr/bin/env python
# coding: utf-8

# CustomExportFeature.py

# フィールド定義を無視してFeatureをコピーする


import arcpy


input_features = arcpy.GetParameter(0)
output_features = arcpy.GetParameter(1)


arcpy.conversion.ExportFeatures(
    in_features=input_features,
    out_features=output_features
)

