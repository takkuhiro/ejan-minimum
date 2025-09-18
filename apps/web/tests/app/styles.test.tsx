/**
 * @jest-environment jsdom
 */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { useRouter, useSearchParams } from "next/navigation";
import StyleSelectionPage from "@/app/styles/page";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";

// Mock Next.js navigation
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock Next.js Link component
jest.mock("next/link", () => {
  return {
    __esModule: true,
    default: ({
      children,
      href,
    }: {
      children: React.ReactNode;
      href: string;
    }) => <a href={href}>{children}</a>,
  };
});

// Mock Next.js Image component
jest.mock("next/image", () => {
  return {
    __esModule: true,
    default: ({ src, alt, ...props }: any) => (
      // eslint-disable-next-line @next/next/no-img-element
      <img src={src} alt={alt} {...props} />
    ),
  };
});

// Mock API client
jest.mock("@/lib/api/client", () => ({
  apiClient: {
    getStyleDetail: jest.fn(),
    generateTutorial: jest.fn(),
  },
}));

// Mock toast notifications
jest.mock("sonner", () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
    loading: jest.fn(),
    dismiss: jest.fn(),
  },
}));

describe("StyleSelectionPage - API Integration", () => {
  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
  };

  const mockSearchParams = new URLSearchParams();

  const mockStyles = [
    {
      id: "style-1",
      title: "ナチュラル美人",
      description: "自然な美しさを引き出すソフトメイク",
      imageUrl: "https://storage.googleapis.com/bucket/style-1.jpg",
    },
    {
      id: "style-2",
      title: "エレガント",
      description: "洗練された大人の魅力を演出",
      imageUrl: "https://storage.googleapis.com/bucket/style-2.jpg",
    },
    {
      id: "style-3",
      title: "トレンディ",
      description: "最新トレンドを取り入れたモダンスタイル",
      imageUrl: "https://storage.googleapis.com/bucket/style-3.jpg",
    },
  ];

  const mockUserPhotoUrl =
    "https://storage.googleapis.com/bucket/user-photo.jpg";

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useSearchParams as jest.Mock).mockReturnValue(mockSearchParams);

    // Reset localStorage
    localStorage.clear();
  });

  describe("Style Loading from URL Parameters", () => {
    it("should load and display styles from URL parameters", async () => {
      // Set up URL parameters with style data
      const stylesParam = encodeURIComponent(JSON.stringify(mockStyles));
      const photoParam = encodeURIComponent(mockUserPhotoUrl);
      mockSearchParams.set("styles", stylesParam);
      mockSearchParams.set("photo", photoParam);

      render(<StyleSelectionPage />);

      // Wait for styles to be loaded
      await waitFor(() => {
        // Check if all styles are displayed
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
        expect(screen.getByText("エレガント")).toBeInTheDocument();
        expect(screen.getByText("トレンディ")).toBeInTheDocument();
      });

      // Check if descriptions are displayed
      expect(
        screen.getByText("自然な美しさを引き出すソフトメイク"),
      ).toBeInTheDocument();
      expect(
        screen.getByText("洗練された大人の魅力を演出"),
      ).toBeInTheDocument();
      expect(
        screen.getByText("最新トレンドを取り入れたモダンスタイル"),
      ).toBeInTheDocument();

      // Check if user photo is displayed
      const userPhoto = screen.getByAltText("あなたの写真");
      expect(userPhoto).toBeInTheDocument();
      expect(userPhoto).toHaveAttribute("src", mockUserPhotoUrl);
    });

    it("should handle missing URL parameters gracefully", () => {
      render(<StyleSelectionPage />);

      // Should show loading or empty state
      expect(screen.getByText("スタイルを選択")).toBeInTheDocument();

      // Should show skeleton loaders or empty state when no data
      // Either skeleton loaders or customize option should be visible
      const skeletons = document.querySelectorAll('[data-slot="skeleton"]');
      const customizeCard = screen.queryByText("カスタマイズ");

      // At least one should be present (skeletons when loading, or customize card when no data)
      expect(skeletons.length > 0 || customizeCard !== null).toBe(true);
    });

    it("should load styles from localStorage as fallback", async () => {
      // Set data in localStorage
      localStorage.setItem("generatedStyles", JSON.stringify(mockStyles));
      localStorage.setItem("userPhoto", mockUserPhotoUrl);

      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
        expect(screen.getByText("エレガント")).toBeInTheDocument();
        expect(screen.getByText("トレンディ")).toBeInTheDocument();
      });
    });
  });

  describe("Style Selection and Details", () => {
    beforeEach(() => {
      const stylesParam = encodeURIComponent(JSON.stringify(mockStyles));
      const photoParam = encodeURIComponent(mockUserPhotoUrl);
      mockSearchParams.set("styles", stylesParam);
      mockSearchParams.set("photo", photoParam);
    });

    it("should fetch style details when a style is selected", async () => {
      const mockStyleDetail = {
        style: {
          ...mockStyles[0],
          tools: ["ファンデーション", "アイシャドウ", "リップ"],
          estimatedTime: "15分",
        },
      };

      (apiClient.getStyleDetail as jest.Mock).mockResolvedValue({
        success: true,
        data: mockStyleDetail,
      });

      render(<StyleSelectionPage />);

      // Wait for styles to load
      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      // Click on a style card
      const styleCard =
        screen.getByText("ナチュラル美人").closest("div[role='button']") ||
        screen.getByText("ナチュラル美人").closest(".cursor-pointer");
      fireEvent.click(styleCard!);

      // Should fetch style details
      await waitFor(() => {
        expect(apiClient.getStyleDetail).toHaveBeenCalledWith("style-1");
      });

      // Should display style details
      await waitFor(() => {
        expect(screen.getByText(/ファンデーション/)).toBeInTheDocument();
        expect(screen.getByText(/15分/)).toBeInTheDocument();
      });
    });

    it("should show error toast when style detail fetch fails", async () => {
      (apiClient.getStyleDetail as jest.Mock).mockResolvedValue({
        success: false,
        error: {
          error: "NetworkError",
          message: "Failed to fetch style details",
        },
      });

      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      const styleCard = screen
        .getByText("ナチュラル美人")
        .closest(".cursor-pointer");
      fireEvent.click(styleCard!);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(
          expect.stringContaining("スタイルの詳細を取得できませんでした"),
        );
      });
    });

    it("should highlight selected style", async () => {
      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      const styleCard = screen
        .getByText("ナチュラル美人")
        .closest(".cursor-pointer") as HTMLElement;
      fireEvent.click(styleCard);

      // Check if the selected style has the selection indicator
      await waitFor(() => {
        expect(styleCard).toHaveClass("ring-2", "ring-primary");
      });

      // Check if check icon is displayed
      const checkIcon = styleCard.querySelector(".lucide-check");
      expect(checkIcon).toBeInTheDocument();
    });
  });

  describe("Tutorial Generation", () => {
    beforeEach(() => {
      const stylesParam = encodeURIComponent(JSON.stringify(mockStyles));
      const photoParam = encodeURIComponent(mockUserPhotoUrl);
      mockSearchParams.set("styles", stylesParam);
      mockSearchParams.set("photo", photoParam);
    });

    it("should navigate to customization page when customize button is clicked", async () => {
      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("カスタマイズ")).toBeInTheDocument();
      });

      const customizeCard = screen
        .getByText("カスタマイズ")
        .closest(".cursor-pointer");
      fireEvent.click(customizeCard!);

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalled();
      });

      // Check if router.push was called with correct URL string
      const pushCall = mockRouter.push.mock.calls[0][0];
      expect(pushCall).toContain("/customize");
      expect(pushCall).toContain("styles=");
      expect(pushCall).toContain("photo=");
    });

    it("should generate tutorial when style is confirmed", async () => {
      const mockTutorialResponse = {
        tutorial: {
          id: "tutorial-1",
          title: "ナチュラル美人メイクアップ",
          description: "自然な美しさを引き出すメイクアップチュートリアル",
          steps: [],
        },
      };

      (apiClient.generateTutorial as jest.Mock).mockResolvedValue({
        success: true,
        data: mockTutorialResponse,
      });

      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      // Select a style
      const styleCard = screen
        .getByText("ナチュラル美人")
        .closest(".cursor-pointer");
      fireEvent.click(styleCard!);

      // Click confirm button
      const confirmButton = screen.getByText("このスタイルで進む");
      fireEvent.click(confirmButton);

      // Should show loading state
      expect(screen.getByText("処理中...")).toBeInTheDocument();

      // Should call generateTutorial API
      await waitFor(() => {
        expect(apiClient.generateTutorial).toHaveBeenCalledWith({
          styleId: "style-1",
        });
      });

      // Should navigate to generating page
      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith(
          expect.stringContaining("/generating"),
        );
      });
    });

    it("should pass customization text when generating tutorial", async () => {
      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      // Select a style
      const styleCard = screen
        .getByText("ナチュラル美人")
        .closest(".cursor-pointer");
      fireEvent.click(styleCard!);

      // Add customization text
      const customizationInput =
        screen.getByPlaceholderText(/もっとナチュラル|赤み/i) ||
        screen.getByLabelText(/カスタマイズ要望/);
      fireEvent.change(customizationInput, {
        target: { value: "もっとナチュラルに" },
      });

      // Click confirm button
      const confirmButton = screen.getByText("このスタイルで進む");
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(apiClient.generateTutorial).toHaveBeenCalledWith({
          styleId: "style-1",
          customizations: "もっとナチュラルに",
        });
      });
    });

    it("should handle tutorial generation error", async () => {
      (apiClient.generateTutorial as jest.Mock).mockResolvedValue({
        success: false,
        error: {
          error: "ServerError",
          message: "Tutorial generation failed",
        },
      });

      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      const styleCard = screen
        .getByText("ナチュラル美人")
        .closest(".cursor-pointer");
      fireEvent.click(styleCard!);

      const confirmButton = screen.getByText("このスタイルで進む");
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(
          expect.stringContaining("チュートリアルの生成に失敗しました"),
        );
      });

      // Should not navigate on error
      expect(mockRouter.push).not.toHaveBeenCalled();
    });
  });

  describe("Image Loading from Cloud Storage", () => {
    beforeEach(() => {
      const stylesParam = encodeURIComponent(JSON.stringify(mockStyles));
      const photoParam = encodeURIComponent(mockUserPhotoUrl);
      mockSearchParams.set("styles", stylesParam);
      mockSearchParams.set("photo", photoParam);
    });

    it("should display Cloud Storage URLs for style images", async () => {
      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      // Check that images are displayed with correct src
      const images = screen.getAllByRole("img");
      const styleImages = images.filter((img) => {
        const src = img.getAttribute("src");
        return (
          src?.includes("storage.googleapis.com") || src?.includes("style-")
        );
      });

      // We should have at least the user photo and style images
      expect(styleImages.length).toBeGreaterThanOrEqual(3);

      // Check specific style images are present
      mockStyles.forEach((style) => {
        const styleImage = screen.getByAltText(style.title);
        expect(styleImage).toBeInTheDocument();
      });
    });

    it("should handle image loading errors gracefully", async () => {
      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      // Simulate image load error
      const images = screen.getAllByRole("img");
      images.forEach((img) => {
        if (img.getAttribute("src")?.includes("style-1")) {
          fireEvent.error(img);
        }
      });

      // Should show fallback or placeholder
      await waitFor(() => {
        const fallbackImage = screen.getByAltText("ナチュラル美人");
        expect(fallbackImage).toBeTruthy();
        // The fallback is handled in the component's getImageSrc function
      });
    });
  });

  describe("Responsive Behavior", () => {
    it("should disable confirm button when no style is selected", async () => {
      const stylesParam = encodeURIComponent(JSON.stringify(mockStyles));
      mockSearchParams.set("styles", stylesParam);

      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      const confirmButton = screen.getByText("このスタイルで進む");
      expect(confirmButton).toBeDisabled();
    });

    it("should enable confirm button when a style is selected", async () => {
      const stylesParam = encodeURIComponent(JSON.stringify(mockStyles));
      mockSearchParams.set("styles", stylesParam);

      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      const styleCard = screen
        .getByText("ナチュラル美人")
        .closest(".cursor-pointer");
      fireEvent.click(styleCard!);

      const confirmButton = screen.getByText("このスタイルで進む");
      expect(confirmButton).toBeEnabled();
    });

    it("should save selection to localStorage for recovery", async () => {
      const stylesParam = encodeURIComponent(JSON.stringify(mockStyles));
      mockSearchParams.set("styles", stylesParam);

      render(<StyleSelectionPage />);

      await waitFor(() => {
        expect(screen.getByText("ナチュラル美人")).toBeInTheDocument();
      });

      const styleCard = screen
        .getByText("ナチュラル美人")
        .closest(".cursor-pointer");
      fireEvent.click(styleCard!);

      await waitFor(() => {
        const savedSelection = localStorage.getItem("selectedStyle");
        expect(savedSelection).toBe(JSON.stringify(mockStyles[0]));
      });
    });
  });
});
