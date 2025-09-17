from google import genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 与えられた顔写真に対して、髪型をばっちりセットした場合のリアルな画像を生成してください。ただし、流行に沿った髪型でナチュラルにお願いします。奇抜すぎるものは避けてください。そして、そのための髪型のセット方法をアドバイスしてください。髪型以外の要素は変更しないでください。
prompt = "Generate a realistic image of a given face photo with a perfect hairstyle. However, please make the hairstyle natural and in line with current trends, and avoid anything too bizarre. Please do not change any elements other than the hairstyle. And please give me advice on how to style the hair to achieve that look."

image = Image.open("./images/IMG_1212.jpg")

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt, image],
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("images/generated_image.png")
