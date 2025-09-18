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
