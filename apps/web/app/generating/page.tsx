"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Sparkles, ImageIcon, Video, CheckCircle } from "lucide-react"

const generationSteps = [
  { id: 1, name: "メイク手順を分析中", icon: Sparkles, duration: 30 },
  { id: 2, name: "ステップ画像を生成中", icon: ImageIcon, duration: 45 },
  { id: 3, name: "解説動画を作成中", icon: Video, duration: 60 },
  { id: 4, name: "最終調整中", icon: CheckCircle, duration: 15 },
]

export default function GeneratingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const totalDuration = generationSteps.reduce((sum, step) => sum + step.duration, 0)
    let elapsed = 0

    const interval = setInterval(() => {
      elapsed += 1
      const newProgress = Math.min((elapsed / totalDuration) * 100, 100)
      setProgress(newProgress)

      // Update current step
      let cumulativeDuration = 0
      for (let i = 0; i < generationSteps.length; i++) {
        cumulativeDuration += generationSteps[i].duration
        if (elapsed <= cumulativeDuration) {
          setCurrentStep(i)
          break
        }
      }

      // Complete and redirect
      if (elapsed >= totalDuration) {
        clearInterval(interval)
        setTimeout(() => {
          window.location.href = "/tutorial"
        }, 1000)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-card to-background flex items-center justify-center">
      <div className="container mx-auto px-4">
        <Card className="max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-bold text-primary mb-4" style={{ fontFamily: "var(--font-playfair)" }}>
              チュートリアルを作成中
            </CardTitle>
            <p className="text-muted-foreground">
              この処理には少しお時間をいただきます。画面を更新せず、そのままでお待ちください。
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
            </div>

            {/* Generation Steps */}
            <div className="space-y-4">
              {generationSteps.map((step, index) => {
                const Icon = step.icon
                const isActive = index === currentStep
                const isCompleted = index < currentStep
                const isUpcoming = index > currentStep

                return (
                  <div
                    key={step.id}
                    className={`flex items-center space-x-4 p-4 rounded-lg transition-all ${
                      isActive ? "bg-primary/10 border border-primary/20" : isCompleted ? "bg-muted/50" : "bg-muted/20"
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
                        <Icon className={`w-5 h-5 ${isActive ? "animate-pulse" : ""}`} />
                      )}
                    </div>
                    <div className="flex-1">
                      <p
                        className={`font-medium ${
                          isActive ? "text-primary" : isCompleted ? "text-foreground" : "text-muted-foreground"
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
                )
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
  )
}
