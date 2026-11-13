import React, { useState } from 'react';
import {
  ShoppingCart,
  Search,
  User,
  ChevronDown,
  Layers,
  BarChart2,
  Shield,
  LogOut,
  Sparkles,
  Zap
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';

export default function Navbar({
  currentPage = 'home',
  onNavigate,
  onOpenChat,
  onOpenAuthPage,
  onSearch
}) {
  const {
    isAuthenticated,
    user,
    isAdmin,
    remainingGuestQueries,
    maxGuestQueries,
    openLoginModal,
    logout,
  } = useAuth();

  const { totalItemCount, openCart } = useCart();
  const [searchInput, setSearchInput] = useState('');
  const [categoriesOpen, setCategoriesOpen] = useState(false);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchInput);
    }
    if (onNavigate && currentPage !== 'shop') {
      onNavigate('shop');
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-white/95 backdrop-blur-md border-b border-neutral-200 shadow-xs">
      {/* Top Banner Notice */}
      <div className="bg-[#0B4232] text-white text-[11px] font-sans py-1.5 px-4 text-center flex items-center justify-center gap-2">
        <Sparkles className="w-3 h-3 text-emerald-300" />
        <span>
          <strong>Shopcart AI Speed Engine</strong> — 99.1% zero-token efficiency & sub-millisecond B-Tree smartphone search
        </span>
        <span className="hidden sm:inline">• Use promo code <strong>SHOPCART50</strong> for 15% instant checkout discount</span>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between gap-4">
        {/* Brand Logo - Inspired by Shopcart */}
        <div className="flex items-center gap-8">
          <button
            onClick={() => onNavigate && onNavigate('home')}
            className="flex items-center gap-2 group text-left"
          >
            <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-[#0B4232] group-hover:scale-105 transition-transform shadow-xs">
              <ShoppingCart className="w-5 h-5 text-emerald-600" />
            </div>
            <div className="flex flex-col">
              <span className="font-display font-extrabold text-xl tracking-tight text-[#0B4232] leading-none">
                Shopcart
              </span>
              <span className="text-[10px] font-sans font-medium text-emerald-600 tracking-wider uppercase mt-0.5">
                AI Smartphone Hub
              </span>
            </div>
          </button>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center gap-6 text-xs font-semibold text-neutral-700">
            <div className="relative">
              <button
                onClick={() => setCategoriesOpen(!categoriesOpen)}
                className="flex items-center gap-1 hover:text-[#0B4232] transition-colors py-2"
              >
                <span>Categories</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </button>

              {categoriesOpen && (
                <div
                  onMouseLeave={() => setCategoriesOpen(false)}
                  className="absolute top-full left-0 w-52 bg-white rounded-2xl shadow-xl border border-neutral-200 p-2 z-50 animate-fadeIn"
                >
                  <button
                    onClick={() => {
                      onNavigate('shop');
                      setCategoriesOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 text-xs font-medium rounded-xl hover:bg-neutral-50 text-neutral-800"
                  >
                    Flagship Phones (₹50k+)
                  </button>
                  <button
                    onClick={() => {
                      onNavigate('shop');
                      setCategoriesOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 text-xs font-medium rounded-xl hover:bg-neutral-50 text-neutral-800"
                  >
                    Mid-Budget 5G (₹15k - ₹35k)
                  </button>
                  <button
                    onClick={() => {
                      onNavigate('shop');
                      setCategoriesOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 text-xs font-medium rounded-xl hover:bg-neutral-50 text-neutral-800"
                  >
                    Best Camera Under 10k
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={() => onNavigate && onNavigate('shop')}
              className={`hover:text-[#0B4232] transition-colors ${
                currentPage === 'shop' ? 'text-[#0B4232] font-bold' : ''
              }`}
            >
              Smartphones
            </button>

            <button
              onClick={() => onNavigate && onNavigate('benchmarks')}
              className={`hover:text-[#0B4232] transition-colors flex items-center gap-1.5 ${
                currentPage === 'benchmarks' ? 'text-[#0B4232] font-bold' : ''
              }`}
            >
              <BarChart2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Benchmarks</span>
            </button>

            <a
              href="#architecture"
              onClick={(e) => {
                if (currentPage !== 'home') {
                  e.preventDefault();
                  onNavigate && onNavigate('home');
                  setTimeout(() => {
                    document.getElementById('architecture')?.scrollIntoView({ behavior: 'smooth' });
                  }, 100);
                }
              }}
              className="hover:text-[#0B4232] transition-colors flex items-center gap-1"
            >
              <Layers className="w-3.5 h-3.5 text-emerald-600" />
              <span>Architecture</span>
            </a>

            <button
              onClick={() => onNavigate && onNavigate('admin')}
              className={`hover:text-[#0B4232] transition-colors ${
                currentPage === 'admin' ? 'text-[#0B4232] font-bold' : ''
              }`}
            >
              Admin
            </button>
          </nav>
        </div>

        {/* Center Search Input - Reference Design */}
        <form onSubmit={handleSearchSubmit} className="hidden md:flex flex-1 max-w-md relative">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search Product (e.g. 'best camera phone under 10k')..."
            className="w-full pl-4 pr-10 py-2.5 bg-neutral-100 hover:bg-neutral-50 focus:bg-white border border-neutral-200 rounded-full text-xs text-neutral-800 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 transition-all shadow-xs"
          />
          <button
            type="submit"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-[#0B4232] transition-colors"
          >
            <Search className="w-4 h-4" />
          </button>
        </form>

        {/* Right Action Icons: Account & Cart */}
        <div className="flex items-center gap-3">
          {/* AI Advisor Button */}
          <button
            onClick={onOpenChat}
            className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 text-[#0B4232] text-xs font-semibold transition-all shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            <span>AI Assistant</span>
          </button>

          {/* Account */}
          {!isAuthenticated ? (
            <button
              onClick={openLoginModal}
              className="flex items-center gap-1.5 text-xs font-semibold text-neutral-700 hover:text-[#0B4232] py-2 px-2.5 rounded-full hover:bg-neutral-100 transition-colors"
            >
              <User className="w-4 h-4 text-neutral-500" />
              <span className="hidden sm:inline">Account</span>
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-neutral-800">
                {user?.name?.split(' ')[0] || 'VIP'}
              </span>
              <button
                onClick={logout}
                className="p-1.5 rounded-full text-neutral-400 hover:text-red-500 hover:bg-neutral-100 transition-colors"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Cart Pill Button - Inspired by Shopcart reference */}
          <button
            onClick={openCart}
            className="relative flex items-center gap-2 px-4 py-2 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white text-xs font-semibold transition-all shadow-sm"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Cart</span>
            {totalItemCount > 0 && (
              <span className="w-5 h-5 rounded-full bg-emerald-400 text-[#0B4232] font-bold text-[10px] flex items-center justify-center">
                {totalItemCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
