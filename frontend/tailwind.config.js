/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        shopcart: {
          primary: '#0B4232',      // Deep forest emerald (Shopcart reference)
          primaryHover: '#064E3B',
          accent: '#10B981',       // Vibrant emerald green
          accentHover: '#059669',
          lightGreen: '#ECFDF5',
          cream: '#FAF7F2',        // Warm hero banner cream
          creamDark: '#F4ECE1',
          bg: '#FFFFFF',
          surface: '#F9FAFB',
          card: '#FFFFFF',
          cardMuted: '#F7F7F7',
          border: '#E5E7EB',
          textDark: '#111827',
          textMuted: '#6B7280',
        },
        // Compatibility aliases mapped to light theme emerald
        nike: {
          black: '#111827',
          surface: '#F9FAFB',
          card: '#FFFFFF',
          cardHover: '#F3F4F6',
          border: '#E5E7EB',
          volt: '#10B981',
          voltHover: '#059669',
          orange: '#F97316',
          blue: '#0EA5E9',
          muted: '#6B7280',
          light: '#FFFFFF',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 2px 10px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02)',
        'card-hover': '0 14px 30px rgba(0, 0, 0, 0.08), 0 4px 10px rgba(0, 0, 0, 0.03)',
        'pill': '0 1px 2px rgba(0, 0, 0, 0.05)',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2.5s infinite',
        'float': 'float 4s ease-in-out infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.03)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        }
      }
    },
  },
  plugins: [],
}
