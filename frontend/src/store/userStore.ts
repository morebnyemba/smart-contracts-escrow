import { create } from 'zustand';

export const useUserStore = create((set) => ({
  user: null,
  token: null,
  isSeller: false,
  login: (token, user) => set({ token, user, isSeller: user?.is_seller || false }),
  logout: () => set({ user: null, token: null, isSeller: false }),
}));
