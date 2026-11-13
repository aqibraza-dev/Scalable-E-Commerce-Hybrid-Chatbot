import React from 'react';
import { ArrowRight, Sparkles, Zap, Shield, Heart } from 'lucide-react';
import PhoneRenderer from '../PhoneRenderer';

export default function Hero({ onOpenChat, onNavigate }) {
  const showcasePhone1 = {
    id: 101,
    name: 'Samsung Galaxy S25 Ultra 5G',
    brand: 'samsung',
    price: 129999,
    ram: 16,
    storage: 512,
    battery_cap: 5000,
    has_5g: 'Yes',
    primary_rear_camera: 200,
    display_size: 6.8,
    display_type: 'Dynamic AMOLED 2X',
    refresh_rate: 120,
  };

  const showcasePhone2 = {
    id: 102,
    name: 'Apple iPhone 16 Pro Max',
    brand: 'apple',
    price: 144900,
    ram: 8,
    storage: 256,
    battery_cap: 4685,
    has_5g: 'Yes',
    primary_rear_camera: 48,
    display_size: 6.9,
    display_type: 'Super Retina XDR OLED',
    refresh_rate: 120,
  };

  return (
    <section className="py-6 sm:py-8 bg-[#FBFBFB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Banner matching reference design: warm cream background, bold dark green text, Buy Now button */}
        <div className="relative rounded-3xl bg-[#FAF5EE] border border-[#F2E8DC] p-6 sm:p-10 lg:p-14 overflow-hidden shadow-xs">
          {/* Subtle floral/leaf watermark glow */}
          <div className="absolute -right-20 -bottom-20 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
            {/* Left Content */}
            <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100/80 text-[#0B4232] text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
                <span>Special Spring Electronics Promotion</span>
              </div>

              <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-[#0B4232] font-display tracking-tight leading-[1.08]">
                Grab Upto 50% Off On Selected Smartphones
              </h1>

              <p className="text-sm sm:text-base text-neutral-600 max-w-lg leading-relaxed font-sans">
                Experience next-generation mobile intelligence with Shopcart. Instant multi-tier search, verified manufacturer warranty, and intelligent AI comparisons.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 pt-2">
                <button
                  onClick={() => onNavigate && onNavigate('shop')}
                  className="px-8 py-3.5 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md hover:shadow-lg flex items-center gap-2"
                >
                  <span>Buy Now</span>
                  <ArrowRight className="w-4 h-4" />
                </button>

                <button
                  onClick={onOpenChat}
                  className="px-6 py-3.5 rounded-full bg-white hover:bg-neutral-50 border border-neutral-300 text-neutral-800 font-semibold text-xs tracking-wider transition-all shadow-xs flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4 text-emerald-600" />
                  <span>Ask AI Assistant</span>
                </button>
              </div>

              {/* Value Props */}
              <div className="pt-4 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-xs text-neutral-600 font-medium">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-600" />
                  <span>Free Express Delivery pan-India</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-600" />
                  <span>7-Day Replacement Guarantee</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-600" />
                  <span>1-Year Official Warranty</span>
                </div>
              </div>
            </div>

            {/* Right: Dynamic Realistic Smartphone Showcase */}
            <div className="lg:col-span-5 flex items-center justify-center gap-4 sm:gap-6 relative">
              <div className="relative">
                <div className="transform -rotate-6 hover:rotate-0 transition-transform duration-500">
                  <PhoneRenderer
                    phone={showcasePhone1}
                    size="md"
                    view="back"
                    interactive={true}
                  />
                </div>
              </div>

              <div className="relative mt-8">
                <div className="transform rotate-6 hover:rotate-0 transition-transform duration-500">
                  <PhoneRenderer
                    phone={showcasePhone2}
                    size="md"
                    view="front"
                    interactive={true}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
