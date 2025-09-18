"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Upload, Sparkles, Users, Palette } from "lucide-react";
import { PhotoUpload } from "@/components/photo-upload";
import { apiClient } from "@/lib/api/client";
import {
  ApiClientError,
  getErrorMessage,
  isNetworkError,
  isTimeoutError,
  isValidationError,
  isServerError,
  retryWithBackoff,
} from "@/lib/api/error-handler";
import { toast } from "sonner";
import type { Gender } from "@/types/api";

export default function WelcomePage() {
  const router = useRouter();
  const [selectedGender, setSelectedGender] = useState<string>("");
  const [uploadedPhoto, setUploadedPhoto] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handlePhotoUpload = (file: File) => {
    setUploadedPhoto(file);
  };

  const handlePhotoRemove = () => {
    setUploadedPhoto(null);
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix (e.g., "data:image/jpeg;base64,")
        const base64String = result.split(",")[1];
        resolve(base64String);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  const handleStartGeneration = async () => {
    if (!selectedGender || !uploadedPhoto) return;

    setIsGenerating(true);

    try {
      // Validate file size before conversion
      const sizeInMB = uploadedPhoto.size / (1024 * 1024);
      if (sizeInMB > 10) {
        toast.error(
          "ファイルサイズが10MBを超えています。小さいファイルを選択してください。",
        );
        setIsGenerating(false);
        return;
      }

      // Convert file to base64
      const base64Photo = await fileToBase64(uploadedPhoto);

      // Show loading toast
      const loadingToast = toast.loading("スタイルを生成中...");

      // Call API to generate styles with retry logic
      const response = await retryWithBackoff(
        () =>
          apiClient.generateStyles(
            {
              photo: base64Photo,
              gender: selectedGender as Gender,
            },
            {
              maxRetries: 1, // retryWithBackoff will handle additional retries
            },
          ),
        {
          maxRetries: 3,
          baseDelay: 1000,
          maxDelay: 10000,
        },
      );

      toast.dismiss(loadingToast);

      if (response.success) {
        toast.success("スタイル生成に成功しました！");

        // Debug: Log the response to check originalImageUrl
        console.log("API Response:", response.data);
        console.log("Original Image URL:", response.data.originalImageUrl);

        // Store styles and original image URL in localStorage
        localStorage.setItem(
          "generatedStyles",
          JSON.stringify(response.data.styles),
        );
        if (response.data.originalImageUrl) {
          localStorage.setItem(
            "originalImageUrl",
            response.data.originalImageUrl,
          );
        } else {
          console.warn("No originalImageUrl in response");
        }

        // Navigate to styles page
        router.push("/styles");
      } else {
        // Handle specific error types
        const error = response.error;
        let errorMessage = "スタイル生成に失敗しました";

        if (isValidationError(error)) {
          errorMessage = "入力データに問題があります: " + error.message;
        } else if (isNetworkError(error)) {
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
            onClick: () => handleStartGeneration(),
          },
        });

        setIsGenerating(false);
        // Reset photo on all errors to disable the button
        setUploadedPhoto(null);
      }
    } catch (error) {
      console.error("Failed to generate styles:", error);

      // Handle unexpected errors
      const errorMessage = getErrorMessage(error);

      if (error instanceof ApiClientError) {
        const apiError = error.error;
        if (isNetworkError(apiError)) {
          toast.error("ネットワーク接続を確認してください", {
            duration: 5000,
            action: {
              label: "再試行",
              onClick: () => handleStartGeneration(),
            },
          });
        } else if (isTimeoutError(apiError)) {
          toast.error("処理がタイムアウトしました", {
            duration: 5000,
            action: {
              label: "再試行",
              onClick: () => handleStartGeneration(),
            },
          });
        } else {
          toast.error(errorMessage, { duration: 5000 });
        }
      } else {
        toast.error(`予期しないエラー: ${errorMessage}`, { duration: 5000 });
      }

      setIsGenerating(false);
      // Reset photo on all errors to disable the button
      setUploadedPhoto(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-card to-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1
            className="text-4xl md:text-6xl font-bold text-primary mb-4"
            style={{ fontFamily: "var(--font-playfair)" }}
          >
            Ejan
          </h1>
          <p className="text-xl text-muted-foreground mb-2">
            あなたに最適なメイクアップを提案します
          </p>
          <p className="text-lg text-foreground max-w-2xl mx-auto">
            AIがあなたの顔写真を分析し、パーソナライズされたメイクアップとヘアスタイルを提案します
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card className="text-center">
            <CardHeader>
              <Sparkles className="w-12 h-12 text-primary mx-auto mb-4" />
              <CardTitle>AI分析</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                最新のAI技術であなたの顔の特徴を分析し、最適なスタイルを提案
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <Users className="w-12 h-12 text-secondary mx-auto mb-4" />
              <CardTitle>パーソナライズ</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                性別や好みに合わせて、あなただけのメイクアップスタイルをカスタマイズ
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <Palette className="w-12 h-12 text-accent mx-auto mb-4" />
              <CardTitle>ステップガイド</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                写真と動画で分かりやすく、メイクアップの手順を詳しく解説
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        {/* Main Form */}
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-2xl text-center">始めましょう</CardTitle>
            <CardDescription className="text-center">
              性別を選択して、あなたの写真をアップロードしてください
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Gender Selection */}
            <div className="space-y-4">
              <Label className="text-lg font-semibold">
                性別を選択してください
              </Label>
              <RadioGroup
                value={selectedGender}
                onValueChange={setSelectedGender}
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="male" id="male" />
                  <Label htmlFor="male">男性</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="female" id="female" />
                  <Label htmlFor="female">女性</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="neutral" id="neutral" />
                  <Label htmlFor="neutral">中性的</Label>
                </div>
              </RadioGroup>
            </div>

            {/* Photo Upload */}
            <div className="space-y-4">
              <Label className="text-lg font-semibold">
                顔写真をアップロード
              </Label>
              <PhotoUpload
                onPhotoUpload={handlePhotoUpload}
                onPhotoRemove={handlePhotoRemove}
              />
              <p className="text-sm text-muted-foreground">
                ※ 10MBまでのJPEG、PNG形式の画像をアップロードできます
              </p>
            </div>

            {/* Generate Button */}
            <Button
              onClick={handleStartGeneration}
              disabled={!selectedGender || !uploadedPhoto || isGenerating}
              className="w-full py-6 text-lg"
              size="lg"
            >
              {isGenerating ? (
                <>
                  <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                  スタイルを生成中...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 mr-2" />
                  メイクアップスタイルを生成する
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
