"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
  Sparkles,
  ImageIcon,
  Video,
  CheckCircle,
  AlertCircle,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
import type { ApiError } from "@/types/api";

const generationSteps = [
  { id: 1, name: "メイク手順を分析中", icon: Sparkles, duration: 30 },
  { id: 2, name: "ステップ画像を生成中", icon: ImageIcon, duration: 45 },
  { id: 3, name: "解説動画を作成中", icon: Video, duration: 60 },
  { id: 4, name: "最終調整中", icon: CheckCircle, duration: 15 },
];

export default function GeneratingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [, setTutorialId] = useState<string | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Extract parameters from search params
  const styleId = searchParams.get("styleId");
  const customization = searchParams.get("customization") || undefined;

  const handleTutorialComplete = useCallback(
    (id: string) => {
      // Stop polling
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      // Set progress to 100%
      setProgress(100);
      setCurrentStep(generationSteps.length - 1);

      // Redirect to tutorial page after a short delay
      setTimeout(() => {
        router.push(`/tutorial?id=${id}`);
      }, 1000);
    },
    [router],
  );

  const startPolling = useCallback(
    (id: string) => {
      // Poll every 10 seconds
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const response = await apiClient.getTutorialStatus(id);

          if (!response.success) {
            console.error("Polling error:", response.error);
            return;
          }

          const { data } = response;

          if (data.status === "COMPLETED") {
            handleTutorialComplete(id);
          } else if (data.status === "FAILED") {
            setError("チュートリアルの生成に失敗しました");
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
            }
          }

          // Update progress if provided
          if (data.progress !== undefined) {
            setProgress(data.progress);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 10000); // 10 seconds
    },
    [handleTutorialComplete],
  );

  const generateTutorial = useCallback(async () => {
    if (!styleId) return;

    setIsGenerating(true);
    setError(null);

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      // Start progress animation
      startProgressAnimation();

      // Call generate tutorial API
      const response = await apiClient.generateTutorial(
        { styleId, customization },
        { signal: abortControllerRef.current.signal },
      );

      if (!response.success) {
        handleError(response.error);
        return;
      }

      const { data } = response;
      setTutorialId(data.id);

      // Check if generation is complete or needs polling
      if (data.status === "COMPLETED") {
        // Tutorial is ready, redirect immediately
        handleTutorialComplete(data.id);
      } else if (data.status === "PROCESSING") {
        // Start polling for status
        startPolling(data.id);
      } else if (data.status === "FAILED") {
        setError("チュートリアルの生成に失敗しました");
      }
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        // Request was aborted, ignore
        return;
      }
      setError("エラーが発生しました");
      console.error("Tutorial generation error:", err);
    }
  }, [styleId, customization, handleTutorialComplete, startPolling]);

  useEffect(() => {
    // Check if styleId exists
    if (!styleId) {
      setError("スタイルが選択されていません");
      return;
    }

    // Start generation
    generateTutorial();

    // Cleanup on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [styleId, generateTutorial]);

  const startProgressAnimation = () => {
    const totalDuration = generationSteps.reduce(
      (sum, step) => sum + step.duration,
      0,
    );
    let elapsed = 0;

    const interval = setInterval(() => {
      elapsed += 1;
      const newProgress = Math.min((elapsed / totalDuration) * 100, 95); // Max 95% until complete
      setProgress(newProgress);

      // Update current step
      let cumulativeDuration = 0;
      for (let i = 0; i < generationSteps.length; i++) {
        cumulativeDuration += generationSteps[i].duration;
        if (elapsed <= cumulativeDuration) {
          setCurrentStep(i);
          break;
        }
      }

      // Stop at 95% and wait for actual completion
      if (elapsed >= totalDuration) {
        clearInterval(interval);
      }
    }, 1000);

    // Store interval for cleanup if needed
    return interval;
  };

  const handleError = (error: ApiError) => {
    setIsGenerating(false);

    if (error.error === "TimeoutError") {
      setError("処理に時間がかかっています");
      toast.error("タイムアウトしました。もう一度お試しください。");
    } else if (error.error === "ServerError") {
      setError("チュートリアルの生成に失敗しました");
      toast.error("サーバーエラーが発生しました。");
    } else {
      setError("エラーが発生しました");
      toast.error(error.message || "予期せぬエラーが発生しました。");
    }
  };

  const handleRetry = () => {
    setError(null);
    setProgress(0);
    setCurrentStep(0);
    generateTutorial();
  };

  // Error states
  if (!styleId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-card to-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">
              スタイルが選択されていません
            </h3>
            <p className="text-muted-foreground mb-4">
              スタイルを選択してからお試しください。
            </p>
            <Link href="/styles">
              <Button>
                <ArrowLeft className="w-4 h-4 mr-2" />
                スタイル選択に戻る
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-card to-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">エラーが発生しました</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
            <div className="flex gap-3 justify-center">
              <Link href="/styles">
                <Button variant="outline">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  戻る
                </Button>
              </Link>
              <Button onClick={handleRetry}>もう一度試す</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-card to-background flex items-center justify-center">
      <div className="container mx-auto px-4">
        <Card className="max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <CardTitle
              className="text-3xl font-bold text-primary mb-4"
              style={{ fontFamily: "var(--font-playfair)" }}
            >
              チュートリアルを作成中
            </CardTitle>
            <p className="text-muted-foreground">
              この処理には約3分お時間をいただきます。画面を更新せず、そのままでお待ちください。
            </p>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>進行状況</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-3" />
              <p className="text-xs text-muted-foreground text-center">
                約3分かかります
              </p>
            </div>

            {/* Generation Steps */}
            <div className="space-y-4">
              {generationSteps.map((step, index) => {
                const Icon = step.icon;
                const isActive = index === currentStep && isGenerating;
                const isCompleted = index < currentStep;
                const _isUpcoming = index > currentStep;

                return (
                  <div
                    key={step.id}
                    className={`flex items-center space-x-4 p-4 rounded-lg transition-all ${
                      isActive
                        ? "bg-primary/10 border border-primary/20"
                        : isCompleted
                          ? "bg-muted/50"
                          : "bg-muted/20"
                    }`}
                  >
                    <div
                      className={`p-2 rounded-full ${
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : isCompleted
                            ? "bg-green-500 text-white"
                            : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {isCompleted ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <Icon
                          className={`w-5 h-5 ${isActive ? "animate-pulse" : ""}`}
                        />
                      )}
                    </div>
                    <div className="flex-1">
                      <p
                        className={`font-medium ${
                          isActive
                            ? "text-primary"
                            : isCompleted
                              ? "text-foreground"
                              : "text-muted-foreground"
                        }`}
                      >
                        {step.name}
                      </p>
                    </div>
                    {isActive && (
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                        <div
                          className="w-2 h-2 bg-primary rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        />
                        <div
                          className="w-2 h-2 bg-primary rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Motivational Message */}
            <div className="text-center p-6 bg-card rounded-lg border">
              <Sparkles className="w-8 h-8 text-primary mx-auto mb-3" />
              <p className="text-lg font-medium mb-2">もうすぐ完成です！</p>
              <p className="text-muted-foreground">
                あなただけの特別なメイクアップチュートリアルを作成しています。完成をお楽しみに！
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
