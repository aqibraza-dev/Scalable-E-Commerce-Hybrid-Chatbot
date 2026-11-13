import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const MAX_GUEST_QUERIES = 5;
const MAX_GUEST_CHARTS = 5;

export function AuthProvider({ children }) {
  // Try loading user session from localStorage
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('aura_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Guest query counter (chats)
  const [guestQueryCount, setGuestQueryCount] = useState(() => {
    try {
      const saved = localStorage.getItem('aura_guest_query_count');
      return saved ? parseInt(saved, 10) : 0;
    } catch {
      return 0;
    }
  });

  // Guest chart counter (hardware spec charts)
  const [guestChartCount, setGuestChartCount] = useState(() => {
    try {
      const saved = localStorage.getItem('aura_guest_chart_count');
      return saved ? parseInt(saved, 10) : 0;
    } catch {
      return 0;
    }
  });

  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('login'); // 'login' | 'signup'

  // Persist session
  useEffect(() => {
    if (user) {
      localStorage.setItem('aura_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('aura_user');
    }
  }, [user]);

  // Persist guest query count
  useEffect(() => {
    localStorage.setItem('aura_guest_query_count', guestQueryCount.toString());
  }, [guestQueryCount]);

  // Persist guest chart count
  useEffect(() => {
    localStorage.setItem('aura_guest_chart_count', guestChartCount.toString());
  }, [guestChartCount]);

  const isAuthenticated = Boolean(user);
  const isAdmin = user?.role === 'admin';
  const remainingGuestQueries = Math.max(0, MAX_GUEST_QUERIES - guestQueryCount);
  const hasReachedGuestLimit = !isAuthenticated && guestQueryCount >= MAX_GUEST_QUERIES;

  const remainingGuestCharts = Math.max(0, MAX_GUEST_CHARTS - guestChartCount);
  const hasReachedGuestChartLimit = !isAuthenticated && guestChartCount >= MAX_GUEST_CHARTS;

  const incrementGuestQueryCount = () => {
    if (!isAuthenticated) {
      setGuestQueryCount((prev) => prev + 1);
    }
  };

  const incrementGuestChartCount = () => {
    if (!isAuthenticated) {
      setGuestChartCount((prev) => prev + 1);
    }
  };

  const login = (email, password) => {
    // Standard mock or custom auth
    const isAdminUser = email.toLowerCase().includes('admin');
    const newUser = {
      id: 'usr_' + Math.random().toString(36).substring(2, 9),
      email,
      name: email.split('@')[0].toUpperCase(),
      role: isAdminUser ? 'admin' : 'customer',
      avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${email}`,
      joinedAt: new Date().toISOString(),
    };
    setUser(newUser);
    setIsAuthModalOpen(false);
    return newUser;
  };

  const quickDemoLogin = (role = 'customer') => {
    const isAdm = role === 'admin';
    const demoUser = {
      id: isAdm ? 'usr_admin_001' : 'usr_member_042',
      email: isAdm ? 'admin@aura-speed.nike' : 'shopper@aura-speed.nike',
      name: isAdm ? 'NIKE SDE ADMIN' : 'AIR PRO MEMBER',
      role: isAdm ? 'admin' : 'customer',
      avatar: isAdm 
        ? 'https://api.dicebear.com/7.x/bottts/svg?seed=AdminNike' 
        : 'https://api.dicebear.com/7.x/bottts/svg?seed=ProShopper',
      joinedAt: new Date().toISOString(),
    };
    setUser(demoUser);
    setIsAuthModalOpen(false);
    return demoUser;
  };

  const signup = (name, email, password) => {
    const newUser = {
      id: 'usr_' + Math.random().toString(36).substring(2, 9),
      email,
      name: name.toUpperCase(),
      role: email.toLowerCase().includes('admin') ? 'admin' : 'customer',
      avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${email}`,
      joinedAt: new Date().toISOString(),
    };
    setUser(newUser);
    setIsAuthModalOpen(false);
    return newUser;
  };

  const logout = () => {
    setUser(null);
  };

  const openLoginModal = () => {
    setAuthModalMode('login');
    setIsAuthModalOpen(true);
  };

  const openSignupModal = () => {
    setAuthModalMode('signup');
    setIsAuthModalOpen(true);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isAdmin,
        guestQueryCount,
        maxGuestQueries: MAX_GUEST_QUERIES,
        remainingGuestQueries,
        hasReachedGuestLimit,
        incrementGuestQueryCount,
        guestChartCount,
        maxGuestCharts: MAX_GUEST_CHARTS,
        remainingGuestCharts,
        hasReachedGuestChartLimit,
        incrementGuestChartCount,
        login,
        signup,
        quickDemoLogin,
        logout,
        isAuthModalOpen,
        setIsAuthModalOpen,
        authModalMode,
        setAuthModalMode,
        openLoginModal,
        openSignupModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
