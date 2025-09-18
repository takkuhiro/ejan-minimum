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
  customization?: string;
}

// Tutorial step
export interface TutorialStep {
  stepNumber: number;
  title: string;
  description: string;
  detailedInstructions?: string;
  imageUrl: string;
  videoUrl: string;
  tools: string[];
  tips?: string[];
}

// Tutorial response
export interface TutorialResponse {
  id: string;
  title: string;
  description: string;
  totalSteps: number;
  steps: TutorialStep[];
  status?: "PROCESSING" | "COMPLETED" | "FAILED";
}

// Tutorial generation response
export interface GenerateTutorialResponse extends TutorialResponse {}

// Style detail response
export interface StyleDetailResponse {
  style: Style & {
    tools?: string[];
    estimatedTime?: string;
  };
}

// Custom style generation request
export interface GenerateCustomStyleRequest {
  styleId?: string;
  customRequest: string;
  isFromScratch?: boolean;
}

// Custom style generation response
export interface GenerateCustomStyleResponse {
  style: Style & {
    steps?: string[];
    tools?: string[];
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
