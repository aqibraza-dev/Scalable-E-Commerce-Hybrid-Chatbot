import React, { useState } from 'react';
import {
  Lock,
  Mail,
  User,
  Shield,
  Zap,
  CheckCircle2,
  ArrowLeft,
  ShoppingCart,
  Sparkles,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import PhoneRenderer from '../PhoneRenderer';

export default function AuthPage({ onBackToStore }) {
  const {
    login,
    signup,
    quickDemoLogin,
    guestQueryCount,
    maxGuestQueries,
    hasReachedGuestLimit,
  } = useAuth();

  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  // Sample flagship for dynamic graphic showcase
  const demoPhone = {
    id: 'auth_showcase',
    name: 'Samsung Galaxy S25 Ultra',
    brand: 'samsung',
    price: 129999,
    ram: 16,
    storage: 512,
    battery_cap: 5000,
    has_5g: 'Yes',
    primary_rear_camera: 200,
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    if (mode === 'signup' && !name) {
      setError('Please enter your full name.');
      return;
    }

    if (mode === 'login') {
      login(email, password);
    } else {
      signup(name, email, password);
    }

    if (onBackToStore) {
      onBackToStore();
    }
  };

  const handleDemoClick = (role) => {
    quickDemoLogin(role);
    if (onBackToStore) {
      onBackToStore();
    }
  };

  return (
    <div className="min-h-screen bg-[#FBFBFB] text-neutral-800 flex flex-col font-sans">
      {/* Top Bar */}
      <div className="p-4 sm:p-6 max-w-7xl mx-auto w-full flex items-center justify-between">
        <button
          onClick={onBackToStore}
          className="inline-flex items-center gap-2 text-xs font-semibold text-neutral-600 hover:text-[#0B4232] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Store</span>
        </button>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-[#0B4232]">
            <ShoppingCart className="w-4 h-4 text-emerald-600" />
          </div>
          <span className="font-display font-extrabold text-base tracking-tight text-[#0B4232]">
            Shopcart <span className="text-emerald-500 font-sans text-xs font-semibold">AI Hub</span>
          </span>
        </div>
      </div>

      {/* Main Split Screen */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-5xl bg-white border border-neutral-200 rounded-3xl shadow-xl overflow-hidden grid grid-cols-1 lg:grid-cols-12">
          {/* Left Column: Brand Hero & Dynamic Graphic */}
          <div className="lg:col-span-5 bg-[#0B4232] text-white p-8 sm:p-10 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-emerald-900/40 relative overflow-hidden">
            {/* Ambient emerald glow */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-400/10 rounded-full blur-3xl pointer-events-none" />

            <div className="space-y-4 relative z-10">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-emerald-300 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Shopcart VIP Member Portal</span>
              </div>

              <h2 className="text-3xl sm:text-4xl font-extrabold text-white font-display tracking-tight leading-tight">
                Shop Smarter. <br />
                <span className="text-emerald-300">Sub-Millisecond</span> <br />
                Hardware Search.
              </h2>

              <p className="text-xs text-emerald-100/80 leading-relaxed">
                Join our smartphone community. Unlock unlimited hybrid AI queries, side-by-side spec comparison charts, instant member discounts, and personalized recommendations.
              </p>
            </div>

            {/* Center: Dynamic Procedural Phone Graphic */}
            <div className="py-6 flex items-center justify-center relative z-10">
              <PhoneRenderer
                phone={demoPhone}
                size="md"
                view="back"
                interactive={true}
              />
            </div>

            {/* Bottom Perks Checklist */}
            <div className="space-y-2 pt-4 border-t border-emerald-800/80 text-xs text-emerald-100 relative z-10">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Unlimited AI hybrid queries & spec charts</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Multi-turn session memory & cart sync</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Instant 15% promo code: <strong>SHOPCART50</strong></span>
              </div>
            </div>
          </div>

          {/* Right Column: Authentication Form */}
          <div className="lg:col-span-7 p-8 sm:p-12 flex flex-col justify-center space-y-6 bg-white">
            {/* Status if guest limit reached */}
            {hasReachedGuestLimit && (
              <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 flex items-center gap-3">
                <div className="p-2 rounded-full bg-amber-100 text-amber-800">
                  <Lock className="w-4 h-4" />
                </div>
                <div className="text-xs">
                  <span className="font-bold text-amber-900 block">
                    Free Guest Limit Reached ({guestQueryCount}/{maxGuestQueries} Queries)
                  </span>
                  <span className="text-[11px] text-amber-700">
                    Sign in below or use instant 1-click demo access to continue without limits.
                  </span>
                </div>
              </div>
            )}

            {/* Mode Switcher Tabs */}
            <div className="flex rounded-full bg-neutral-100 p-1 border border-neutral-200">
              <button
                type="button"
                onClick={() => setMode('login')}
                className={`flex-1 py-2.5 rounded-full text-xs font-bold tracking-wider transition-all ${
                  mode === 'login'
                    ? 'bg-[#0B4232] text-white shadow-sm'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setMode('signup')}
                className={`flex-1 py-2.5 rounded-full text-xs font-bold tracking-wider transition-all ${
                  mode === 'signup'
                    ? 'bg-[#0B4232] text-white shadow-sm'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                Create Account
              </button>
            </div>

            {/* Instant 1-Click Demo Logins */}
            <div className="space-y-2">
              <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider text-center">
                Instant 1-Click Demo Access
              </div>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => handleDemoClick('customer')}
                  className="py-2.5 px-3 rounded-2xl bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 text-[#0B4232] text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-2xs"
                >
                  <User className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Pro Member</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoClick('admin')}
                  className="py-2.5 px-3 rounded-2xl bg-amber-50 border border-amber-200 hover:bg-amber-100 text-amber-900 text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-2xs"
                >
                  <Shield className="w-3.5 h-3.5 text-amber-700" />
                  <span>Admin Demo</span>
                </button>
              </div>
            </div>

            <div className="relative flex py-1 items-center">
              <div className="flex-grow border-t border-neutral-200"></div>
              <span className="flex-shrink mx-3 text-[11px] font-medium text-neutral-400 uppercase">
                Or with credentials
              </span>
              <div className="flex-grow border-t border-neutral-200"></div>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-xs font-medium text-center">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === 'signup' && (
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
                      className="w-full pl-10 pr-4 py-3 bg-neutral-50 border border-neutral-200 rounded-2xl text-xs sm:text-sm text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 focus:bg-white transition-colors"
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
                    className="w-full pl-10 pr-4 py-3 bg-neutral-50 border border-neutral-200 rounded-2xl text-xs sm:text-sm text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 focus:bg-white transition-colors"
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
                    className="w-full pl-10 pr-4 py-3 bg-neutral-50 border border-neutral-200 rounded-2xl text-xs sm:text-sm text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 focus:bg-white transition-colors"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3.5 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 mt-2"
              >
                <span>{mode === 'login' ? 'Sign In Now' : 'Create Free Account'}</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </form>

            <div className="pt-2 text-center text-[11px] text-neutral-400 font-mono">
              256-BIT ENCRYPTED • SECURE AUTHENTICATION • PRIVACY GUARANTEED
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
