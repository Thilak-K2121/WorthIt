import React from 'react';
import { Link } from 'react-router-dom';
import { Users, Clock, ThumbsUp, Star, ArrowRight, ShieldCheck, PlusCircle } from 'lucide-react';
import { getScoreColor } from '../../utils/formatters';

export default function ProductCard({ product }) {
  const hasReviews = (product.total_owners_count || 0) > 0;

  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between group hover:border-[#00D09C] hover:shadow-card-hover transition-all duration-300">
      <div>
        {/* Top Header Strip */}
        <div className="flex items-center justify-between text-xs mb-3">
          <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 font-extrabold tracking-wider uppercase text-[11px] border border-emerald-200">
            {product.brand}
          </span>
          <span className="px-2.5 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-semibold text-slate-600">
            {product.country_market || 'Global'}
          </span>
        </div>

        {/* Model Title */}
        <Link to={`/products/${product.id}`}>
          <h3 className="text-xl font-black text-slate-900 group-hover:text-emerald-700 transition-colors line-clamp-1">
            {product.model_name}
          </h3>
        </Link>
        <p className="text-xs text-slate-500 mt-2 line-clamp-2 leading-relaxed min-h-[32px]">
          {product.description || 'Tracking long-term daily wear, battery degradation, and verified repurchase sentiment.'}
        </p>

        {/* Primary Longitudinal Metrics Strip */}
        <div className="grid grid-cols-2 gap-3 mt-5 pt-4 border-t border-slate-100">
          <div className="bg-slate-50 rounded-2xl p-3 border border-slate-200/70 flex flex-col justify-between">
            <span className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider block">
              12M+ Score
            </span>
            <div className="flex items-center gap-1.5 mt-1">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
              <span className={`text-base font-black ${getScoreColor(product.avg_overall_satisfaction)}`}>
                {product.avg_overall_satisfaction ? `${product.avg_overall_satisfaction.toFixed(1)} / 5.0` : 'Early Stage'}
              </span>
            </div>
          </div>

          <div className="bg-emerald-50/60 rounded-2xl p-3 border border-emerald-100 flex flex-col justify-between">
            <span className="text-[10px] text-emerald-800 font-extrabold uppercase tracking-wider block">
              Repurchase Rate
            </span>
            <div className="flex items-center gap-1.5 mt-1">
              <ThumbsUp className="w-4 h-4 text-emerald-600" />
              <span className="text-base font-black text-emerald-800">
                {product.would_buy_again_percentage != null ? `${product.would_buy_again_percentage}%` : 'Collecting'}
              </span>
            </div>
          </div>
        </div>

        {/* Sample Meta Stats */}
        <div className="flex items-center justify-between text-xs text-slate-500 mt-4 pt-2">
          <span className="flex items-center gap-1.5 font-medium">
            <Users className="w-3.5 h-3.5 text-slate-400" />
            <span><strong className="text-slate-800 font-bold">{product.total_owners_count || 0}</strong> tracked owners</span>
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <Clock className="w-3.5 h-3.5 text-emerald-600" />
            <span><strong className="text-emerald-700 font-bold">{product.long_term_owners_count || 0}</strong> at 12m+</span>
          </span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
        <Link
          to={`/compare?product_a=${product.id}`}
          className="text-xs font-bold text-slate-500 hover:text-slate-900 transition-colors"
        >
          + Compare
        </Link>
        <Link
          to={`/products/${product.id}`}
          className="px-4 py-2 rounded-xl btn-lexi-mint text-xs font-bold flex items-center gap-1.5 group-hover:scale-[1.02]"
        >
          <span>Analyze Insights</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
