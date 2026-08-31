import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Clock, ThumbsUp } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="space-y-28 py-10">
      {/* 1. Hero Section matching exact LexiGuard Landing Page */}
      <section className="text-center max-w-5xl mx-auto pt-16 pb-12 px-4 space-y-8">
        {/* Main Big & Bold Headline with pop-in animation */}
        <div className="hero-animate-title">
          <h1 className="text-5xl sm:text-7xl lg:text-[80px] font-black tracking-tight text-slate-900 leading-[1.08]">
            Clarity in Every Review.<br />
            <span className="text-[#00D09C]">Confidence in Every Phone.</span>
          </h1>
        </div>

        {/* Subtitle with slight delay */}
        <div className="hero-animate-subtitle">
          <p className="text-slate-600 text-lg sm:text-xl max-w-3xl mx-auto leading-relaxed font-normal">
            Stop buying smartphones based on 48-hour unboxings. WorthIt is your longitudinal ownership guardian, transforming months of real user experience into simple, actionable advice.
          </p>
        </div>

        {/* "Analyze a Phone Now" Primary Mint CTA Button matching exact LexiGuard rectangular-pill shape */}
        <div className="pt-2 hero-animate-btn">
          <Link
            to="/products"
            className="inline-flex items-center justify-center px-8 py-3.5 rounded-xl bg-[#00D09C] hover:bg-[#00b88a] text-white font-extrabold text-base shadow-mint hover:shadow-mint-hover transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            Analyze a Phone Now
          </Link>
        </div>
      </section>

      {/* 2. Feature Banner ("A Simple Path to Long-Term Clarity") matching reference */}
      <section className="bg-slate-50/70 border-t border-b border-slate-100 py-20 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 hero-animate-cards">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
              A Simple Path to Long-Term Clarity
            </h2>
            <p className="text-sm sm:text-base text-slate-500 mt-2.5">
              Why longitudinal data transforms how you evaluate your next smartphone.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div 
              className="bg-white p-8 rounded-2xl lexi-card space-y-4 stagger-card"
              style={{ animationDelay: '0.12s' }}
            >
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center">
                <Clock className="w-6 h-6" strokeWidth={2.5} />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                1. Multi-Year Ownership Logs
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Track experience milestones at 3, 6, 12, 18, and 24 months to see how real battery life and camera performance hold up over time.
              </p>
            </div>

            <div 
              className="bg-white p-8 rounded-2xl lexi-card space-y-4 stagger-card"
              style={{ animationDelay: '0.24s' }}
            >
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center">
                <ShieldCheck className="w-6 h-6" strokeWidth={2.5} />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                2. Sample Size Transparency
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Zero fake precision. We display verified sample sizes and confidence badges (e.g. <em>Early Data n=8</em> vs <em>High Confidence n=643</em>).
              </p>
            </div>

            <div 
              className="bg-white p-8 rounded-2xl lexi-card space-y-4 stagger-card"
              style={{ animationDelay: '0.36s' }}
            >
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center">
                <ThumbsUp className="w-6 h-6" strokeWidth={2.5} />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                3. "Would You Buy It Again?"
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                The ultimate repurchase metric from real owners after their smartphone has aged past the initial honeymoon period.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
