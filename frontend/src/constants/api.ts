export const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/** Backend origin for resolving relative URLs (e.g. /storage/...) */
const BACKEND_ORIGIN = API_BASE_URL.replace(/\/api\/v\d+.*$/, '') || 'http://localhost:8000';

/** Resolve image URL - prepend backend origin for relative paths */
export function resolveImageUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return `${BACKEND_ORIGIN}${url.startsWith('/') ? '' : '/'}${url}`;
}

export const TOKEN_KEY = 'simplecommerce_access_token';
export const REFRESH_TOKEN_KEY = 'simplecommerce_refresh_token';
export const USER_KEY = 'simplecommerce_user';
