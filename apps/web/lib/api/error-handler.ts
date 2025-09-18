import { ApiError } from "@/types/api";

export class ApiClientError extends Error {
  public readonly error: ApiError;

  constructor(error: ApiError) {
    super(error.message);
    this.name = "ApiClientError";
    this.error = error;
  }
}

export function isApiError(error: unknown): error is ApiClientError {
  return error instanceof ApiClientError;
}

export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unknown error occurred";
}

export function isNetworkError(error: ApiError): boolean {
  return error.error === "NetworkError";
}

export function isTimeoutError(error: ApiError): boolean {
  return error.error === "TimeoutError";
}

export function isValidationError(error: ApiError): boolean {
  return error.error === "ValidationError";
}

export function isServerError(error: ApiError): boolean {
  return (
    error.error === "ServerError" ||
    (error.statusCode ? error.statusCode >= 500 : false)
  );
}

export function shouldRetry(error: ApiError): boolean {
  return isNetworkError(error) || isTimeoutError(error) || isServerError(error);
}

// Retry configuration
export interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
}

export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
};

export function calculateBackoffDelay(
  attempt: number,
  config: RetryConfig = DEFAULT_RETRY_CONFIG,
): number {
  const delay = Math.min(
    config.baseDelay * Math.pow(2, attempt - 1),
    config.maxDelay,
  );
  // Add jitter to avoid thundering herd
  const jitter = Math.random() * 0.3 * delay;
  return Math.round(delay + jitter);
}

// Utility function to wait for a specified time
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Generic retry function with exponential backoff
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  config: RetryConfig = DEFAULT_RETRY_CONFIG,
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 1; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if error is retryable
      if (isApiError(error) && shouldRetry(error.error)) {
        // If this is not the last attempt, wait and retry
        if (attempt < config.maxRetries) {
          const backoffDelay = calculateBackoffDelay(attempt, config);
          await delay(backoffDelay);
          continue;
        }
      }

      // Non-retryable error or last attempt - throw immediately
      throw error;
    }
  }

  // This should never be reached, but TypeScript needs it
  throw lastError;
}
