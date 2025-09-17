import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from main import generate_video


class TestVideoGeneration:
    """Veo3動画生成Functionのテスト"""

    def test_generate_video_success(self):
        """正常な動画生成のテスト"""
        # Given: 有効なリクエストデータ
        request_data = {
            "image_url": "https://storage.googleapis.com/bucket/test-image.jpg",
            "prompt": "髪を濡らす動作の解説動画",
            "step_number": 1
        }

        # Mock request object
        mock_request = Mock()
        mock_request.get_json.return_value = request_data

        # Mock Veo3 API response
        mock_operation = Mock()
        mock_operation.done = True
        mock_video = Mock()
        mock_video.video = Mock()
        mock_operation.response.generated_videos = [mock_video]

        with patch('main.genai.Client') as mock_client, \
             patch('main.storage.Client') as mock_storage_client, \
             patch('main.time.sleep'), \
             patch('main.requests.get') as mock_requests, \
             patch.dict('main.os.environ', {'GOOGLE_API_KEY': 'test_key', 'STORAGE_BUCKET': 'test_bucket'}):

            # Setup mocks
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.content = b'image_data'

            mock_client.return_value.models.generate_videos.return_value = mock_operation
            mock_client.return_value.operations.get.return_value = mock_operation
            mock_client.return_value.files.download.return_value = b'video_data'

            mock_bucket = Mock()
            mock_blob = Mock()
            mock_blob.public_url = "https://storage.googleapis.com/bucket/video-123.mp4"
            mock_bucket.blob.return_value = mock_blob
            mock_storage_client.return_value.bucket.return_value = mock_bucket

            # When: 関数を実行
            result = generate_video(mock_request)

            # Then: 期待される結果を確認
            assert result["status"] == "success"
            assert "video_url" in result
            assert result["video_url"].startswith("https://storage.googleapis.com/")
            assert "duration" in result

    def test_generate_video_invalid_request(self):
        """無効なリクエストのテスト"""
        # Given: 無効なリクエストデータ（必須フィールド欠如）
        mock_request = Mock()
        mock_request.get_json.return_value = {
            "prompt": "動画生成プロンプト"
            # image_urlが欠如
        }

        # When: 関数を実行
        result = generate_video(mock_request)

        # Then: エラーが返される
        assert result["status"] == "failed"
        assert "error" in result
        assert "image_url" in result["error"]

    def test_generate_video_veo3_api_failure(self):
        """Veo3 API呼び出し失敗のテスト"""
        # Given: 有効なリクエストだが、API呼び出しが失敗
        request_data = {
            "image_url": "https://storage.googleapis.com/bucket/test-image.jpg",
            "prompt": "動画生成プロンプト",
            "step_number": 1
        }

        mock_request = Mock()
        mock_request.get_json.return_value = request_data

        with patch('main.genai.Client') as mock_client, \
             patch('main.requests.get') as mock_requests, \
             patch.dict('main.os.environ', {'GOOGLE_API_KEY': 'test_key', 'STORAGE_BUCKET': 'test_bucket'}):
            # Setup image request mock
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.content = b'image_data'

            # API呼び出しでエラーが発生
            mock_client.return_value.models.generate_videos.side_effect = Exception("API Error")

            # When: 関数を実行
            result = generate_video(mock_request)

            # Then: エラーが返される
            assert result["status"] == "failed"
            assert "error" in result

    def test_generate_video_timeout(self):
        """タイムアウト処理のテスト"""
        # Given: Veo3の処理が長時間かかる場合
        request_data = {
            "image_url": "https://storage.googleapis.com/bucket/test-image.jpg",
            "prompt": "動画生成プロンプト",
            "step_number": 1
        }

        mock_request = Mock()
        mock_request.get_json.return_value = request_data

        # Always return pending operation (never completes)
        mock_operation = Mock()
        mock_operation.done = False

        with patch('main.genai.Client') as mock_client, \
             patch('main.time.sleep'), \
             patch('main.time.time') as mock_time, \
             patch('main.requests.get') as mock_requests, \
             patch.dict('main.os.environ', {'GOOGLE_API_KEY': 'test_key', 'STORAGE_BUCKET': 'test_bucket'}):

            # Simulate timeout (start + 600 seconds)
            mock_time.side_effect = [0, 650]  # start=0, check=650 (timeout)

            # Setup image request mock
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.content = b'image_data'

            mock_client.return_value.models.generate_videos.return_value = mock_operation
            mock_client.return_value.operations.get.return_value = mock_operation

            # When: 関数を実行
            result = generate_video(mock_request)

            # Then: タイムアウトエラーが返される
            assert result["status"] == "failed"
            assert "timeout" in result["error"].lower()

    def test_generate_unique_filename(self):
        """ユニークなファイル名生成のテスト"""
        from main import generate_unique_filename

        # When: ファイル名を2回生成
        filename1 = generate_unique_filename("video", "mp4")
        filename2 = generate_unique_filename("video", "mp4")

        # Then: 異なるファイル名が生成される
        assert filename1 != filename2
        assert filename1.startswith("video-")
        assert filename1.endswith(".mp4")
        assert filename2.startswith("video-")
        assert filename2.endswith(".mp4")