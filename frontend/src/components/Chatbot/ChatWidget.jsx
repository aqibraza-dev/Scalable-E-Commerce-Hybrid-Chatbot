import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  X,
  Send,
  Zap,
  Lock,
  Plus,
  Trash2,
  Clock,
  Shield,
  ShoppingBag,
  Sparkles,
  Maximize2,
  Minimize2,
  Cpu,
  Check,
  ChevronRight,
  BarChart2,
  Bot
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import PhoneRenderer from '../PhoneRenderer';
import ChatSpecChart from './ChatSpecChart';

const INITIAL_GREETING = {
  id: 'msg_welcome',
  sender: 'bot',
  text: "👋 **Hello! Welcome to Shopcart AI Advisor.**\nI can help you search smartphones, compare specs, find the best deals for your budget, or manage your shopping cart.\n\n*Try asking:*\n- *'Best camera phone under 10k rupees'*\n- *'Best camera phone under mid budget'*\n- *'Sabse sasta aur mahanga phone dikhao'*\n- *'Compare Vivo V50 and Realme P3 Pro'*\n- *'What is your return policy?'*",
  routing_tier: 'TIER_3_TYPICAL_BOT',
  tokens_used: 0,
  tokens_saved: 350,
  execution_time_ms: 0.8,
  cache_hit: true,
  timestamp: Date.now(),
};

export default function ChatWidget({ isOpen, onClose, initialQuery = '' }) {
  const {
    isAuthenticated,
    user,
    hasReachedGuestLimit,
    remainingGuestQueries,
    maxGuestQueries,
    incrementGuestQueryCount,
    guestChartCount,
    maxGuestCharts,
    remainingGuestCharts,
    hasReachedGuestChartLimit,
    incrementGuestChartCount,
    openLoginModal,
  } = useAuth();

  const {
    cart,
    addToCart,
    openCart,
    clearCart,
    subtotal,
    totalItemCount
  } = useCart();

  // Sessions state
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem('shopcart_chat_sessions');
      return saved ? JSON.parse(saved) : [{ id: 'session_default', title: 'Main Chat', messages: [INITIAL_GREETING] }];
    } catch {
      return [{ id: 'session_default', title: 'Main Chat', messages: [INITIAL_GREETING] }];
    }
  });

  const [activeSessionId, setActiveSessionId] = useState('session_default');
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const messagesEndRef = useRef(null);

  // Active session helper
  const currentSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];
  const messages = currentSession?.messages || [];

  // Persist sessions
  useEffect(() => {
    localStorage.setItem('shopcart_chat_sessions', JSON.stringify(sessions));
  }, [sessions]);

  // Handle initialQuery when opened
  useEffect(() => {
    if (isOpen && initialQuery) {
      setInputText(initialQuery);
    }
  }, [isOpen, initialQuery]);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const updateSessionMessages = (sessionId, newMessages, titleUpdate = null) => {
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id === sessionId) {
          return {
            ...s,
            messages: newMessages,
            title: titleUpdate || s.title,
            updatedAt: Date.now(),
          };
        }
        return s;
      })
    );
  };

  const createNewSession = () => {
    const newId = 'session_' + Math.random().toString(36).substring(2, 9);
    const newSession = {
      id: newId,
      title: `Conversation ${sessions.length + 1}`,
      messages: [INITIAL_GREETING],
      createdAt: Date.now(),
    };
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newId);
    setIsSidebarOpen(false);
  };

  const deleteSession = (sessionId, e) => {
    e.stopPropagation();
    if (sessions.length <= 1) {
      updateSessionMessages(sessionId, [INITIAL_GREETING], 'Main Chat');
      return;
    }
    const filtered = sessions.filter((s) => s.id !== sessionId);
    setSessions(filtered);
    if (activeSessionId === sessionId) {
      setActiveSessionId(filtered[0].id);
    }
  };

  // Conversational Intent Interceptor (Cart & Local context)
  const processLocalIntents = (query) => {
    const q = query.toLowerCase().trim();

    // 1. View Cart Intent
    if (q === 'view cart' || q === 'show cart' || q === 'show my cart' || q === 'what is in my cart' || q === 'cart') {
      if (cart.length === 0) {
        return {
          handled: true,
          response: "🛒 **Your Cart is currently empty.**\nBrowse our smartphones or ask me to recommend models, then tap *'Add to Cart'*!",
          routing_tier: 'TIER_3_TYPICAL_BOT',
          tokens_used: 0,
          tokens_saved: 300,
          execution_time_ms: 0.5,
          cart_action: { type: 'view_empty' }
        };
      }

      const itemsList = cart.map((item, i) => `${i + 1}. **${item.name}** (x${item.quantity}) — ₹${(item.price * item.quantity).toLocaleString('en-IN')}`).join('\n');
      return {
        handled: true,
        response: `🛍️ **Current Shopping Cart (${totalItemCount} items)**:\n${itemsList}\n\n**Subtotal**: ₹${subtotal.toLocaleString('en-IN')}\nClick below to open your cart and checkout!`,
        routing_tier: 'TIER_3_TYPICAL_BOT',
        tokens_used: 0,
        tokens_saved: 320,
        execution_time_ms: 0.8,
        cart_action: { type: 'view_summary' }
      };
    }

    // 2. Clear Cart Intent
    if (q === 'clear cart' || q === 'empty cart') {
      clearCart();
      return {
        handled: true,
        response: "🗑️ **Shopping Cart Cleared.** All items have been removed from your cart.",
        routing_tier: 'TIER_3_TYPICAL_BOT',
        tokens_used: 0,
        tokens_saved: 250,
        execution_time_ms: 0.6,
      };
    }

    // 3. Checkout Intent
    if (q === 'checkout' || q === 'proceed to checkout' || q === 'go to checkout') {
      openCart();
      return {
        handled: true,
        response: "🛍️ **Opening your Shopping Cart for Checkout.**\nApply promo code **SHOPCART50** for 15% discount, and complete your order with express delivery!",
        routing_tier: 'TIER_3_TYPICAL_BOT',
        tokens_used: 0,
        tokens_saved: 280,
        execution_time_ms: 0.5,
        cart_action: { type: 'checkout' }
      };
    }

    // 4. Quick Contextual Add-to-Cart Intent
    if (q === 'add to cart' || q === 'add it to cart' || q === 'add this to cart' || q === 'buy it') {
      let recentProduct = null;
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].products && messages[i].products.length > 0) {
          recentProduct = messages[i].products[0];
          break;
        }
      }
      if (recentProduct) {
        addToCart(recentProduct);
        return {
          handled: true,
          response: `⚡ **Added ${recentProduct.name} to your Cart!** (Price: ₹${(recentProduct.price || 0).toLocaleString('en-IN')})\nYour cart now has ${totalItemCount + 1} item(s). Click below to review or checkout!`,
          routing_tier: 'TIER_3_TYPICAL_BOT',
          tokens_used: 0,
          tokens_saved: 350,
          execution_time_ms: 0.5,
          products: [recentProduct],
          cart_action: { type: 'add_success', product: recentProduct }
        };
      }
    }

    return { handled: false };
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    const query = inputText.trim();
    if (!query || isLoading) return;

    // Check guest limit
    if (hasReachedGuestLimit) {
      openLoginModal();
      return;
    }

    // Append user message
    const userMsg = {
      id: 'msg_user_' + Date.now(),
      sender: 'user',
      text: query,
      timestamp: Date.now(),
    };

    const updatedMessages = [...messages, userMsg];
    updateSessionMessages(
      activeSessionId,
      updatedMessages,
      messages.length === 1 ? query.substring(0, 24) : null
    );

    setInputText('');
    setIsLoading(true);
    incrementGuestQueryCount();

    // 1. Check local client-side fast intents
    const local = processLocalIntents(query);
    if (local.handled) {
      setTimeout(() => {
        const botMsg = {
          id: 'msg_bot_' + Date.now(),
          sender: 'bot',
          text: local.response,
          routing_tier: local.routing_tier,
          tokens_used: local.tokens_used,
          tokens_saved: local.tokens_saved,
          execution_time_ms: local.execution_time_ms,
          cart_action: local.cart_action,
          products: local.products || [],
          timestamp: Date.now(),
        };
        updateSessionMessages(activeSessionId, [...updatedMessages, botMsg]);
        setIsLoading(false);
      }, 150);
      return;
    }

    // 2. Send request to FastAPI backend
    try {
      const recentHistory = messages.slice(-4).map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          mode: 'hybrid',
          user_id: user?.id || 'guest_user',
          history: recentHistory,
          cart_items: cart,
        }),
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();

      if (data.cart_action && data.cart_action.type === 'add' && data.cart_action.product) {
        addToCart(data.cart_action.product);
      }

      const botMsg = {
        id: 'msg_bot_' + Date.now(),
        sender: 'bot',
        text: data.response,
        routing_tier: data.routing_tier,
        tokens_used: data.tokens_used,
        tokens_saved: data.tokens_saved,
        execution_time_ms: data.execution_time_ms,
        cache_hit: data.cache_hit,
        similarity_score: data.similarity_score,
        pii_redacted: data.pii_redacted,
        redactions: data.redactions,
        products: data.products || [],
        cart_action: data.cart_action,
        timestamp: Date.now(),
      };

      updateSessionMessages(activeSessionId, [...updatedMessages, botMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const fallbackMsg = {
        id: 'msg_bot_' + Date.now(),
        sender: 'bot',
        text: "⚡ I encountered an issue reaching the search service. Please verify the FastAPI backend is running.",
        routing_tier: 'TIER_0_NETWORK_FALLBACK',
        tokens_used: 0,
        tokens_saved: 0,
        execution_time_ms: 10,
        timestamp: Date.now(),
      };
      updateSessionMessages(activeSessionId, [...updatedMessages, fallbackMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderTierBadge = (tier, timeMs, tokensSaved) => {
    switch (tier) {
      case 'TIER_0_GUARDRAIL_BLOCKED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-red-50 border border-red-200 text-red-700 text-[10px] font-mono font-bold">
            <Shield className="w-2.5 h-2.5" /> GUARDRAIL BLOCKED ({timeMs}ms)
          </span>
        );
      case 'TIER_1_EXACT_CACHE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[10px] font-mono font-bold">
            <Zap className="w-2.5 h-2.5" /> EXACT CACHE ({timeMs}ms • {tokensSaved} tokens saved)
          </span>
        );
      case 'TIER_2_SEMANTIC_CACHE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-cyan-50 border border-cyan-200 text-cyan-800 text-[10px] font-mono font-bold">
            <Sparkles className="w-2.5 h-2.5" /> SEMANTIC CACHE ({timeMs}ms)
          </span>
        );
      case 'TIER_3_TYPICAL_BOT':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-[10px] font-mono font-bold">
            <Cpu className="w-2.5 h-2.5" /> DETERMINISTIC SQL BOT ({timeMs}ms • 0 Tokens)
          </span>
        );
      case 'TIER_4_PURE_LLM':
      case 'TIER_4_LLM_RAG':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-800 text-[10px] font-mono font-bold">
            <Bot className="w-2.5 h-2.5" /> HYBRID LLM RAG ({timeMs}ms)
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-neutral-100 border border-neutral-200 text-neutral-600 text-[10px] font-mono">
            {tier}
          </span>
        );
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/40 backdrop-blur-sm animate-fadeIn">
      <div
        className={`relative bg-white border border-neutral-200 shadow-2xl rounded-3xl flex flex-col overflow-hidden transition-all duration-300 ${
          isExpanded
            ? 'w-full h-full max-w-6xl max-h-[92vh]'
            : 'w-full max-w-3xl h-[640px]'
        }`}
      >
        {/* Chat Header */}
        <div className="px-6 py-4 bg-neutral-50/90 border-b border-neutral-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-xl bg-white border border-neutral-200 text-neutral-500 hover:text-neutral-900 transition-colors shadow-xs"
              title="Chat History"
            >
              <Clock className="w-4 h-4" />
            </button>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-display font-extrabold text-sm tracking-tight text-[#0B4232]">
                  Shopcart AI Assistant
                </span>
                <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              </div>
              <div className="flex items-center gap-2 text-[11px] font-sans text-neutral-500">
                <span>Multi-Tier Hybrid Search</span>
                <span>•</span>
                {isAuthenticated ? (
                  <span className="text-emerald-700 font-bold">VIP UNLIMITED</span>
                ) : (
                  <span>
                    Guest: <strong className="text-emerald-800 font-mono">{remainingGuestQueries}/{maxGuestQueries} queries</strong>
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-neutral-500 hover:text-neutral-900 rounded-xl hover:bg-neutral-100 transition-colors"
              title={isExpanded ? 'Restore' : 'Maximize'}
            >
              {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={onClose}
              className="p-2 text-neutral-500 hover:text-neutral-900 rounded-xl hover:bg-neutral-100 transition-colors"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Main Body */}
        <div className="flex-1 flex overflow-hidden relative">
          {/* History Sidebar */}
          {isSidebarOpen && (
            <div className="absolute inset-y-0 left-0 w-64 bg-neutral-50 border-r border-neutral-200 z-20 flex flex-col p-4 shadow-xl animate-fadeIn">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold uppercase text-neutral-700 tracking-wider">
                  CHAT SESSIONS
                </span>
                <button
                  onClick={createNewSession}
                  className="flex items-center gap-1 px-3 py-1 rounded-full bg-[#0B4232] text-white font-semibold text-xs hover:bg-[#064E3B] transition-colors shadow-xs"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>NEW</span>
                </button>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                {sessions.map((sess) => (
                  <div
                    key={sess.id}
                    onClick={() => {
                      setActiveSessionId(sess.id);
                      setIsSidebarOpen(false);
                    }}
                    className={`p-3 rounded-2xl cursor-pointer text-xs flex items-center justify-between group transition-all ${
                      sess.id === activeSessionId
                        ? 'bg-emerald-50 border border-emerald-300 text-[#0B4232] font-bold shadow-xs'
                        : 'bg-white border border-neutral-200 text-neutral-600 hover:border-neutral-300'
                    }`}
                  >
                    <span className="truncate flex-1">{sess.title}</span>
                    <button
                      onClick={(e) => deleteSession(sess.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-neutral-400 hover:text-red-500 p-1 transition-opacity"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Messages Stream */}
          <div className="flex-1 flex flex-col overflow-hidden bg-neutral-50/50">
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${
                    msg.sender === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  {/* Sender Tag */}
                  <div className="text-[10px] font-mono text-neutral-500 mb-1 px-1 flex items-center gap-2">
                    <span>{msg.sender === 'user' ? 'YOU' : 'SHOPCART AI'}</span>
                    {msg.routing_tier && renderTierBadge(msg.routing_tier, msg.execution_time_ms, msg.tokens_saved)}
                  </div>

                  {/* Message Bubble */}
                  <div
                    className={`max-w-[85%] rounded-3xl px-5 py-3.5 text-xs sm:text-sm leading-relaxed shadow-sm ${
                      msg.sender === 'user'
                        ? 'bg-[#0B4232] text-white font-medium'
                        : 'bg-white border border-neutral-200/90 text-neutral-900'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.text}</div>

                    {/* Cart Action Button / Summary Widget */}
                    {msg.cart_action && (
                      <div className="mt-3 pt-2.5 border-t border-neutral-200 flex items-center gap-2">
                        <button
                          onClick={openCart}
                          className="px-4 py-2 rounded-full bg-[#0B4232] text-white font-semibold text-xs flex items-center gap-1.5 hover:bg-[#064E3B] transition-all shadow-xs"
                        >
                          <ShoppingBag className="w-3.5 h-3.5" />
                          <span>OPEN CART ({totalItemCount})</span>
                        </button>
                      </div>
                    )}

                    {/* Embedded Product Recommendations */}
                    {msg.products && msg.products.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-neutral-200 space-y-3">
                        <div className="text-[11px] font-mono font-bold uppercase text-emerald-800">
                          RECOMMENDED SMARTPHONES ({msg.products.length}):
                        </div>

                        {/* Interactive Comparison Chart if 2+ products */}
                        {msg.products.length >= 2 && (
                          <ChatSpecChart
                            products={msg.products}
                            title="Side-by-Side Comparison Chart"
                          />
                        )}

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {msg.products.map((prod) => (
                            <div
                              key={prod.id || prod.name}
                              className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200 hover:border-emerald-500 transition-colors flex gap-3 items-center group shadow-xs"
                            >
                              {/* Procedural Phone Mini View */}
                              <div className="w-14 h-20 bg-white rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden border border-neutral-200 p-1">
                                <PhoneRenderer
                                  phone={prod}
                                  size="xs"
                                  view="back"
                                  interactive={false}
                                />
                              </div>

                              <div className="flex-1 min-w-0">
                                <h5 className="font-bold text-neutral-900 text-xs truncate">
                                  {prod.name}
                                </h5>
                                <div className="text-[10px] text-neutral-500 font-mono mt-0.5">
                                  {prod.ram ? `${Math.round(prod.ram)}GB RAM` : '8GB'} • {prod.primary_rear_camera || 50}MP • {prod.battery_cap}mAh
                                </div>
                                <div className="flex items-center justify-between mt-2">
                                  <span className="text-xs font-extrabold text-neutral-900 font-sans">
                                    ₹{(prod.price || 0).toLocaleString('en-IN')}
                                  </span>
                                  <button
                                    onClick={() => addToCart(prod)}
                                    className="px-3 py-1 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white text-[10px] font-bold uppercase transition-colors flex items-center gap-1 shadow-xs"
                                  >
                                    <ShoppingBag className="w-3 h-3" />
                                    <span>ADD</span>
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex items-center gap-2 p-3 text-xs font-mono text-neutral-500">
                  <div className="w-2 h-2 rounded-full bg-emerald-600 animate-ping" />
                  <span>Scanning B-Tree index & executing hybrid orchestrator...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggested Prompt Chips */}
            <div className="px-5 py-2.5 border-t border-neutral-200 bg-white flex items-center gap-2 overflow-x-auto scrollbar-none">
              <span className="text-[10px] font-mono text-neutral-400 uppercase flex-shrink-0 font-bold">
                PROMPTS:
              </span>
              {[
                'Best camera phone under 10k rupees',
                'Best camera phone under mid budget',
                'Sabse sasta aur mahanga phone dikhao',
                'Compare Vivo V50 and Realme P3 Pro',
                'Who are you?',
                'What is your return policy?'
              ].map((p) => (
                <button
                  key={p}
                  onClick={() => {
                    setInputText(p);
                  }}
                  className="px-3 py-1 rounded-full bg-neutral-100 hover:bg-emerald-50 hover:text-[#0B4232] border border-neutral-200/80 text-neutral-700 text-xs whitespace-nowrap transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-neutral-200 flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Ask about phones, camera quality, specs, comparisons, or policies..."
                className="flex-1 px-4 py-3 bg-neutral-100 border border-neutral-200 rounded-full text-xs sm:text-sm text-neutral-900 placeholder-neutral-400 focus:outline-none focus:border-emerald-600 transition-colors shadow-xs"
              />
              <button
                type="submit"
                disabled={isLoading || !inputText.trim()}
                className="px-5 py-3 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white text-xs font-bold uppercase transition-colors flex items-center gap-1.5 shadow-xs disabled:opacity-50"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
