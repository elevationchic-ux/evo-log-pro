import { getSession } from 'next-auth/react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface RequestConfig extends RequestInit {
  params?: Record<string, any>;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function getAuthToken(): Promise<string | null> {
  try {
    const session = await getSession();
    return session?.accessToken || null;
  } catch {
    return null;
  }
}

export async function apiClient<T = any>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<T> {
  const { params, ...fetchConfig } = config;

  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) url += `?${queryString}`;
  }

  // Get auth token
  const token = await getAuthToken();

  // Build headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...fetchConfig.headers,
  };

  try {
    const response = await fetch(url, {
      ...fetchConfig,
      headers,
    });

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    if (!contentType?.includes('application/json')) {
      if (!response.ok) {
        throw new ApiError(response.status, 'Unexpected response format');
      }
      return response.text() as Promise<T>;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(response.status, data.detail || 'An error occurred');
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(0, 'Network error');
  }
}

// Helper methods
export const api = {
  get: <T>(endpoint: string, config?: RequestConfig) =>
    apiClient<T>(endpoint, { ...config, method: 'GET' }),
  
  post: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    apiClient<T>(endpoint, { ...config, method: 'POST', body: JSON.stringify(data) }),
  
  put: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    apiClient<T>(endpoint, { ...config, method: 'PUT', body: JSON.stringify(data) }),
  
  patch: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    apiClient<T>(endpoint, { ...config, method: 'PATCH', body: JSON.stringify(data) }),
  
  delete: <T>(endpoint: string, config?: RequestConfig) =>
    apiClient<T>(endpoint, { ...config, method: 'DELETE' }),
};

export default apiClient;