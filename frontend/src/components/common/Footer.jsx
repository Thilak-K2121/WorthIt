import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50 mt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-[#00D09C] flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <span className="text-xl font-black tracking-tight text-slate-900">
                Worth<span className="text-[#00D09C]">It</span>
              </span>
            </div>
            <p className="text-sm text-slate-500 max-w-md leading-relaxed">
              The longitudinal smartphone intelligence platform. Uncovering battery degradation curves, real software stability, and true repurchase sentiment after 3, 6, 12, and 24 months of daily wear.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3">
              Explore
            </h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li><Link to="/products" className="hover:text-[#00D09C] transition-colors">Smartphone Catalog</Link></li>
              <li><Link to="/compare" className="hover:text-[#00D09C] transition-colors">Long-Term Comparison</Link></li>
              <li><Link to="/submit" className="hover:text-[#00D09C] transition-colors">Log Ownership</Link></li>
              <li><Link to="/suggest" className="hover:text-[#00D09C] transition-colors">Request New Device</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3">
              Transparency
            </h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li><Link to="/about" className="hover:text-[#00D09C] transition-colors">Trust Model & Sample Sizes</Link></li>
              <li><Link to="/admin" className="hover:text-[#00D09C] transition-colors">Automated Discovery Logs</Link></li>
              <li><a href="http://127.0.0.1:8000/api/v1/docs" target="_blank" rel="noreferrer" className="hover:text-[#00D09C] transition-colors">REST API Docs</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} WorthIt Longitudinal Intelligence. Open Source Architecture.</p>
          <div className="flex items-center gap-1.5 font-medium text-slate-600">
            <span>Verified Long-Term Ownership Data</span>
            <ShieldCheck className="w-4 h-4 text-emerald-600 inline" />
          </div>
        </div>
      </div>
    </footer>
  );
}
