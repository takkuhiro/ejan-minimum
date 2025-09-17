import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

# https://ai.google.dev/gemini-api/docs/video?hl=ja&example=dialogue#python

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


prompt = """\
Do your hair now. First, Wet your hair: First, I'll lightly wet all of your hair. The key is to moisten it evenly from the roots to the ends.
"""

# Load the image using the Image class
image_path = "./images/IMG_1206.jpg"
with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()

# Create Image object using the SDK's Image class
image = types.Image(imageBytes=image_bytes, mimeType="image/jpeg")

# Generate video with Veo 3 using the image.
operation = client.models.generate_videos(
    model="veo-3.0-generate-001",
    prompt=prompt,
    image=image,
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("videos/veo3_with_image_input.mp4")
print("Generated video saved to veo3_with_image_input.mp4")
