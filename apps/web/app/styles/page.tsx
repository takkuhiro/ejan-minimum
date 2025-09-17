"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Plus, Sparkles, Check } from "lucide-react"
import Link from "next/link"

// Mock data for generated styles
const mockStyles = [
  {
    id: 1,
    name: "ナチュラル美人",
    description: "自然な美しさを引き出すソフトメイク",
    imageUrl: "/natural-japanese-makeup-style.jpg",
    tags: ["ナチュラル", "デイリー", "上品"],
  },
  {
    id: 2,
    name: "エレガント",
    description: "洗練された大人の魅力を演出",
    imageUrl: "/elegant-japanese-makeup-style.jpg",
    tags: ["エレガント", "フォーマル", "大人っぽい"],
  },
  {
    id: 3,
    name: "トレンディ",
    description: "最新トレンドを取り入れたモダンスタイル",
    imageUrl: "/trendy-japanese-makeup-style.jpg",
    tags: ["トレンド", "モダン", "個性的"],
  },
]

export default function StyleSelectionPage() {
  const [selectedStyle, setSelectedStyle] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleStyleSelect = (styleId: number) => {
    setSelectedStyle(styleId)
  }

  const handleCustomize = () => {
    // Navigate to customization page
    window.location.href = "/customize"
  }

  const handleConfirmSelection = () => {
    if (!selectedStyle) return

    setIsLoading(true)
    // Navigate to customization page with selected style
    setTimeout(() => {
      window.location.href = `/customize?style=${selectedStyle}`
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-card to-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              戻る
            </Button>
          </Link>
          <div className="text-center flex-1">
            <h1 className="text-3xl font-bold text-primary" style={{ fontFamily: "var(--font-playfair)" }}>
              スタイルを選択
            </h1>
            <p className="text-muted-foreground mt-2">お気に入りのメイクアップスタイルを選んでください</p>
          </div>
          <div className="w-20" /> {/* Spacer for centering */}
        </div>

        {/* Original Photo */}
        <div className="mb-8">
          <Card className="max-w-sm mx-auto">
            <CardHeader>
              <CardTitle className="text-center text-lg">あなたの写真</CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src="/japanese-person-portrait.png"
                alt="Original photo"
                className="w-full h-48 object-cover rounded-lg"
              />
            </CardContent>
          </Card>
        </div>

        {/* Style Options */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {mockStyles.map((style) => (
            <Card
              key={style.id}
              className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                selectedStyle === style.id ? "ring-2 ring-primary shadow-lg" : ""
              }`}
              onClick={() => handleStyleSelect(style.id)}
            >
              <CardHeader className="pb-3">
                <div className="relative">
                  <img
                    src={style.imageUrl || "/placeholder.svg"}
                    alt={style.name}
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  {selectedStyle === style.id && (
                    <div className="absolute top-2 right-2 bg-primary text-primary-foreground rounded-full p-1">
                      <Check className="w-4 h-4" />
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <CardTitle className="text-lg mb-2">{style.name}</CardTitle>
                <p className="text-sm text-muted-foreground mb-3">{style.description}</p>
              </CardContent>
            </Card>
          ))}

          {/* Custom Option */}
          <Card
            className="cursor-pointer transition-all duration-200 hover:shadow-lg border-dashed border-2 border-muted-foreground/30 hover:border-primary/50"
            onClick={handleCustomize}
          >
            <CardContent className="flex flex-col items-center justify-center h-full min-h-[300px] text-center">
              <div className="bg-muted rounded-full p-6 mb-4">
                <Plus className="w-8 h-8 text-muted-foreground" />
              </div>
              <CardTitle className="text-lg mb-2">カスタマイズ</CardTitle>
              <p className="text-sm text-muted-foreground">自分だけのオリジナルスタイルを作成</p>
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <Button onClick={handleConfirmSelection} disabled={!selectedStyle || isLoading} size="lg" className="px-8">
            {isLoading ? (
              <>
                <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                処理中...
              </>
            ) : (
              "このスタイルで進む"
            )}
          </Button>
        </div>

        {/* Help Text */}
        <div className="text-center mt-8">
          <p className="text-sm text-muted-foreground">スタイルを選択後、さらに細かい調整が可能です</p>
        </div>
      </div>
    </div>
  )
}
