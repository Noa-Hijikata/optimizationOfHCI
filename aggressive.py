import pandas as pd, json, os, collections

LOG_FILE = "logs.csv"
CONFIG_DIR = "personalized"
os.makedirs(CONFIG_DIR, exist_ok=True)

logs = pd.read_csv(LOG_FILE, dtype=str)
logs["value"] = logs["value"].fillna("")

for uid, g in logs.groupby("user_id"):
    if not uid or uid.strip() == "":
        continue
    # カテゴリ追加ボタン頻度
    cat_cnt = collections.Counter(
        [
            v.replace(" 追加", "")
            for v in g[g["event"] == "button"]["value"]
            if "追加" in str(v)
        ]
    )
    category_order = [c for c, _ in cat_cnt.most_common()] + [
        c for c in ["交通費", "宿泊費", "会議費", "物品", "その他"] if c not in cat_cnt
    ]

    # アクションボタン順
    act_cnt = collections.Counter(
        [
            v
            for v in g[(g["event"] == "button") & (~g["value"].str.contains("追加"))][
                "value"
            ]
        ]
    )
    base = ["登録", "下書き保存", "クリア"]
    button_order = [b for b, _ in act_cnt.most_common() if b in base] + [
        b for b in base if b not in act_cnt
    ]

    # サジェスト
    stations = [
        v for v in g[g["field"].isin(["交通費_出発", "交通費_到着"])]["value"] if v
    ]
    vendors = [
        v for v in g[g["field"].isin(["店名", "宿泊名", "vendor"])]["value"] if v
    ]
    phrases = [v for v in g[g["field"] == "摘要"]["value"] if v]

    def topn(lst, n=5):
        cnt = collections.Counter(lst)
        return [k for k, _ in cnt.most_common(n)]

    # デフォルト値（最頻）
    project = g[g["field"] == "プロジェクト"]["value"].mode()
    tax = g[g["field"] == "税"]["value"].mode()
    pay = g[g["field"] == "支払"]["value"].mode()

    cfg = {
        "category_order": (
            category_order[:5]
            if category_order
            else ["交通費", "会議費", "宿泊費", "物品", "その他"]
        ),
        "button_order": button_order if button_order else base,
        "suggest": {
            "stations": topn(stations, 5) or ["東京", "品川", "新大阪"],
            "vendors": topn(vendors, 5) or [],
            "purpose_phrases": topn(phrases, 5) or ["顧客訪問", "定例会議", "出張"],
        },
        "defaults": {
            "project": (project.iloc[0] if not project.empty else "A-42"),
            "tax": int(tax.iloc[0]) if not tax.empty else 10,
            "payment": (pay.iloc[0] if not pay.empty else "立替"),
        },
    }
    with open(os.path.join(CONFIG_DIR, f"{uid}.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"generated: {uid}.json")
