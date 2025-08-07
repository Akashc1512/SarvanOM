"use client";

import React from "react";
import { SarvanomLoader, SarvanomLoaderFullScreen, SarvanomLoaderInline } from "@/ui/SarvanomLoader";

export default function LoaderDemoPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            🌌 Cosmic Galaxy Loader Demo
          </h1>
          <p className="text-xl text-cyan-300 mb-2">
            Enhanced particle-based galaxy with vibrant cosmic colors
          </p>
          <p className="text-purple-300">
            200 individual stars rotating around a central sun with realistic orbital mechanics
          </p>
        </div>

        {/* Main Demo Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Standard Loader */}
          <div className="bg-black/20 backdrop-blur-sm rounded-2xl p-8 border border-purple-500/20">
            <h2 className="text-2xl font-semibold text-white mb-4 text-center">
              Standard Galaxy Loader
            </h2>
            <div className="flex justify-center">
              <SarvanomLoader size={120} />
            </div>
            <div className="mt-4 text-center">
              <p className="text-cyan-300 text-sm">
                • 200 unique particles with 8 different star types
              </p>
              <p className="text-purple-300 text-sm">
                • Realistic orbital mechanics (120s rotation)
              </p>
              <p className="text-pink-300 text-sm">
                • Enhanced glow effects and depth layers
              </p>
            </div>
          </div>

          {/* Inline Loader */}
          <div className="bg-black/20 backdrop-blur-sm rounded-2xl p-8 border border-cyan-500/20">
            <h2 className="text-2xl font-semibold text-white mb-4 text-center">
              Inline Galaxy Loader
            </h2>
            <div className="flex justify-center">
              <SarvanomLoaderInline size={80} />
            </div>
            <div className="mt-4 text-center">
              <p className="text-cyan-300 text-sm">
                • Compact version for UI integration
              </p>
              <p className="text-purple-300 text-sm">
                • Perfect for buttons and small spaces
              </p>
              <p className="text-pink-300 text-sm">
                • Maintains all cosmic effects
              </p>
            </div>
          </div>
        </div>

        {/* Color Palette Showcase */}
        <div className="bg-black/20 backdrop-blur-sm rounded-2xl p-8 border border-pink-500/20 mb-12">
          <h2 className="text-2xl font-semibold text-white mb-6 text-center">
            🌈 Cosmic Color Palette
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-300 to-blue-400 rounded-full mx-auto mb-2"></div>
              <p className="text-cyan-300 text-sm">Blue Stars</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-300 to-pink-400 rounded-full mx-auto mb-2"></div>
              <p className="text-purple-300 text-sm">Purple Stars</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-yellow-300 to-orange-400 rounded-full mx-auto mb-2"></div>
              <p className="text-yellow-300 text-sm">Yellow Stars</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-green-300 to-emerald-400 rounded-full mx-auto mb-2"></div>
              <p className="text-green-300 text-sm">Green Stars</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-red-300 to-pink-400 rounded-full mx-auto mb-2"></div>
              <p className="text-red-300 text-sm">Red Giants</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-indigo-300 to-purple-400 rounded-full mx-auto mb-2"></div>
              <p className="text-indigo-300 text-sm">Indigo Stars</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-teal-300 to-cyan-400 rounded-full mx-auto mb-2"></div>
              <p className="text-teal-300 text-sm">Teal Stars</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-amber-300 to-yellow-400 rounded-full mx-auto mb-2"></div>
              <p className="text-amber-300 text-sm">Amber Stars</p>
            </div>
          </div>
        </div>

        {/* Technical Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-black/20 backdrop-blur-sm rounded-xl p-6 border border-cyan-500/20">
            <h3 className="text-lg font-semibold text-white mb-3">🚀 Performance</h3>
            <ul className="text-sm text-cyan-300 space-y-1">
              <li>• 200 optimized particles</li>
              <li>• CSS-based animations</li>
              <li>• Hardware acceleration</li>
              <li>• Smooth 60fps rendering</li>
            </ul>
          </div>
          
          <div className="bg-black/20 backdrop-blur-sm rounded-xl p-6 border border-purple-500/20">
            <h3 className="text-lg font-semibold text-white mb-3">✨ Effects</h3>
            <ul className="text-sm text-purple-300 space-y-1">
              <li>• Multi-layer glow effects</li>
              <li>• Orbital ring animations</li>
              <li>• Staggered particle delays</li>
              <li>• Realistic depth layers</li>
            </ul>
          </div>
          
          <div className="bg-black/20 backdrop-blur-sm rounded-xl p-6 border border-pink-500/20">
            <h3 className="text-lg font-semibold text-white mb-3">🎨 Customization</h3>
            <ul className="text-sm text-pink-300 space-y-1">
              <li>• Configurable size prop</li>
              <li>• Custom className support</li>
              <li>• Multiple variants</li>
              <li>• Responsive design</li>
            </ul>
          </div>
        </div>

        {/* Full Screen Demo */}
        <div className="bg-black/20 backdrop-blur-sm rounded-2xl p-8 border border-yellow-500/20">
          <h2 className="text-2xl font-semibold text-white mb-4 text-center">
            🌟 Full Screen Experience
          </h2>
          <p className="text-center text-yellow-300 mb-6">
            Click the button below to experience the full cosmic immersion
          </p>
          <div className="flex justify-center">
            <button 
              onClick={() => window.open('/loader-demo/fullscreen', '_blank')}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-105"
            >
              Launch Full Screen Demo
            </button>
          </div>
        </div>

        {/* Usage Examples */}
        <div className="mt-12 bg-black/20 backdrop-blur-sm rounded-2xl p-8 border border-emerald-500/20">
          <h2 className="text-2xl font-semibold text-white mb-6 text-center">
            💻 Usage Examples
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-emerald-300 mb-3">React Component</h3>
              <pre className="bg-black/50 rounded-lg p-4 text-sm text-emerald-200 overflow-x-auto">
{`import { SarvanomLoader } from "@/ui/SarvanomLoader";

// Standard usage
<SarvanomLoader size={120} />

// Custom size
<SarvanomLoader size={80} className="my-4" />

// Full screen variant
<SarvanomLoaderFullScreen />

// Inline variant
<SarvanomLoaderInline size={40} />`}
              </pre>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-emerald-300 mb-3">Features</h3>
              <ul className="text-sm text-emerald-200 space-y-2">
                <li>✅ 200 unique cosmic particles</li>
                <li>✅ 8 different star color types</li>
                <li>✅ Realistic orbital mechanics</li>
                <li>✅ Enhanced glow and shadow effects</li>
                <li>✅ Responsive and customizable</li>
                <li>✅ Optimized for performance</li>
                <li>✅ Multiple size variants</li>
                <li>✅ Full screen immersive mode</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 