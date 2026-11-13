import React, { useState } from 'react';
import { X, Lock, Mail, User, Shield, Sparkles, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AuthModal() {
  const {
    isAuthModalOpen,
    setIsAuthModalOpen,
    authModalMode,
    setAuthModalMode,
    login,
    signup,
    quickDemoLogin,
    guestQueryCount,
    maxGuestQueries,
    hasReachedGuestLimit,
  } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  if (!isAuthModalOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all required fields.');
      return;
    }

    if (authModalMode === 'signup' && !name) {
      setError('Please enter your full name.');
      return;
    }

    if (authModalMode === 'login') {
      login(email, password);
    } else {
      signup(name, email, password);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-neutral-900/60 backdrop-blur-xs transition-opacity"
        onClick={() => setIsAuthModalOpen(false)}
      />

      <div className="relative w-full max-w-md bg-white border border-neutral-200 rounded-3xl shadow-2xl p-6 sm:p-8 overflow-hidden z-10">
        {/* Close Button */}
        <button
          onClick={() => setIsAuthModalOpen(false)}
          className="absolute top-5 right-5 p-2 rounded-full text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Heading */}
        <div className="text-center space-y-2 mb-6">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            <span>{hasReachedGuestLimit ? 'Guest Query Cap Reached' : 'Shopcart Member Access'}</span>
          </div>
          <h2 className="text-2xl font-extrabold text-neutral-900 font-display tracking-tight">
            {authModalMode === 'login' ? 'Sign In to Shopcart' : 'Join Shopcart AI'}
          </h2>
          <p className="text-xs text-neutral-500">
            {hasReachedGuestLimit
              ? `You've used all ${maxGuestQueries} free guest queries. Sign in to unlock unlimited AI chats, spec charts, and 15% discount.`
              : 'Unlock unlimited hybrid AI intelligence, cart sync, and member-only pricing.'}
          </p>
        </div>

        {/* Quick Demo Logins */}
        <div className="space-y-2 mb-6">
          <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider text-center">
            Instant 1-Click Demo Access
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => quickDemoLogin('customer')}
              className="py-2.5 px-3 rounded-2xl bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 text-[#0B4232] text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-2xs"
            >
              <User className="w-3.5 h-3.5 text-emerald-600" />
              <span>Pro Member</span>
            </button>
            <button
              type="button"
              onClick={() => quickDemoLogin('admin')}
              className="py-2.5 px-3 rounded-2xl bg-amber-50 border border-amber-200 hover:bg-amber-100 text-amber-900 text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-2xs"
            >
              <Shield className="w-3.5 h-3.5 text-amber-700" />
              <span>Admin Demo</span>
            </button>
          </div>
        </div>

        <div className="relative flex py-1 items-center mb-5">
          <div className="flex-grow border-t border-neutral-200"></div>
          <span className="flex-shrink mx-3 text-[11px] font-medium text-neutral-400 uppercase">
            Or with email
          </span>
          <div className="flex-grow border-t border-neutral-200"></div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-xs font-medium text-center">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {authModalMode === 'signup' && (
            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-neutral-400" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Alex Rivera"
                  className="w-full pl-10 pr-4 py-2.5 bg-neutral-50 border border-neutral-200 rounded-2xl text-xs sm:text-sm text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 focus:bg-white transition-colors"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-neutral-700 mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-neutral-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="shopper@shopcart.com"
                className="w-full pl-10 pr-4 py-2.5 bg-neutral-50 border border-neutral-200 rounded-2xl text-xs sm:text-sm text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 focus:bg-white transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-neutral-700 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-neutral-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-neutral-50 border border-neutral-200 rounded-2xl text-xs sm:text-sm text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 focus:bg-white transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md mt-2"
          >
            {authModalMode === 'login' ? 'Sign In' : 'Create Free Account'}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-5 text-center text-xs text-neutral-500">
          {authModalMode === 'login' ? (
            <span>
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setError('');
                  setAuthModalMode('signup');
                }}
                className="text-emerald-700 font-semibold hover:underline"
              >
                Sign up free
              </button>
            </span>
          ) : (
            <span>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setError('');
                  setAuthModalMode('login');
                }}
                className="text-emerald-700 font-semibold hover:underline"
              >
                Sign in
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
