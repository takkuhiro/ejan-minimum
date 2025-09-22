"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Plus, Sparkles, Check, Clock, Wand2 } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import {
  ApiClientError,
  getErrorMessage,
  isNetworkError,
  isTimeoutError,
  isServerError,
  retryWithBackoff,
} from "@/lib/api/error-handler";
import { truncateTitle, truncateDescription } from "@/lib/utils";
import type { Style, StyleDetailResponse } from "@/types/api";

export default function StyleSelectionPage() {
  const router = useRouter();

  const [styles, setStyles] = useState<Style[]>([]);
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
  const [selectedStyle, setSelectedStyle] = useState<Style | null>(null);
  const [selectedStyleDetails, setSelectedStyleDetails] = useState<
    StyleDetailResponse["style"] | null
  >(null);
  const [customizationText, setCustomizationText] = useState("");
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [imageLoadErrors, setImageLoadErrors] = useState<Set<string>>(
    new Set(),
  );

  // Load styles and original image from localStorage on mount
  useEffect(() => {
    const savedStyles = localStorage.getItem("generatedStyles");
    const savedOriginalUrl = localStorage.getItem("originalImageUrl");

    // Debug: Log localStorage values
    console.log("Saved styles:", savedStyles);
    console.log("Saved original URL:", savedOriginalUrl);

    if (savedStyles) {
      try {
        setStyles(JSON.parse(savedStyles));
        if (savedOriginalUrl) {
          setOriginalImageUrl(savedOriginalUrl);
          console.log("Set original image URL:", savedOriginalUrl);
        } else {
          console.warn("No original URL found in localStorage");
        }
      } catch (error) {
        console.error("Error parsing localStorage styles:", error);
        toast.error("スタイル情報の読み込みに失敗しました");
        router.push("/");
      }
    } else {
      // No styles found, redirect to home
      toast.error("スタイル情報が見つかりません");
      router.push("/");
    }
  }, [router]);

  const handleStyleSelect = async (style: Style) => {
    setSelectedStyle(style);

    // Save selection to localStorage for recovery
    localStorage.setItem("selectedStyle", JSON.stringify(style));

    // Fetch style details with retry logic
    setIsLoadingDetails(true);
    try {
      const response = await retryWithBackoff(
        () => apiClient.getStyleDetail(style.id),
        {
          maxRetries: 2,
          baseDelay: 500,
          maxDelay: 3000,
        },
      );

      if (response.success) {
        setSelectedStyleDetails(response.data.style);
      } else {
        const error = response.error;
        let errorMessage = "スタイルの詳細を取得できませんでした";

        if (isNetworkError(error)) {
          errorMessage = "ネットワーク接続を確認してください";
        } else if (isTimeoutError(error)) {
          errorMessage = "リクエストがタイムアウトしました";
        } else if (isServerError(error)) {
          errorMessage = "サーバーエラーが発生しました";
        }

        toast.error(errorMessage, { duration: 3000 });
      }
    } catch (error) {
      console.error("Error fetching style details:", error);
      const errorMessage = getErrorMessage(error);
      toast.error(`エラー: ${errorMessage}`, { duration: 3000 });
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleCustomize = () => {
    // Navigate to customization page
    router.push("/customize");
  };

  const handleConfirmSelection = async () => {
    if (!selectedStyle) {
      console.error("handleConfirmSelection: No style selected");
      return;
    }

    if (!originalImageUrl) {
      console.error("handleConfirmSelection: No original image URL");
      toast.error("元画像が見つかりません");
      return;
    }

    console.log(
      "handleConfirmSelection: Starting with style:",
      selectedStyle.id,
    );
    console.log(
      "handleConfirmSelection: Customization text:",
      customizationText,
    );

    setIsGenerating(true);
    const loadingToast = toast.loading("チュートリアルを生成中...");

    // Use rawDescription from Gemini if available, otherwise fallback to description
    let rawDescription =
      selectedStyle.rawDescription || selectedStyle.description || "";

    // If there's customization text, append it to the raw description
    if (customizationText) {
      rawDescription = rawDescription
        ? `${rawDescription} カスタマイズ要望: ${customizationText}`
        : `カスタマイズ要望: ${customizationText}`;
    }

    try {
      const request = {
        rawDescription: rawDescription,
        originalImageUrl: originalImageUrl,
        styleId: selectedStyle.id, // Optional field for backward compatibility
        ...(customizationText && { customization: customizationText }),
      };

      console.log("handleConfirmSelection: API request:", request);

      const response = await retryWithBackoff(
        () => apiClient.generateTutorial(request),
        {
          maxRetries: 3,
          baseDelay: 1000,
          maxDelay: 10000,
        },
      );

      console.log("handleConfirmSelection: API response:", response);
      toast.dismiss(loadingToast);

      if (response.success) {
        console.log(
          "handleConfirmSelection: Success, tutorial data:",
          response.data,
        );

        // Save tutorial data and related information to localStorage
        localStorage.setItem("currentTutorial", JSON.stringify(response.data));
        localStorage.setItem("selectedStyleId", selectedStyle.id);
        localStorage.setItem(
          "selectedStyle",
          JSON.stringify({
            ...selectedStyle,
            rawDescription: rawDescription, // Save the raw description for potential retry
          }),
        );
        if (originalImageUrl) {
          localStorage.setItem("originalImageUrl", originalImageUrl);
        }

        toast.success("チュートリアルの生成を開始しました");

        // Navigate directly to tutorial page with the generated tutorial ID
        const tutorialId = response.data.id;
        console.log(
          "handleConfirmSelection: Navigating to tutorial:",
          tutorialId,
        );
        router.push(`/tutorial?id=${tutorialId}`);
      } else {
        console.error(
          "handleConfirmSelection: API request failed:",
          response.error,
        );
        const error = response.error;
        let errorMessage = "チュートリアルの生成に失敗しました";

        if (isNetworkError(error)) {
          console.error("handleConfirmSelection: Network error");
          errorMessage = "ネットワーク接続を確認してください";
        } else if (isTimeoutError(error)) {
          console.error("handleConfirmSelection: Timeout error");
          errorMessage = "処理がタイムアウトしました。もう一度お試しください";
        } else if (isServerError(error)) {
          console.error(
            "handleConfirmSelection: Server error, status:",
            error.statusCode,
          );
          errorMessage =
            "サーバーエラーが発生しました。しばらく待ってから再試行してください";
        } else if (error.message) {
          console.error(
            "handleConfirmSelection: Error message:",
            error.message,
          );
          errorMessage = error.message;
        }

        toast.error(errorMessage, {
          duration: 5000,
          action: {
            label: "再試行",
            onClick: () => handleConfirmSelection(),
          },
        });
      }
    } catch (error) {
      console.error("handleConfirmSelection: Unexpected error:", error);
      console.error("handleConfirmSelection: Error details:", {
        name: error instanceof Error ? error.name : "Unknown",
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      });
      toast.dismiss(loadingToast);

      if (error instanceof ApiClientError) {
        const apiError = error.error;
        if (isNetworkError(apiError) || isTimeoutError(apiError)) {
          toast.error("接続エラーが発生しました", {
            duration: 5000,
            action: {
              label: "再試行",
              onClick: () => handleConfirmSelection(),
            },
          });
        } else {
          toast.error(getErrorMessage(error), { duration: 5000 });
        }
      } else {
        toast.error("予期しないエラーが発生しました", { duration: 5000 });
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleImageError = (styleId: string) => {
    setImageLoadErrors((prev) => new Set(prev).add(styleId));
  };

  const getImageSrc = (style: Style) => {
    if (imageLoadErrors.has(style.id)) {
      return "/placeholder.svg";
    }
    return style.imageUrl || "/placeholder.svg";
  };

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
            <h1
              className="text-3xl font-bold text-primary"
              style={{ fontFamily: "var(--font-playfair)" }}
            >
              スタイルを選択
            </h1>
            <p className="text-muted-foreground mt-2">
              お気に入りのメイクアップスタイルを選んでください
            </p>
          </div>
          <div className="w-20" /> {/* Spacer for centering */}
        </div>

        {/* Original Image Display */}
        {originalImageUrl && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-center mb-4">
              アップロードした画像
            </h2>
            <div className="max-w-md mx-auto">
              <Card className="overflow-hidden">
                <div className="relative w-full h-80">
                  <Image
                    src={originalImageUrl}
                    alt="アップロードした画像"
                    fill
                    className="object-cover"
                    onError={(e) => {
                      console.error(
                        "Failed to load original image:",
                        originalImageUrl,
                      );
                      console.error("Error event:", e);
                      setOriginalImageUrl(null);
                    }}
                  />
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* Style Options */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-center mb-4">
            生成されたスタイル
          </h2>
        </div>

        {styles.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {styles.map((style) => (
              <Card
                key={style.id}
                className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                  selectedStyle?.id === style.id
                    ? "ring-2 ring-primary shadow-lg"
                    : ""
                }`}
                onClick={() => handleStyleSelect(style)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    handleStyleSelect(style);
                  }
                }}
              >
                <CardHeader className="pb-3">
                  <div className="relative">
                    <div className="relative w-full h-48 overflow-hidden rounded-lg">
                      <Image
                        src={getImageSrc(style)}
                        alt={style.title}
                        fill
                        className="object-cover"
                        onError={() => handleImageError(style.id)}
                      />
                    </div>
                    {selectedStyle?.id === style.id && (
                      <div className="absolute top-2 right-2 bg-primary text-primary-foreground rounded-full p-1">
                        <Check className="w-4 h-4 lucide-check" />
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <CardTitle className="text-lg mb-2">
                    {truncateTitle(style.title, 12)}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mb-3">
                    {truncateDescription(style.description, 35)}
                  </p>

                  {/* Display style details if selected and loaded */}
                  {selectedStyle?.id === style.id && selectedStyleDetails && (
                    <div className="mt-4 space-y-2">
                      {selectedStyleDetails.tools &&
                        selectedStyleDetails.tools.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {selectedStyleDetails.tools
                              .slice(0, 3)
                              .map((tool, index) => (
                                <Badge
                                  key={index}
                                  variant="secondary"
                                  className="text-xs"
                                >
                                  {tool}
                                </Badge>
                              ))}
                            {selectedStyleDetails.tools.length > 3 && (
                              <Badge variant="secondary" className="text-xs">
                                +{selectedStyleDetails.tools.length - 3}
                              </Badge>
                            )}
                          </div>
                        )}
                      {selectedStyleDetails.estimatedTime && (
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Clock className="w-3 h-3 mr-1" />
                          <span>{selectedStyleDetails.estimatedTime}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Loading skeleton for details */}
                  {selectedStyle?.id === style.id && isLoadingDetails && (
                    <div className="mt-4 space-y-2">
                      <Skeleton className="h-6 w-full" />
                      <Skeleton className="h-4 w-2/3" />
                    </div>
                  )}
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
                <p className="text-sm text-muted-foreground">
                  自分だけのオリジナルスタイルを作成
                </p>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardHeader className="pb-3">
                  <Skeleton className="w-full h-48 rounded-lg" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-6 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Customization Input */}
        {selectedStyle && (
          <Card className="max-w-2xl mx-auto mb-8">
            <CardContent className="pt-6">
              <Label htmlFor="customization">
                カスタマイズ要望（オプション）
              </Label>
              <div className="flex gap-2 mt-2">
                <Input
                  id="customization"
                  type="text"
                  placeholder="例：もっとナチュラルに、赤みを抑えて..."
                  value={customizationText}
                  onChange={(e) => setCustomizationText(e.target.value)}
                  className="flex-1"
                />
                <Button variant="outline" size="icon">
                  <Wand2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <Button
            onClick={handleConfirmSelection}
            disabled={!selectedStyle || isGenerating}
            size="lg"
            className="px-8"
          >
            {isGenerating ? (
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
          <p className="text-sm text-muted-foreground">
            スタイルを選択後、さらに細かい調整が可能です
          </p>
        </div>
      </div>
    </div>
  );
}
