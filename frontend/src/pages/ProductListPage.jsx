// ==============================================================================
// Product List Page - 17-Brand Directory & Search Catalog View
// ==============================================================================
// This page provides a dual-view experience:
// 1. Default Directory View: 17 curated brand cards with visual badges and model counts.
// 2. Filtered/Search View: Brand spotlight header with model grid and longitudinal metrics.
// Includes buffered search input to prevent keystroke focus hijacking and 1-click filter reset.
// ==============================================================================

import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  Search, Smartphone, ArrowRight, ArrowLeft, Apple, Sparkles, 
  Zap, Cpu, Layers, Globe, ShieldCheck, PlusCircle, Scale, Flame, Award, Gamepad2, Radio, Camera, Shield
} from 'lucide-react';
import { api } from '../services/api';
import ProductCard from '../components/product/ProductCard';

// Brand Registry: Curated metadata (names, taglines, icons, and themes) for all 17 supported smartphone manufacturers
const BRAND_REGISTRY = {
  'apple': {
    name: 'Apple',
    title: 'Apple iPhone Series',
    tagline: 'Premium titanium chassis, 5+ years of iOS updates & strong resale retention.',
    highlights: ['5+ Years iOS Updates', 'Long-Term Resale Value', 'Titanium Durability'],
    anticipatedModels: ['iPhone 16 Pro Max', 'iPhone 15 Pro', 'iPhone 15', 'iPhone 14 Plus'],
    icon: Apple,
    color: 'text-slate-900',
    bg: 'bg-slate-100'
  },
  'samsung': {
    name: 'Samsung',
    title: 'Samsung Galaxy Series',
    tagline: 'Dynamic AMOLED displays, versatile optics & flagship OneUI durability.',
    highlights: ['7-Year OS Support', 'Dynamic AMOLED Tech', 'Versatile Camera Sensors'],
    anticipatedModels: ['Galaxy S24 Ultra', 'Galaxy S23 Ultra', 'Galaxy Z Fold 6', 'Galaxy A55'],
    icon: Smartphone,
    color: 'text-blue-600',
    bg: 'bg-blue-50'
  },
  'google': {
    name: 'Google',
    title: 'Google Pixel Series',
    tagline: 'Pure Android experience, computational photography & 7 years of Feature Drops.',
    highlights: ['Pixel Feature Drops', 'Computational Cameras', 'Clean Android UI'],
    anticipatedModels: ['Pixel 9 Pro XL', 'Pixel 8 Pro', 'Pixel 8a', 'Pixel 7 Pro'],
    icon: Sparkles,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50'
  },
  'oneplus': {
    name: 'OnePlus',
    title: 'OnePlus Flagship Series',
    tagline: 'Ultra-fast charging endurance, high-tier performance & smooth OxygenOS.',
    highlights: ['100W Fast Charging', 'Smooth OxygenOS', 'Hasselblad Optics'],
    anticipatedModels: ['OnePlus 12', 'OnePlus 12R', 'OnePlus Open', 'OnePlus Nord 4'],
    icon: Zap,
    color: 'text-red-600',
    bg: 'bg-red-50'
  },
  'vivo': {
    name: 'Vivo',
    title: 'Vivo X & V Series',
    tagline: 'Zeiss optics partnership, gimbal optical stabilization & portrait photography.',
    highlights: ['Zeiss Optics Co-Op', 'V3 Imaging Chip', 'Gimbal Stabilization'],
    anticipatedModels: ['Vivo X100 Pro', 'Vivo X100 Ultra', 'Vivo V40 Pro', 'Vivo T3 Ultra'],
    icon: Camera,
    color: 'text-sky-600',
    bg: 'bg-sky-50'
  },
  'iqoo': {
    name: 'iQOO',
    title: 'iQOO Performance Series',
    tagline: 'Extreme gaming frame rates, dedicated SuperComputing chips & fast flash charge.',
    highlights: ['Q1 SuperComputing Chip', '120W FlashCharge', 'Bypass Gaming Charging'],
    anticipatedModels: ['iQOO 12 Pro', 'iQOO Neo 9 Pro', 'iQOO Z9 Turbo', 'iQOO 11'],
    icon: Gamepad2,
    color: 'text-amber-500',
    bg: 'bg-amber-50'
  },
  'realme': {
    name: 'Realme',
    title: 'Realme GT & Number Series',
    tagline: 'Flagship killer specs, high peak brightness displays & rapid charging tech.',
    highlights: ['GT Mode Performance', '6000-nit Displays', 'Sony LYT Sensors'],
    anticipatedModels: ['Realme GT 6', 'Realme GT 6T', 'Realme 13 Pro+', 'Realme 12 Pro+'],
    icon: Flame,
    color: 'text-yellow-600',
    bg: 'bg-yellow-50'
  },
  'oppo': {
    name: 'Oppo',
    title: 'Oppo Find & Reno Series',
    tagline: 'Hasselblad dual periscope cameras, ColorOS fluidity & high battery health engine.',
    highlights: ['Battery Health Engine', 'Dual Periscope Zoom', 'Fluid ColorOS'],
    anticipatedModels: ['Oppo Find X7 Ultra', 'Oppo Reno 12 Pro', 'Oppo Find N3', 'Oppo F27 Pro+'],
    icon: Shield,
    color: 'text-emerald-700',
    bg: 'bg-emerald-50'
  },
  'xiaomi': {
    name: 'Xiaomi',
    title: 'Xiaomi & Redmi Series',
    tagline: 'High-spec hardware, Leica optics collaboration & HyperOS ecosystem.',
    highlights: ['Leica Optics Co-Op', 'High-Spec Displays', 'Fast HyperOS'],
    anticipatedModels: ['Xiaomi 14 Ultra', 'Xiaomi 14 Civi', 'Redmi Note 13 Pro+', 'Xiaomi 13 Pro'],
    icon: Layers,
    color: 'text-orange-600',
    bg: 'bg-orange-50'
  },
  'poco': {
    name: 'Poco',
    title: 'Poco F & X Series',
    tagline: 'Maximum benchmark performance per rupee, LiquidCool tech & aggressive value.',
    highlights: ['Flagship Snapdragons', 'LiquidCool 4.0', 'WildBoost Optimization'],
    anticipatedModels: ['Poco F6 Pro', 'Poco F6', 'Poco X6 Pro', 'Poco M6 Plus'],
    icon: Zap,
    color: 'text-yellow-500',
    bg: 'bg-yellow-50'
  },
  'motorola': {
    name: 'Motorola',
    title: 'Motorola Edge & Razr Series',
    tagline: 'Near-stock Android software, ergonomic curves & durable Edge series.',
    highlights: ['Near-Stock HelloUI', '125W Fast Charging', 'Ergonomic Curved Displays'],
    anticipatedModels: ['Edge 50 Ultra', 'Razr 50 Ultra', 'Edge 50 Pro', 'Moto G84 5G'],
    icon: Globe,
    color: 'text-indigo-600',
    bg: 'bg-indigo-50'
  },
  'nothing': {
    name: 'Nothing',
    title: 'Nothing Phone Series',
    tagline: 'Distinctive transparent design, glyph interface & lightweight NothingOS.',
    highlights: ['Glyph Interface', 'Zero Bloatware', 'Unique Aesthetics'],
    anticipatedModels: ['Nothing Phone (2)', 'Nothing Phone (2a) Plus', 'Nothing Phone (2a)', 'CMF Phone 1'],
    icon: Cpu,
    color: 'text-slate-800',
    bg: 'bg-slate-100'
  },
  'asus': {
    name: 'Asus & ROG',
    title: 'Asus ROG & Zenfone Series',
    tagline: 'Hardcore mobile gaming cooling, AirTriggers & compact ergonomic flagships.',
    highlights: ['AirTrigger Ultrasonic', 'GameCool 8 Thermal', '6000mAh Battery'],
    anticipatedModels: ['ROG Phone 8 Pro', 'Zenfone 11 Ultra', 'ROG Phone 7 Ultimate'],
    icon: Gamepad2,
    color: 'text-rose-600',
    bg: 'bg-rose-50'
  },
  'sony': {
    name: 'Sony',
    title: 'Sony Xperia Series',
    tagline: 'Alpha camera sensor integration, 4K OLED HDR displays & headphone jack retention.',
    highlights: ['Continuous Optical Zoom', 'Alpha Camera App', 'Zero Notch 4K OLED'],
    anticipatedModels: ['Xperia 1 VI', 'Xperia 1 V', 'Xperia 5 V', 'Xperia 10 VI'],
    icon: Radio,
    color: 'text-purple-600',
    bg: 'bg-purple-50'
  },
  'honor': {
    name: 'Honor',
    title: 'Honor Magic Series',
    tagline: 'Silicon-carbon battery tech, ultra-tough Rhino glass & AI eye comfort displays.',
    highlights: ['Silicon-Carbon Battery', '3840Hz PWM Dimming', 'Rhino Glass Durability'],
    anticipatedModels: ['Honor Magic 6 Pro', 'Honor 200 Pro', 'Honor Magic V3', 'Honor 90'],
    icon: Award,
    color: 'text-teal-600',
    bg: 'bg-teal-50'
  },
  'infinix': {
    name: 'Infinix',
    title: 'Infinix GT & Zero Series',
    tagline: 'Cyber mecha gaming designs, curved AMOLED screens & aggressive budget pricing.',
    highlights: ['Cyber Mecha LEDs', 'JBL Sound Tuning', 'Clean XOS Updates'],
    anticipatedModels: ['Infinix GT 20 Pro', 'Infinix Zero 30 5G', 'Infinix Note 40 Pro+'],
    icon: Sparkles,
    color: 'text-cyan-600',
    bg: 'bg-cyan-50'
  },
  'micromax': {
    name: 'MicroMax',
    title: 'MicroMax Series',
    tagline: 'Affordable Indian smartphone lineup focused on everyday value and battery longevity.',
    highlights: ['Budget Battery Life', 'Clean Stock Android', 'Everyday Durability'],
    anticipatedModels: ['MicroMax Q381', 'MicroMax IN Note 2', 'MicroMax IN 2b'],
    icon: Smartphone,
    color: 'text-amber-600',
    bg: 'bg-amber-50'
  }
};

export default function ProductListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [dbBrands, setDbBrands] = useState([]);
  const [loading, setLoading] = useState(true);

  const selectedBrand = searchParams.get('brand') || '';
  const searchParam = searchParams.get('search') || '';
  const [searchInput, setSearchInput] = useState(searchParam);

  // Sync searchInput when URL parameter changes (e.g. browser back/forward)
  useEffect(() => {
    setSearchInput(searchParam);
  }, [searchParam]);

  useEffect(() => {
    async function fetchCatalog() {
      setLoading(true);
      try {
        const [productsRes, brandsRes] = await Promise.all([
          api.getProducts({
            search: searchParam || undefined,
            brand: selectedBrand || undefined,
            page_size: 500
          }),
          api.getBrands().catch(() => [])
        ]);
        setProducts(productsRes.items || []);
        if (Array.isArray(brandsRes)) {
          setDbBrands(brandsRes);
        }
      } catch (err) {
        console.error('Error loading products:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchCatalog();
  }, [selectedBrand, searchParam]);

  // Combine static registry brands, distinct database brands, and loaded product brands
  const loadedProductBrands = products.map(p => p.brand).filter(Boolean);
  const combinedBrandSet = new Set([
    ...Object.keys(BRAND_REGISTRY).map(k => BRAND_REGISTRY[k].name),
    ...dbBrands,
    ...loadedProductBrands
  ]);
  const allBrands = Array.from(combinedBrandSet).sort((a, b) => a.localeCompare(b));

  const getBrandMeta = (brandName) => {
    const key = (brandName || '').toLowerCase();
    if (BRAND_REGISTRY[key]) {
      return BRAND_REGISTRY[key];
    }
    return {
      name: brandName,
      title: `${brandName} Series`,
      highlights: ['Long-Term Reliability', 'Battery Health Tracking', 'Owner Repurchase Rate'],
      anticipatedModels: [`${brandName} Flagship`, `${brandName} Pro`, `${brandName} Lite`],
      icon: Smartphone,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50'
    };
  };

  /**
   * Sets the active brand filter in the URL query string and triggers data fetch.
   */
  const handleSelectBrand = (brandName) => {
    const newParams = new URLSearchParams();
    if (brandName) {
      newParams.set('brand', brandName);
    }
    setSearchParams(newParams);
  };

  /**
   * Clears all brand and search parameters from the URL and resets input buffer,
   * returning the user to the 17-brand directory.
   */
  const handleClearAllFilters = () => {
    setSearchInput('');
    setSearchParams({});
  };

  /**
   * Handles explicit form search submission (Enter key or Search button click).
   * Updates route query parameters without interrupting user typing focus.
   */
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const newParams = new URLSearchParams(searchParams);
    const query = searchInput.trim();
    if (query) {
      newParams.set('search', query);
    } else {
      newParams.delete('search');
    }
    setSearchParams(newParams);
  };

  const activeMeta = selectedBrand ? getBrandMeta(selectedBrand) : null;
  const ActiveIcon = activeMeta?.icon || Smartphone;

  return (
    <div className="space-y-12 py-8 max-w-6xl mx-auto">
      {/* 1. CONDITIONAL VIEW: All Brands Directory (Default) */}
      {!selectedBrand && !searchParam ? (
        <div className="space-y-10">
          {/* Hero Header with Pop-In */}
          <div className="text-center max-w-3xl mx-auto space-y-4">
            <div className="hero-animate-title">
              <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight leading-tight">
                Smartphone Brands.<br />
                <span className="text-[#00D09C]">Verified Long-Term Reliability.</span>
              </h1>
            </div>
            <div className="hero-animate-subtitle">
              <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto font-normal">
                Choose any brand below to view its phone lineup, real-world battery degradation, and verified repurchase sentiment.
              </p>
            </div>
          </div>

          {/* Search bar with explicit Search button & Enter key support */}
          <div className="max-w-2xl mx-auto hero-animate-cards">
            <form onSubmit={handleSearchSubmit} className="relative flex items-center gap-2">
              <div className="relative flex-grow">
                <Search className="w-5 h-5 text-slate-400 absolute left-5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Search any phone (e.g. Apple, S24 Ultra, Pixel 8, Vivo X100, Nord 4)..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-full pl-14 pr-10 py-4 rounded-2xl bg-white border border-slate-200 shadow-sm text-slate-900 text-sm focus:outline-none focus:border-[#00D09C] transition-all"
                />
                {searchInput && (
                  <button
                    type="button"
                    onClick={() => { setSearchInput(''); handleClearAllFilters(); }}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-sm p-1"
                  >
                    ✕
                  </button>
                )}
              </div>
              <button
                type="submit"
                className="px-6 py-4 rounded-2xl bg-[#00D09C] hover:bg-[#00b88a] text-white font-bold text-sm shadow-mint hover:shadow-mint-hover transition-all shrink-0"
              >
                Search
              </button>
            </form>
          </div>

          {/* Brand Cards Grid covering all major global & Indian brands */}
          <div className="space-y-6 hero-animate-cards">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-black text-slate-900 tracking-tight">
                Select a Brand to Explore
              </h2>
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                {allBrands.length} Brands Available
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {allBrands.map((bName, idx) => {
                const meta = getBrandMeta(bName);
                const Icon = meta.icon;
                const brandDeviceCount = products.filter(p => p.brand.toLowerCase() === bName.toLowerCase()).length;

                return (
                  <button
                    key={bName}
                    onClick={() => handleSelectBrand(bName)}
                    style={{ animationDelay: `${idx * 0.045}s` }}
                    className="bg-white rounded-3xl p-7 lexi-card text-left flex flex-col justify-between group hover:border-[#00D09C] transition-all stagger-card"
                  >
                    <div className="space-y-4">
                      {/* Brand Icon */}
                      <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-slate-50 border border-slate-100 group-hover:scale-105 transition-transform">
                        <Icon className={`w-7 h-7 ${meta.color}`} strokeWidth={2.2} />
                      </div>

                      <div>
                        <h3 className="text-2xl font-black text-slate-900 group-hover:text-emerald-700 transition-colors">
                          {meta.name}
                        </h3>
                        <p className="text-xs text-slate-500 mt-1.5 leading-relaxed min-h-[36px]">
                          {meta.tagline}
                        </p>
                      </div>
                    </div>

                    <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
                      <span className="font-bold text-slate-400">
                        {brandDeviceCount > 0 ? `${brandDeviceCount} Models Tracked` : 'Explore Models'}
                      </span>
                      <span className="inline-flex items-center gap-1 font-extrabold text-emerald-600 group-hover:translate-x-1 transition-transform">
                        <span>View Lineup</span>
                        <ArrowRight className="w-4 h-4" />
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        /* 2. CONDITIONAL VIEW: Brand Spotlight & Devices Lineup / Search Results */
        <div className="space-y-8 animate-fade-in-up">
          {/* Back Navigation Bar & Persistent Search Input */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
            <button
              onClick={handleClearAllFilters}
              className="inline-flex items-center justify-center gap-2 text-xs font-extrabold text-slate-700 hover:text-slate-900 transition-colors px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 shrink-0 cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to All Brands</span>
            </button>

            {/* Inline search bar in results view */}
            <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 flex-grow max-w-md">
              <div className="relative flex-grow">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Search another model..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-full pl-10 pr-8 py-2 rounded-xl bg-white border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-[#00D09C]"
                />
                {searchInput && (
                  <button
                    type="button"
                    onClick={() => { setSearchInput(''); handleClearAllFilters(); }}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs p-0.5"
                  >
                    ✕
                  </button>
                )}
              </div>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-[#00D09C] hover:bg-[#00b88a] text-white font-bold text-xs shrink-0 shadow-sm cursor-pointer"
              >
                Search
              </button>
            </form>

            <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-center shrink-0">
              {selectedBrand ? `${selectedBrand} Lineup` : `Search: "${searchParam}"`} ({products.length} devices)
            </span>
          </div>

          {/* Attractive Brand Spotlight Card */}
          {activeMeta && (
            <div className="bg-gradient-to-r from-slate-50 via-emerald-50/20 to-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex items-start gap-4">
                  <div className="w-16 h-16 rounded-2xl bg-white border border-slate-200 flex items-center justify-center shadow-sm shrink-0">
                    <ActiveIcon className={`w-9 h-9 ${activeMeta.color}`} strokeWidth={2.2} />
                  </div>
                  <div className="space-y-1">
                    <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
                      {activeMeta.title}
                    </h1>
                    <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
                      {activeMeta.tagline}
                    </p>
                  </div>
                </div>

                {/* Pre-selected Log Device Action Button */}
                <div className="flex items-center gap-3 shrink-0">
                  <Link
                    to={`/submit?brand=${encodeURIComponent(activeMeta.name)}`}
                    className="px-5 py-2.5 rounded-xl btn-lexi-mint text-xs font-bold flex items-center gap-2"
                  >
                    <PlusCircle className="w-4 h-4" />
                    <span>Review a {activeMeta.name} Phone</span>
                  </Link>
                </div>
              </div>

              {/* Brand Highlight Badges */}
              {activeMeta.highlights && (
                <div className="flex items-center gap-2.5 flex-wrap pt-2 border-t border-slate-200/60 text-xs">
                  <span className="font-extrabold uppercase text-[10px] text-slate-400 tracking-wider">
                    Longitudinal Focus:
                  </span>
                  {activeMeta.highlights.map((h, i) => (
                    <span key={i} className="px-3 py-1 rounded-xl bg-white border border-slate-200 text-slate-700 font-semibold shadow-subtle flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-[#00D09C]" />
                      <span>{h}</span>
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Devices Grid / Beautiful Intake Hub */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map(n => (
                <div key={n} className="h-64 rounded-3xl bg-slate-100 animate-pulse border border-slate-200" />
              ))}
            </div>
          ) : products.length > 0 ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map(product => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              {/* Bottom Community Suggestion Card */}
              <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="space-y-1 text-center sm:text-left">
                  <h4 className="text-base font-extrabold text-slate-900">
                    Own a different {selectedBrand} smartphone?
                  </h4>
                  <p className="text-xs text-slate-500">
                    Submit your exact model to initialize tracking for real battery health and software stability.
                  </p>
                </div>
                <Link
                  to={`/suggest?brand=${encodeURIComponent(selectedBrand)}`}
                  className="px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold shrink-0 transition-colors"
                >
                  Suggest Another Model
                </Link>
              </div>
            </div>
          ) : (
            /* Attractive Brand Intake Hub for New/Unlisted Brands */
            <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200 shadow-sm text-center space-y-6 max-w-2xl mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-[#00D09C] flex items-center justify-center mx-auto shadow-sm">
                <ActiveIcon className="w-8 h-8" />
              </div>

              <div className="space-y-2">
                <h3 className="text-2xl font-black text-slate-900">
                  {selectedBrand} Long-Term Index Opening
                </h3>
                <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
                  Be the first owner to log long-term battery degradation and software stability for {selectedBrand} smartphones.
                </p>
              </div>

              {/* 1-Click Anticipated Models */}
              {activeMeta?.anticipatedModels && activeMeta.anticipatedModels.length > 0 && (
                <div className="pt-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2.5">
                    Popular {selectedBrand} Models:
                  </span>
                  <div className="flex items-center justify-center gap-2 flex-wrap">
                    {activeMeta.anticipatedModels.map((m, idx) => (
                      <Link
                        key={idx}
                        to={`/suggest?brand=${encodeURIComponent(selectedBrand)}`}
                        className="px-3.5 py-1.5 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-200 text-xs font-bold text-slate-700 hover:text-emerald-800 transition-colors"
                      >
                        + {m}
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
                <Link
                  to={`/submit?brand=${encodeURIComponent(selectedBrand)}`}
                  className="w-full sm:w-auto px-7 py-3 rounded-xl btn-lexi-mint text-xs font-extrabold flex items-center justify-center gap-2"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Review a {selectedBrand} Phone</span>
                </Link>

                <Link
                  to={`/suggest?brand=${encodeURIComponent(selectedBrand)}`}
                  className="w-full sm:w-auto px-6 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 text-xs font-bold transition-colors"
                >
                  Suggest Specific Model
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
