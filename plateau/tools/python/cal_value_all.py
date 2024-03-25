#!/usr/bin/env python
# coding: utf-8

# cal_value.py

# 建物単価を取得する

import arcpy
import pandas as pd
import os
import traceback

FeatureClass = r"C:\plateau\work\work.gdb\work_lod0"
tables_folder_path=r"C:\plateau\tools\tables"


# -----------------------------------------------------------------
'''
建物単価の取得
'''
# -----------------------------------------------------------------

def get_value_building_per_sqare_meter_coms(row):
    '''
    用途と構造種別から建物単価を取得
    '''
    
    # 設定テーブル読み込み
    file_value_building_per_sqare_meter=os.path.join(tables_folder_path, "評価額_建物単価.csv")

    list_res = []
   
    usage = int(row["bldg_usage1"])
    buildingStructureType = int(row["uro_BuildingDetailAttribute_buildingStructureType"])

    list_res.append(
        pd.read_csv(file_value_building_per_sqare_meter).set_index('建物用途').at[usage, "構造種別_{}".format(buildingStructureType)]
    )
    list_res.append(0)
    return list_res

   
def get_value_building_per_sqare_meter(row):
    '''
    建物単価の取得
    '''

    buildingType = row["buildingType"]
    
    list_res = []
    # 建物種別によって資産評価額の算出方法は変わる
    if(buildingType == 0):
        # ブランク(buildingType : 0)の場合はSKIP
        list_res.append(0)
        list_res.append(0)
    else:
        # ブランク以外
        list_res = get_value_building_per_sqare_meter_coms(row)

    return tuple(list_res)

# -----------------------------------------------------------------
'''
主処理：以下をまとめて実施
・建物単価を取得
・平均階高の算出
・建物評価額の算出
・最後に処理結果をCSVに出力
'''
# -----------------------------------------------------------------
def main():

    # Set the progressor
    arcpy.SetProgressor("step", "評価額算出処理...", 0, 8, 1)


    # 一連の評価額算出処理に必要な項目を抽出
    out_put_field = ["bldg_Building_gml_id",
                     "bldg_usage1", "buildingType", "height",
                     "uro_BuildingDetailAttribute_buildingStructureType", "uro_buildingIDAttribute_prefecture",
                     "totalFloorArea",
                    #  "value_building", 
                     "storeysAbove", "storeysBelow", "storeys",
                     "houseType"
                     ]

    # out_put_field = ["bldg_Building_gml_id","bldg_usage1","uro_BuildingDetailAttribute_buildingStructureType", "buildingType", "uro_buildingIDAttribute_prefecture"]
    npa_result = arcpy.da.FeatureClassToNumPyArray(FeatureClass, out_put_field)
    df_result = pd.DataFrame(npa_result)

    ## ログ
    arcpy.SetProgressorPosition()
    arcpy.AddMessage("Get Data : Done")

    arcpy.SetProgressorLabel("建物単価、屋内動産単価 : 取得")
    # 全種別の建物単価と商業施設の屋内動産の単価を取得    
    list_params = ["value_building_per_sqare_meter", "value_indoor_movable_property"]
    df_result[list_params] = df_result.apply(lambda x: get_value_building_per_sqare_meter(x), axis=1, result_type='expand')

    ## ログ
    arcpy.SetProgressorPosition()
    arcpy.AddMessage("get_value_building_per_sqare_meter : Done")

    arcpy.SetProgressorLabel("平均階高 : 算出")
    # 平均階高の算出 : floor_height -> height / storeysAbove
    df_result["floor_height"] = df_result["height"] / df_result["storeysAbove"]
    arcpy.SetProgressorPosition()

    arcpy.SetProgressorLabel("建物評価額 : 算出")
    # 建物評価額を算出 -> value_building : value_building_per_sqare_meter * totalFloorArea
    df_result["value_building"] = df_result["value_building_per_sqare_meter"] * df_result["totalFloorArea"]

    ## ログ
    arcpy.SetProgressorPosition()
    arcpy.AddMessage("calculation value_building : Done")

    # ここで必要な項目についてはフィールド定義を補填しておく
    list_params = ["value_building_Above", "value_building_Below"]
    df_result[list_params] = tuple([0.0, 0.0])
    list_params = ["value_contents_Above", "value_contents_Below", "value_contents"]
    df_result[list_params] = tuple([0.0, 0.0, 0.0])

    # 算出結果をCSV出力する
    file_temp_output=os.path.join(tables_folder_path, "temp_value_all.csv")
    df_result.to_csv(file_temp_output, columns=["bldg_Building_gml_id", 
                                                "value_building_per_sqare_meter", "value_indoor_movable_property",
                                                "floor_height",
                                                "value_building",
                                                "value_building_Above", "value_building_Below",
                                                "value_contents_Above", "value_contents_Below", 
                                                "value_contents"
                                                ])

    arcpy.SetProgressorPosition()

if __name__ == "__main__":
    try:
        
        main()

    except Exception as e:
        # ログ等
        except_str = traceback.format_exc()
        arcpy.AddError(except_str)
