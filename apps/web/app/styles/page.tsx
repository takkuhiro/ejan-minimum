"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { truncateTitle, truncateDescription } from "@/lib/utils";
import type { Style } from "@/types/api";

export default function StyleSelectionPage() {
  const router = useRouter();

  const [styles, setStyles] = useState<Style[]>([]);
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
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

  const handleStyleSelect = (style: Style) => {
    if (!originalImageUrl) {
      toast.error("元画像が見つかりません");
      return;
    }

    // Save the selected style with originalImageUrl embedded and navigate to customize page
    const styleWithOriginal = {
      ...style,
      originalImageUrl: originalImageUrl,
    };

    localStorage.setItem("selectedStyle", JSON.stringify(styleWithOriginal));
    router.push("/customize");
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
                <div className="relative w-full h-100">
                  <Image
                    src={originalImageUrl}
                    alt="アップロードした画像"
                    fill
                    className="object-contain w-full"
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
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {styles.map((style) => (
              <Card
                key={style.id}
                className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:ring-2 hover:ring-primary"
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
                    <div className="relative w-full h-90 overflow-hidden rounded-lg">
                      <Image
                        src={getImageSrc(style)}
                        alt={style.title}
                        fill
                        className="object-contain w-full"
                        onError={() => handleImageError(style.id)}
                      />
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardTitle className="text-lg mb-2">
                    {truncateTitle(style.title, 12)}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mb-3">
                    {truncateDescription(style.description, 35)}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
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

        {/* Help Text */}
        <div className="text-center mt-12">
          <p className="text-sm text-muted-foreground">
            スタイルを選択後、さらに細かい調整が可能です
          </p>
        </div>
      </div>
    </div>
  );
}
