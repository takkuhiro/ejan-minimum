"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  ArrowLeft,
  ArrowRight,
  Play,
  Pause,
  RotateCcw,
  Clock,
  CheckCircle,
} from "lucide-react";
import Link from "next/link";

// Mock tutorial data
const tutorialSteps = [
  {
    id: 1,
    name: "ベースメイク",
    duration: 5,
    description:
      "肌を整えて、美しいベースを作ります。ファンデーションを薄く均等に塗り、自然な仕上がりを目指しましょう。",
    imageUrl: "/makeup-step-base.jpg",
    videoUrl: "/makeup-step-base-video.mp4",
    tips: [
      "スポンジを湿らせて使うと自然な仕上がりになります",
      "首との境目をぼかすことを忘れずに",
    ],
  },
  {
    id: 2,
    name: "アイブロウ",
    duration: 3,
    description:
      "眉毛を整えて、顔の印象を決定づけます。自然な眉の形に沿って、足りない部分を補いましょう。",
    imageUrl: "/makeup-step-eyebrow.jpg",
    videoUrl: "/makeup-step-eyebrow-video.mp4",
    tips: [
      "眉頭は薄く、眉尻に向かって濃くするのがポイント",
      "毛流れに沿って描くと自然に見えます",
    ],
  },
  {
    id: 3,
    name: "アイシャドウ",
    duration: 8,
    description:
      "目元に深みと立体感を与えます。グラデーションを意識して、自然な陰影を作りましょう。",
    imageUrl: "/makeup-step-eyeshadow.jpg",
    videoUrl: "/makeup-step-eyeshadow-video.mp4",
    tips: [
      "明るい色から暗い色の順番で重ねる",
      "ブラシでしっかりぼかすことが大切",
    ],
  },
  {
    id: 4,
    name: "マスカラ",
    duration: 4,
    description:
      "まつ毛を長く、美しく仕上げます。根元からしっかりと塗り、セパレートさせましょう。",
    imageUrl: "/makeup-step-mascara.jpg",
    videoUrl: "/makeup-step-mascara-video.mp4",
    tips: [
      "ビューラーで事前にカールをつける",
      "ダマにならないよう少量ずつ重ねる",
    ],
  },
  {
    id: 5,
    name: "チーク",
    duration: 3,
    description:
      "頬に血色感をプラスして、健康的な印象を演出します。笑った時に高くなる部分に入れましょう。",
    imageUrl: "/makeup-step-cheek.jpg",
    videoUrl: "/makeup-step-cheek-video.mp4",
    tips: ["薄く少しずつ重ねる", "頬骨の高い位置に入れると立体感が出ます"],
  },
  {
    id: 6,
    name: "リップ",
    duration: 2,
    description:
      "最後にリップで全体を仕上げます。唇の形を整えて、美しい口元を作りましょう。",
    imageUrl: "/makeup-step-lip.jpg",
    videoUrl: "/makeup-step-lip-video.mp4",
    tips: ["リップライナーで輪郭を整える", "中央から外側に向かって塗る"],
  },
];

export default function TutorialPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  const totalDuration = tutorialSteps.reduce(
    (sum, step) => sum + step.duration,
    0,
  );
  const completedDuration = completedSteps.reduce(
    (sum, stepIndex) => sum + tutorialSteps[stepIndex].duration,
    0,
  );
  const progress = (completedDuration / totalDuration) * 100;

  const handleStepComplete = () => {
    if (!completedSteps.includes(currentStep)) {
      setCompletedSteps([...completedSteps, currentStep]);
    }
  };

  const handleNext = () => {
    if (currentStep < tutorialSteps.length - 1) {
      setCurrentStep(currentStep + 1);
      setIsVideoPlaying(false);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setIsVideoPlaying(false);
    }
  };

  const handleStepSelect = (stepIndex: number) => {
    setCurrentStep(stepIndex);
    setIsVideoPlaying(false);
  };

  const handleRestart = () => {
    setCurrentStep(0);
    setCompletedSteps([]);
    setIsVideoPlaying(false);
  };

  const currentStepData = tutorialSteps[currentStep];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-card to-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Link href="/customize">
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
              メイクアップチュートリアル
            </h1>
            <p className="text-muted-foreground mt-2">
              ステップバイステップで美しく変身
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={handleRestart}>
            <RotateCcw className="w-4 h-4 mr-2" />
            最初から
          </Button>
        </div>

        {/* Progress */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">進行状況</span>
              <span className="text-sm text-muted-foreground">
                {completedSteps.length} / {tutorialSteps.length} ステップ完了
              </span>
            </div>
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between text-xs text-muted-foreground mt-1">
              <span>完了時間: {completedDuration}分</span>
              <span>総時間: {totalDuration}分</span>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Step List */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">ステップ一覧</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {tutorialSteps.map((step, index) => (
                  <button
                    key={step.id}
                    onClick={() => handleStepSelect(index)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      index === currentStep
                        ? "bg-primary text-primary-foreground"
                        : completedSteps.includes(index)
                          ? "bg-green-50 border border-green-200"
                          : "bg-muted hover:bg-muted/80"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">{step.name}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Clock className="w-3 h-3" />
                          <span className="text-xs">{step.duration}分</span>
                        </div>
                      </div>
                      {completedSteps.includes(index) && (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      )}
                    </div>
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Current Step */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-2xl">
                    ステップ {currentStep + 1}: {currentStepData.name}
                  </CardTitle>
                  <Badge
                    variant="outline"
                    className="flex items-center space-x-1"
                  >
                    <Clock className="w-3 h-3" />
                    <span>{currentStepData.duration}分</span>
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-6">
                  {currentStepData.description}
                </p>

                {/* Video Player */}
                <div className="relative mb-6">
                  <div className="aspect-video bg-muted rounded-lg overflow-hidden">
                    <img
                      src={currentStepData.imageUrl || "/placeholder.svg"}
                      alt={`${currentStepData.name} tutorial`}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Button
                        size="lg"
                        onClick={() => setIsVideoPlaying(!isVideoPlaying)}
                        className="bg-black/50 hover:bg-black/70 text-white"
                      >
                        {isVideoPlaying ? (
                          <Pause className="w-6 h-6" />
                        ) : (
                          <Play className="w-6 h-6" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Step Image */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">完成イメージ</h3>
                  <img
                    src={currentStepData.imageUrl || "/placeholder.svg"}
                    alt={`${currentStepData.name} result`}
                    className="w-full max-w-md mx-auto rounded-lg"
                  />
                </div>

                {/* Tips */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">コツ・ポイント</h3>
                  <ul className="space-y-2">
                    {currentStepData.tips.map((tip, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                        <span className="text-sm">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-between">
                  <Button
                    variant="outline"
                    onClick={handlePrevious}
                    disabled={currentStep === 0}
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    前のステップ
                  </Button>

                  <Button
                    onClick={handleStepComplete}
                    variant={
                      completedSteps.includes(currentStep)
                        ? "secondary"
                        : "default"
                    }
                  >
                    {completedSteps.includes(currentStep) ? (
                      <>
                        <CheckCircle className="w-4 h-4 mr-2" />
                        完了済み
                      </>
                    ) : (
                      "このステップを完了"
                    )}
                  </Button>

                  <Button
                    onClick={handleNext}
                    disabled={currentStep === tutorialSteps.length - 1}
                  >
                    次のステップ
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Completion Message */}
            {completedSteps.length === tutorialSteps.length && (
              <Card className="border-green-200 bg-green-50">
                <CardContent className="pt-6 text-center">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-green-800 mb-2">
                    おめでとうございます！
                  </h3>
                  <p className="text-green-700">
                    すべてのステップが完了しました。素晴らしい仕上がりですね！
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
