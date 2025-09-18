"use client";

import { useState } from "react";
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

export default function WelcomePage() {
  const [selectedGender, setSelectedGender] = useState<string>("");
  const [uploadedPhoto, setUploadedPhoto] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handlePhotoUpload = (file: File) => {
    setUploadedPhoto(file);
  };

  const handleStartGeneration = async () => {
    if (!selectedGender || !uploadedPhoto) return;

    setIsGenerating(true);
    // TODO: Implement API call to generate makeup styles
    // For now, simulate loading
    setTimeout(() => {
      // Navigate to style selection page
      window.location.href = "/styles";
    }, 3000);
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
              <PhotoUpload onPhotoUpload={handlePhotoUpload} />
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
