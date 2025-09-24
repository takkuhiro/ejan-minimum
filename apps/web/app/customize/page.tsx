"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ArrowLeft, Sparkles, Wand2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import { truncateTitle, truncateDescription } from "@/lib/utils";
import {
  isNetworkError,
  isTimeoutError,
  isServerError,
  retryWithBackoff,
} from "@/lib/api/error-handler";
import type { Style } from "@/types/api";
import Image from "next/image";

export default function CustomizePage() {
  const router = useRouter();
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
  const [currentStyle, setCurrentStyle] = useState<Style | null>(null);
  const [customRequest, setCustomRequest] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGeneratingTutorial, setIsGeneratingTutorial] = useState(false);

  useEffect(() => {
    // Load selected style from localStorage
    const savedStyle = localStorage.getItem("selectedStyle");

    if (!savedStyle) {
      // No style selected, redirect back to styles page
      toast.error("スタイルが選択されていません");
      router.push("/styles");
      return;
    }

    try {
      const styleData = JSON.parse(savedStyle) as Style & {
        originalImageUrl?: string;
      };

      // Extract originalImageUrl from the style data
      if (styleData.originalImageUrl) {
        setOriginalImageUrl(styleData.originalImageUrl);
      }

      setCurrentStyle(styleData);
    } catch (error) {
      console.error("Error loading style from localStorage:", error);
      toast.error("スタイル情報の読み込みに失敗しました");
      router.push("/styles");
    }
  }, [router]);

  const handleGenerate = async () => {
    if (!customRequest.trim() || !currentStyle || !originalImageUrl) return;

    setIsGenerating(true);
    const loadingToast = toast.loading("スタイルをカスタマイズ中...");

    try {
      // Call API to generate custom style using both original and style images
      const response = await retryWithBackoff(
        () =>
          apiClient.generateCustomStyle({
            originalImageUrl: originalImageUrl, // Original uploaded photo
            styleImageUrl: currentStyle.imageUrl, // Selected style image
            customRequest,
            title: currentStyle.title,
            description: currentStyle.description,
            rawDescription:
              currentStyle.rawDescription || currentStyle.description || "",
          }),
        {
          maxRetries: 2,
          baseDelay: 1000,
          maxDelay: 5000,
        },
      );

      toast.dismiss(loadingToast);

      if (response.success) {
        // Update the style with API response (response.data is the style directly)
        const style = response.data;
        setCurrentStyle(style);

        toast.success("スタイルを更新しました");
      } else {
        const error = response.error;
        let errorMessage = "カスタマイズに失敗しました";

        if (isNetworkError(error)) {
          errorMessage = "ネットワーク接続を確認してください";
        } else if (isTimeoutError(error)) {
          errorMessage = "処理がタイムアウトしました";
        } else if (isServerError(error)) {
          errorMessage = "サーバーエラーが発生しました";
        }

        toast.error(errorMessage, {
          duration: 5000,
          action: {
            label: "再試行",
            onClick: () => handleGenerate(),
          },
        });
      }
    } catch (error) {
      toast.dismiss(loadingToast);
      console.error("Error generating custom style:", error);
      toast.error("エラーが発生しました", {
        description:
          error instanceof Error ? error.message : "もう一度お試しください",
        duration: 5000,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleConfirm = async () => {
    if (!currentStyle || !originalImageUrl) {
      toast.error("必要な情報が不足しています");
      return;
    }

    setIsGeneratingTutorial(true);
    const loadingToast = toast.loading("チュートリアルを生成中...");

    // Prepare raw description
    const rawDescription =
      currentStyle.rawDescription || currentStyle.description || "";

    try {
      const request = {
        rawDescription: rawDescription,
        originalImageUrl: originalImageUrl,
        styleId: currentStyle.id,
        finalStyleImageUrl: currentStyle.imageUrl, // Use the current (possibly regenerated) style image
      };

      const response = await retryWithBackoff(
        () => apiClient.generateTutorial(request),
        {
          maxRetries: 3,
          baseDelay: 1000,
          maxDelay: 10000,
        },
      );

      toast.dismiss(loadingToast);

      if (response.success) {
        // Save tutorial data to localStorage
        localStorage.setItem("currentTutorial", JSON.stringify(response.data));

        toast.success("チュートリアルの生成を開始しました");

        // Navigate to tutorial page with the generated tutorial ID
        const tutorialId = response.data.id;
        router.push(`/tutorial?id=${tutorialId}`);
      } else {
        const error = response.error;
        let errorMessage = "チュートリアルの生成に失敗しました";

        if (isNetworkError(error)) {
          errorMessage = "ネットワーク接続を確認してください";
        } else if (isTimeoutError(error)) {
          errorMessage = "処理がタイムアウトしました。もう一度お試しください";
        } else if (isServerError(error)) {
          errorMessage =
            "サーバーエラーが発生しました。しばらく待ってから再試行してください";
        } else if (error.message) {
          errorMessage = error.message;
        }

        toast.error(errorMessage, {
          duration: 5000,
          action: {
            label: "再試行",
            onClick: () => handleConfirm(),
          },
        });
      }
    } catch (error) {
      toast.dismiss(loadingToast);
      console.error("Error generating tutorial:", error);
      toast.error("予期しないエラーが発生しました", { duration: 5000 });
    } finally {
      setIsGeneratingTutorial(false);
    }
  };

  // If no style loaded yet, show loading
  if (!currentStyle) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-card to-background flex items-center justify-center">
        <div className="text-center">
          <Sparkles className="w-12 h-12 mx-auto mb-4 animate-pulse text-primary" />
          <p className="text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    );
  }

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
          </div>
          <div className="w-20" />
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-[1fr_400px] gap-8">
            {/* Current Style Display - Larger */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    {truncateTitle(currentStyle.title, 15)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative w-full h-[500px] mb-4 bg-muted/10 rounded-lg">
                    <Image
                      src={currentStyle.imageUrl || "/placeholder.svg"}
                      alt={currentStyle.title}
                      fill
                      className="object-contain rounded-lg"
                    />
                  </div>
                  <p className="text-muted-foreground mb-4">
                    {truncateDescription(currentStyle.description, 50)}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Customization Panel - Narrower */}
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
                      どのように調整したいですか？
                    </label>
                    <Textarea
                      placeholder={
                        "例: もっと華やかにして、アイシャドウを濃くしたい"
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
                        調整中...
                      </>
                    ) : (
                      <>
                        <Wand2 className="w-4 h-4 mr-2" />
                        調整する
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Confirm Button - At the bottom, full width */}
          <div className="mt-8">
            <Button
              onClick={handleConfirm}
              size="lg"
              className="w-full"
              disabled={isGeneratingTutorial}
            >
              {isGeneratingTutorial ? (
                <>
                  <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                  生成中...
                </>
              ) : (
                "これで決まり"
              )}
            </Button>
            <p className="text-sm text-muted-foreground text-center mt-2">
              詳細な手順書を作成します（約3分）
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
