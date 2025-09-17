#!/usr/bin/env python3
"""
シンプルなエンドポイントテスト
最小限のコードで画像をアップロードしてテスト
"""

import base64
import requests

# === 設定 ===
IMAGE_PATH = "/Users/s15112/Downloads/IMG_1206.jpg"  # テストする画像ファイルのパス
GENDER = "male"  # male, female, neutral から選択
API_URL = "http://localhost:8000/api/styles/generate"


# 画像を読み込んでBase64エンコード
with open(IMAGE_PATH, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# APIを呼び出し
response = requests.post(API_URL, json={"photo": image_base64, "gender": GENDER})

# 結果を表示
print(response.json())
