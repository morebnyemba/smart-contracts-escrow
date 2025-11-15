const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  if (token && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return { error: errorData.detail || 'An error occurred' };
    }

    const data = await response.json();
    return { data };
  } catch {
    return { error: 'Network error occurred' };
  }
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_seller: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

export interface SellerProfile {
  id: number;
  user: User;
  public_seller_id: string;
  account_type: 'INDIVIDUAL' | 'COMPANY';
  company_name?: string;
  verification_document?: string;
  verification_status: 'UNVERIFIED' | 'PENDING' | 'VERIFIED';
  skills: ServiceCategory[];
}

export interface ServiceCategory {
  id: number;
  name: string;
  slug: string;
}

export interface CreateSellerProfileData {
  account_type: 'INDIVIDUAL' | 'COMPANY';
  company_name?: string;
  skill_ids?: number[];
}

// Authentication APIs
export const authAPI = {
  register: (data: RegisterData) =>
    fetchAPI<AuthResponse>('/api/users/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: LoginData) =>
    fetchAPI<{ access: string; refresh: string }>('/api/users/auth/login/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getCurrentUser: () =>
    fetchAPI<User>('/api/users/auth/user/', {
      method: 'GET',
    }),

  refreshToken: (refresh: string) =>
    fetchAPI<{ access: string }>('/api/users/auth/token/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh }),
    }),
};

// Seller APIs
export const sellerAPI = {
  getProfile: () =>
    fetchAPI<SellerProfile>('/api/users/seller/profile/', {
      method: 'GET',
    }),

  createProfile: (data: CreateSellerProfileData) =>
    fetchAPI<SellerProfile>('/api/users/seller/profile/create/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateProfile: (data: Partial<CreateSellerProfileData>) =>
    fetchAPI<SellerProfile>('/api/users/seller/profile/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};

// Service Categories API
export const categoriesAPI = {
  getAll: () =>
    fetchAPI<ServiceCategory[]>('/api/users/categories/', {
      method: 'GET',
    }),
};
