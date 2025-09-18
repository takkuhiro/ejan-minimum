// API Request/Response types for EJAN

// Gender type for style generation
export type Gender = "male" | "female" | "neutral";

// Style generation request
export interface GenerateStylesRequest {
  photo: string; // Base64 encoded image
  gender: Gender;
}

// Style response
export interface Style {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
}

// Style generation response
export interface GenerateStylesResponse {
  styles: Style[];
}

// Tutorial generation request
export interface GenerateTutorialRequest {
  styleId: string;
  customizations?: string;
}

// Tutorial step
export interface TutorialStep {
  stepNumber: number;
  title: string;
  description: string;
  imageUrl: string;
  videoUrl?: string;
  tools?: string[];
}

// Tutorial response
export interface Tutorial {
  id: string;
  title: string;
  description: string;
  steps: TutorialStep[];
  totalTime?: string;
}

// Tutorial generation response
export interface GenerateTutorialResponse {
  tutorial: Tutorial;
}

// Style detail response
export interface StyleDetailResponse {
  style: Style & {
    tools?: string[];
    estimatedTime?: string;
  };
}

// Error response
export interface ApiError {
  error: string;
  message: string;
  statusCode?: number;
  details?: Record<string, any>;
}

// API Response wrapper
export type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError };
