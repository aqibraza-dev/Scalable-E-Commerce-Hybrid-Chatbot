import React, { useMemo, useState } from 'react';

/**
 * Procedural Dynamic Phone Image Generator in Pure JavaScript / SVG.
 * Generates distinct, high-fidelity vector hardware mockups for every smartphone model,
 * calculating brand-specific camera chassis, metallic rim finishes, authentic color palettes,
 * periscope telephoto optics, and dual-view screen graphics.
 */

// Palette definitions per brand with realistic flagship and mid-range colorways
const BRAND_COLOR_PALETTES = {
  apple: [
    { name: 'Natural Titanium', back: ['#9A9791', '#7E7B74'], frame: '#B0ADA7', lens: '#D1CEC8', text: '#E5E4E0' },
    { name: 'Desert Gold', back: ['#D6BA96', '#BFA380'], frame: '#DEC7AA', lens: '#F0DBC3', text: '#FFF4E8' },
    { name: 'Deep Purple', back: ['#3E344A', '#261F2E'], frame: '#5A4E68', lens: '#786888', text: '#E9D5FF' },
    { name: 'Alpine Emerald', back: ['#2F483D', '#1B2C24'], frame: '#436153', lens: '#5D8572', text: '#D1FAE5' },
    { name: 'White Titanium', back: ['#F3F2EE', '#DFDED9'], frame: '#E5E4DF', lens: '#FAF9F5', text: '#374151' },
    { name: 'Black Titanium', back: ['#2E2E31', '#1A1A1C'], frame: '#424247', lens: '#58585E', text: '#F3F4F6' },
  ],
  samsung: [
    { name: 'Titanium Gray', back: ['#8C8B86', '#6D6C67'], frame: '#A5A49E', lens: '#C4C3BD', text: '#F4F4F5' },
    { name: 'Amber Yellow', back: ['#E6C488', '#C6A265'], frame: '#EED3A1', lens: '#FCE7C2', text: '#451A03' },
    { name: 'Cobalt Violet', back: ['#353654', '#212236'], frame: '#4C4E73', lens: '#6A6D9C', text: '#E0E7FF' },
    { name: 'Emerald Jade', back: ['#214A3A', '#132E24'], frame: '#346B55', lens: '#4D9477', text: '#D1FAE5' },
    { name: 'Marble Cream', back: ['#F5F5F0', '#DFDFD8'], frame: '#E8E8E1', lens: '#FAFBF7', text: '#292524' },
    { name: 'Onyx Black', back: ['#232427', '#121315'], frame: '#383A40', lens: '#51535A', text: '#FAFAFA' },
  ],
  google: [
    { name: 'Bay Blue', back: ['#6EA5D8', '#4C82B4'], frame: '#8ABBE8', lens: '#B8D8F8', text: '#082F49' },
    { name: 'Porcelain White', back: ['#F9F7F2', '#E7E2D7'], frame: '#ECE7DC', lens: '#FAF8F4', text: '#44403C' },
    { name: 'Hazel Sage', back: ['#838D7E', '#60695B'], frame: '#9CA697', lens: '#BFC8BA', text: '#F4F7F4' },
    { name: 'Rose Coral', back: ['#E8B4A8', '#C99285'], frame: '#F2C6BC', lens: '#FCE0D9', text: '#4C0519' },
    { name: 'Obsidian Black', back: ['#2C2D30', '#1B1C1D'], frame: '#434448', lens: '#5E6066', text: '#F8FAFC' },
  ],
  oneplus: [
    { name: 'Flowy Emerald', back: ['#114D3C', '#072E23'], frame: '#1E6E56', lens: '#34D399', text: '#ECFDF5' },
    { name: 'Glacial White', back: ['#E9EDF1', '#CCD4DB'], frame: '#DCE2E7', lens: '#F8FAFC', text: '#1E293B' },
    { name: 'Silky Black', back: ['#1F2023', '#111213'], frame: '#35373B', lens: '#4E5057', text: '#F1F5F9' },
    { name: 'Deep Teal', back: ['#0E4A4E', '#062C2E'], frame: '#166E74', lens: '#2DD4BF', text: '#CCFBF1' },
  ],
  xiaomi: [
    { name: 'Titan Silver', back: ['#AAB2BA', '#889098'], frame: '#C0C7CE', lens: '#E2E8F0', text: '#0F172A' },
    { name: 'Alpine Green', back: ['#1E4535', '#10291F'], frame: '#2E614B', lens: '#10B981', text: '#ECFDF5' },
    { name: 'Ice Blue', back: ['#8BAED4', '#6085AC'], frame: '#A5C4E6', lens: '#BFDBFE', text: '#172554' },
    { name: 'Cosmic Black', back: ['#1C1D21', '#0E0F11'], frame: '#32343A', lens: '#4E5058', text: '#F8FAFC' },
  ],
  vivo: [
    { name: 'Sunset Dazzle', back: ['#F9A8D4', '#818CF8'], frame: '#F472B6', lens: '#C084FC', text: '#4A044E' },
    { name: 'Peacock Blue', back: ['#0284C7', '#075985'], frame: '#38BDF8', lens: '#7DD3FC', text: '#F0F9FF' },
    { name: 'Feather Green', back: ['#6EE7B7', '#059669'], frame: '#A7F3D0', lens: '#D1FAE5', text: '#064E3B' },
    { name: 'Magic Night', back: ['#1E1B2E', '#0F0C1B'], frame: '#383253', lens: '#564E7A', text: '#FAF5FF' },
  ],
  realme: [
    { name: 'Sunrise Orange', back: ['#FB923C', '#EA580C'], frame: '#FDBA74', lens: '#FED7AA', text: '#431407' },
    { name: 'Oasis Green', back: ['#16A34A', '#14532D'], frame: '#4ADE80', lens: '#86EFAC', text: '#F0FDF4' },
    { name: 'Mirror Silver', back: ['#CBD5E1', '#94A3B8'], frame: '#E2E8F0', lens: '#F1F5F9', text: '#0F172A' },
  ],
  nothing: [
    { name: 'Crystal White', back: ['#FAFAFA', '#E4E4E7'], frame: '#FFFFFF', lens: '#D4D4D8', text: '#18181B' },
    { name: 'Dark Smoke', back: ['#242528', '#131416'], frame: '#3A3C41', lens: '#52545B', text: '#FAFAFA' },
  ],
  motorola: [
    { name: 'Pantone Peach', back: ['#FDBA74', '#FB923C'], frame: '#FED7AA', lens: '#FFEDD5', text: '#7C2D12' },
    { name: 'Midnight Blue', back: ['#1E293B', '#0F172A'], frame: '#334155', lens: '#64748B', text: '#F8FAFC' },
    { name: 'Viva Magenta', back: ['#BE185D', '#831843'], frame: '#F472B6', lens: '#FBCFE8', text: '#FFF1F2' },
  ],
  default: [
    { name: 'Graphite Slate', back: ['#334155', '#1E293B'], frame: '#475569', lens: '#94A3B8', text: '#F8FAFC' },
    { name: 'Forest Emerald', back: ['#065F46', '#022C22'], frame: '#059669', lens: '#34D399', text: '#ECFDF5' },
    { name: 'Platinum Silver', back: ['#CBD5E1', '#94A3B8'], frame: '#E2E8F0', lens: '#F8FAFC', text: '#0F172A' },
  ]
};

// Camera layout style per brand
const BRAND_CAMERA_STYLES = {
  apple: 'apple_pro',
  samsung: 'samsung_vertical',
  google: 'pixel_visor',
  oneplus: 'oneplus_dial',
  xiaomi: 'xiaomi_matrix',
  vivo: 'vivo_halo',
  oppo: 'oppo_matrix',
  realme: 'realme_dial',
  nothing: 'nothing_glyph',
  motorola: 'moto_matrix',
  poco: 'xiaomi_matrix',
  iqoo: 'vivo_halo',
  honor: 'oneplus_dial',
  default: 'samsung_vertical'
};

export default function PhoneRenderer({
  phone = {},
  view = 'back', // 'back' | 'front'
  size = 'md',   // 'sm' | 'md' | 'lg'
  interactive = true,
  className = ''
}) {
  const [currentView, setCurrentView] = useState(view);
  const [isHovered, setIsHovered] = useState(false);

  const brandKey = (phone.brand || '').toLowerCase().trim();
  const phoneName = (phone.name || '').toLowerCase();
  const phoneId = phone.id || 0;

  // Derive unique model colorway from string hash
  const colorway = useMemo(() => {
    const palette = BRAND_COLOR_PALETTES[brandKey] || BRAND_COLOR_PALETTES.default;
    let hash = phoneId;
    for (let i = 0; i < phoneName.length; i++) {
      hash = (hash << 5) - hash + phoneName.charCodeAt(i);
      hash |= 0;
    }
    const index = Math.abs(hash) % palette.length;
    return palette[index];
  }, [brandKey, phoneName, phoneId]);

  const cameraStyle = BRAND_CAMERA_STYLES[brandKey] || BRAND_CAMERA_STYLES.default;

  // Responsive sizing dimensions
  const dimensions = useMemo(() => {
    switch (size) {
      case 'sm':
        return { width: 90, height: 160, rx: 18, stroke: 1.5, scale: 0.5 };
      case 'lg':
        return { width: 220, height: 390, rx: 34, stroke: 3, scale: 1.2 };
      case 'md':
      default:
        return { width: 145, height: 260, rx: 24, stroke: 2, scale: 0.85 };
    }
  }, [size]);

  const { width, height, rx } = dimensions;
  const price = phone.price || 24999;
  const isFlagship = price > 45000;
  const cameraMP = Math.round(phone.primary_rear_camera || 50);
  const hasPeriscope = cameraMP >= 50 && (isFlagship || price >= 30000);

  // Gradient ID prefix
  const idPrefix = useMemo(() => `phone-${phoneId || Math.random().toString(36).substring(2, 7)}`, [phoneId]);

  return (
    <div
      className={`relative inline-flex flex-col items-center justify-center select-none ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div 
        className="relative transition-transform duration-500 ease-out"
        style={{
          transform: isHovered && interactive ? 'translateY(-6px) scale(1.02)' : 'none',
        }}
      >
        {/* Soft Ambient Light Glow & Realistic Shadow */}
        <div 
          className="absolute -inset-2 bg-gradient-to-b from-black/5 to-black/25 blur-xl -z-10 rounded-full opacity-60 transition-opacity duration-300"
          style={{ opacity: isHovered ? 0.9 : 0.45 }}
        />

        <svg
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="drop-shadow-lg overflow-visible"
        >
          <defs>
            {/* Chassis Body Gradient */}
            <linearGradient id={`${idPrefix}-chassis`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={colorway.back[0]} />
              <stop offset="100%" stopColor={colorway.back[1]} />
            </linearGradient>

            {/* Precision Metallic Frame Rim */}
            <linearGradient id={`${idPrefix}-frame`} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="0.6" />
              <stop offset="35%" stopColor={colorway.frame} />
              <stop offset="70%" stopColor="#000000" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#ffffff" stopOpacity="0.5" />
            </linearGradient>

            {/* Specular Sheen Diagonal Reflection */}
            <linearGradient id={`${idPrefix}-sheen`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="0.28" />
              <stop offset="30%" stopColor="#ffffff" stopOpacity="0.08" />
              <stop offset="65%" stopColor="#ffffff" stopOpacity="0" />
            </linearGradient>

            {/* Optical Anti-Reflective Lens Coating */}
            <radialGradient id={`${idPrefix}-lens-glare`} cx="32%" cy="32%" r="68%">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.85" />
              <stop offset="40%" stopColor="#6366F1" stopOpacity="0.6" />
              <stop offset="75%" stopColor="#1E1B4B" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#020617" />
            </radialGradient>

            {/* Camera Bezel Ring Glow */}
            <linearGradient id={`${idPrefix}-lens-ring`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.8" />
              <stop offset="50%" stopColor={colorway.lens} />
              <stop offset="100%" stopColor="#000000" stopOpacity="0.6" />
            </linearGradient>
          </defs>

          {/* Phone Unibody Chassis */}
          <rect
            x="2"
            y="2"
            width={width - 4}
            height={height - 4}
            rx={rx}
            fill={`url(#${idPrefix}-chassis)`}
            stroke={`url(#${idPrefix}-frame)`}
            strokeWidth={dimensions.stroke}
          />

          {currentView === 'back' ? (
            /* ========================================================
               PHONE REAR CHASSIS & BRAND CAMERA ARCHITECTURE
               ======================================================== */
            <g>
              {/* Specular Glass Sheen Cut */}
              <path
                d={`M 8 2 Q ${width * 0.5} 2 ${width - 8} 2 L 6 ${height * 0.75} Z`}
                fill={`url(#${idPrefix}-sheen)`}
              />

              {/* Antenna Band Gaps */}
              <line x1="2" y1={height * 0.18} x2="5" y2={height * 0.18} stroke="#9CA3AF" strokeWidth="1.5" />
              <line x1={width - 5} y1={height * 0.18} x2={width - 2} y2={height * 0.18} stroke="#9CA3AF" strokeWidth="1.5" />
              <line x1="2" y1={height * 0.82} x2="5" y2={height * 0.82} stroke="#9CA3AF" strokeWidth="1.5" />
              <line x1={width - 5} y1={height * 0.82} x2={width - 2} y2={height * 0.82} stroke="#9CA3AF" strokeWidth="1.5" />

              {/* ---------------- 1. GOOGLE PIXEL HORIZONTAL VISOR ---------------- */}
              {cameraStyle === 'pixel_visor' && (
                <g>
                  {/* Visor Bar with metallic trim */}
                  <rect
                    x="2"
                    y={height * 0.14}
                    width={width - 4}
                    height={height * 0.155}
                    rx="6"
                    fill="#18181B"
                    stroke={colorway.frame}
                    strokeWidth="1.5"
                  />
                  {/* Pill cutout for lenses */}
                  <rect
                    x={width * 0.14}
                    y={height * 0.165}
                    width={width * 0.44}
                    height={height * 0.105}
                    rx="12"
                    fill="#09090B"
                  />
                  {/* Main sensor */}
                  <circle cx={width * 0.25} cy={height * 0.218} r={width * 0.075} fill={`url(#${idPrefix}-lens-glare)`} stroke={colorway.lens} strokeWidth="1" />
                  <circle cx={width * 0.23} cy={height * 0.205} r={width * 0.02} fill="#FFFFFF" opacity="0.8" />
                  {/* Ultra-wide */}
                  <circle cx={width * 0.44} cy={height * 0.218} r={width * 0.065} fill={`url(#${idPrefix}-lens-glare)`} stroke={colorway.lens} strokeWidth="1" />
                  {/* Periscope / Dual Flash */}
                  <circle cx={width * 0.76} cy={height * 0.218} r={width * 0.038} fill="#FEF08A" stroke="#EAB308" strokeWidth="0.5" />
                </g>
              )}

              {/* ---------------- 2. APPLE PRO TRIPLE TRIANGLE ---------------- */}
              {cameraStyle === 'apple_pro' && (
                <g>
                  {/* Frosted Glass Contoured Square */}
                  <rect
                    x={width * 0.08}
                    y={height * 0.065}
                    width={width * 0.44}
                    height={width * 0.44}
                    rx="16"
                    fill="#18181B"
                    fillOpacity="0.45"
                    stroke={`url(#${idPrefix}-lens-ring)`}
                    strokeWidth="1.2"
                  />
                  {/* Lens 1 (Top Left) */}
                  <circle cx={width * 0.20} cy={height * 0.065 + width * 0.13} r={width * 0.085} fill="#09090B" stroke={`url(#${idPrefix}-lens-ring)`} strokeWidth="2" />
                  <circle cx={width * 0.20} cy={height * 0.065 + width * 0.13} r={width * 0.065} fill={`url(#${idPrefix}-lens-glare)`} />
                  <circle cx={width * 0.18} cy={height * 0.065 + width * 0.11} r={width * 0.02} fill="#FFFFFF" opacity="0.8" />

                  {/* Lens 2 (Bottom Left) */}
                  <circle cx={width * 0.20} cy={height * 0.065 + width * 0.31} r={width * 0.085} fill="#09090B" stroke={`url(#${idPrefix}-lens-ring)`} strokeWidth="2" />
                  <circle cx={width * 0.20} cy={height * 0.065 + width * 0.31} r={width * 0.065} fill={`url(#${idPrefix}-lens-glare)`} />

                  {/* Lens 3 (Right Center) */}
                  <circle cx={width * 0.39} cy={height * 0.065 + width * 0.22} r={width * 0.085} fill="#09090B" stroke={`url(#${idPrefix}-lens-ring)`} strokeWidth="2" />
                  <circle cx={width * 0.39} cy={height * 0.065 + width * 0.22} r={width * 0.065} fill={`url(#${idPrefix}-lens-glare)`} />

                  {/* True-Tone Flash & LiDAR */}
                  <circle cx={width * 0.39} cy={height * 0.065 + width * 0.10} r={width * 0.035} fill="#FEF08A" />
                  <circle cx={width * 0.39} cy={height * 0.065 + width * 0.34} r={width * 0.024} fill="#000000" />
                </g>
              )}

              {/* ---------------- 3. ONEPLUS / REALME CIRCULAR DIAL ---------------- */}
              {(cameraStyle === 'oneplus_dial' || cameraStyle === 'realme_dial') && (
                <g>
                  {/* Knurled Outer Bezel */}
                  <circle
                    cx={width * 0.42}
                    cy={height * 0.22}
                    r={width * 0.27}
                    fill="#18181B"
                    stroke={`url(#${idPrefix}-lens-ring)`}
                    strokeWidth="2.5"
                  />
                  {/* Quad Symmetrical Optics */}
                  <circle cx={width * 0.31} cy={height * 0.18} r={width * 0.07} fill={`url(#${idPrefix}-lens-glare)`} stroke="#3F3F46" />
                  <circle cx={width * 0.53} cy={height * 0.18} r={width * 0.07} fill={`url(#${idPrefix}-lens-glare)`} stroke="#3F3F46" />
                  <circle cx={width * 0.31} cy={height * 0.26} r={width * 0.07} fill={`url(#${idPrefix}-lens-glare)`} stroke="#3F3F46" />
                  <circle cx={width * 0.53} cy={height * 0.26} r={width * 0.045} fill="#FEF08A" />

                  {/* Center Brand Accent Logo */}
                  <text x={width * 0.42} y={height * 0.225} textAnchor="middle" fill="#9CA3AF" fontSize="7" fontWeight="bold" letterSpacing="0.5px">
                    {brandKey === 'oneplus' ? 'H' : '50M'}
                  </text>
                </g>
              )}

              {/* ---------------- 4. VIVO ZEISS HALO RING ---------------- */}
              {cameraStyle === 'vivo_halo' && (
                <g>
                  <circle
                    cx={width * 0.5}
                    cy={height * 0.22}
                    r={width * 0.28}
                    fill="#09090B"
                    stroke={`url(#${idPrefix}-lens-ring)`}
                    strokeWidth="2"
                  />
                  <circle cx={width * 0.4} cy={height * 0.18} r={width * 0.075} fill={`url(#${idPrefix}-lens-glare)`} />
                  <circle cx={width * 0.6} cy={height * 0.18} r={width * 0.075} fill={`url(#${idPrefix}-lens-glare)`} />
                  <circle cx={width * 0.5} cy={height * 0.265} r={width * 0.075} fill={`url(#${idPrefix}-lens-glare)`} />
                  {/* ZEISS Blue Badge */}
                  <rect x={width * 0.44} y={height * 0.12} width={width * 0.12} height="6" rx="2" fill="#2563EB" />
                  <text x={width * 0.5} y={height * 0.12 + 5} textAnchor="middle" fill="#FFFFFF" fontSize="5" fontWeight="bold">ZEISS</text>
                </g>
              )}

              {/* ---------------- 5. NOTHING GLYPH INTERFACE ---------------- */}
              {cameraStyle === 'nothing_glyph' && (
                <g>
                  {/* Illuminated Glyph Lines */}
                  <path
                    d={`M ${width * 0.2} ${height * 0.12} A ${width * 0.25} ${width * 0.25} 0 0 1 ${width * 0.8} ${height * 0.12}`}
                    stroke="#FFFFFF"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    fill="none"
                    opacity="0.85"
                  />
                  <line x1={width * 0.5} y1={height * 0.45} x2={width * 0.5} y2={height * 0.72} stroke="#FFFFFF" strokeWidth="2" opacity="0.8" />
                  <circle cx={width * 0.5} cy={height * 0.58} r={width * 0.18} stroke="#FFFFFF" strokeWidth="2" fill="none" opacity="0.75" />
                  {/* Dual Floating Lenses */}
                  <circle cx={width * 0.25} cy={height * 0.18} r={width * 0.08} fill="#09090B" stroke="#E4E4E7" strokeWidth="1.5" />
                  <circle cx={width * 0.25} cy={height * 0.18} r={width * 0.06} fill={`url(#${idPrefix}-lens-glare)`} />
                  <circle cx={width * 0.25} cy={height * 0.29} r={width * 0.08} fill="#09090B" stroke="#E4E4E7" strokeWidth="1.5" />
                  <circle cx={width * 0.25} cy={height * 0.29} r={width * 0.06} fill={`url(#${idPrefix}-lens-glare)`} />
                </g>
              )}

              {/* ---------------- 6. SAMSUNG / UNIVERSAL FLOATING RINGS ---------------- */}
              {(cameraStyle === 'samsung_vertical' || cameraStyle === 'xiaomi_matrix' || cameraStyle === 'oppo_matrix' || cameraStyle === 'moto_matrix') && (
                <g>
                  {/* Lens 1: Primary Sensor */}
                  <circle cx={width * 0.22} cy={height * 0.12} r={width * 0.09} fill="#0C0A09" stroke={`url(#${idPrefix}-lens-ring)`} strokeWidth="2.2" />
                  <circle cx={width * 0.22} cy={height * 0.12} r={width * 0.068} fill={`url(#${idPrefix}-lens-glare)`} />
                  <circle cx={width * 0.20} cy={height * 0.108} r={width * 0.02} fill="#FFFFFF" opacity="0.8" />

                  {/* Lens 2: Ultra-wide Sensor */}
                  <circle cx={width * 0.22} cy={height * 0.215} r={width * 0.09} fill="#0C0A09" stroke={`url(#${idPrefix}-lens-ring)`} strokeWidth="2.2" />
                  <circle cx={width * 0.22} cy={height * 0.215} r={width * 0.068} fill={`url(#${idPrefix}-lens-glare)`} />

                  {/* Lens 3: Telephoto / Periscope Prism */}
                  {hasPeriscope ? (
                    <g>
                      <rect
                        x={width * 0.13}
                        y={height * 0.285}
                        width={width * 0.18}
                        height={width * 0.18}
                        rx="4"
                        fill="#0C0A09"
                        stroke={`url(#${idPrefix}-lens-ring)`}
                        strokeWidth="2"
                      />
                      <rect
                        x={width * 0.16}
                        y={height * 0.285 + width * 0.03}
                        width={width * 0.12}
                        height={width * 0.12}
                        rx="2"
                        fill={`url(#${idPrefix}-lens-glare)`}
                      />
                    </g>
                  ) : (
                    <g>
                      <circle cx={width * 0.22} cy={height * 0.31} r={width * 0.09} fill="#0C0A09" stroke={`url(#${idPrefix}-lens-ring)`} strokeWidth="2.2" />
                      <circle cx={width * 0.22} cy={height * 0.31} r={width * 0.068} fill={`url(#${idPrefix}-lens-glare)`} />
                    </g>
                  )}

                  {/* Laser AF & Flash */}
                  <circle cx={width * 0.42} cy={height * 0.165} r={width * 0.035} fill="#FEF08A" stroke="#EAB308" strokeWidth="0.5" />
                  <circle cx={width * 0.42} cy={height * 0.245} r={width * 0.025} fill="#EF4444" />
                </g>
              )}

              {/* Model Branding Typography */}
              <g transform={`translate(${width / 2}, ${height * 0.82})`}>
                <text
                  textAnchor="middle"
                  fill={colorway.text}
                  fillOpacity="0.45"
                  fontSize={width * 0.078}
                  fontWeight="800"
                  fontFamily="system-ui, sans-serif"
                  letterSpacing="2.5px"
                >
                  {(phone.brand || 'SMARTPHONE').toUpperCase()}
                </text>
                <text
                  y={width * 0.095}
                  textAnchor="middle"
                  fill={colorway.text}
                  fillOpacity="0.5"
                  fontSize={width * 0.046}
                  fontWeight="600"
                  letterSpacing="1px"
                >
                  {cameraMP}MP • {phone.has_5g === 'Yes' || phone.has_5g ? '5G' : '4G'}
                </text>
              </g>

              {/* Minimalist Industrial Regulatory Bar */}
              <line x1={width * 0.42} y1={height * 0.94} x2={width * 0.58} y2={height * 0.94} stroke={colorway.text} strokeOpacity="0.25" strokeWidth="1" strokeLinecap="round" />
            </g>
          ) : (
            /* ========================================================
               PHONE FRONT / DISPLAY VIEW
               ======================================================== */
            <g>
              {/* Outer Screen Bezel */}
              <rect
                x="4"
                y="4"
                width={width - 8}
                height={height - 8}
                rx={rx - 2}
                fill="#000000"
              />

              {/* Display Area Clip */}
              <clipPath id={`${idPrefix}-screen-clip`}>
                <rect
                  x="6"
                  y="6"
                  width={width - 12}
                  height={height - 12}
                  rx={rx - 4}
                />
              </clipPath>

              <g clipPath={`url(#${idPrefix}-screen-clip)`}>
                {/* Modern Vivid Wallpaper */}
                <rect
                  x="6"
                  y="6"
                  width={width - 12}
                  height={height - 12}
                  fill="#0B132B"
                />
                {/* Dynamic Art Curves */}
                <path
                  d={`M 6 ${height * 0.35} Q ${width * 0.4} ${height * 0.15} ${width - 6} ${height * 0.55} L ${width - 6} ${height - 6} L 6 ${height - 6} Z`}
                  fill="#10B981"
                  fillOpacity="0.35"
                />
                <circle cx={width * 0.8} cy={height * 0.22} r={width * 0.35} fill="#0EA5E9" fillOpacity="0.3" />
                <circle cx={width * 0.2} cy={height * 0.7} r={width * 0.4} fill="#6366F1" fillOpacity="0.35" />

                {/* Clock HUD */}
                <text
                  x={width / 2}
                  y={height * 0.25}
                  textAnchor="middle"
                  fill="#FFFFFF"
                  fontSize={width * 0.18}
                  fontWeight="800"
                  fontFamily="Inter, sans-serif"
                  letterSpacing="-1px"
                >
                  09:41
                </text>
                <text
                  x={width / 2}
                  y={height * 0.32}
                  textAnchor="middle"
                  fill="#E5E7EB"
                  fontSize={width * 0.055}
                  fontWeight="600"
                >
                  {phone.name ? phone.name.split(' ').slice(0, 2).join(' ').toUpperCase() : '5G ACTIVE'}
                </text>

                {/* Specs Pill Overlays on Screen */}
                <g transform={`translate(${width * 0.12}, ${height * 0.56})`}>
                  <rect width={width * 0.76} height="18" rx="9" fill="#000000" fillOpacity="0.65" stroke="#FFFFFF" strokeOpacity="0.15" />
                  <text x={width * 0.38} y="13" textAnchor="middle" fill="#34D399" fontSize="9" fontWeight="700">
                    {phone.refresh_rate ? `${Math.round(phone.refresh_rate)}Hz AMOLED` : '120Hz LTPO'}
                  </text>
                </g>

                <g transform={`translate(${width * 0.12}, ${height * 0.66})`}>
                  <rect width={width * 0.76} height="18" rx="9" fill="#000000" fillOpacity="0.65" stroke="#FFFFFF" strokeOpacity="0.15" />
                  <text x={width * 0.38} y="13" textAnchor="middle" fill="#38BDF8" fontSize="9" fontWeight="700">
                    {phone.battery_cap ? `${phone.battery_cap} mAh Battery` : '5000 mAh'}
                  </text>
                </g>

                {/* Bottom Gesture Bar */}
                <rect
                  x={width * 0.32}
                  y={height - 16}
                  width={width * 0.36}
                  height="3.5"
                  rx="2"
                  fill="#FFFFFF"
                  fillOpacity="0.85"
                />
              </g>

              {/* Front Camera: Dynamic Island or Centered Punch-Hole */}
              {brandKey === 'apple' ? (
                <rect
                  x={width / 2 - width * 0.15}
                  y="10"
                  width={width * 0.30}
                  height="10"
                  rx="5"
                  fill="#000000"
                  stroke="#27272A"
                  strokeWidth="0.5"
                />
              ) : (
                <circle cx={width / 2} cy="14" r="4.5" fill="#000000" stroke="#3F3F46" strokeWidth="0.5" />
              )}
            </g>
          )}
        </svg>

        {/* Colorway & Price Badge at Bottom */}
        {size !== 'sm' && (
          <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 whitespace-nowrap px-3 py-0.5 rounded-full bg-white/95 border border-neutral-200 text-[10px] font-sans font-bold tracking-tight text-neutral-800 shadow-sm flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: colorway.back[0] }} />
            <span>{colorway.name}</span>
            <span>•</span>
            <span className="text-emerald-700 font-bold">₹{(phone.price || 0).toLocaleString('en-IN')}</span>
          </div>
        )}
      </div>

      {/* Interactive Chassis vs Screen Toggle */}
      {interactive && size !== 'sm' && (
        <div className="mt-5 flex items-center gap-1 p-1 bg-neutral-100/90 rounded-full border border-neutral-200 text-[11px] font-semibold text-neutral-600 shadow-sm">
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); setCurrentView('back'); }}
            className={`px-3 py-0.5 rounded-full transition-all ${
              currentView === 'back' ? 'bg-[#0B4232] text-white font-bold shadow-sm' : 'hover:text-neutral-900'
            }`}
          >
            Chassis
          </button>
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); setCurrentView('front'); }}
            className={`px-3 py-0.5 rounded-full transition-all ${
              currentView === 'front' ? 'bg-[#0B4232] text-white font-bold shadow-sm' : 'hover:text-neutral-900'
            }`}
          >
            Screen
          </button>
        </div>
      )}
    </div>
  );
}
