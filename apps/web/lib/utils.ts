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

/**
 * Convert snake_case object keys to camelCase
 */
export function snakeToCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

/**
 * Recursively convert all snake_case keys in an object to camelCase
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function convertKeysToCamelCase<T = any>(obj: any): T {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToCamelCase(item)) as T;
  }

  if (typeof obj === "object") {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const converted: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const camelKey = snakeToCamelCase(key);
        converted[camelKey] = convertKeysToCamelCase(obj[key]);
      }
    }
    return converted as T;
  }

  return obj;
}
