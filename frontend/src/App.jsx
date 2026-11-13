import React, { useState, useEffect } from 'react';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import Navbar from './components/Layout/Navbar';
import Hero from './components/Layout/Hero';
import ProductGrid from './components/Catalog/ProductGrid';
import ProductDetailModal from './components/Catalog/ProductDetailModal';
import CartDrawer from './components/Cart/CartDrawer';
import AuthModal from './components/Auth/AuthModal';
import AuthPage from './components/Auth/AuthPage';
import ChatWidget from './components/Chatbot/ChatWidget';
import AdminPanel from './components/Admin/AdminPanel';
import BenchmarksPage from './components/Benchmarks/BenchmarksPage';
import ArchitectureVisualizer from './components/Architecture/ArchitectureVisualizer';
import {
  MessageSquare,
  Shield,
  Zap,
  Sparkles,
  Layers,
  ArrowRight,
  TrendingUp,
  Cpu,
  Database,
  Search,
  ShoppingCart
} from 'lucide-react';

function AppContent() {
  const [currentPage, setCurrentPage] = useState(() => {
    const hash = window.location.hash.replace('#', '').toLowerCase();
    if (['shop', 'benchmarks', 'admin', 'auth', 'architecture'].includes(hash)) {
      return hash === 'architecture' ? 'home' : hash;
    }
    return 'home';
  });

  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInitialQuery, setChatInitialQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [shopSearchQuery, setShopSearchQuery] = useState('');

  // Synchronize hash with current page
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '').toLowerCase();
      if (['shop', 'benchmarks', 'admin', 'auth'].includes(hash)) {
        setCurrentPage(hash);
      } else if (hash === 'home' || hash === '') {
        setCurrentPage('home');
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const navigateTo = (page) => {
    setCurrentPage(page);
    window.location.hash = page === 'home' ? '' : page;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleOpenChatWithQuery = (query) => {
    setChatInitialQuery(query || '');
    setIsChatOpen(true);
  };

  const handleNavbarSearch = (query) => {
    setShopSearchQuery(query);
    navigateTo('shop');
  };

  if (currentPage === 'auth') {
    return (
      <AuthPage
        onBackToStore={() => navigateTo('home')}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#FBFBFB] text-neutral-800 flex flex-col font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* Top Navigation */}
      <Navbar
        currentPage={currentPage}
        onNavigate={navigateTo}
        onOpenChat={() => setIsChatOpen(true)}
        onOpenAuthPage={() => navigateTo('auth')}
        onSearch={handleNavbarSearch}
      />

      {/* Main Page Content */}
      <main className="flex-1">
        {/* ===================== HOME PAGE ===================== */}
        {currentPage === 'home' && (
          <div>
            {/* Hero Banner with Shopcart Style */}
            <Hero
              onOpenChat={() => setIsChatOpen(true)}
              onOpenCatalog={() => navigateTo('shop')}
            />

            {/* Architecture Visualizer Section */}
            <section id="architecture" className="py-12 bg-white border-y border-neutral-200">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
                <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                  <div>
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-[#0B4232] text-xs font-semibold mb-2">
                      <Layers className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Live Interactive System Architecture</span>
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-extrabold text-neutral-900 font-display tracking-tight">
                      5-Tier Optimization Pipeline & Workflow
                    </h2>
                    <p className="text-xs sm:text-sm text-neutral-500 max-w-2xl mt-1">
                      See how Shopcart bypasses LLM overhead using deterministic SQLite B-Trees and semantic vector caching to achieve sub-millisecond smartphone lookups with zero token costs.
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => navigateTo('benchmarks')}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-neutral-100 hover:bg-neutral-200 text-neutral-800 text-xs font-semibold transition-colors"
                    >
                      <span>View Benchmarks</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Architecture Interactive Canvas with Live Cases */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <ArchitectureVisualizer
                  onSelectProduct={(p) => setSelectedProduct(p)}
                />
              </div>
            </section>

            {/* Trending & Featured Smartphones */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
              <div className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                <div>
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold mb-2">
                    <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Popular Smartphone Models</span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-neutral-900 font-display tracking-tight">
                    Trending Phones & Deals
                  </h2>
                  <p className="text-xs sm:text-sm text-neutral-500 max-w-xl">
                    Every device model features procedural SVG industrial chassis design, accurate brand colorways, and camera cluster architectures.
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => navigateTo('shop')}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white text-xs font-semibold shadow-xs transition-all"
                  >
                    <span>View All Phones</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Product Grid */}
              <ProductGrid
                onSelectProduct={(prod) => setSelectedProduct(prod)}
                onOpenChatWithQuery={handleOpenChatWithQuery}
                limit={8}
              />
            </section>

            {/* Architectural Highlights Value Proposition */}
            <section className="bg-[#FAF5EE] border-t border-neutral-200 py-16">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center max-w-2xl mx-auto mb-12">
                  <span className="text-xs font-bold text-emerald-700 tracking-wider uppercase">
                    Why Choose Shopcart AI
                  </span>
                  <h3 className="text-2xl sm:text-3xl font-extrabold text-neutral-900 font-display tracking-tight mt-1">
                    Enterprise Speed Without The Cloud Token Bill
                  </h3>
                  <p className="text-xs sm:text-sm text-neutral-600 mt-2">
                    Standard e-commerce chatbots invoke $0.003 LLMs on every catalog click. Shopcart resolves 99.1% of queries with sub-10ms deterministic speed.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white p-6 rounded-3xl border border-neutral-200 shadow-xs space-y-3">
                    <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                      <Zap className="w-5 h-5" />
                    </div>
                    <h4 className="text-base font-bold text-neutral-900">0.02ms Exact Hash Cache</h4>
                    <p className="text-xs text-neutral-500 leading-relaxed">
                      Frequent queries like &quot;iPhone 15&quot; or &quot;best camera phone&quot; are stored in a microsecond in-memory LRU cache with attached product cards and Add to Cart actions.
                    </p>
                  </div>

                  <div className="bg-white p-6 rounded-3xl border border-neutral-200 shadow-xs space-y-3">
                    <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                      <Database className="w-5 h-5" />
                    </div>
                    <h4 className="text-base font-bold text-neutral-900">FTS5 SQLite B-Tree Index</h4>
                    <p className="text-xs text-neutral-500 leading-relaxed">
                      Instant multi-parameter filtering across 1,376 smartphones by price, RAM, camera megapixels, and 5G connectivity with zero token expenditure.
                    </p>
                  </div>

                  <div className="bg-white p-6 rounded-3xl border border-neutral-200 shadow-xs space-y-3">
                    <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                      <Shield className="w-5 h-5" />
                    </div>
                    <h4 className="text-base font-bold text-neutral-900">Tier 0 Security Guardrails</h4>
                    <p className="text-xs text-neutral-500 leading-relaxed">
                      High-speed regex filters instantly neutralize prompt injection, jailbreaks, and system prompt leakage attacks before any compute or LLM tokens are allocated.
                    </p>
                  </div>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* ===================== SHOP / CATALOG PAGE ===================== */}
        {currentPage === 'shop' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 pb-6">
              <div>
                <h1 className="text-3xl font-extrabold text-neutral-900 font-display tracking-tight">
                  All Smartphones
                </h1>
                <p className="text-xs sm:text-sm text-neutral-500 mt-1">
                  Browse 1,376 indexed smartphones with real-time specs, live pricing, and procedural renders.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setIsChatOpen(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 border border-emerald-200 text-[#0B4232] text-xs font-semibold hover:bg-emerald-100 transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Ask AI for Recommendations</span>
                </button>
              </div>
            </div>

            {/* Product Grid */}
            <ProductGrid
              onSelectProduct={(prod) => setSelectedProduct(prod)}
              onOpenChatWithQuery={handleOpenChatWithQuery}
              initialSearchQuery={shopSearchQuery}
            />
          </div>
        )}

        {/* ===================== BENCHMARKS PAGE ===================== */}
        {currentPage === 'benchmarks' && (
          <BenchmarksPage
            onSelectProduct={(prod) => setSelectedProduct(prod)}
            onOpenChatWithQuery={handleOpenChatWithQuery}
          />
        )}

        {/* ===================== ADMIN PAGE ===================== */}
        {currentPage === 'admin' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <AdminPanel onClose={() => navigateTo('home')} />
          </div>
        )}
      </main>

      {/* Footer - Light Theme matching Shopcart */}
      <footer className="border-t border-neutral-200 bg-white py-12 text-xs text-neutral-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-[#0B4232]">
                <ShoppingCart className="w-4 h-4 text-emerald-600" />
              </div>
              <span className="font-display font-extrabold text-sm text-[#0B4232]">
                Shopcart AI Smartphone Platform
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-neutral-600">
              <span>FastAPI 0.115+</span>
              <span>•</span>
              <span>SQLite FTS5 BM25</span>
              <span>•</span>
              <span>L1 / L2 Semantic Cache</span>
              <span>•</span>
              <span>Framer Motion & Recharts</span>
              <span>•</span>
              <span>100% Vector Procedural Renders</span>
            </div>
          </div>

          <div className="border-t border-neutral-100 pt-6 flex flex-col sm:flex-row justify-between items-center gap-4 text-neutral-400">
            <div>
              Clean Light Theme Design Inspired by Shopcart • Sub-millisecond Hybrid Architecture
            </div>
            <div className="flex gap-5 text-neutral-600 font-semibold">
              <button onClick={() => navigateTo('home')} className="hover:text-[#0B4232] transition-colors">
                Home
              </button>
              <button onClick={() => navigateTo('shop')} className="hover:text-[#0B4232] transition-colors">
                Shop
              </button>
              <button onClick={() => navigateTo('benchmarks')} className="hover:text-[#0B4232] transition-colors">
                Benchmarks
              </button>
              <button onClick={() => navigateTo('admin')} className="hover:text-[#0B4232] transition-colors">
                Admin
              </button>
              <button onClick={() => setIsChatOpen(true)} className="hover:text-[#0B4232] transition-colors">
                AI Assistant
              </button>
            </div>
          </div>
        </div>
      </footer>

      {/* Floating Chat Trigger Button - Shopcart Emerald */}
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 z-40 px-5 py-3.5 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white shadow-xl hover:shadow-2xl hover:scale-105 transition-all group flex items-center gap-2.5"
        title="Open Shopcart AI Assistant"
      >
        <MessageSquare className="w-5 h-5 fill-current text-emerald-300" />
        <span className="font-display font-bold text-xs uppercase tracking-wider">
          Shopcart AI
        </span>
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
      </button>

      {/* Modals & Drawers */}
      <ProductDetailModal
        phone={selectedProduct}
        onClose={() => setSelectedProduct(null)}
        onAskAI={(q) => handleOpenChatWithQuery(q)}
      />

      <CartDrawer />
      <AuthModal />
      <ChatWidget
        isOpen={isChatOpen}
        onClose={() => {
          setIsChatOpen(false);
          setChatInitialQuery('');
        }}
        initialQuery={chatInitialQuery}
      />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <AppContent />
      </CartProvider>
    </AuthProvider>
  );
}
