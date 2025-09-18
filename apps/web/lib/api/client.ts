import {
  GenerateStylesRequest,
  GenerateStylesResponse,
  GenerateTutorialRequest,
  GenerateTutorialResponse,
  TutorialResponse,
  StyleDetailResponse,
  ApiError,
  ApiResponse,
} from "@/types/api";

export interface ApiClientConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
}

export interface RequestOptions {
  maxRetries?: number;
  signal?: AbortSignal;
}

export class ApiClient {
  public readonly baseUrl: string;
  private readonly apiKey?: string;
  private readonly timeout: number;

  constructor(config?: ApiClientConfig) {
    this.baseUrl =
      config?.baseUrl ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000";
    this.apiKey = config?.apiKey;
    this.timeout = config?.timeout || 240000; // 4 minutes default
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit & { timeout?: number; maxRetries?: number } = {},
  ): Promise<ApiResponse<T>> {
    const { timeout = this.timeout, maxRetries = 1, ...fetchOptions } = options;

    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(fetchOptions.headers as Record<string, string>),
    };

    if (this.apiKey) {
      headers["X-API-Key"] = this.apiKey;
    }

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        let timeoutId: NodeJS.Timeout | undefined;

        // Create promise that rejects on timeout
        const timeoutPromise = new Promise<never>((_, reject) => {
          timeoutId = setTimeout(() => {
            controller.abort();
            reject(new Error("TimeoutError"));
          }, timeout);
        });

        if (fetchOptions.signal) {
          // Handle external abort signal
          const abortHandler = () => controller.abort();
          fetchOptions.signal.addEventListener("abort", abortHandler);
        }

        const response = await Promise.race([
          fetch(url, {
            ...fetchOptions,
            headers,
            signal: controller.signal,
          }),
          timeoutPromise,
        ]);

        if (timeoutId) clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response);
          return {
            success: false,
            error: errorData,
          };
        }

        const data = await response.json();
        return {
          success: true,
          data: data as T,
        };
      } catch (error) {
        // Check if timeout
        if (error instanceof Error && error.message === "TimeoutError") {
          return {
            success: false,
            error: {
              error: "TimeoutError",
              message: `Request timed out after ${timeout}ms`,
            },
          };
        }

        // Check if aborted
        if (
          error instanceof Error &&
          (error.name === "AbortError" || error.message === "Aborted")
        ) {
          return {
            success: false,
            error: {
              error: "AbortError",
              message: "Request was aborted",
            },
          };
        }

        // If not the last attempt, wait and retry
        if (attempt < maxRetries) {
          await this.delay(Math.pow(2, attempt - 1) * 1000); // Exponential backoff
          continue;
        }

        // Network or other errors
        return {
          success: false,
          error: {
            error: "NetworkError",
            message:
              error instanceof Error ? error.message : "Unknown error occurred",
          },
        };
      }
    }

    // Should never reach here, but TypeScript needs it
    return {
      success: false,
      error: {
        error: "UnknownError",
        message: "Unexpected error occurred",
      },
    };
  }

  private async parseErrorResponse(response: Response): Promise<ApiError> {
    try {
      const errorData = await response.json();
      return {
        ...errorData,
        statusCode: response.status,
      };
    } catch {
      return {
        error: "ServerError",
        message: `Server returned ${response.status}`,
        statusCode: response.status,
      };
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  private validatePhotoSize(photo: string): boolean {
    // Rough estimate: Base64 is ~4/3 the size of binary
    const sizeInBytes = (photo.length * 3) / 4;
    const sizeInMB = sizeInBytes / (1024 * 1024);
    return sizeInMB <= 10;
  }

  async generateStyles(
    request: GenerateStylesRequest,
    options?: RequestOptions,
  ): Promise<ApiResponse<GenerateStylesResponse>> {
    // Validate photo size
    if (!this.validatePhotoSize(request.photo)) {
      return {
        success: false,
        error: {
          error: "ValidationError",
          message: "Photo size exceeds 10MB limit",
        },
      };
    }

    return this.request<GenerateStylesResponse>("/api/styles/generate", {
      method: "POST",
      body: JSON.stringify(request),
      signal: options?.signal,
      maxRetries: options?.maxRetries || 1,
    });
  }

  async generateTutorial(
    request: GenerateTutorialRequest,
    options?: RequestOptions,
  ): Promise<ApiResponse<GenerateTutorialResponse>> {
    return this.request<GenerateTutorialResponse>("/api/tutorials/generate", {
      method: "POST",
      body: JSON.stringify(request),
      signal: options?.signal,
      maxRetries: options?.maxRetries || 1,
    });
  }

  async getStyleDetail(
    styleId: string,
    options?: RequestOptions,
  ): Promise<ApiResponse<StyleDetailResponse>> {
    return this.request<StyleDetailResponse>(`/api/styles/${styleId}`, {
      method: "GET",
      signal: options?.signal,
      maxRetries: options?.maxRetries || 1,
    });
  }

  async getTutorial(
    tutorialId: string,
    options?: RequestOptions,
  ): Promise<ApiResponse<TutorialResponse>> {
    return this.request<TutorialResponse>(`/api/tutorials/${tutorialId}`, {
      method: "GET",
      signal: options?.signal,
      maxRetries: options?.maxRetries || 1,
    });
  }

  async getTutorialStatus(
    tutorialId: string,
    options?: RequestOptions,
  ): Promise<ApiResponse<{ status: string; progress?: number }>> {
    return this.request<{ status: string; progress?: number }>(
      `/api/tutorials/${tutorialId}/status`,
      {
        method: "GET",
        signal: options?.signal,
        maxRetries: options?.maxRetries || 1,
      },
    );
  }
}

// Singleton instance
let apiClientInstance: ApiClient | null = null;

export function getApiClient(config?: ApiClientConfig): ApiClient {
  if (!apiClientInstance) {
    apiClientInstance = new ApiClient(config);
  }
  return apiClientInstance;
}

// Export convenience functions
export const apiClient = {
  generateStyles: (request: GenerateStylesRequest, options?: RequestOptions) =>
    getApiClient().generateStyles(request, options),

  generateTutorial: (
    request: GenerateTutorialRequest,
    options?: RequestOptions,
  ) => getApiClient().generateTutorial(request, options),

  getStyleDetail: (styleId: string, options?: RequestOptions) =>
    getApiClient().getStyleDetail(styleId, options),

  getTutorial: (tutorialId: string, options?: RequestOptions) =>
    getApiClient().getTutorial(tutorialId, options),

  getTutorialStatus: (tutorialId: string, options?: RequestOptions) =>
    getApiClient().getTutorialStatus(tutorialId, options),
};
