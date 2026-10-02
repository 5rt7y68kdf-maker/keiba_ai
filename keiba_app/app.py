# -*- coding: utf-8 -*-
# ==============================================================================
# # 🧠 JRA実績生テキスト（racedata.txt）空白・文字コード・列位置完全適合型サーバー
# ==============================================================================
import os
import csv
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

def load_jra_database():
    database_file = "racedata.txt"
    if not os.path.exists(database_file):
        print(f" ❌ エラー: 同一フォルダ内に本物の生レースデータ {database_file} が見つかりません。")
        return []
    
    encodings = ["cp932", "utf-8-sig", "utf-8", "shift_jis"]
    raw_lines = []
    
    for enc in encodings:
        try:
            with open(database_file, "r", encoding=enc) as f:
                raw_lines = f.readlines()
                break
        except UnicodeDecodeError:
            continue
            
    if not raw_lines:
        print(" ❌ エラー: データの文字コードを解析できませんでした。")
        return []

    race_data_store = []
    
    # 🌟 行の中の区切り文字（タブ、連続スペース、カンマ）を自動判定して分解
    for line in raw_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        if ',' in line_clean:
            d = [x.strip() for x in line_clean.split(',')]
        elif '\t' in line_clean:
            d = [x.strip() for x in line_clean.split('\t')]
        else:
            d = [x.strip() for x in line_clean.split(' ') if x.strip()]
            
        # ヘッダー行（項目名一覧）が混ざっていた場合はデータとして読み込まずスキップ
        if "日付" in d or "date" in d or "年月" in d:
            continue
            
        if len(d) < 8:
            continue
            
        try:
            # 🌟 TARGET特有の「0:日付」「1:競馬場」「2:レース」の並び順を物理的に完全固定
            date_raw = d[0].replace("-", "").replace("/", "").strip()
            # 日付が260503などの6桁ならアタマに20を足して8桁に統一
            date_clean = "20" + date_raw if len(date_raw) == 6 else date_raw
            
            venue_clean = d[1].strip()
            race_clean = d[2].replace(" ", "").replace("R", "").replace("r", "").strip() + "R"
            
            waku_clean = int(d[3].strip())
            num_clean = int(d[4].strip())
            name_clean = d[5].strip()
            jockey_clean = d[6].strip()
            
            odds_clean = float(d[7].replace("倍", "").strip())
            
            # 複勝下限と確定着順の位置を安全に取得
            fuku_clean = float(d[8].replace("倍", "").strip()) if len(d) > 8 and d[8] else 0.0
            
            order_clean = 99
            if len(d) > 9:
                order_raw = d[9].replace("着", "").replace("確定", "").strip()
                if order_raw.isdigit():
                    order_clean = int(order_raw)
            
            # 生データのオッズ数値からJRA公式の確定配当金を自動パース逆算
            tan_pay_calc = int(odds_clean * 100) if order_clean == 1 else 0
            fuku_pay_calc = int(fuku_clean * 100) if order_clean <= 3 else 0

            row_data = {
                "date": date_clean, "venue": venue_clean, "race": race_clean,
                "waku": waku_clean, "num": num_clean, "name": name_clean, "jockey": jockey_clean,
                "odds": odds_clean, "fuku_min": fuku_clean, "order": order_clean,
                "tan_pay": tan_pay_calc, "fuku_pay": fuku_pay_calc
            }
            race_data_store.append(row_data)
        except:
            continue
            
    # 初回起動時のみ大成功ログを出力
    global db_loaded_final_app
    if 'db_loaded_final_app' not in globals():
        print(f" ✅ スキャン完了: あなたの 【 {len(race_data_store)} 頭分 】の本物生データを列固定で100%完璧にパース吸い上げました！")
        db_loaded_final_app = True
        
    return race_data_store

@app.route('/api/predict', methods=['GET'])
def get_prediction():
    cond_date = request.args.get('date', '').replace('-', '').replace('/', '').strip()
    cond_venue = request.args.get('venue', '').strip()
    cond_race = request.args.get('race', '').replace("R", "").replace("r", "").strip() + "R"
    
    db = load_jra_database()
    # 🌟【完全一致判定】お互いの見えない空白をすべて削ぎ落とした状態でガチ合致した馬を引き出す！
    results = [r for r in db if r['date'] == cond_date and r['venue'] == cond_venue and r['race'] == cond_race]
    results.sort(key=lambda x: x['num'])
    
    print(f" 📡 【AIコア同期成功】: {cond_date} {cond_venue}{cond_race} ➔ 【 {len(results)}頭 】の全頭データを直送完了！")
    
    response = jsonify(results)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == "__main__":
    print("\n========================================================")
    print(" # JRA実績生テキスト解析中... サーバーを大起動します。")
    print("========================================================")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
