~/develop/ejan-minimum/apps/api/samples (feat/kiro-ssd)+$
on video_generation
h_veo3.py  
Traceback (most recent call last):
  File "/Users/s15112/develop/ejan-minimum/apps/api/samples/video_generation_with_veo3.py", line 27, in <module>
    operation = client.models.generate_videos(
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/google/genai/models.py", line 7013, in generate_videos
    return self._generate_videos(
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/google/genai/models.py", line 6457, in _generate_videos
    response = self._api_client.request(
               ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/google/genai/_api_client.py", line 1290, in request
    response = self._request(http_request, http_options, stream=False)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/google/genai/_api_client.py", line 1126, in _request
    return self._retry(self._request_once, http_request, stream)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/tenacity/__init__.py", line 477, in __call__
    do = self.iter(retry_state=retry_state)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/tenacity/__init__.py", line 378, in iter
    result = action(retry_state)
             ^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/tenacity/__init__.py", line 420, in exc_check
    raise retry_exc.reraise()
          ^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/tenacity/__init__.py", line 187, in reraise
    raise self.last_attempt.result()
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/.local/share/uv/python/cpython-3.12.8-macos-aarch64-none/lib/python3.12/concurrent/futures/_base.py", line 449, in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/.local/share/uv/python/cpython-3.12.8-macos-aarch64-none/lib/python3.12/concurrent/futures/_base.py", line 401, in __get_result
    raise self._exception
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/tenacity/__init__.py", line 480, in __call__
    result = fn(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/google/genai/_api_client.py", line 1103, in _request_once
    errors.APIError.raise_for_response(response)
  File "/Users/s15112/develop/ejan-minimum/apps/api/.venv/lib/python3.12/site-packages/google/genai/errors.py", line 108, in raise_for_response
    raise ClientError(status_code, response_json, response)
google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}]}}