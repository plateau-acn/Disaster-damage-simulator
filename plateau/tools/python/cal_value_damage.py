#!/usr/bin/env python
# coding: utf-8

# cal_value_damage.py

# 建物と被害想定データから損傷率、損害額を算出する
# 算出結果をファイルに保存する処理
# 浸水と土砂の2ケースがありうるが、参照先のテーブルが変わるだけでロジックそのものは同じ

import arcpy
import pandas as pd
import os
import traceback

tables_folder_path=r"C:\plateau\tools\tables"
FeatureClass = r"C:\plateau\work\work.gdb\work_lod0_sims"

file_temp_damage_rate_output=os.path.join(tables_folder_path, "temp_damage_rate.csv")

# 損傷率・損害額計算（全体）
def cal_damagerate(row):
    '''
    損傷率・損害額演算の振り分け元
    被害がないことが明確な場合はこの時点で0を返却する
    返却対象の項目は以下の３つ
    ・建物被害額 : damage_value_building
    ・家財・屋内動産被害額 : damage_value_contents
    ・合計被害額 : damage_value_total
    '''
    
    # 共通処理：浸水していない場合は損傷なし
    list_res = []

    flood = row["sims_result"]

    if(pd.isnull(row["sims_result"]) or flood is None or flood == 0):
        list_res.append(0)
        list_res.append(0)
        list_res.append(0)
        return tuple(list_res)    
    

    # ブランクの場合はSKIPする
    buildingType = row["buildingType"]
    if(buildingType==0):
        list_res.append(0)
        list_res.append(0)
        list_res.append(0)
        return tuple(list_res)    


    # それ以外の場合は、損傷率算出ロジックを通るものとする
    return cal_damagerate_coms(row)

# 損傷率・損害額計算 ---------------------------------------------------------------------
def cal_damagerate_coms_pattern(row, table_file_building_damage_rate, key_building):
    '''
    損傷率算出処理。
    参照されるテーブルが異なっている（＋建物の場合のキー項目名が異なる）だけなので共通化してある
    フロア毎の評価額を使用して、それぞれの階に対して損傷率を取得して損害額を合計する
    そのため以下の値が必要となる
    ・平均階高
    ・フロア平均の資産評価額：建物
    ・階数：地上、地下
    ・被害深さ：浸水もしくは土砂の深さ
    '''

    list_res = []

    # シミュレーション種別を判定し、参照先テーブルファイルのプレフィックスを決める(0:浸水,1:土砂)
    sims_type_str = '浸水' if row["sims_type"] == 0 else '土砂'

    # 参照先テーブル指定 : 浸水か土砂かの差はプレフィックスの部分のみ
    file_building_damage_rate_coms_pattern = os.path.join(tables_folder_path, sims_type_str + table_file_building_damage_rate)

    # 平均階高取得
    floor_height = row["floor_height"]

    # フロア平均の資産評価額
    value_building_storeys = row["value_building_storeys"]

    # 参照テーブル読み込み
    df_file_building_damage_rate = pd.read_csv(file_building_damage_rate_coms_pattern)

    # <この判定では未満を抽出するようにしているので注意>
    floor_all_damage_building_rate = df_file_building_damage_rate.query('f_min < @floor_height and f_max >= @floor_height')[key_building].iat[0]


    # 地下の有無：地下がある場合は地下損害額の算出：地下は基本的にすべてになるので損害率から算出。それに地下階数を掛け合わせる
    storeysBelow = row["storeysBelow"]
    if(storeysBelow > 0):
        damage_below_building = floor_all_damage_building_rate * value_building_storeys * storeysBelow
    else:
        damage_below_building = 0


    # 地上分
    flood = row["sims_result"]
    storeysAbove = int(row["storeysAbove"])

    tmp_flood = flood
    tmp_damage_value_building = 0

    for count in (range(storeysAbove)):

        if(tmp_flood>floor_height):
            # 平均階高より浸水深のほうが大きい（その階は全滅）
            tmp_flood = tmp_flood - floor_height
            
            # 平均階高に対する損傷率×フロアごとの資産額
            tmp_damage_value_building = tmp_damage_value_building + floor_all_damage_building_rate * value_building_storeys
        else:
            damage_building_rate = df_file_building_damage_rate.query('f_min < @tmp_flood and f_max >= @tmp_flood')[key_building].iat[0]
            tmp_damage_value_building = tmp_damage_value_building + damage_building_rate * value_building_storeys
            
            # 平均階高のほうが浸水深が大きくなったので処理は終了。これより上階は被害なし
            break

    damage_value_total = tmp_damage_value_building + damage_below_building
    
    list_res.append(tmp_damage_value_building + damage_below_building)
    list_res.append(0)
    list_res.append(damage_value_total)
            
    
    return tuple(list_res)    


def cal_damagerate_coms(row):

    usage = int(row["bldg_usage1"])
    buildingStructureType = int(row["uro_BuildingDetailAttribute_buildingStructureType"])
    key_building = "{}_{}".format(usage, buildingStructureType)

    return cal_damagerate_coms_pattern(row, 
                                       "損傷率_建物.csv", 
                                       key_building)


def main():


    out_put_field = ["bldg_Building_gml_id", "buildingType",
                    "storeys", "storeysAbove", "storeysBelow", "floor_height", 
                    "value_building_storeys", "value_contents_storeys",
                    "value_building_Above", "value_building_Below",
                    "value_contents_Above", "value_contents_Below",
                    "sims_result", "sims_type",
                    "bldg_usage1","uro_BuildingDetailAttribute_buildingStructureType"]
    npa_result = arcpy.da.FeatureClassToNumPyArray(FeatureClass, out_put_field)
    df_result = pd.DataFrame(npa_result)


    list_params = ["damage_value_building", "damage_value_contents", "damage_value_total"]
    df_result[list_params] = df_result.apply(lambda x: cal_damagerate(x), axis=1, result_type='expand')
    df_result.to_csv(file_temp_damage_rate_output, columns=["bldg_Building_gml_id", "damage_value_building", "damage_value_contents", "damage_value_total"])





if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        # ログ出力等
        except_str = traceback.format_exc()
        arcpy.AddError(except_str)
