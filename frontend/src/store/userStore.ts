import { create } from 'zustand';

interface User {
  id: number;
  username: string;
  is_seller?: boolean;
}

interface UserStore {
  user: User | null;
  token: string | null;
  isSeller: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  token: null,
  isSeller: false,
  login: (token, user) => set({ token, user, isSeller: user?.is_seller || false }),
  logout: () => set({ user: null, token: null, isSeller: false }),
}));
