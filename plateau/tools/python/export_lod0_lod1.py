#!/usr/bin/env python
# coding: utf-8

# export_lod0_lod1.py

import os

import arcpy
target_gdb = arcpy.GetParameter(0) # 対象のLODが格納されているGDB
target_gdb = arcpy.GetParameterAsText(0)
output_gdb = r"C:\plateau\work\work.gdb"

def export_lod0(_target_gdb):
    arcpy.AddMessage("LOD0 : ExportFeatures")

    arcpy.conversion.ExportFeatures(
        in_features=os.path.join(_target_gdb, "lod0_Building"),
        out_features=os.path.join(output_gdb, "lod0_Building_ExportFeatures")
    )
    arcpy.AddMessage("LOD0 : ExportFeatures Done")

    
def export_lod1(_target_gdb):
    arcpy.AddMessage("LOD1 : ExportFeatures")
    arcpy.conversion.ExportFeatures(
        in_features=os.path.join(_target_gdb, "lod1_Building"),
        out_features=os.path.join(output_gdb, "lod1_Building_ExportFeatures")
    )
    arcpy.AddMessage("LOD01: ExportFeatures Done")


def main():

    arcpy.SetProgressor("step", 
                        "Copying LOD1/LOD0 to geodatabase...",
                        0, 2, 1)

    export_lod0(target_gdb)
    arcpy.SetProgressorLabel("Copying LOD1...")
    arcpy.SetProgressorPosition()


    export_lod1(target_gdb)

    arcpy.ResetProgressor()



if __name__ == "__main__":
    main()

