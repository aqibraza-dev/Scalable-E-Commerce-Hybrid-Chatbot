import React, { useState } from 'react';
import { X, Trash2, Plus, Minus, ArrowRight, ShieldCheck, Tag, ShoppingBag, Check } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import PhoneRenderer from '../PhoneRenderer';
import confetti from 'canvas-confetti';

export default function CartDrawer() {
  const {
    cart,
    isCartOpen,
    closeCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    subtotal,
    totalItemCount,
    discountAmount,
    promoCode,
    applyPromo,
    shippingFee,
    finalTotal,
    freeShippingThreshold,
  } = useCart();

  const [couponInput, setCouponInput] = useState('');
  const [checkoutSuccess, setCheckoutSuccess] = useState(false);

  if (!isCartOpen) return null;

  const handleApplyPromo = (e) => {
    e.preventDefault();
    if (couponInput.trim()) {
      applyPromo(couponInput);
      setCouponInput('');
    }
  };

  const handleCheckout = () => {
    if (cart.length === 0) return;
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#0B4232', '#10B981', '#F59E0B'],
    });
    setCheckoutSuccess(true);
    setTimeout(() => {
      clearCart();
      setCheckoutSuccess(false);
      closeCart();
    }, 2800);
  };

  const progressToFreeShipping = Math.min(
    100,
    Math.round((subtotal / freeShippingThreshold) * 100)
  );

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-fadeIn">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
        onClick={closeCart}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white border-l border-neutral-200 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-neutral-200 flex items-center justify-between bg-neutral-50/80">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-50 text-[#0B4232] flex items-center justify-center border border-emerald-200">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-extrabold tracking-tight text-neutral-900 font-display">
                  Your Cart ({totalItemCount})
                </h2>
                <span className="text-[11px] text-neutral-500 font-medium">
                  Express Dispatch Ready
                </span>
              </div>
            </div>
            <button
              onClick={closeCart}
              className="p-2 rounded-full text-neutral-400 hover:text-neutral-900 hover:bg-neutral-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Free Shipping Meter */}
          <div className="px-6 py-3 bg-emerald-50/50 border-b border-emerald-100">
            <div className="flex items-center justify-between text-xs mb-1 font-medium">
              <span className="text-emerald-900">
                {subtotal >= freeShippingThreshold ? (
                  <span className="text-[#0B4232] font-bold flex items-center gap-1">
                    <Check className="w-3.5 h-3.5 text-emerald-600" /> Free Express Delivery Unlocked!
                  </span>
                ) : (
                  <span>
                    Add <strong className="text-emerald-950">₹{(freeShippingThreshold - subtotal).toLocaleString('en-IN')}</strong> for Free Shipping
                  </span>
                )}
              </span>
              <span className="text-emerald-800 font-mono text-[11px]">{progressToFreeShipping}%</span>
            </div>
            <div className="w-full bg-emerald-200/80 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-[#0B4232] h-full transition-all duration-500 rounded-full"
                style={{ width: `${progressToFreeShipping}%` }}
              />
            </div>
          </div>

          {/* Cart Item List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-[#FBFBFB]">
            {checkoutSuccess ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
                <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center animate-bounce">
                  <ShieldCheck className="w-10 h-10" />
                </div>
                <h3 className="text-2xl font-extrabold text-neutral-900 font-display">
                  Order Confirmed!
                </h3>
                <p className="text-xs text-neutral-600 max-w-xs">
                  Your smartphone order is being prepared for express delivery.
                </p>
                <div className="px-4 py-2 rounded-full bg-neutral-100 border border-neutral-200 font-mono text-xs text-[#0B4232] font-bold">
                  TRACKING ID: SC-{Math.random().toString(36).substring(2, 8).toUpperCase()}
                </div>
              </div>
            ) : cart.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
                <div className="w-16 h-16 rounded-full bg-neutral-100 border border-neutral-200 flex items-center justify-center text-neutral-400">
                  <ShoppingBag className="w-8 h-8" />
                </div>
                <h3 className="text-base font-bold text-neutral-900 font-display">
                  Your Cart is Empty
                </h3>
                <p className="text-xs text-neutral-500 max-w-xs">
                  Explore our smartphones catalog or ask our AI chatbot to find recommendations.
                </p>
                <button
                  onClick={closeCart}
                  className="px-6 py-2.5 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white font-semibold text-xs tracking-wider transition-all shadow-xs"
                >
                  Explore Catalog
                </button>
              </div>
            ) : (
              cart.map((item) => (
                <div
                  key={item.id}
                  className="p-3.5 rounded-2xl bg-white border border-neutral-200 flex gap-4 items-center shadow-xs"
                >
                  {/* Phone Procedural Thumbnail */}
                  <div className="w-14 h-20 bg-neutral-50 rounded-xl flex items-center justify-center overflow-hidden flex-shrink-0 border border-neutral-200 p-1">
                    <PhoneRenderer
                      phone={item}
                      size="xs"
                      view="back"
                      interactive={false}
                    />
                  </div>

                  {/* Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-1">
                      <h4 className="text-xs font-bold text-neutral-900 truncate">
                        {item.name}
                      </h4>
                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="text-neutral-400 hover:text-red-500 p-1 transition-colors"
                        title="Remove"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="text-[11px] text-neutral-500 font-mono mt-0.5">
                      {item.ram ? `${Math.round(item.ram)}GB` : '8GB'} • {item.has_5g ? '5G' : '4G'} • {item.brand}
                    </div>

                    <div className="flex items-center justify-between mt-2.5">
                      <span className="text-xs font-extrabold text-neutral-900 font-sans">
                        ₹{(item.price * item.quantity).toLocaleString('en-IN')}
                      </span>

                      {/* Quantity Stepper */}
                      <div className="flex items-center border border-neutral-300 rounded-full bg-neutral-50 px-1 py-0.5 text-xs">
                        <button
                          onClick={() => updateQuantity(item.id, -1)}
                          className="p-1 text-neutral-500 hover:text-neutral-900"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="px-2 font-mono font-bold text-neutral-900 text-xs">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, 1)}
                          className="p-1 text-neutral-500 hover:text-neutral-900"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer & Checkout Area */}
          {cart.length > 0 && !checkoutSuccess && (
            <div className="p-6 border-t border-neutral-200 bg-white space-y-4">
              {/* Promo Code Input */}
              <form onSubmit={handleApplyPromo} className="flex gap-2">
                <div className="relative flex-1">
                  <Tag className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    type="text"
                    value={couponInput}
                    onChange={(e) => setCouponInput(e.target.value)}
                    placeholder="PROMO CODE (e.g. SHOPCART50)"
                    className="w-full pl-9 pr-3 py-2 bg-neutral-100 border border-neutral-200 rounded-full text-xs font-mono uppercase text-neutral-900 placeholder-neutral-400 focus:outline-none focus:border-emerald-600"
                  />
                </div>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#0B4232] hover:bg-[#064E3B] text-white rounded-full text-xs font-bold uppercase transition-colors shadow-xs"
                >
                  Apply
                </button>
              </form>

              {promoCode && (
                <div className="flex items-center justify-between text-xs px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-[#0B4232]">
                  <span>Code Applied: <strong>{promoCode}</strong></span>
                  <span>-₹{discountAmount.toLocaleString('en-IN')}</span>
                </div>
              )}

              {/* Price Breakdown */}
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-neutral-600">
                  <span>Subtotal</span>
                  <span className="font-mono">₹{subtotal.toLocaleString('en-IN')}</span>
                </div>
                {discountAmount > 0 && (
                  <div className="flex justify-between text-emerald-700 font-semibold">
                    <span>Discount</span>
                    <span className="font-mono">-₹{discountAmount.toLocaleString('en-IN')}</span>
                  </div>
                )}
                <div className="flex justify-between text-neutral-600">
                  <span>Express Shipping</span>
                  <span>{shippingFee === 0 ? <strong className="text-emerald-700">FREE</strong> : `₹${shippingFee}`}</span>
                </div>
                <div className="flex justify-between text-sm font-bold text-neutral-900 pt-2 border-t border-neutral-200">
                  <span>Total</span>
                  <span className="text-base font-extrabold text-[#0B4232]">₹{finalTotal.toLocaleString('en-IN')}</span>
                </div>
              </div>

              {/* Checkout Button */}
              <button
                onClick={handleCheckout}
                className="w-full py-3.5 rounded-full bg-[#0B4232] hover:bg-[#064E3B] text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-md transition-all font-display"
              >
                Proceed to Checkout
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="flex items-center justify-center gap-2 text-[10px] text-neutral-500 font-medium">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
                <span>256-Bit Encrypted • 7-Day Hassle-Free Returns</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
