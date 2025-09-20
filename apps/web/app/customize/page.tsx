"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Sparkles, Wand2, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/api/client";
import { truncateTitle, truncateDescription } from "@/lib/utils";
import type { Style } from "@/types/api";

// Extended style type for UI display
interface ExtendedStyle extends Style {
  name: string;
  steps?: string[];
  tools?: string[];
}

// Mock style data - will be replaced with API data
const mockStyleData: Record<string, ExtendedStyle> = {
  "1": {
    id: "1",
    name: "ナチュラル美人",
    title: "ナチュラル美人",
    imageUrl: "/natural-japanese-makeup-result.jpg",
    description:
      "自然な美しさを引き出すソフトメイクで、日常使いにぴったりのスタイルです。",
    steps: [
      "ベースメイクで肌を整える",
      "アイブロウで眉毛を自然に整える",
      "アイシャドウでナチュラルなグラデーション",
      "マスカラで自煨なまつ毛を演出",
      "チークで血色感をプラス",
      "リップで仕上げ",
    ],
    tools: [
      "ファンデーション",
      "アイブロウペンシル",
      "アイシャドウパレット",
      "マスカラ",
      "チーク",
      "リップ",
    ],
  },
};

export default function CustomizePage() {
  const _router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [selectedStyleId, setSelectedStyleId] = useState<string | null>(null);
  const [customRequest, setCustomRequest] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStyle, setCurrentStyle] = useState<ExtendedStyle>(
    mockStyleData["1"],
  );
  const [isFromScratch, setIsFromScratch] = useState(false);

  useEffect(() => {
    // Get style ID from URL params
    const styleId = searchParams.get("style");

    if (styleId && styleId in mockStyleData) {
      setSelectedStyleId(styleId);
      setCurrentStyle(mockStyleData[styleId as keyof typeof mockStyleData]);
    } else {
      setIsFromScratch(true);
    }
  }, [searchParams]);

  const handleGenerate = async () => {
    if (!customRequest.trim()) return;

    setIsGenerating(true);

    try {
      // Call API to generate custom style
      const response = await apiClient.generateCustomStyle({
        styleId: selectedStyleId || undefined,
        customRequest,
        isFromScratch,
      });

      if (response.success) {
        // Update the style with API response
        const { style } = response.data;
        setCurrentStyle({
          ...style,
          name: truncateTitle(style.title, 15),
          steps: style.steps || currentStyle.steps,
          tools: style.tools || currentStyle.tools,
        });

        toast({
          title: "スタイルを更新しました",
          description: "カスタマイズ内容が反映されました",
        });
      } else {
        throw new Error(response.error.message);
      }
    } catch (error) {
      // For testing, fall back to mock data
      if (process.env.NODE_ENV === "test" || !process.env.NEXT_PUBLIC_API_URL) {
        await new Promise((resolve) => setTimeout(resolve, 3000));
        setCurrentStyle({
          ...currentStyle,
          name: "カスタマイズされたスタイル",
          title: "カスタマイズされたスタイル",
          description: `${currentStyle.description} カスタマイズされたスタイルです。`,
        });
        toast({
          title: "スタイルを更新しました",
          description: "カスタマイズ内容が反映されました",
        });
      } else {
        toast({
          title: "エラーが発生しました",
          description:
            error instanceof Error ? error.message : "もう一度お試しください",
          variant: "destructive",
        });
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleConfirm = () => {
    // Since customization page is currently not actively used,
    // we'll keep this function empty for now
    // TODO: Implement proper tutorial generation flow if this page is reactivated
    toast({
      title: "この機能は現在利用できません",
      description: "スタイル選択ページからお試しください",
      variant: "destructive",
    });
  };

  const handleStartFromScratch = () => {
    setIsFromScratch(true);
    setSelectedStyleId(null);
    setCurrentStyle({
      id: "custom",
      name: "カスタムスタイル",
      title: "カスタムスタイル",
      imageUrl: "/custom-makeup-placeholder.jpg",
      description: "あなただけのオリジナルメイクアップスタイルを作成します。",
      steps: [],
      tools: [],
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-card to-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Link href="/styles">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              戻る
            </Button>
          </Link>
          <div className="text-center flex-1">
            <h1
              className="text-3xl font-bold text-primary"
              style={{ fontFamily: "var(--font-playfair)" }}
            >
              スタイル調整
            </h1>
            <p className="text-muted-foreground mt-2">
              お好みに合わせて細かく調整できます
            </p>
          </div>
          <div className="w-20" />
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Current Style Display */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {currentStyle.name}
                  {!isFromScratch && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleStartFromScratch}
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      0から設定する
                    </Button>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <img
                  src={currentStyle.imageUrl || "/placeholder.svg"}
                  alt={currentStyle.name}
                  className="w-full h-64 object-cover rounded-lg mb-4"
                />
                <p className="text-muted-foreground mb-4">
                  {truncateDescription(currentStyle.description, 50)}
                </p>

                {currentStyle.steps.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-semibold mb-2">メイク手順:</h3>
                    <ol className="list-decimal list-inside space-y-1 text-sm">
                      {currentStyle.steps.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {currentStyle.tools.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2">必要な道具:</h3>
                    <div className="flex flex-wrap gap-2">
                      {currentStyle.tools.map((tool) => (
                        <Badge key={tool} variant="outline">
                          {tool}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Customization Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Wand2 className="w-5 h-5 mr-2" />
                  カスタマイズ
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    {isFromScratch
                      ? "どのようなメイクをしたいですか？"
                      : "どのように調整したいですか？"}
                  </label>
                  <Textarea
                    placeholder={
                      isFromScratch
                        ? "例: 韓国風のメイクで、ピンクのリップと猫目アイラインを使いたい"
                        : "例: もっと華やかにして、アイシャドウを濃くしたい"
                    }
                    value={customRequest}
                    onChange={(e) => setCustomRequest(e.target.value)}
                    rows={4}
                  />
                </div>

                <Button
                  onClick={handleGenerate}
                  disabled={!customRequest.trim() || isGenerating}
                  className="w-full"
                >
                  {isGenerating ? (
                    <>
                      <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-4 h-4 mr-2" />
                      生成する
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Confirm Button */}
            <Card>
              <CardContent className="pt-6">
                <Button onClick={handleConfirm} size="lg" className="w-full">
                  これで決まり
                </Button>
                <p className="text-sm text-muted-foreground text-center mt-2">
                  詳細な手順書を作成します（約3分）
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
