import React from 'react';
import { ShieldCheck, Users, AlertTriangle, Scale, Database } from 'lucide-react';

export default function AboutTrustPage() {
  return (
    <div className="py-8 max-w-4xl mx-auto space-y-12">
      {/* Header with Pop-In */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold hero-animate-title">
          <ShieldCheck className="w-4 h-4 text-[#00D09C]" />
          <span>Platform Trust & Methodology Manifesto</span>
        </div>
        <div className="hero-animate-subtitle">
          <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight">
            How Longitudinal Data Works on WorthIt
          </h1>
          <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed mt-3">
            Why we built a platform focused exclusively on what happens during ownership, and how we protect against fake reviews and misleading statistics.
          </p>
        </div>
      </div>

      {/* Core Principles Grid with Pop-In */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 hero-animate-cards">
        <div className="bg-white rounded-3xl p-7 border border-slate-200 shadow-sm space-y-3 lexi-card">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center">
            <Users className="w-5 h-5" strokeWidth={2.5} />
          </div>
          <h3 className="text-lg font-black text-slate-900">
            1. Sample Size Transparency
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
            Every statistic on WorthIt displays the exact sample size (e.g. <code>n=643</code>). If a device only has 6 registered owners, the platform labels it as <em>"Early Data — Directional Sample Only"</em> rather than claiming authoritative statistical certainty.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-7 border border-slate-200 shadow-sm space-y-3 lexi-card">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center">
            <Scale className="w-5 h-5" strokeWidth={2.5} />
          </div>
          <h3 className="text-lg font-black text-slate-900">
            2. Structured Experience, Not Star Spam
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
            Generic 5-star ratings fail because users vote based on shipping speed or first-day euphoria. We capture structured dimensions: battery degradation perception, thermal throttling, update stability, and repair costs.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-7 border border-slate-200 shadow-sm space-y-3 lexi-card">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center">
            <Database className="w-5 h-5" strokeWidth={2.5} />
          </div>
          <h3 className="text-lg font-black text-slate-900">
            3. Provenance-Backed Discovery
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
            Our automated pipeline uses Tavily Search for real-time web discovery and Google Gemini for strict JSON extraction. We retain full source links and snippet provenance for every discovered smartphone.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-7 border border-slate-200 shadow-sm space-y-3 lexi-card">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-amber-500" strokeWidth={2.5} />
          </div>
          <h3 className="text-lg font-black text-slate-900">
            4. User-Reported vs Lab Failure Rates
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
            Reported problems (e.g. green lines or motherboard swaps) are clearly marked as <em>"Reported by real owners"</em>. We do not claim to possess internal OEM return rate logs, ensuring scientific honesty.
          </p>
        </div>
      </div>

      {/* Confidence Tier Matrix Table */}
      <div className="bg-white rounded-3xl p-7 border border-slate-200 shadow-sm space-y-4 animate-fade-in-up delay-200">
        <h3 className="text-xl font-black text-slate-900">
          Our Confidence Tier Rating System
        </h3>

        <div className="divide-y divide-slate-100 text-xs sm:text-sm">
          <div className="grid grid-cols-3 py-4 items-center">
            <span className="font-black text-emerald-700">High Statistical Confidence</span>
            <span className="font-mono text-slate-600 font-semibold">100+ owners (20+ at 12m+)</span>
            <span className="text-slate-500">Authoritative long-term reliability and degradation profile.</span>
          </div>

          <div className="grid grid-cols-3 py-4 items-center">
            <span className="font-black text-teal-700">Growing Confidence</span>
            <span className="font-mono text-slate-600 font-semibold">25 to 99 owners</span>
            <span className="text-slate-500">Reliable representation of initial and mid-term ownership.</span>
          </div>

          <div className="grid grid-cols-3 py-4 items-center">
            <span className="font-black text-amber-700">Early Trends</span>
            <span className="font-mono text-slate-600 font-semibold">5 to 24 owners</span>
            <span className="text-slate-500">Preliminary directional insights.</span>
          </div>

          <div className="grid grid-cols-3 py-4 items-center">
            <span className="font-black text-rose-700">Early Data</span>
            <span className="font-mono text-slate-600 font-semibold">&lt; 5 owners</span>
            <span className="text-slate-500">Extremely small sample size; ratings may not represent typical units.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
