import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PhotoUpload } from "@/components/photo-upload";
import "@testing-library/jest-dom";

describe("PhotoUpload", () => {
  const mockOnPhotoUpload = jest.fn();

  beforeEach(() => {
    mockOnPhotoUpload.mockClear();
    // Mock URL.createObjectURL
    global.URL.createObjectURL = jest.fn(
      () => "blob:http://localhost:3000/test-preview",
    );
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("should render upload area initially", () => {
    render(<PhotoUpload onPhotoUpload={mockOnPhotoUpload} />);
    expect(screen.getByText("写真をアップロード")).toBeInTheDocument();
    expect(
      screen.getByText(/ここに画像をドラッグ&ドロップするか、クリックして選択/),
    ).toBeInTheDocument();
  });

  it("should handle file selection via input", async () => {
    render(<PhotoUpload onPhotoUpload={mockOnPhotoUpload} />);

    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = screen
      .getByRole("button", { name: /ファイルを選択/i })
      .closest("div")
      ?.querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLInputElement, file);

      expect(mockOnPhotoUpload).toHaveBeenCalledWith(file);
      expect(screen.getByText("test.jpg")).toBeInTheDocument();
      expect(screen.getByText("アップロード済み")).toBeInTheDocument();
    }
  });

  it("should validate file type", async () => {
    const alertSpy = jest.spyOn(window, "alert").mockImplementation(() => {});
    render(<PhotoUpload onPhotoUpload={mockOnPhotoUpload} />);

    const file = new File(["test"], "test.txt", { type: "text/plain" });
    const input = screen
      .getByRole("button", { name: /ファイルを選択/i })
      .closest("div")
      ?.querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLInputElement, file);

      expect(alertSpy).toHaveBeenCalledWith("画像ファイルを選択してください");
      expect(mockOnPhotoUpload).not.toHaveBeenCalled();
    }
  });

  it("should validate file size", async () => {
    const alertSpy = jest.spyOn(window, "alert").mockImplementation(() => {});
    render(<PhotoUpload onPhotoUpload={mockOnPhotoUpload} />);

    // Create a file larger than 10MB
    const largeFile = new File(["x".repeat(11 * 1024 * 1024)], "large.jpg", {
      type: "image/jpeg",
    });
    Object.defineProperty(largeFile, "size", { value: 11 * 1024 * 1024 });

    const input = screen
      .getByRole("button", { name: /ファイルを選択/i })
      .closest("div")
      ?.querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLInputElement, largeFile);

      expect(alertSpy).toHaveBeenCalledWith(
        "ファイルサイズは10MB以下にしてください",
      );
      expect(mockOnPhotoUpload).not.toHaveBeenCalled();
    }
  });

  it("should handle drag and drop", async () => {
    render(<PhotoUpload onPhotoUpload={mockOnPhotoUpload} />);

    const dropZone = screen
      .getByText("写真をアップロード")
      .closest(".cursor-pointer") as HTMLElement;
    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });

    const dataTransfer = {
      files: [file],
      items: [
        {
          kind: "file",
          getAsFile: () => file,
        },
      ],
    };

    fireEvent.dragEnter(dropZone);
    fireEvent.dragOver(dropZone);
    fireEvent.drop(dropZone, { dataTransfer });

    await waitFor(() => {
      expect(mockOnPhotoUpload).toHaveBeenCalledWith(file);
      expect(screen.getByText("test.jpg")).toBeInTheDocument();
    });
  });

  it("should allow removing uploaded file", async () => {
    render(<PhotoUpload onPhotoUpload={mockOnPhotoUpload} />);

    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    const input = screen
      .getByRole("button", { name: /ファイルを選択/i })
      .closest("div")
      ?.querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLInputElement, file);
      expect(screen.getByText("test.jpg")).toBeInTheDocument();

      const removeButton = screen.getByRole("button", { name: "" });
      await userEvent.click(removeButton);

      expect(screen.queryByText("test.jpg")).not.toBeInTheDocument();
      expect(screen.getByText("写真をアップロード")).toBeInTheDocument();
    }
  });

  it("should display file size correctly", async () => {
    render(<PhotoUpload onPhotoUpload={mockOnPhotoUpload} />);

    const file = new File(["x".repeat(2.5 * 1024 * 1024)], "test.jpg", {
      type: "image/jpeg",
    });
    Object.defineProperty(file, "size", { value: 2.5 * 1024 * 1024 });

    const input = screen
      .getByRole("button", { name: /ファイルを選択/i })
      .closest("div")
      ?.querySelector('input[type="file"]');

    if (input) {
      await userEvent.upload(input as HTMLInputElement, file);
      expect(screen.getByText("2.50 MB")).toBeInTheDocument();
    }
  });
});
