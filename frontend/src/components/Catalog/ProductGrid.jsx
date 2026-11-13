import React, { useState, useEffect } from 'react';
import {
  Search,
  SlidersHorizontal,
  ChevronDown,
  Heart,
  Star,
  ShoppingBag,
  Zap,
  Check,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import PhoneRenderer from '../PhoneRenderer';
import { useCart } from '../../context/CartContext';

const BRANDS = ['All Brands', 'Samsung', 'Apple', 'OnePlus', 'Google', 'Xiaomi', 'Realme', 'Vivo', 'Motorola', 'Nothing'];
const PRICE_PRESETS = [
  { label: 'All Prices', min: null, max: null },
  { label: 'Under ₹10,000', min: null, max: 10000 },
  { label: '₹15,000 - ₹35,000 (Mid-Budget)', min: 15000, max: 35000 },
  { label: '₹35,000 - ₹60,000 (Upper-Mid)', min: 35000, max: 60000 },
  { label: 'Above ₹60,000 (Flagship)', min: 60000, max: null },
];

export default function ProductGrid({
  onSelectProduct,
  onOpenChatWithQuery,
  initialSearch = ''
}) {
  const { addToCart } = useCart();

  const [products, setProducts] = useState([]);
  const [totalMatches, setTotalMatches] = useState(0);
  const [executionTimeMs, setExecutionTimeMs] = useState(0.8);
  const [fromCache, setFromCache] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Wishlist state (stored locally)
  const [wishlist, setWishlist] = useState(() => {
    try {
      const saved = localStorage.getItem('shopcart_wishlist');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  // Filter States
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [selectedBrand, setSelectedBrand] = useState('All Brands');
  const [pricePreset, setPricePreset] = useState('All Prices');
  const [has5GOnly, setHas5GOnly] = useState(false);
  const [minRam, setMinRam] = useState(0);
  const [sortBy, setSortBy] = useState('relevance');

  // Pill dropdown popovers
  const [activeDropdown, setActiveDropdown] = useState(null);

  useEffect(() => {
    if (initialSearch !== undefined) {
      setSearchQuery(initialSearch);
    }
  }, [initialSearch]);

  const toggleWishlist = (phoneId, e) => {
    e.stopPropagation();
    setWishlist((prev) => {
      const updated = { ...prev, [phoneId]: !prev[phoneId] };
      localStorage.setItem('shopcart_wishlist', JSON.stringify(updated));
      return updated;
    });
  };

  // Fetch products
  const fetchProducts = async () => {
    setIsLoading(true);
    try {
      const currentPreset = PRICE_PRESETS.find((p) => p.label === pricePreset) || PRICE_PRESETS[0];

      const payload = {
        query: searchQuery.trim() || null,
        brand: selectedBrand === 'All Brands' ? null : selectedBrand.toLowerCase(),
        min_price: currentPreset.min,
        max_price: currentPreset.max,
        has_5g: has5GOnly ? 'Yes' : null,
        min_ram: minRam > 0 ? minRam : null,
        sort_by: sortBy,
        limit: 28,
      };

      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setProducts(data.products || []);
        setTotalMatches(data.total_matches || 0);
        setExecutionTimeMs(data.execution_time_ms || 1.1);
        setFromCache(data.from_cache || false);
      }
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchProducts();
    }, 150);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedBrand, pricePreset, has5GOnly, minRam, sortBy]);

  return (
    <div className="space-y-8">
      {/* ----------------- SHOPCART PILL FILTERS BAR (Reference Design) ----------------- */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-neutral-200">
        <div className="flex flex-wrap items-center gap-2">
          {/* 1. Brand Pill */}
          <div className="relative">
            <button
              onClick={() => setActiveDropdown(activeDropdown === 'brand' ? null : 'brand')}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold border transition-all ${
                selectedBrand !== 'All Brands'
                  ? 'bg-[#0B4232] text-white border-[#0B4232]'
                  : 'bg-neutral-100/80 text-neutral-800 border-neutral-200 hover:bg-neutral-200/80'
              }`}
            >
              <span>{selectedBrand}</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {activeDropdown === 'brand' && (
              <div
                onMouseLeave={() => setActiveDropdown(null)}
                className="absolute top-full left-0 mt-1 w-44 bg-white rounded-2xl shadow-xl border border-neutral-200 p-2 z-30 space-y-1 animate-fadeIn"
              >
                {BRANDS.map((b) => (
                  <button
                    key={b}
                    onClick={() => {
                      setSelectedBrand(b);
                      setActiveDropdown(null);
                    }}
                    className={`w-full text-left px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
                      selectedBrand === b ? 'bg-emerald-50 text-[#0B4232] font-bold' : 'hover:bg-neutral-50 text-neutral-700'
                    }`}
                  >
                    {b}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 2. Price Pill */}
          <div className="relative">
            <button
              onClick={() => setActiveDropdown(activeDropdown === 'price' ? null : 'price')}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold border transition-all ${
                pricePreset !== 'All Prices'
                  ? 'bg-[#0B4232] text-white border-[#0B4232]'
                  : 'bg-neutral-100/80 text-neutral-800 border-neutral-200 hover:bg-neutral-200/80'
              }`}
            >
              <span>{pricePreset}</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {activeDropdown === 'price' && (
              <div
                onMouseLeave={() => setActiveDropdown(null)}
                className="absolute top-full left-0 mt-1 w-56 bg-white rounded-2xl shadow-xl border border-neutral-200 p-2 z-30 space-y-1 animate-fadeIn"
              >
                {PRICE_PRESETS.map((p) => (
                  <button
                    key={p.label}
                    onClick={() => {
                      setPricePreset(p.label);
                      setActiveDropdown(null);
                    }}
                    className={`w-full text-left px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
                      pricePreset === p.label ? 'bg-emerald-50 text-[#0B4232] font-bold' : 'hover:bg-neutral-50 text-neutral-700'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 3. RAM Pill */}
          <div className="relative">
            <button
              onClick={() => setActiveDropdown(activeDropdown === 'ram' ? null : 'ram')}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold border transition-all ${
                minRam > 0
                  ? 'bg-[#0B4232] text-white border-[#0B4232]'
                  : 'bg-neutral-100/80 text-neutral-800 border-neutral-200 hover:bg-neutral-200/80'
              }`}
            >
              <span>{minRam > 0 ? `${minRam}GB+ RAM` : 'RAM'}</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {activeDropdown === 'ram' && (
              <div
                onMouseLeave={() => setActiveDropdown(null)}
                className="absolute top-full left-0 mt-1 w-36 bg-white rounded-2xl shadow-xl border border-neutral-200 p-2 z-30 space-y-1 animate-fadeIn"
              >
                {[0, 6, 8, 12, 16].map((r) => (
                  <button
                    key={r}
                    onClick={() => {
                      setMinRam(r);
                      setActiveDropdown(null);
                    }}
                    className={`w-full text-left px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
                      minRam === r ? 'bg-emerald-50 text-[#0B4232] font-bold' : 'hover:bg-neutral-50 text-neutral-700'
                    }`}
                  >
                    {r === 0 ? 'All RAM' : `${r}GB & Above`}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 4. 5G Toggle Pill */}
          <button
            onClick={() => setHas5GOnly(!has5GOnly)}
            className={`px-4 py-2 rounded-full text-xs font-semibold border transition-all ${
              has5GOnly
                ? 'bg-[#0B4232] text-white border-[#0B4232]'
                : 'bg-neutral-100/80 text-neutral-800 border-neutral-200 hover:bg-neutral-200/80'
            }`}
          >
            5G Ready
          </button>

          {/* Reset Filters */}
          {(selectedBrand !== 'All Brands' || pricePreset !== 'All Prices' || minRam > 0 || has5GOnly || searchQuery) && (
            <button
              onClick={() => {
                setSelectedBrand('All Brands');
                setPricePreset('All Prices');
                setMinRam(0);
                setHas5GOnly(false);
                setSearchQuery('');
              }}
              className="text-xs font-medium text-neutral-500 hover:text-red-600 transition-colors px-2 underline"
            >
              Reset
            </button>
          )}
        </div>

        {/* Sort by Pill (Right aligned) */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-neutral-500 font-medium">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3.5 py-1.5 bg-neutral-100 border border-neutral-200 rounded-full text-xs font-semibold text-neutral-800 focus:outline-none focus:border-[#0B4232] cursor-pointer"
          >
            <option value="relevance">Relevance</option>
            <option value="camera_desc">Best Camera (High MP)</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="battery_desc">Battery Capacity</option>
            <option value="ram_desc">Highest RAM</option>
          </select>
        </div>
      </div>

      {/* Heading & Telemetry */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <h2 className="text-2xl font-extrabold text-neutral-900 font-display tracking-tight">
          Smartphones For You!
        </h2>

        <div className="flex items-center gap-3 text-xs font-mono text-neutral-500">
          <span>
            Found <strong className="text-neutral-900">{totalMatches}</strong> smartphones
          </span>
          <span>•</span>
          <span className="flex items-center gap-1 text-emerald-700 font-semibold">
            <Zap className="w-3 h-3 text-emerald-600" />
            <span>SQLite B-Tree: {executionTimeMs}ms</span>
          </span>
          {fromCache && (
            <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
              CACHE HIT
            </span>
          )}
        </div>
      </div>

      {/* ----------------- PRODUCT GRID ----------------- */}
      {isLoading ? (
        <div className="py-24 flex flex-col items-center justify-center text-center space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-[#0B4232] border-t-transparent animate-spin" />
          <span className="text-xs font-mono text-neutral-500">
            Filtering catalog with sub-millisecond query execution...
          </span>
        </div>
      ) : products.length === 0 ? (
        <div className="py-20 text-center space-y-4 bg-neutral-50 rounded-3xl border border-neutral-200 p-8">
          <p className="text-sm text-neutral-600 font-medium">
            No smartphones matched your exact filter combination.
          </p>
          <button
            onClick={() => {
              setSelectedBrand('All Brands');
              setPricePreset('All Prices');
              setMinRam(0);
              setHas5GOnly(false);
              setSearchQuery('');
            }}
            className="px-6 py-2.5 rounded-full bg-[#0B4232] text-white font-semibold text-xs shadow-sm hover:bg-[#064E3B]"
          >
            Clear All Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((phone) => {
            const isWishlisted = !!wishlist[phone.id];
            const reviewCount = 80 + (phone.id % 95);

            return (
              <div
                key={phone.id}
                onClick={() => onSelectProduct && onSelectProduct(phone)}
                className="group relative bg-[#F7F7F7] hover:bg-white border border-neutral-100 hover:border-neutral-200 rounded-3xl p-5 flex flex-col justify-between transition-all duration-300 shadow-xs hover:shadow-card-hover cursor-pointer"
              >
                {/* Top Section: Wishlist Heart Button */}
                <div className="relative w-full">
                  <button
                    onClick={(e) => toggleWishlist(phone.id, e)}
                    className="absolute right-0 top-0 z-10 w-8 h-8 rounded-full bg-white shadow-xs border border-neutral-200/80 flex items-center justify-center transition-transform hover:scale-110"
                    title={isWishlisted ? 'Remove from wishlist' : 'Save to wishlist'}
                  >
                    <Heart
                      className={`w-4 h-4 transition-colors ${
                        isWishlisted ? 'fill-red-500 text-red-500' : 'text-neutral-400 hover:text-red-500'
                      }`}
                    />
                  </button>

                  {/* Procedural Phone Vector Graphic */}
                  <div className="py-4 flex items-center justify-center overflow-hidden">
                    <PhoneRenderer
                      phone={phone}
                      size="md"
                      view="back"
                      interactive={true}
                    />
                  </div>
                </div>

                {/* Card Meta & Details */}
                <div className="mt-3 space-y-2">
                  {/* Title & Price Header */}
                  <div className="flex items-baseline justify-between gap-2">
                    <h3 className="font-extrabold text-sm text-neutral-900 tracking-tight line-clamp-1 group-hover:text-emerald-800 transition-colors">
                      {phone.name}
                    </h3>
                    <div className="text-sm font-extrabold text-neutral-900 font-sans whitespace-nowrap">
                      ₹{(phone.price || 19999).toLocaleString('en-IN')}
                    </div>
                  </div>

                  {/* Spec Subtitle */}
                  <p className="text-[11px] text-neutral-500 line-clamp-1">
                    {Math.round(phone.ram || 8)}GB RAM, {phone.battery_cap}mAh, {Math.round(phone.primary_rear_camera || 50)}MP Camera
                  </p>

                  {/* Star Reviews - Reference Style (5 Emerald Stars) */}
                  <div className="flex items-center gap-1.5 pt-0.5">
                    <div className="flex items-center text-emerald-600">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-3.5 h-3.5 fill-current" />
                      ))}
                    </div>
                    <span className="text-[11px] text-neutral-500 font-medium">
                      ({reviewCount})
                    </span>
                  </div>

                  {/* Action Pill Button: Add to Cart */}
                  <div className="pt-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        addToCart(phone);
                      }}
                      className="w-full py-2.5 rounded-full border border-neutral-900 text-neutral-900 hover:bg-[#0B4232] hover:border-[#0B4232] hover:text-white transition-all text-xs font-bold flex items-center justify-center gap-2 group/btn shadow-xs"
                    >
                      <span>Add to Cart</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
