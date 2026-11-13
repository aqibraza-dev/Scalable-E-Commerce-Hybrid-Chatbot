import React, { createContext, useContext, useState, useEffect } from 'react';

const CartContext = createContext(null);

const FREE_SHIPPING_THRESHOLD = 999;
const TAX_RATE = 0.18; // 18% GST standard for smartphones

export function CartProvider({ children }) {
  const [cart, setCart] = useState(() => {
    try {
      const saved = localStorage.getItem('aura_cart');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [isCartOpen, setIsCartOpen] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [discountPercent, setDiscountPercent] = useState(0);
  const [flatDiscount, setFlatDiscount] = useState(0);
  const [toastMessage, setToastMessage] = useState(null);

  // Persist cart
  useEffect(() => {
    localStorage.setItem('aura_cart', JSON.stringify(cart));
  }, [cart]);

  const showToast = (message) => {
    setToastMessage(message);
    setTimeout(() => {
      setToastMessage(null);
    }, 3500);
  };

  const addToCart = (product, quantity = 1) => {
    if (!product || !product.id) return;

    setCart((prev) => {
      const existingIndex = prev.findIndex((item) => item.id === product.id);
      if (existingIndex > -1) {
        const updated = [...prev];
        updated[existingIndex].quantity += quantity;
        return updated;
      } else {
        return [
          ...prev,
          {
            id: product.id,
            name: product.name,
            brand: product.brand,
            price: product.price || 19999,
            ram: product.ram,
            storage: product.storage,
            battery_cap: product.battery_cap,
            primary_rear_camera: product.primary_rear_camera,
            has_5g: product.has_5g,
            quantity: quantity,
          },
        ];
      }
    });

    showToast(`⚡ Added ${product.name} to Cart`);
  };

  const removeFromCart = (productId) => {
    setCart((prev) => prev.filter((item) => item.id !== productId));
    showToast('Removed item from cart');
  };

  const updateQuantity = (productId, delta) => {
    setCart((prev) =>
      prev
        .map((item) => {
          if (item.id === productId) {
            const newQty = item.quantity + delta;
            return newQty > 0 ? { ...item, quantity: newQty } : null;
          }
          return item;
        })
        .filter(Boolean)
    );
  };

  const clearCart = () => {
    setCart([]);
    setDiscountPercent(0);
    setFlatDiscount(0);
    setPromoCode('');
    showToast('Cart cleared');
  };

  const applyPromo = (code) => {
    const cleaned = (code || '').trim().toUpperCase();
    if (cleaned === 'NIKEAIR' || cleaned === 'AURA15') {
      setDiscountPercent(15);
      setFlatDiscount(0);
      setPromoCode(cleaned);
      showToast('🔥 Promo Applied: 15% NIKE Member Discount!');
      return { success: true, message: '15% discount applied' };
    } else if (cleaned === 'SPEED500' || cleaned === 'AURA500') {
      setFlatDiscount(500);
      setDiscountPercent(0);
      setPromoCode(cleaned);
      showToast('⚡ Promo Applied: ₹500 Instant Discount!');
      return { success: true, message: '₹500 flat discount applied' };
    } else {
      showToast('❌ Invalid Promo Code');
      return { success: false, message: 'Invalid promo code' };
    }
  };

  // Calculations
  const subtotal = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
  const totalItemCount = cart.reduce((acc, item) => acc + item.quantity, 0);
  
  const discountAmount = Math.round(
    (subtotal * (discountPercent / 100)) + flatDiscount
  );
  
  const discountedSubtotal = Math.max(0, subtotal - discountAmount);
  const shippingFee = subtotal === 0 || discountedSubtotal >= FREE_SHIPPING_THRESHOLD ? 0 : 99;
  const estimatedTax = Math.round(discountedSubtotal * 0.05); // Simplified display tax
  const finalTotal = discountedSubtotal + shippingFee;

  return (
    <CartContext.Provider
      value={{
        cart,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        isCartOpen,
        setIsCartOpen,
        openCart: () => setIsCartOpen(true),
        closeCart: () => setIsCartOpen(false),
        subtotal,
        totalItemCount,
        discountAmount,
        discountPercent,
        promoCode,
        applyPromo,
        shippingFee,
        estimatedTax,
        finalTotal,
        freeShippingThreshold: FREE_SHIPPING_THRESHOLD,
        toastMessage,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
