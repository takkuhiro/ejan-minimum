"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ArrowLeft,
  ArrowRight,
  Play,
  Pause,
  RotateCcw,
  Clock,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { apiClient } from "@/lib/api/client";
import { TutorialResponse } from "@/types/api";
import { toast } from "sonner";

export default function TutorialPage() {
  const searchParams = useSearchParams();
  const videoRef = useRef<HTMLVideoElement>(null);

  const [tutorial, setTutorial] = useState<TutorialResponse | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get tutorial ID from URL
  const tutorialId = searchParams.get("id");

  useEffect(() => {
    if (!tutorialId) {
      setError("チュートリアルが見つかりません");
      setIsLoading(false);
      return;
    }

    loadTutorial(tutorialId);
  }, [tutorialId]);

  // Handle video state changes
  useEffect(() => {
    if (!videoRef.current) return;

    const handlePlay = () => setIsVideoPlaying(true);
    const handlePause = () => setIsVideoPlaying(false);

    const video = videoRef.current;
    video.addEventListener("play", handlePlay);
    video.addEventListener("pause", handlePause);

    return () => {
      video.removeEventListener("play", handlePlay);
      video.removeEventListener("pause", handlePause);
    };
  }, [tutorial, currentStep]);

  const loadTutorial = async (id: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getTutorial(id);

      if (!response.success) {
        if (response.error.error === "NotFound") {
          setError("チュートリアルが見つかりません");
        } else {
          setError("チュートリアルの読み込みに失敗しました");
        }
        return;
      }

      setTutorial(response.data);
    } catch (err) {
      setError("エラーが発生しました");
      console.error("Failed to load tutorial:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStepComplete = () => {
    if (!completedSteps.includes(currentStep)) {
      setCompletedSteps([...completedSteps, currentStep]);
      toast.success("ステップを完了しました！");
    }
  };

  const handleNext = () => {
    if (!tutorial) return;
    if (currentStep < tutorial.steps.length - 1) {
      setCurrentStep(currentStep + 1);
      setIsVideoPlaying(false);
      // Reset video when changing steps
      if (videoRef.current) {
        videoRef.current.pause();
        videoRef.current.currentTime = 0;
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setIsVideoPlaying(false);
      // Reset video when changing steps
      if (videoRef.current) {
        videoRef.current.pause();
        videoRef.current.currentTime = 0;
      }
    }
  };

  const handleStepSelect = (stepIndex: number) => {
    setCurrentStep(stepIndex);
    setIsVideoPlaying(false);
    // Reset video when changing steps
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
    }
  };

  const handleRestart = () => {
    setCurrentStep(0);
    setCompletedSteps([]);
    setIsVideoPlaying(false);
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
    }
  };

  const toggleVideoPlayback = () => {
    if (!videoRef.current) return;

    if (isVideoPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
  };

  // Calculate progress
  const progress = tutorial
    ? (completedSteps.length / tutorial.steps.length) * 100
    : 0;

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-card to-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">{error}</h3>
            <p className="text-muted-foreground mb-4">
              チュートリアルの読み込みに問題が発生しました。
            </p>
            <div className="flex gap-3 justify-center">
              <Link href="/styles">
                <Button variant="outline">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  スタイル選択に戻る
                </Button>
              </Link>
              {tutorialId && (
                <Button onClick={() => loadTutorial(tutorialId)}>
                  もう一度試す
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-card to-background">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center mb-8">
            <Skeleton className="h-10 w-64" />
          </div>
          <Card className="mb-8">
            <CardContent className="pt-6">
              <Skeleton className="h-2 w-full" />
            </CardContent>
          </Card>
          <div className="grid lg:grid-cols-4 gap-8">
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-32" />
                </CardHeader>
                <CardContent className="space-y-2">
                  {[1, 2, 3, 4].map((i) => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </CardContent>
              </Card>
            </div>
            <div className="lg:col-span-3">
              <Card>
                <CardHeader>
                  <Skeleton className="h-8 w-48" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-64 w-full mb-4" />
                  <Skeleton className="h-40 w-full" />
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!tutorial) {
    return null;
  }

  const currentStepData = tutorial.steps[currentStep];

  // Calculate total duration (mock - could be from backend)
  const totalDuration = tutorial.steps.length * 3; // Assuming 3 minutes per step
  const completedDuration = completedSteps.length * 3;

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
              {tutorial.title}
            </h1>
            <p className="text-muted-foreground mt-2">{tutorial.description}</p>
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
                {completedSteps.length} / {tutorial.steps.length} ステップ完了
              </span>
            </div>
            <Progress
              value={progress}
              className="h-2"
              data-value={Math.round(progress)}
            />
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
                {tutorial.steps.map((step, index) => (
                  <button
                    key={`step-${step.stepNumber}-${index}`}
                    onClick={() => handleStepSelect(index)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      index === currentStep
                        ? "bg-primary text-primary-foreground"
                        : completedSteps.includes(index)
                          ? "bg-green-50 border border-green-200"
                          : "bg-muted hover:bg-muted/80"
                    }`}
                    aria-label={step.title}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">{step.title}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Clock className="w-3 h-3" />
                          <span className="text-xs">3分</span>
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
                    ステップ {currentStep + 1}: {currentStepData.title}
                  </CardTitle>
                  <Badge
                    variant="outline"
                    className="flex items-center space-x-1"
                  >
                    <Clock className="w-3 h-3" />
                    <span>3分</span>
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-6">
                  {currentStepData.description}
                </p>

                {currentStepData.detailedInstructions && (
                  <div className="mb-6 p-4 bg-muted rounded-lg">
                    <p className="text-sm">
                      {currentStepData.detailedInstructions}
                    </p>
                  </div>
                )}

                {/* Video Player */}
                <div className="relative mb-6">
                  <div className="aspect-video bg-black rounded-lg overflow-hidden">
                    {currentStepData.videoUrl ? (
                      <>
                        <video
                          ref={videoRef}
                          src={currentStepData.videoUrl}
                          className="w-full h-full object-contain"
                          loop
                          playsInline
                          role="video"
                          aria-label={`${currentStepData.title} tutorial video`}
                        />
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                          <Button
                            size="lg"
                            onClick={toggleVideoPlayback}
                            className="bg-black/50 hover:bg-black/70 text-white pointer-events-auto"
                            aria-label={isVideoPlaying ? "一時停止" : "再生"}
                          >
                            {isVideoPlaying ? (
                              <Pause className="w-6 h-6" />
                            ) : (
                              <Play className="w-6 h-6" />
                            )}
                          </Button>
                        </div>
                      </>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-muted">
                        <p className="text-muted-foreground">
                          動画を読み込み中...
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Step Image */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">完成イメージ</h3>
                  {currentStepData.imageUrl ? (
                    <div className="relative w-full max-w-md mx-auto rounded-lg overflow-hidden">
                      <Image
                        src={currentStepData.imageUrl}
                        alt={`${currentStepData.title} result`}
                        width={800}
                        height={600}
                        className="w-full h-auto"
                        priority
                      />
                    </div>
                  ) : (
                    <div className="w-full max-w-md mx-auto aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
                      <p className="text-muted-foreground">
                        画像を読み込み中...
                      </p>
                    </div>
                  )}
                </div>

                {/* Tools */}
                {currentStepData.tools && currentStepData.tools.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-semibold mb-3">必要な道具</h3>
                    <div className="flex flex-wrap gap-2">
                      {currentStepData.tools.map((tool, index) => (
                        <Badge key={index} variant="secondary">
                          {tool}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tips */}
                {currentStepData.tips && currentStepData.tips.length > 0 && (
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
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-between">
                  <Button
                    variant="outline"
                    onClick={handlePrevious}
                    disabled={currentStep === 0}
                    aria-label="前のステップ"
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
                    aria-label={
                      completedSteps.includes(currentStep)
                        ? "完了済み"
                        : "このステップを完了"
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
                    disabled={currentStep === tutorial.steps.length - 1}
                    aria-label="次のステップ"
                  >
                    次のステップ
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Completion Message */}
            {completedSteps.length === tutorial.steps.length && (
              <Card className="border-green-200 bg-green-50">
                <CardContent className="pt-6 text-center">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-green-800 mb-2">
                    おめでとうございます！
                  </h3>
                  <p className="text-green-700">
                    すべてのステップが完了しました。素晴らしい仕上がりですね！
                  </p>
                  <div className="mt-6">
                    <Link href="/">
                      <Button className="mr-3">新しいスタイルを試す</Button>
                    </Link>
                    <Button variant="outline" onClick={handleRestart}>
                      もう一度見る
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
