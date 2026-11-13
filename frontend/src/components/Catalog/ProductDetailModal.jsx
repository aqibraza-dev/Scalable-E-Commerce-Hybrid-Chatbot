import React from 'react';
import {
  X,
  ShoppingBag,
  Zap,
  ShieldCheck,
  Truck,
  RotateCcw,
  Cpu,
  Battery,
  Camera,
  Layers,
  MessageSquare,
  Sparkles,
  Star
} from 'lucide-react';
import PhoneRenderer from '../PhoneRenderer';
import { useCart } from '../../context/CartContext';

export default function ProductDetailModal({ phone, onClose, onAskAI }) {
  const { addToCart, openCart } = useCart();

  if (!phone) return null;

  const price = phone.price || 19999;
  const emiPerMonth = Math.round(price / 12);

  const handleBuyNow = () => {
    addToCart(phone, 1);
    openCart();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm p-3 sm:p-6 flex items-center justify-center animate-fadeIn">
      <div className="relative w-full max-w-4xl bg-white border border-neutral-200 rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-full text-neutral-400 hover:text-neutral-900 hover:bg-neutral-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Left: Procedural Phone Showcase Canvas */}
        <div className="w-full md:w-5/12 bg-neutral-50 p-6 flex flex-col items-center justify-center border-b md:border-b-0 md:border-r border-neutral-200 relative">
          <div className="absolute top-4 left-4 inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-[#0B4232] text-[10px] font-semibold uppercase">
            <Sparkles className="w-3 h-3 text-emerald-600" />
            <span>Interactive Vector Mockup</span>
          </div>

          <PhoneRenderer
            phone={phone}
            size="lg"
            view="back"
            interactive={true}
            className="my-4"
          />

          <span className="text-[11px] text-neutral-500 font-sans mt-1">
            Click toggle buttons above to inspect chassis and screen
          </span>
        </div>

        {/* Right: Specifications & Commerce Actions */}
        <div className="w-full md:w-7/12 p-6 sm:p-8 flex flex-col justify-between space-y-6">
          <div>
            {/* Brand Tag & 5G Pill */}
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full bg-neutral-100 text-neutral-700 font-semibold text-[11px] uppercase tracking-wider">
                {phone.brand}
              </span>
              {phone.has_5g === 'Yes' && (
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 font-semibold text-[11px] uppercase tracking-wider border border-emerald-200">
                  5G Ready
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-neutral-900 font-display tracking-tight">
              {phone.name}
            </h1>

            {/* Reviews */}
            <div className="flex items-center gap-2 mt-2">
              <div className="flex items-center text-emerald-600">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-current" />
                ))}
              </div>
              <span className="text-xs font-semibold text-neutral-600">4.9 • 128 Reviews</span>
            </div>

            {/* Price & EMI */}
            <div className="mt-4 flex items-baseline gap-3">
              <span className="text-3xl font-extrabold text-neutral-900 font-sans">
                ₹{price.toLocaleString('en-IN')}
              </span>
              <span className="text-xs text-neutral-500">
                Inclusive of all taxes
              </span>
            </div>

            <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-medium border border-emerald-200">
              <Zap className="w-3.5 h-3.5 text-emerald-600" />
              <span>Or <strong>₹{emiPerMonth.toLocaleString('en-IN')}/month</strong> with No-Cost EMI</span>
            </div>

            {/* Hardware Specification Grid */}
            <div className="mt-6 grid grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200/80 flex items-center gap-3">
                <Cpu className="w-4 h-4 text-emerald-700 flex-shrink-0" />
                <div>
                  <div className="text-[10px] text-neutral-500 font-mono">PROCESSOR</div>
                  <div className="font-bold text-neutral-900 truncate">{phone.processor_brand || 'Octa-Core Flagship'}</div>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200/80 flex items-center gap-3">
                <Layers className="w-4 h-4 text-cyan-700 flex-shrink-0" />
                <div>
                  <div className="text-[10px] text-neutral-500 font-mono">RAM & STORAGE</div>
                  <div className="font-bold text-neutral-900">{Math.round(phone.ram || 8)}GB • {Math.round(phone.storage || 128)}GB</div>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200/80 flex items-center gap-3">
                <Battery className="w-4 h-4 text-emerald-700 flex-shrink-0" />
                <div>
                  <div className="text-[10px] text-neutral-500 font-mono">BATTERY</div>
                  <div className="font-bold text-neutral-900">{phone.battery_cap || 5000} mAh ({phone.has_fast_charging || 'Fast Charging'})</div>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200/80 flex items-center gap-3">
                <Camera className="w-4 h-4 text-indigo-700 flex-shrink-0" />
                <div>
                  <div className="text-[10px] text-neutral-500 font-mono">CAMERA SYSTEM</div>
                  <div className="font-bold text-neutral-900">{Math.round(phone.primary_rear_camera || 50)}MP Main Sensor</div>
                </div>
              </div>
            </div>

            {/* Policy Highlights */}
            <div className="mt-5 grid grid-cols-3 gap-2 text-[11px] text-neutral-600 font-medium pt-4 border-t border-neutral-100">
              <div className="flex items-center gap-1.5">
                <Truck className="w-3.5 h-3.5 text-emerald-700" />
                <span>Express 24-48h</span>
              </div>
              <div className="flex items-center gap-1.5">
                <RotateCcw className="w-3.5 h-3.5 text-emerald-700" />
                <span>7-Day Return</span>
              </div>
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
                <span>1-Yr Warranty</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-2.5 pt-4 border-t border-neutral-200">
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => addToCart(phone, 1)}
                className="py-3 px-4 rounded-full border border-neutral-900 text-neutral-900 hover:bg-neutral-100 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-xs"
              >
                <ShoppingBag className="w-4 h-4" />
                <span>Add to Cart</span>
              </button>

              <button
                onClick={handleBuyNow}
                className="py-3 px-4 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-md"
              >
                <span>Buy Now</span>
              </button>
            </div>

            {onAskAI && (
              <button
                onClick={() => {
                  onAskAI(`Tell me all key highlights and specs of ${phone.name}`);
                  onClose();
                }}
                className="w-full py-2.5 rounded-full bg-neutral-100 hover:bg-neutral-200/80 text-neutral-800 text-xs font-medium flex items-center justify-center gap-2 transition-colors"
              >
                <MessageSquare className="w-3.5 h-3.5 text-emerald-700" />
                <span>Ask AI Advisor about {phone.name}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
