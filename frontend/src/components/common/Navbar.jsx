import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, Sparkles } from 'lucide-react';

export default function Navbar() {
  const [isDiscoveryActive, setIsDiscoveryActive] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const checkActiveJob = () => {
      const active = localStorage.getItem('worthit_active_discovery');
      setIsDiscoveryActive(Boolean(active));
    };

    checkActiveJob();
    const interval = setInterval(checkActiveJob, 2000);
    return () => clearInterval(interval);
  }, [location.pathname]);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo matching LexiGuard */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-[#00D09C] flex items-center justify-center shadow-sm">
              <ShieldCheck className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
            <span className="text-2xl font-black tracking-tight text-slate-900">
              WorthIt
            </span>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-600">
            <Link to="/products" className="hover:text-slate-900 transition-colors">
              Explore Phones
            </Link>
            <Link to="/compare" className="hover:text-slate-900 transition-colors">
              Compare
            </Link>
            <Link to="/submit" className="hover:text-slate-900 transition-colors">
              Share Experience
            </Link>
            <Link to="/suggest" className="hover:text-slate-900 transition-colors">
              Missing Phone?
            </Link>
            <Link to="/admin" className="hover:text-slate-900 transition-colors relative flex items-center gap-1.5">
              <span>Discovery</span>
              {isDiscoveryActive && (
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200 animate-pulse">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                  Live
                </span>
              )}
            </Link>
          </nav>

          {/* Top-Right "Sign In" Button matching LexiGuard (links to /products) */}
          <div className="flex items-center gap-3">
            <Link
              to="/products"
              className="px-5 py-2 rounded-lg bg-[#00D09C] hover:bg-[#00b88a] text-white font-bold text-sm shadow-mint hover:shadow-mint-hover transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
