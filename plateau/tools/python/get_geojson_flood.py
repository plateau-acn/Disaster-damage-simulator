#!/usr/bin/env python
# coding: utf-8

# get_geojson_flood.py

# 浸水もしくは土砂シミュレーションシステムに対してAPIでGeoJson形式のデータを取得し、
# 取得結果をファイルに保存する処理


import requests
import traceback
import os

import arcpy
target_layer = arcpy.GetParameter(0) # シミュレーション中心レイヤー
flood_height = arcpy.GetParameter(1) # 浸水深
flood_radius = arcpy.GetParameter(2) # 範囲


params_message = "flood_height : {0} , flood_radius : {1} ".format(flood_height, flood_radius)
arcpy.AddMessage(params_message)

params = {
    'flood_height':flood_height ,
    'flood_radius':flood_radius
    }

folder_path = r"C:\plateau\tools\tables"
dl_file_path = os.path.join(folder_path, "sim_flood.geojson")

url = 'https://oyo-mvp-alsv.com/api/make_flood_prediction'

def get_geojson(url, _params, _dl_file_path):

    arcpy.AddMessage("get_geojson : request" + url)
    # API Call
    res = requests.post(url, json=_params)

    print(res)
    print(res.url)
    print(res.headers['Content-Type'])

    # Json形式に変換
    import json
    json_data = res.json()

    # ファイル出力
    arcpy.AddMessage("get_geojson : file output : " + _dl_file_path)
    with open(_dl_file_path, 'w') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    arcpy.AddMessage("get_geojson : file output : done")


def main():

    list_target = []
    # 対象のフィーチャ数分繰り返す
    with arcpy.da.SearchCursor(target_layer, ["x", "y"]) as SelCur:
        for SelDat in SelCur:
            list_target.append(SelDat)


    for t in list_target:
        print(t)
        #id = t[0]
        x = t[0]
        y = t[1]
        arcpy.AddMessage(x)
        arcpy.AddMessage(y)

        params["lon"] = x
        params["lat"] = y

        get_geojson(url, params, dl_file_path)

        # 基本的には一つのポイントのみを対象にするのでループを繰り返すことはない想定。
        # 条件を指定するのであれば、リストを作成する際に使用して、対象を先頭行にもってくること
        break

    # パラメータで取得した浸水深をポイントデータに付与しておく
    arcpy.management.CalculateField(target_layer,
                                    "flood_height",
                                    flood_height
                                    )


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        # ログとか
        except_str = traceback.format_exc()
        arcpy.AddError(except_str)
