# 構造化出力で以下を生成する
# > class JapaneseStyleInfo(BaseModel):
# >     """Model for Japanese style information."""
# >     title: str = Field(description="日本語のタイトル（10文字以内）")
# >     description: str = Field(description="日本語の説明文（50文字以内）")
# $RAW_DESCRIPTIONはNano Bananaで生成した英語のスタイル説明です。
STYLE_INFO_GENERATION_PROMPT = """\
以下の英語のスタイル説明を日本語に翻訳し、魅力的なタイトル（10文字以内）と説明文（50文字以内）を生成してください。
タイトルはキャッチーで覚えやすいものにしてください。
説明文は簡潔でわかりやすくしてください。

英語の説明:
$RAW_DESCRIPTION
"""

STYLE_VARIATIONS = {
    # Male styles with hair only
    "male0_hair": "Textured and Dynamic Style Hair: Hair styled with matte-finish wax to create natural movement and dimension. Leave a few strands of hair falling over the forehead for a refined, effortless look. The hair has a subtle sheen without being shiny or greasy, achieving an elegant finish. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    "male1_hair": "Professional Quiff Style Hair: Hair styled with strong-hold gel, swept upward and backward to create an elegant quiff-to-slicked-back silhouette. Achieve a sophisticated, mature appearance that conveys competence and professionalism. The hair has a polished shine with clean, defined hairline and minimal flyaways. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    "male2_hair": "Trendy Center Part Style Hair: Popular Asian center part hairstyle with straight to slightly wavy hair divided clearly down the middle. Create subtle volume at the crown with hair flowing naturally from temples along the cheekbones. Achieve organized texture bundles with healthy shine (no greasiness). Add gentle waves at the tips for movement and dynamism. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    # Male styles with makeup only
    "male0_makeup": "Korean K-Beauty Style Makeup: Achieve a porcelain-like matte yet luminous skin finish inspired by K-POP idols and Korean actors. Emphasize eyes with subtle eyeshadow and eyeliner, and enhance lips with tinted color. Apply strategic shading and highlighting to create dimensional facial contours. Create a sophisticated, polished appearance that complements modern fashion trends. Keep the current hairstyle unchanged.",
    "male1_makeup": "Natural Grooming Style Makeup: The most common men's makeup approach designed to be undetectable. Use BB cream or concealer to naturally cover skin imperfections, dark circles, and acne marks. Groom and shape eyebrows for a clean, professional appearance. Focus on achieving a fresh, healthy complexion suitable for business and daily interactions. Keep the current hairstyle unchanged.",
    "male2_makeup": "Natural Style Makeup: Enhance natural features with a focus on clear skin and subtle definition. Use a light foundation or BB cream for an even skin tone, conceal any imperfections without masking the natural texture. Apply a neutral eyeshadow or a hint of warmth to the eyelids for a healthy glow. Define brows gently with a pencil or powder to frame the face naturally. Finish with a clear or natural-toned lip balm for hydration and a soft, healthy look. The aim is to create a fresh, effortless appearance that highlights the subject's inherent attractiveness. Keep the current hairstyle unchanged.",
    # Male styles with both hair and makeup
    "male0_both": "Textured and Dynamic Style Hair: Hair styled with matte-finish wax to create natural movement and dimension. Leave a few strands of hair falling over the forehead for a refined, effortless look. The hair has a subtle sheen without being shiny or greasy, achieving an elegant finish. Keep the original hair color unchanged. Makeup: Achieve a porcelain-like matte yet luminous skin finish inspired by K-POP idols and Korean actors. Emphasize eyes with subtle eyeshadow and eyeliner, and enhance lips with tinted color. Apply strategic shading and highlighting to create dimensional facial contours. Create a sophisticated, polished appearance that complements modern fashion trends.",
    "male1_both": "Professional Quiff Style Hair: Hair styled with strong-hold gel, swept upward and backward to create an elegant quiff-to-slicked-back silhouette. Achieve a sophisticated, mature appearance that conveys competence and professionalism. The hair has a polished shine with clean, defined hairline and minimal flyaways. Keep the original hair color unchanged. Makeup: The most common men's makeup approach designed to be undetectable. Use BB cream or concealer to naturally cover skin imperfections, dark circles, and acne marks. Groom and shape eyebrows for a clean, professional appearance. Focus on achieving a fresh, healthy complexion suitable for business and daily interactions.",
    "male2_both": "Trendy Center Part Style Hair: Popular Asian center part hairstyle with straight to slightly wavy hair divided clearly down the middle. Create subtle volume at the crown with hair flowing naturally from temples along the cheekbones. Achieve organized texture bundles with healthy shine (no greasiness). Add gentle waves at the tips for movement and dynamism. Keep the original hair color unchanged. Makeup: Enhance natural features with a focus on clear skin and subtle definition. Use a light foundation or BB cream for an even skin tone, conceal any imperfections without masking the natural texture. Apply a neutral eyeshadow or a hint of warmth to the eyelids for a healthy glow. Define brows gently with a pencil or powder to frame the face naturally. Finish with a clear or natural-toned lip balm for hydration and a soft, healthy look. The aim is to create a fresh, effortless appearance that highlights the subject's inherent attractiveness.",
    # Female styles with hair only
    "female0_hair": "Cute and Playful Style Hair: Create adorable impressions with soft, rounded silhouettes. Style options include fluffy bun hairstyles with wisps left around the face, or twin tails positioned high for energetic cuteness or low near the ears for a soft, girly impression. Add gentle curls to loose strands for extra sweetness. Maintain voluminous, bouncy textures throughout. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    "female1_hair": "Cool and Sharp Style Hair: Achieve a sleek, intellectual atmosphere with clean lines. Style straight hair with high shine for a sophisticated, polished look. Alternative wet-look styling with styling products creates a modern, editorial vibe. Keep hair smooth and controlled for a sharp, confident impression. Maintain the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    "female2_hair": "Natural and Effortless Style Hair: Create relaxed, gentle impressions with unstudied styling. Apply loose waves throughout the hair and tousle with fingers for airy, soft movement. Style in a low, casual ponytail with intentionally messy texture and face-framing pieces left out for a natural finish. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    # Female styles with makeup only
    "female0_makeup": "Natural Clean Beauty Makeup: Enhance natural skin texture to bring out healthy radiance. Apply foundation thinly to avoid heavy coverage. Choose skin-toned blush and lip colors that blend seamlessly. Use brown or beige eyeshadows for subtle contouring. Create a fresh, clean impression as if barely wearing makeup. Perfect for school, office, and daily occasions. Keep the current hairstyle unchanged.",
    "female1_makeup": "Feminine Romantic Makeup: Emphasize feminine charm and sweetness. Apply pink or coral blush softly for a gentle glow. Choose glossy pink or red lips for vibrant appeal. Use soft pink or brown eyeshadows for a tender atmosphere. Apply mascara thoroughly to make eyes appear larger. Perfect for dates and special occasions when you want to enhance feminine allure. Keep the current hairstyle unchanged.",
    "female2_makeup": "Cool Sophisticated Makeup: Create a strong, confident impression. Finish base makeup with semi-matte or matte texture. Use effective shading and highlighting to emphasize facial structure. Draw defined eyeliner and use cool-toned eyeshadows like grey, khaki, or brown for depth. Select calm lip colors like beige or bordeaux for an intellectual, mature atmosphere. Keep the current hairstyle unchanged.",
    # Female styles with both hair and makeup
    "female0_both": "Cute and Playful Style Hair: Create adorable impressions with soft, rounded silhouettes. Style options include fluffy bun hairstyles with wisps left around the face, or twin tails positioned high for energetic cuteness or low near the ears for a soft, girly impression. Add gentle curls to loose strands for extra sweetness. Maintain voluminous, bouncy textures throughout. Keep the original hair color unchanged. Makeup: Enhance natural skin texture to bring out healthy radiance. Apply foundation thinly to avoid heavy coverage. Choose skin-toned blush and lip colors that blend seamlessly. Use brown or beige eyeshadows for subtle contouring. Create a fresh, clean impression as if barely wearing makeup. Perfect for school, office, and daily occasions.",
    "female1_both": "Cool and Sharp Style Hair: Achieve a sleek, intellectual atmosphere with clean lines. Style straight hair with high shine for a sophisticated, polished look. Alternative wet-look styling with styling products creates a modern, editorial vibe. Keep hair smooth and controlled for a sharp, confident impression. Maintain the original hair color unchanged. Makeup: Emphasize feminine charm and sweetness. Apply pink or coral blush softly for a gentle glow. Choose glossy pink or red lips for vibrant appeal. Use soft pink or brown eyeshadows for a tender atmosphere. Apply mascara thoroughly to make eyes appear larger. Perfect for dates and special occasions when you want to enhance feminine allure.",
    "female2_both": "Natural and Effortless Style Hair: Create relaxed, gentle impressions with unstudied styling. Apply loose waves throughout the hair and tousle with fingers for airy, soft movement. Style in a low, casual ponytail with intentionally messy texture and face-framing pieces left out for a natural finish. Keep the original hair color unchanged. Makeup: Create a strong, confident impression. Finish base makeup with semi-matte or matte texture. Use effective shading and highlighting to emphasize facial structure. Draw defined eyeliner and use cool-toned eyeshadows like grey, khaki, or brown for depth. Select calm lip colors like beige or bordeaux for an intellectual, mature atmosphere.",
    # Neutral styles with hair only
    "neutral0_hair": "Cool and Sharp Style Hair: Eliminate excess elements and create linear silhouettes for an intellectual, refined atmosphere. Use wax or gel to achieve tight, controlled textures for a clean impression. Style with straight lines - keep bangs perfectly straight or sides tightly controlled to emphasize the cool aesthetic. Maintain sleek, minimalist styling throughout. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    "neutral1_hair": "Casual and Rough Style Hair: Embrace an unstudied, tousled aesthetic to bring out relaxed, natural charm. Create messy movement with perms or styling products for a carefree vibe. Focus on defined hair bundles and texture separation for lightness and dimensional depth. Style with intentional dishevelment for effortless appeal. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    "neutral2_hair": "Mode and Individualist Style Hair: Feature asymmetrical designs and textural variations for high-fashion, unique styling. Create mysterious atmospheres with left-right asymmetric silhouettes. Apply oils or gels for wet-look textures that add editorial, modern impressions. Emphasize avant-garde elements and artistic expression. Keep the original hair color unchanged. Keep the current facial features and makeup unchanged.",
    # Neutral styles with makeup only
    "neutral0_makeup": "Natural and Androgynous Style Makeup: Focus on skin prep and grooming. Use moisturizers on dry areas to create a healthy glow, and simply groom the eyebrows for a clean finish. Keep the current hairstyle unchanged.",
    "neutral1_makeup": "Cool and Edgy Style Makeup: A matte base and a sharp contour to define the face. A slightly winged eyeliner and a matte lip color that subdues natural tones will enhance a sleek, modern look. Keep the current hairstyle unchanged.",
    "neutral2_makeup": "Soft and Feminine Style Makeup: A dewy foundation with soft, sheer eyeshadows and blush in pink or orange tones. A glossy lip adds a touch of femininity and warmth. Keep the current hairstyle unchanged.",
    # Neutral styles with both hair and makeup
    "neutral0_both": "Cool and Sharp Style Hair: Eliminate excess elements and create linear silhouettes for an intellectual, refined atmosphere. Use wax or gel to achieve tight, controlled textures for a clean impression. Style with straight lines - keep bangs perfectly straight or sides tightly controlled to emphasize the cool aesthetic. Maintain sleek, minimalist styling throughout. Keep the original hair color unchanged. Makeup: Focus on skin prep and grooming. Use moisturizers on dry areas to create a healthy glow, and simply groom the eyebrows for a clean finish.",
    "neutral1_both": "Casual and Rough Style Hair: Embrace an unstudied, tousled aesthetic to bring out relaxed, natural charm. Create messy movement with perms or styling products for a carefree vibe. Focus on defined hair bundles and texture separation for lightness and dimensional depth. Style with intentional dishevelment for effortless appeal. Keep the original hair color unchanged. Makeup: A matte base and a sharp contour to define the face. A slightly winged eyeliner and a matte lip color that subdues natural tones will enhance a sleek, modern look.",
    "neutral2_both": "Mode and Individualist Style Hair: Feature asymmetrical designs and textural variations for high-fashion, unique styling. Create mysterious atmospheres with left-right asymmetric silhouettes. Apply oils or gels for wet-look textures that add editorial, modern impressions. Emphasize avant-garde elements and artistic expression. Keep the original hair color unchanged. Makeup: A dewy foundation with soft, sheer eyeshadows and blush in pink or orange tones. A glossy lip adds a touch of femininity and warmth.",
}

STYLE_IMAGE_GENERATION_PROMPT = """\
Transform the provided portrait with professional hairstyling and makeup artistry while preserving the subject's natural identity and facial features.

GENDER: $GENDER_TEXT
STYLE DIRECTION: $STYLE_VARIATION

Technical Requirements:
- Maintain photorealistic quality with natural lighting and skin texture
- Preserve the subject's unique facial structure, features, and identity completely
- Apply sophisticated hairstyling and makeup techniques following current beauty trends
- Ensure seamless integration between the original face and new styling elements
- Create a polished, magazine-quality result suitable for professional beauty portfolios

Output Requirements:
1. Generate a high-quality transformed image with the specified styling
2. Provide a concise description of the achieved look and key techniques applied

The transformation should appear natural and achievable through professional styling, avoiding any unrealistic or artificial modifications to the person's fundamental appearance.
"""

TRANSLATE_CUSTOM_REQUEST_PROMPT = """\
Translate the following Japanese text to English:
```
$CUSTOM_REQUEST
```

Please include only the English translation result, and do not include anything unnecessary.
"""

STYLE_CUSTOMIZE_PROMPT = """\
Generate a new realistic image that incorporates the following custom request: $CUSTOM_REQUEST
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
Given two images, generate a result image by applying only the following step to the first image.

INPUT IMAGES:
- Image 1: Current state (either an initial face or partially styled from previous steps)
- Image 2: Final target style (a reference for the complete transformation)

Current Step to Apply:
$STEP_TITLE_EN: $STEP_DESCRIPTION_EN

Tools Used: $TOOLS_NEEDED

**The generated image must be based on Image 1, with the features of the applied area matching Image 2 perfectly.**

Quality Standards:
- Seamless blending between modified and unmodified areas
- Consistent lighting and skin texture throughout
- Natural-looking intermediate result that could exist in real life
- Clear visible progress toward the final look without jumping ahead
"""

TUTORIAL_VIDEO_PROMPT_GENERATION_PROMPT = """\
動画生成モデルであるVeoの入力にあたる英語のプロンプトを生成してください。
現在、ヘアスタイルとメイクアップのチュートリアル動画をステップごとに作成しています。


# チュートリアル全体のステップの流れ (参考までに)
$RAW_DESCRIPTION


# 今回生成すべきステップ箇所の説明
$TITLE_EN: $DESCRIPTION_EN


# 利用可能な道具
（道具は全て使う必要はなく、必要なものを選択してください。）
$TOOLS_NEEDED


これらを考慮し、現在のステップ箇所をこなすために、ユーザーが最もためになるような動画シーンを生成したいです。
動画は現在のステップ内の**ワンシーン**である必要があります。
動画生成モデルが高精度に動画を生成できるようにシーンの情景を詳細に説明してください。
そのための、シーンの情景を詳細に説明した英語のプロンプトを生成してください。（英語のプロンプトのみ出力してください。）
"""

TUTORIAL_STEP_VIDEO_REQUIREMENTS = """\
Video Generation Requirements:
- Show the subject's hands performing the actual styling/makeup application technique
- Capture natural, realistic movements as if filming a real beauty tutorial
- Maintain consistent lighting and camera angle throughout the sequence
- Smooth, continuous action only one scene
- Natural pacing that matches real-world beauty application speed
"""

# TUTORIAL_STEP_VIDEO_GENERATION_PROMPT = """\
# Create a realistic tutorial one scene video showing the subject performing the specified beauty technique in real-time.
# 
# TUTORIAL STEP: $TITLE_EN
# DETAILED INSTRUCTION: $DESCRIPTION_EN
# TOOLS NEEDED: $TOOLS_NEEDED
# 
# Video Generation Requirements:
# - Show the subject's hands performing the actual styling/makeup application technique
# - Capture natural, realistic movements as if filming a real beauty tutorial
# - Display the gradual transformation as the technique is applied
# - Include appropriate tools being used (brushes, combs, styling products, etc.) (You don't need to use all the specified items. Please select the necessary tools for a portion of the operation.)
# - Maintain consistent lighting and camera angle throughout the sequence
# - Smooth, continuous action
# - only one scene
# 
# Visual Style:
# - Professional beauty tutorial aesthetic with clear visibility of the technique
# - Soft, flattering lighting that highlights the transformation process
# - Close-up framing that shows both the face and hands working
# - Smooth camera work without shakiness or abrupt movements
# - Natural pacing that matches real-world beauty application speed
# 
# The video should appear as if professionally filmed in a beauty studio setting, showing the authentic process of someone applying the specified technique to achieve the desired look.
# """
