from google import genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 与えられた2つの顔写真はメイク前とメイク後の写真です。これらの中間に当たる写真を生成してください。
prompt = "Given two facial images, one before makeup and one after, generate a photo that represents an intermediate stage between them."
# 与えられた2つの顔写真はメイク前とメイク後の写真です。 メイク前: female.jpeg, メイク後: comp.png これらの中間に当たる画像として、髪のセットをしていない状態の写真を生成してください。
prompt = "Given two face photos, the first is a photo before makeup, and the second is a photo with all makeup completed. Please generate a photo of the first photo with the following makeup applied. $MAKEUP_DESCRIPTION"

image0 = Image.open("resources/images/female.jpeg")
image1 = Image.open("resources/images/comp.png")

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt, image0, image1],
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("resources/images/generated_image1.png")
