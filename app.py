# -*- coding: utf-8 -*-
import os
import csv
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# 🌟【根本改善】リンダーのURL（トップページ）にアクセスされたら、index.htmlを画面として100%正しく表示する命令！
@app.route('/', methods=['GET'])
def index_page():
    html_file = "index.html"
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "❌ index.html が見つかりません。GitHubのトップ画面に配置してください。"

def load_jra_database():
    database_file = "racedata.txt"
    if not os.path.exists(database_file):
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
        return []

    race_data_store = []
    for line in raw_lines:
        line_clean = line.strip()
        if not line_clean: continue
        
        # カンマ、タブ、スペースでの区切りに全自動対応
        if ',' in line_clean:
            d = [x.strip() for x in line_clean.split(',')]
        elif '\t' in line_clean:
            d = [x.strip() for x in line_clean.split('\t')]
        else:
            d = [x.strip() for x in line_clean.split(' ') if x.strip()]
            
        if "日付" in d or "date" in d or "年月" in d: continue
        if len(d) < 8: continue
            
        try:
            date_raw = d[0].replace("-", "").replace("/", "").strip()
            date_clean = "20" + date_raw if len(date_raw) == 6 else date_raw
            venue_clean = d[1].strip()
            race_clean = d[2].replace(" ", "").replace("R", "").replace("r", "").strip() + "R"
            
            waku_clean = int(d[3])
            num_clean = int(d[4])
            name_clean = d[5].strip()
            jockey_clean = d[6].strip()
            odds_clean = float(d[7].replace("倍", "").strip())
            fuku_clean = float(d[8].replace("倍", "").strip()) if len(d) > 8 and d[8] else 0.0
            
            order_clean = 99
            if len(d) > 9:
                order_raw = d[9].replace("着", "").replace("確定", "").strip()
                if order_raw.isdigit(): order_clean = int(order_raw)
            
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
            
    return race_data_store

@app.route('/api/predict', methods=['GET'])
def get_prediction():
    cond_date = request.args.get('date', '').replace('-', '').replace('/', '').strip()
    cond_venue = request.args.get('venue', '').strip()
    cond_race = request.args.get('race', '').replace("R", "").replace("r", "").strip() + "R"
    
    db = load_jra_database()
    results = [r for r in db if r['date'] == cond_date and r['venue'] == cond_venue and r['race'] == cond_race]
    results.sort(key=lambda x: x['num'])
    
    response = jsonify(results)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
