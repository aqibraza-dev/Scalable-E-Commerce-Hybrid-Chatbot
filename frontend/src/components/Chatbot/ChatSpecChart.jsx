import React, { useRef, useEffect } from 'react';
import { Download, BarChart2 } from 'lucide-react';

/**
 * Interactive SVG/Canvas Spec Comparison Chart for Chatbot & Catalog.
 * Compares 2-4 smartphones across Price, Battery, RAM, Storage, and Camera.
 * Supports downloading the chart as a clean SVG or PNG file.
 */
export default function ChatSpecChart({
  products = [],
  title = 'Hardware Benchmark Comparison',
  guestChartRemaining = null,
  onRender = null,
}) {
  const chartRef = useRef(null);
  const hasRenderedRef = useRef(false);

  useEffect(() => {
    if (!hasRenderedRef.current) {
      hasRenderedRef.current = true;
      onRender?.();
    }
  }, []);

  if (!products || products.length === 0) return null;

  // Normalized metrics
  const maxPrice = Math.max(...products.map(p => p.price || 1), 80000);
  const maxBattery = Math.max(...products.map(p => p.battery_cap || 1), 6000);
  const maxRam = Math.max(...products.map(p => p.ram || 1), 16);
  const maxCamera = Math.max(...products.map(p => p.primary_rear_camera || 1), 200);

  const colors = ['#d4ff00', '#38bdf8', '#ff4d12', '#a855f7'];

  const downloadSVG = () => {
    if (!chartRef.current) return;
    const svgData = new XMLSerializer().serializeToString(chartRef.current);
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `aura-comparison-${Date.now()}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="my-3 p-4 rounded-xl bg-nike-card/90 border border-nike-border shadow-lg">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-nike-border/60">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-nike-volt" />
          <span className="text-xs font-mono font-bold uppercase text-white tracking-wider">
            {title}
          </span>
          {guestChartRemaining && (
            <span className="px-2 py-0.5 rounded-full bg-nike-volt/10 border border-nike-volt/30 text-[9px] font-mono font-bold text-nike-volt">
              Guest Chart ({guestChartRemaining})
            </span>
          )}
        </div>
        <button
          onClick={downloadSVG}
          className="flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white text-[10px] font-mono transition-colors"
          title="Download vector SVG"
        >
          <Download className="w-3 h-3" />
          <span>EXPORT SVG</span>
        </button>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mb-4 text-[11px] font-medium">
        {products.map((p, idx) => (
          <div key={p.id || idx} className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: colors[idx % colors.length] }}
            />
            <span className="text-zinc-200 font-bold truncate max-w-[140px]">
              {p.name}
            </span>
          </div>
        ))}
      </div>

      {/* Comparison Bars */}
      <div className="space-y-3.5 text-xs">
        {/* Price (Inverted: lower price = higher budget score, but we display actual ₹ value) */}
        <div>
          <div className="flex justify-between text-[11px] font-mono text-zinc-400 mb-1">
            <span>PRICE (₹ INR)</span>
            <span>Lower is more affordable</span>
          </div>
          <div className="space-y-1.5">
            {products.map((p, idx) => {
              const pct = Math.min(100, Math.round(((p.price || 0) / maxPrice) * 100));
              return (
                <div key={p.id || idx} className="flex items-center gap-2">
                  <div className="w-24 text-[10px] font-bold text-zinc-300 truncate">
                    {p.name.split(' ')[0]}
                  </div>
                  <div className="flex-1 bg-zinc-800/80 h-3.5 rounded-full overflow-hidden p-0.5">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${Math.max(12, pct)}%`,
                        backgroundColor: colors[idx % colors.length],
                      }}
                    />
                  </div>
                  <div className="w-16 text-right font-mono font-bold text-[10px] text-white">
                    ₹{(p.price || 0).toLocaleString('en-IN')}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Battery Capacity */}
        <div>
          <div className="flex justify-between text-[11px] font-mono text-zinc-400 mb-1">
            <span>BATTERY CAPACITY (mAh)</span>
            <span>Higher is longer endurance</span>
          </div>
          <div className="space-y-1.5">
            {products.map((p, idx) => {
              const cap = p.battery_cap || 5000;
              const pct = Math.min(100, Math.round((cap / maxBattery) * 100));
              return (
                <div key={p.id || idx} className="flex items-center gap-2">
                  <div className="w-24 text-[10px] font-bold text-zinc-300 truncate">
                    {p.name.split(' ')[0]}
                  </div>
                  <div className="flex-1 bg-zinc-800/80 h-3.5 rounded-full overflow-hidden p-0.5">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${Math.max(12, pct)}%`,
                        backgroundColor: colors[idx % colors.length],
                      }}
                    />
                  </div>
                  <div className="w-16 text-right font-mono font-bold text-[10px] text-white">
                    {cap} mAh
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* RAM */}
        <div>
          <div className="flex justify-between text-[11px] font-mono text-zinc-400 mb-1">
            <span>RAM (GB)</span>
            <span>Multitasking capacity</span>
          </div>
          <div className="space-y-1.5">
            {products.map((p, idx) => {
              const ram = p.ram || 8;
              const pct = Math.min(100, Math.round((ram / maxRam) * 100));
              return (
                <div key={p.id || idx} className="flex items-center gap-2">
                  <div className="w-24 text-[10px] font-bold text-zinc-300 truncate">
                    {p.name.split(' ')[0]}
                  </div>
                  <div className="flex-1 bg-zinc-800/80 h-3.5 rounded-full overflow-hidden p-0.5">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${Math.max(12, pct)}%`,
                        backgroundColor: colors[idx % colors.length],
                      }}
                    />
                  </div>
                  <div className="w-16 text-right font-mono font-bold text-[10px] text-white">
                    {Math.round(ram)} GB
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Camera Sensor */}
        <div>
          <div className="flex justify-between text-[11px] font-mono text-zinc-400 mb-1">
            <span>MAIN CAMERA (MP)</span>
            <span>Sensor resolution</span>
          </div>
          <div className="space-y-1.5">
            {products.map((p, idx) => {
              const cam = Math.round(p.primary_rear_camera || 50);
              const pct = Math.min(100, Math.round((cam / maxCamera) * 100));
              return (
                <div key={p.id || idx} className="flex items-center gap-2">
                  <div className="w-24 text-[10px] font-bold text-zinc-300 truncate">
                    {p.name.split(' ')[0]}
                  </div>
                  <div className="flex-1 bg-zinc-800/80 h-3.5 rounded-full overflow-hidden p-0.5">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${Math.max(12, pct)}%`,
                        backgroundColor: colors[idx % colors.length],
                      }}
                    />
                  </div>
                  <div className="w-16 text-right font-mono font-bold text-[10px] text-white">
                    {cam} MP
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Hidden Standalone SVG for pristine vector export */}
      <svg
        ref={chartRef}
        width="600"
        height="320"
        viewBox="0 0 600 320"
        className="hidden"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="600" height="320" fill="#111115" rx="12" />
        <text x="30" y="40" fill="#d4ff00" fontSize="16" fontWeight="bold" fontFamily="monospace">
          AURA INTELLIGENCE // {title.toUpperCase()}
        </text>
        <line x1="30" y1="55" x2="570" y2="55" stroke="#27272a" strokeWidth="1" />
        {products.map((p, i) => (
          <g key={i} transform={`translate(30, ${75 + i * 55})`}>
            <text x="0" y="15" fill="#ffffff" fontSize="13" fontWeight="bold" fontFamily="sans-serif">
              {p.name}
            </text>
            <text x="0" y="32" fill="#a1a1aa" fontSize="11" fontFamily="monospace">
              ₹{(p.price || 0).toLocaleString('en-IN')} | {p.battery_cap}mAh | {Math.round(p.ram)}GB RAM | {Math.round(p.primary_rear_camera)}MP
            </text>
            <rect x="250" y="8" width="300" height="18" fill="#1f2937" rx="9" />
            <rect
              x="250"
              y="8"
              width={Math.max(30, Math.min(300, (p.battery_cap / maxBattery) * 300))}
              height="18"
              fill={colors[i % colors.length]}
              rx="9"
            />
          </g>
        ))}
      </svg>
    </div>
  );
}
