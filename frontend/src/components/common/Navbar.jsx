import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';

// The admin console (/admin) is intentionally not linked here; open it by URL.
export default function Navbar() {
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
          </nav>
        </div>
      </div>
    </header>
  );
}
