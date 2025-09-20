"""
Veo3動画生成Cloud Function

このCloud Functionは、画像URLとプロンプトを受け取り、
Veo3 APIを使用して動画を生成し、Google Cloud Storageに保存します。
"""

import os
import time
import uuid
import requests
import random
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()


def generate_video(request) -> Dict[str, Any]:
    """
    Veo3を使用して動画を生成するメイン関数

    Args:
        request: HTTPリクエストオブジェクト

    Returns:
        Dict: 生成結果（成功時はvideo_url、失敗時はerror）
    """
    start_time = time.time()

    try:
        # リクエストデータの取得と検証
        request_data = request.get_json()
        if not request_data:
            return {"status": "failed", "error": "No JSON data provided"}

        # 必須フィールドの検証（promptまたはinstruction_textのいずれかが必要）
        image_url = request_data.get("image_url")
        prompt = request_data.get("prompt") or request_data.get("instruction_text")

        if not image_url:
            return {"status": "failed", "error": "Missing required field: image_url"}
        if not prompt:
            return {"status": "failed", "error": "Missing required field: prompt or instruction_text"}

        step_number = request_data.get("step_number", 1)
        target_gcs_path = request_data.get("target_gcs_path")

        # Google API クライアントの初期化
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"status": "failed", "error": "GOOGLE_API_KEY not configured"}

        genai_client = genai.Client(api_key=api_key)

        # 画像データの取得
        response = requests.get(image_url)
        if response.status_code != 200:
            return {"status": "failed", "error": f"Failed to fetch image from {image_url}"}

        image_bytes = response.content
        image = types.Image(imageBytes=image_bytes, mimeType="image/jpeg")

        # Veo3による動画生成開始（リトライロジック付き）
        operation = generate_video_with_retry(
            genai_client,
            prompt=prompt,
            image=image,
            step_number=step_number
        )

        if not operation:
            return {
                "status": "failed",
                "error": "Failed to generate video after multiple retries due to rate limit"
            }

        # ポーリングによる生成完了待機（最大540秒）
        timeout_seconds = 540
        while not operation.done:
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                return {"status": "failed", "error": "Video generation timeout after 540 seconds"}

            time.sleep(10)
            operation = genai_client.operations.get(operation)

        # 動画データの取得
        video = operation.response.generated_videos[0]
        video_data = genai_client.files.download(file=video.video)

        # Cloud Storageに保存
        bucket_name = os.getenv("STORAGE_BUCKET")
        if not bucket_name:
            return {"status": "failed", "error": "STORAGE_BUCKET not configured"}

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        # ファイルパスを決定
        if target_gcs_path:
            # 指定されたパスを使用（bucketプレフィックスを除去）
            if target_gcs_path.startswith(f"gs://{bucket_name}/"):
                blob_path = target_gcs_path[len(f"gs://{bucket_name}/"):]
            elif target_gcs_path.startswith(f"{bucket_name}/"):
                blob_path = target_gcs_path[len(f"{bucket_name}/"):]
            else:
                blob_path = target_gcs_path
        else:
            # デフォルトのパスを使用
            filename = generate_unique_filename(f"video-step-{step_number}", "mp4")
            blob_path = f"videos/{filename}"

        blob = bucket.blob(blob_path)

        # 動画データをアップロード
        blob.upload_from_string(video_data, content_type="video/mp4")

        # 公開URLの生成
        video_url = blob.public_url

        duration = int(time.time() - start_time)

        return {
            "status": "success",
            "video_url": video_url,
            "duration": duration
        }

    except Exception as e:
        duration = int(time.time() - start_time)
        return {
            "status": "failed",
            "error": str(e),
            "duration": duration
        }


def generate_video_with_retry(
    client: genai.Client,
    prompt: str,
    image: types.Image,
    step_number: int = 1,
    max_retries: int = 5
) -> Optional[Any]:
    """
    指数バックオフによるリトライを行いながらVeo3で動画生成

    Args:
        client: Google AI クライアント
        prompt: 動画生成用のプロンプト
        image: 入力画像
        step_number: ステップ番号（ログ出力用）
        max_retries: 最大リトライ回数

    Returns:
        生成操作オブジェクト、失敗時はNone
    """
    for attempt in range(max_retries):
        try:
            # 動画生成を試行
            operation = client.models.generate_videos(
                # model="veo-3.0-generate-001",
                model="veo-3.0-fast-generate-001",
                # model="veo-2.0-generate-001",
                prompt=prompt,
                image=image,
            )
            return operation

        except ClientError as e:
            # Rate limitエラー（429）の場合のみリトライ
            if e.status_code == 429:
                if attempt < max_retries - 1:
                    # 指数バックオフの計算
                    # 基本待機時間: 10秒, 20秒, 40秒, 80秒, 160秒（最大約2.7分）
                    # ジッターを追加して同時リトライを防ぐ
                    base_wait = min(10 * (2 ** attempt), 300)  # 最大5分
                    jitter = random.uniform(0, base_wait * 0.1)  # 最大10%のジッター
                    wait_time = base_wait + jitter

                    print(f"Step {step_number}: Rate limit hit. Retry {attempt + 1}/{max_retries} "
                          f"after {wait_time:.1f} seconds")
                    time.sleep(wait_time)
                else:
                    # 最後のリトライも失敗
                    print(f"Step {step_number}: Failed after {max_retries} retries due to rate limit")
                    return None
            else:
                # Rate limit以外のエラーはリトライしない
                print(f"Step {step_number}: Non-retryable error: {e}")
                raise
        except Exception as e:
            # その他の予期しないエラーもリトライしない
            print(f"Step {step_number}: Unexpected error: {e}")
            raise

    return None


def generate_unique_filename(prefix: str, extension: str) -> str:
    """
    ユニークなファイル名を生成

    Args:
        prefix: ファイル名のプレフィックス
        extension: 拡張子

    Returns:
        str: ユニークなファイル名
    """
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}-{timestamp}-{unique_id}.{extension}"


# Cloud Functions エントリーポイント
def main(request):
    """
    Cloud Functionsのエントリーポイント

    Args:
        request: Cloud Functions HTTPリクエストオブジェクト

    Returns:
        Tuple[str, int]: (JSON文字列, HTTPステータスコード)
    """
    import json

    # CORS ヘッダーを設定
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    # OPTIONS リクエスト (CORS プリフライト) の処理
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    # POST リクエストのみ処理
    if request.method != 'POST':
        return (json.dumps({"status": "failed", "error": "Only POST method allowed"}), 405, headers)

    # 動画生成処理を実行
    result = generate_video(request)

    # ステータスコードを決定
    status_code = 200 if result["status"] == "success" else 500

    return (json.dumps(result), status_code, headers)
