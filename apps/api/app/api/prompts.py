# 構造化出力で以下を生成する
# > class JapaneseStyleInfo(BaseModel):
# >     """Model for Japanese style information."""
# >     title: str = Field(description="日本語のタイトル（10文字以内）")
# >     description: str = Field(description="日本語の説明文（30文字以内）")
# $RAW_DESCRIPTIONはNano Bananaで生成した英語のスタイル説明です。
STYLE_INFO_GENERATION_PROMPT = """\
以下の英語のスタイル説明を日本語に翻訳し、魅力的なタイトル（10文字以内）と説明文（30文字以内）を生成してください。
タイトルはキャッチーで覚えやすいものにしてください。
説明文は簡潔でわかりやすくしてください。

英語の説明:
$RAW_DESCRIPTION
"""

STYLE_VARIATIONS = {
    "male0": "Fresh and Natural Style Hair: A neat, short haircut in a natural color. The front is kept down slightly to create a light, effortless feel. Use minimal wax to maintain the hair's natural flow. Makeup: Focus on grooming. Tidy the eyebrows and use lip balm to prevent dryness. Avoid foundation and keep the skin tone even for a healthy appearance.",
    "male1": "Sophisticated and Conservative Style Hair: Dark, short hair with a sleek side part or slicked-back style. A glossy finish adds a polished, intelligent impression. Makeup: Fill in sparse areas of the eyebrows for a defined shape. Use a translucent powder to control shine and maintain a clean look.",
    "male2": "Soft and Casual Style Hair: A light mushroom cut or a slightly longer wolf cut. Ash or beige hair colors will soften the overall look. Makeup: Use an eyebrow pencil to match the hair color and a light BB cream to even out the skin. A tinted lip balm adds a healthy flush of color.",
    "female0": "Elegant and Feminine Style Hair: A sleek, glossy long hairstyle or a soft, inward-curling bob. The bangs can be swept to the side or kept as a see-through fringe for a lighter feel. Makeup: A dewy, translucent base. Use soft, skin-tone eyeshadows like beige or pale pink. A glossy finish on the lips gives a natural, fresh look.",
    "female1": "Cool and Professional Style Hair: A sharp chin-length bob or a medium-length style with swept-back bangs. Dark hair colors create a sophisticated and composed impression. Makeup: A matte foundation. A sharp winged eyeliner adds a cool edge, while nude or deep-colored lipstick enhances the mature, elegant vibe.",
    "female2": "Cute and Doll-like Style Hair: A cute outward or inward-curling bob with straight-across bangs. Adding highlights can create a fun, dimensional look. Makeup: Use glittery eyeshadows and highlight the undereye bags (aegyo sal) for a sparkling effect. Pink or coral blush on the apples of the cheeks and a cute-colored lipstick complete the youthful look.",
    "neutral0": "Natural and Androgynous Style Hair: A versatile mushroom short cut or a short style that exposes the ears. Dark hair colors contribute to a cool and neutral look. Makeup: Focus on skin prep and grooming. Use moisturizers on dry areas to create a healthy glow, and simply groom the eyebrows for a clean finish.",
    "neutral1": "Cool and Edgy Style Hair: A wet-look short cut or a two-block undercut with shaved sides. These styles are distinct yet cohesive. Makeup: A matte base and a sharp contour to define the face. A slightly winged eyeliner and a matte lip color that subdues natural tones will enhance a sleek, modern look.",
    "neutral2": "Soft and Feminine Style Hair: A soft perm or a slightly longer wolf cut. Lighter hair colors create a gentle and relaxed atmosphere. Makeup: A dewy foundation with soft, sheer eyeshadows and blush in pink or orange tones. A glossy lip adds a touch of femininity and warmth.",
}

STYLE_IMAGE_GENERATION_PROMPT = """\
Generate a realistic image of the given face photo with a perfect $GENDER_TEXT hairstyle and makeup style.
STYLE: $STYLE_VARIATION
Please make the style natural and in line with current trends. Avoid anything too bizarre or extreme.
Keep the facial features and identity unchanged, only modify the hairstyle and makeup.
Provide a brief description of the style and steps to achieve this look and you must generate the image.
"""

GENERATE_TUTORIAL_STRUCTURE_PROMPT = """\
以下のスタイルを実現するための、詳細な段階別メイクアップとヘアスタイリングのチュートリアルを作成してください。

# スタイル説明
$STYLE_DESCRIPTION

$COMPLEMENT

以下の要素を含む完全なチュートリアルを提供してください。
- 明確なタイトルと説明
- 特定のテクニックを含む段階的な手順
- 各ステップの所要時間の目安
- 必要な道具と製品

**重要**: 各ステップには以下のフィールドを必ず含めてください：
   - title: 日本語のステップタイトル
   - description: 日本語の詳細な説明
   - title_en: 英語のステップタイトル（必須）
   - description_en: 英語の詳細な説明（必須）

ステップ数は**最大5ステップまで**にしてください。
このスタイルを学んでいる人にとって、明確でわかりやすい指示にしてください。
"""

TUTORIAL_STEP_IMAGE_GENERATION_PROMPT = """\
Generate completed face image with these changes to the provided face images.
When two images are provided:
- The first image is the previous step's result
- The second image is the final target style
Create a natural progression from the previous step towards the final style with the only following description. (Do not change other than the following description.)
$STEP_TITLE_EN: $STEP_DESCRIPTION_EN
Ensure the changes are appropriate for this specific step while maintaining consistency with the overall transformation.
"""

TUTORIAL_STEP_VIDEO_GENERATION_PROMPT = """\
Generate a video of the given face photo with the following instruction.
$TITLE_EN: $DESCRIPTION_EN
"""
