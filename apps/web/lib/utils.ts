import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 文字列を指定された長さで切り詰めます
 * @param str 対象の文字列
 * @param maxLength 最大文字数
 * @returns 省略された文字列
 */
export function truncateText(str: string, maxLength: number): string {
  if (!str) return "";
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength) + "...";
}

/**
 * スタイルのタイトルを省略表示用に整形
 * @param title タイトル
 * @param maxLength 最大文字数（デフォルト: 10）
 */
export function truncateTitle(title: string, maxLength: number = 10): string {
  return truncateText(title, maxLength);
}

/**
 * スタイルの説明文を省略表示用に整形
 * @param description 説明文
 * @param maxLength 最大文字数（デフォルト: 30）
 */
export function truncateDescription(
  description: string,
  maxLength: number = 30,
): string {
  return truncateText(description, maxLength);
}
