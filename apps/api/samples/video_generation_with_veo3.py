import time
import random
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from dotenv import load_dotenv
import os

load_dotenv()

# https://ai.google.dev/gemini-api/docs/video?hl=ja&example=dialogue#python

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


prompt = """\
Do your hair now. First, Wet your hair: First, I'll lightly wet all of your hair. The key is to moisten it evenly from the roots to the ends.
"""

# Load the image using the Image class
image_path = "./resources/images/IMG_1206.jpg"
with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()

# Create Image object using the SDK's Image class
image = types.Image(imageBytes=image_bytes, mimeType="image/jpeg")


# Generate video with Veo 3 using the image with retry logic.
def generate_video_with_retry(max_retries=5):
    """Generate video with exponential backoff retry for rate limit errors."""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Generating video...")
            operation = client.models.generate_videos(
                # model="veo-3.0-generate-001",
                model="veo-3.0-fast-generate-001",
                # model="veo-2.0-generate-001",
                prompt=prompt,
                image=image,
            )
            print("Successfully initiated video generation")
            return operation

        except ClientError as e:
            # Check if it's a rate limit error (429)
            if e.status_code == 429:
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    base_wait = min(10 * (2**attempt), 300)  # Max 5 minutes
                    jitter = random.uniform(0, base_wait * 0.1)
                    wait_time = base_wait + jitter

                    print(f"Rate limit hit. Retrying after {wait_time:.1f} seconds...")
                    print(f"Error details: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"Failed after {max_retries} attempts due to rate limit")
                    raise
            else:
                # Non-rate-limit error, don't retry
                print(f"Non-retryable error: {e}")
                raise

        except Exception as e:
            # Unexpected error, don't retry
            print(f"Unexpected error: {e}")
            raise

    raise Exception(f"Failed to generate video after {max_retries} attempts")


# Generate video with retry logic
try:
    operation = generate_video_with_retry()
except Exception as e:
    print(f"Failed to generate video: {e}")
    exit(1)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("resources/videos/veo3_with_image_input.mp4")
print("Generated video saved to veo3_with_image_input.mp4")
