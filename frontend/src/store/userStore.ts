import { create } from 'zustand';
import { User } from '@/lib/api';

interface User {
  id: number;
  username: string;
  is_seller?: boolean;
}

interface UserState {
  user: User | null;
  token: string | null;
  isSeller: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  accessToken: typeof window !== 'undefined' ? localStorage.getItem('access_token') : null,
  refreshToken: typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null,
  isSeller: false,
  
  login: (accessToken, refreshToken, user) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
    set({ 
      accessToken, 
      refreshToken, 
      user, 
      isSeller: user?.is_seller || false 
    });
  },
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    set({ user: null, accessToken: null, refreshToken: null, isSeller: false });
  },
  
  setUser: (user) => {
    set({ user, isSeller: user?.is_seller || false });
  },
  
  updateToken: (accessToken) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
    }
    set({ accessToken });
  },
}));
