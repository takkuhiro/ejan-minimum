import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "next/navigation";
import WelcomePage from "@/app/page";
import { apiClient } from "@/lib/api/client";
import "@testing-library/jest-dom";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

// Mock API client
jest.mock("@/lib/api/client", () => ({
  apiClient: {
    generateStyles: jest.fn(),
  },
}));

// Mock toast notifications
jest.mock("sonner", () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
    loading: jest.fn(() => "toast-id"),
    dismiss: jest.fn(),
  },
  Toaster: () => null,
}));

describe("WelcomePage API Integration", () => {
  const mockPush = jest.fn();
  const mockRouter = {
    push: mockPush,
    replace: jest.fn(),
    prefetch: jest.fn(),
  };

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    mockPush.mockClear();
    (apiClient.generateStyles as jest.Mock).mockClear();
    global.URL.createObjectURL = jest.fn(
      () => "blob:http://localhost:3000/test",
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should call API when submitting form with valid data", async () => {
    const mockResponse = {
      success: true,
      data: {
        styles: [
          {
            id: "1",
            title: "Style 1",
            description: "Desc 1",
            imageUrl: "http://example.com/1.jpg",
          },
          {
            id: "2",
            title: "Style 2",
            description: "Desc 2",
            imageUrl: "http://example.com/2.jpg",
          },
          {
            id: "3",
            title: "Style 3",
            description: "Desc 3",
            imageUrl: "http://example.com/3.jpg",
          },
        ],
      },
    };

    (apiClient.generateStyles as jest.Mock).mockResolvedValue(mockResponse);

    render(<WelcomePage />);

    // Select gender
    const femaleRadio = screen.getByLabelText("女性");
    await userEvent.click(femaleRadio);

    // Upload photo
    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await userEvent.upload(input, file);

    // Click generate button
    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });
    await userEvent.click(generateButton);

    // Check if API was called with correct parameters
    await waitFor(() => {
      expect(apiClient.generateStyles).toHaveBeenCalledWith(
        expect.objectContaining({
          photo: expect.any(String), // Base64 encoded
          gender: "female",
        }),
        expect.any(Object),
      );
    });
  });

  it("should convert file to base64 before sending", async () => {
    const mockResponse = {
      success: true,
      data: {
        styles: [
          {
            id: "1",
            title: "Style 1",
            description: "Desc 1",
            imageUrl: "http://example.com/1.jpg",
          },
        ],
      },
    };

    (apiClient.generateStyles as jest.Mock).mockResolvedValue(mockResponse);

    render(<WelcomePage />);

    // Select gender
    const maleRadio = screen.getByLabelText("男性");
    await userEvent.click(maleRadio);

    // Create a file with specific content
    const fileContent = "test-image-content";
    const file = new File([fileContent], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await userEvent.upload(input, file);

    // Click generate button
    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });
    await userEvent.click(generateButton);

    // Verify base64 encoding was performed
    await waitFor(() => {
      const callArgs = (apiClient.generateStyles as jest.Mock).mock.calls[0];
      expect(callArgs[0].photo).toMatch(/^data:image\/jpeg;base64,/);
      expect(callArgs[0].gender).toBe("male");
    });
  });

  it("should navigate to styles page on successful response", async () => {
    const mockResponse = {
      success: true,
      data: {
        styles: [
          {
            id: "1",
            title: "Style 1",
            description: "Desc 1",
            imageUrl: "http://example.com/1.jpg",
          },
        ],
      },
    };

    (apiClient.generateStyles as jest.Mock).mockImplementation(() =>
      Promise.resolve(mockResponse),
    );

    render(<WelcomePage />);

    // Select gender
    const neutralRadio = screen.getByLabelText("中性的");
    await userEvent.click(neutralRadio);

    // Upload photo
    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;

    // Mock FileReader
    const mockFileReader = {
      readAsDataURL: jest.fn(),
      onload: null as any,
      onerror: null as any,
      result: "data:image/jpeg;base64,dGVzdA==",
    };

    jest
      .spyOn(window, "FileReader")
      .mockImplementation(() => mockFileReader as any);

    await userEvent.upload(input, file);

    // Trigger FileReader onload
    if (mockFileReader.onload) {
      mockFileReader.onload();
    }

    // Click generate button
    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });
    await userEvent.click(generateButton);

    // Check navigation with styles data
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(
        expect.stringContaining("/styles?data="),
      );
    });
  });

  it("should show loading state during API call", async () => {
    // Create a promise we can control
    let resolvePromise: (value: any) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    (apiClient.generateStyles as jest.Mock).mockReturnValue(pendingPromise);

    render(<WelcomePage />);

    // Select gender and upload photo
    const femaleRadio = screen.getByLabelText("女性");
    await userEvent.click(femaleRadio);

    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await userEvent.upload(input, file);

    // Click generate button
    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });
    await userEvent.click(generateButton);

    // Check loading state
    expect(screen.getByText(/スタイルを生成中.../i)).toBeInTheDocument();
    expect(generateButton).toBeDisabled();

    // Resolve the promise
    resolvePromise!({
      success: true,
      data: { styles: [] },
    });

    // Wait for loading to complete
    await waitFor(() => {
      expect(
        screen.queryByText(/スタイルを生成中.../i),
      ).not.toBeInTheDocument();
    });
  });

  it("should handle API error gracefully", async () => {
    const mockError = {
      success: false,
      error: {
        error: "ServerError",
        message: "Failed to generate styles",
      },
    };

    (apiClient.generateStyles as jest.Mock).mockResolvedValue(mockError);

    render(<WelcomePage />);

    // Select gender and upload photo
    const maleRadio = screen.getByLabelText("男性");
    await userEvent.click(maleRadio);

    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await userEvent.upload(input, file);

    // Click generate button
    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });
    await userEvent.click(generateButton);

    // Wait for error handling
    await waitFor(() => {
      // Should not navigate on error
      expect(mockPush).not.toHaveBeenCalled();
      // Button should be enabled again
      expect(generateButton).not.toBeDisabled();
    });
  });

  it("should disable generate button when required fields are missing", () => {
    render(<WelcomePage />);

    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });

    // Button should be disabled initially
    expect(generateButton).toBeDisabled();
  });

  it("should enable generate button only when both gender and photo are selected", async () => {
    render(<WelcomePage />);

    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });

    // Initially disabled
    expect(generateButton).toBeDisabled();

    // Select gender
    const femaleRadio = screen.getByLabelText("女性");
    await userEvent.click(femaleRadio);

    // Still disabled without photo
    expect(generateButton).toBeDisabled();

    // Upload photo
    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await userEvent.upload(input, file);

    // Now should be enabled
    await waitFor(() => {
      expect(generateButton).not.toBeDisabled();
    });
  });

  it("should handle network timeout error", async () => {
    const mockError = {
      success: false,
      error: {
        error: "TimeoutError",
        message: "Request timed out after 30000ms",
      },
    };

    (apiClient.generateStyles as jest.Mock).mockResolvedValue(mockError);

    render(<WelcomePage />);

    // Select gender and upload photo
    const maleRadio = screen.getByLabelText("男性");
    await userEvent.click(maleRadio);

    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await userEvent.upload(input, file);

    // Click generate button
    const generateButton = screen.getByRole("button", {
      name: /メイクアップスタイルを生成する/i,
    });
    await userEvent.click(generateButton);

    // Wait for timeout handling
    await waitFor(() => {
      expect(mockPush).not.toHaveBeenCalled();
      expect(generateButton).not.toBeDisabled();
    });
  });
});
