import { ApiClient } from "@/lib/api/client";
import {
  GenerateStylesRequest,
  GenerateStylesResponse,
  GenerateTutorialRequest,
  GenerateTutorialResponse,
  StyleDetailResponse,
  ApiError,
} from "@/types/api";

// Mock fetch globally
global.fetch = jest.fn();

describe("ApiClient", () => {
  let apiClient: ApiClient;
  const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Set default API URL
    process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000";
    apiClient = new ApiClient();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe("constructor", () => {
    it("should use environment variable for API URL", () => {
      expect(apiClient.baseUrl).toBe("http://localhost:8000");
    });

    it("should use default URL when environment variable is not set", () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      const client = new ApiClient();
      expect(client.baseUrl).toBe("http://localhost:8000");
    });
  });

  describe("generateStyles", () => {
    const mockRequest: GenerateStylesRequest = {
      photo: "base64encodedphoto",
      gender: "female",
    };

    const mockResponse: GenerateStylesResponse = {
      styles: [
        {
          id: "style1",
          title: "Natural Makeup",
          description: "A fresh, natural look",
          imageUrl: "https://storage.googleapis.com/bucket/style1.jpg",
        },
        {
          id: "style2",
          title: "Evening Glam",
          description: "Sophisticated evening makeup",
          imageUrl: "https://storage.googleapis.com/bucket/style2.jpg",
        },
        {
          id: "style3",
          title: "Bold and Colorful",
          description: "Creative and vibrant makeup",
          imageUrl: "https://storage.googleapis.com/bucket/style3.jpg",
        },
      ],
    };

    it("should successfully generate styles", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.generateStyles(mockRequest);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/styles/generate",
        expect.objectContaining({
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(mockRequest),
          signal: expect.any(AbortSignal),
        }),
      );

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockResponse);
      }
    });

    it("should handle API errors", async () => {
      const errorResponse: ApiError = {
        error: "ValidationError",
        message: "Invalid image format",
        statusCode: 400,
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => errorResponse,
      } as Response);

      const result = await apiClient.generateStyles(mockRequest);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toEqual(errorResponse);
      }
    });

    it("should handle network errors", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      const result = await apiClient.generateStyles(mockRequest);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.error).toBe("NetworkError");
        expect(result.error.message).toContain("Network error");
      }
    });

    it("should validate photo size before sending", async () => {
      const largePhoto = "a".repeat(15 * 1024 * 1024); // 15MB
      const largeRequest: GenerateStylesRequest = {
        photo: largePhoto,
        gender: "male",
      };

      const result = await apiClient.generateStyles(largeRequest);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.error).toBe("ValidationError");
        expect(result.error.message).toContain("Photo size exceeds 10MB limit");
      }
      expect(mockFetch).not.toHaveBeenCalled();
    });
  });

  describe("generateTutorial", () => {
    const mockRequest: GenerateTutorialRequest = {
      styleId: "style1",
      customizations: "Add more emphasis on contouring",
    };

    const mockResponse: GenerateTutorialResponse = {
      tutorial: {
        id: "tutorial1",
        title: "Natural Makeup Tutorial",
        description: "Step-by-step guide for natural makeup",
        steps: [
          {
            stepNumber: 1,
            title: "Prep your skin",
            description: "Cleanse and moisturize",
            imageUrl: "https://storage.googleapis.com/bucket/step1.jpg",
            videoUrl: "https://storage.googleapis.com/bucket/step1.mp4",
            tools: ["Cleanser", "Moisturizer"],
          },
          {
            stepNumber: 2,
            title: "Apply foundation",
            description: "Even out skin tone",
            imageUrl: "https://storage.googleapis.com/bucket/step2.jpg",
            videoUrl: "https://storage.googleapis.com/bucket/step2.mp4",
            tools: ["Foundation", "Beauty sponge"],
          },
        ],
        totalTime: "15 minutes",
      },
    };

    it("should successfully generate tutorial", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.generateTutorial(mockRequest);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/tutorials/generate",
        expect.objectContaining({
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(mockRequest),
          signal: expect.any(AbortSignal),
        }),
      );

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockResponse);
      }
    });

    it("should handle timeout for long-running requests", async () => {
      jest.useFakeTimers();

      // Mock a request that never resolves
      mockFetch.mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                ok: true,
                json: async () => mockResponse,
              } as Response);
            }, 300000); // 5 minutes
          }),
      );

      const resultPromise = apiClient.generateTutorial(mockRequest);

      // Fast-forward time
      jest.advanceTimersByTime(240000); // 4 minutes timeout

      const result = await resultPromise;

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.error).toBe("TimeoutError");
        expect(result.error.message).toContain("Request timed out");
      }

      jest.useRealTimers();
    });

    it("should retry on failure with exponential backoff", async () => {
      // First two attempts fail, third succeeds
      mockFetch
        .mockRejectedValueOnce(new Error("Network error"))
        .mockRejectedValueOnce(new Error("Network error"))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        } as Response);

      const result = await apiClient.generateTutorial(mockRequest, {
        maxRetries: 3,
      });

      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(result.success).toBe(true);
    });

    it("should fail after max retries", async () => {
      mockFetch.mockRejectedValue(new Error("Network error"));

      const result = await apiClient.generateTutorial(mockRequest, {
        maxRetries: 3,
      });

      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.error).toBe("NetworkError");
      }
    });
  });

  describe("getStyleDetail", () => {
    const styleId = "style1";
    const mockResponse: StyleDetailResponse = {
      style: {
        id: "style1",
        title: "Natural Makeup",
        description: "A fresh, natural look",
        imageUrl: "https://storage.googleapis.com/bucket/style1.jpg",
        tools: ["Foundation", "Blush", "Mascara"],
        estimatedTime: "15 minutes",
      },
    };

    it("should successfully get style details", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.getStyleDetail(styleId);

      expect(mockFetch).toHaveBeenCalledWith(
        `http://localhost:8000/api/styles/${styleId}`,
        expect.objectContaining({
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          signal: expect.any(AbortSignal),
        }),
      );

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockResponse);
      }
    });

    it("should handle 404 not found", async () => {
      const errorResponse: ApiError = {
        error: "NotFound",
        message: "Style not found",
        statusCode: 404,
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => errorResponse,
      } as Response);

      const result = await apiClient.getStyleDetail("nonexistent");

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.statusCode).toBe(404);
        expect(result.error.error).toBe("NotFound");
      }
    });
  });

  describe("request interceptor", () => {
    it("should add API key header if configured", async () => {
      apiClient = new ApiClient({ apiKey: "test-api-key" });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ styles: [] }),
      } as Response);

      await apiClient.generateStyles({
        photo: "photo",
        gender: "neutral",
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            "X-API-Key": "test-api-key",
          }),
        }),
      );
    });
  });

  describe("error handling", () => {
    it("should parse JSON error responses", async () => {
      const errorResponse = {
        error: "ValidationError",
        message: "Invalid request",
        details: {
          field: "photo",
          issue: "Required field",
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => errorResponse,
      } as Response);

      const result = await apiClient.generateStyles({
        photo: "",
        gender: "female",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.details).toEqual(errorResponse.details);
      }
    });

    it("should handle non-JSON error responses", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: async () => "Internal Server Error",
        json: async () => {
          throw new Error("Not JSON");
        },
      } as unknown as Response);

      const result = await apiClient.generateStyles({
        photo: "photo",
        gender: "male",
      });

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.error).toBe("ServerError");
        expect(result.error.statusCode).toBe(500);
      }
    });
  });

  describe("abort functionality", () => {
    it("should allow aborting requests", async () => {
      const abortController = new AbortController();

      mockFetch.mockImplementationOnce(
        () =>
          new Promise((resolve, reject) => {
            setTimeout(() => {
              reject(new Error("Aborted"));
            }, 100);
          }),
      );

      const resultPromise = apiClient.generateStyles(
        {
          photo: "photo",
          gender: "female",
        },
        { signal: abortController.signal },
      );

      // Abort the request
      abortController.abort();

      const result = await resultPromise;

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.error).toBe("AbortError");
      }
    });
  });
});
