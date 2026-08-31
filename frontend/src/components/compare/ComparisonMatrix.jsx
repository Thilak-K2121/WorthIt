import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, Sparkles } from 'lucide-react';
import ConfidenceBanner from '../common/ConfidenceBanner';
import { getScoreColor } from '../../utils/formatters';

export default function ComparisonMatrix({ comparisonData }) {
  if (!comparisonData) return null;

  const { product_a: a, product_b: b, key_takeaways: takeaways } = comparisonData;

  return (
    <div className="space-y-8">
      {/* Key Insights Callout Banner */}
      {takeaways && takeaways.length > 0 && (
        <div className="p-6 rounded-3xl bg-emerald-50 border border-emerald-200 shadow-sm">
          <h4 className="text-sm font-extrabold text-emerald-900 flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-[#00D09C]" />
            Long-Term Data Takeaways
          </h4>
          <ul className="space-y-1.5 text-xs text-slate-700">
            {takeaways.map((t, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-600 font-bold">•</span>
                <span className="font-medium">{t}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Side-by-Side Header Matrix */}
      <div className="grid grid-cols-2 gap-4">
        {/* Device A */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 block mb-1">
            {a.brand}
          </span>
          <h3 className="text-2xl font-black text-slate-900">
            {a.model_name}
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Released: {a.release_date || 'N/A'} • {a.total_owners} owners ({a.long_term_owners} at 12m+)
          </p>
          <div className="mt-3.5">
            <ConfidenceBanner confidence={a.confidence} />
          </div>
        </div>

        {/* Device B */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700 block mb-1">
            {b.brand}
          </span>
          <h3 className="text-2xl font-black text-slate-900">
            {b.model_name}
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Released: {b.release_date || 'N/A'} • {b.total_owners} owners ({b.long_term_owners} at 12m+)
          </p>
          <div className="mt-3.5">
            <ConfidenceBanner confidence={b.confidence} />
          </div>
        </div>
      </div>

      {/* Longitudinal Matrix Comparison Rows */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 text-xs font-bold uppercase tracking-wider text-slate-600">
          Longitudinal Reliability & Sentiment Comparison
        </div>

        <div className="divide-y divide-slate-100 text-sm">
          {/* Overall Score */}
          <div className="grid grid-cols-3 p-4 items-center">
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(a.overall_satisfaction.score)}>
                {a.overall_satisfaction.formatted}
              </span>
            </div>
            <div className="text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
              Overall Long-Term Score
            </div>
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(b.overall_satisfaction.score)}>
                {b.overall_satisfaction.formatted}
              </span>
            </div>
          </div>

          {/* Battery Degradation & Life */}
          <div className="grid grid-cols-3 p-4 items-center">
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(a.battery_satisfaction.score)}>
                {a.battery_satisfaction.formatted}
              </span>
            </div>
            <div className="text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
              Battery Satisfaction
            </div>
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(b.battery_satisfaction.score)}>
                {b.battery_satisfaction.formatted}
              </span>
            </div>
          </div>

          {/* Performance */}
          <div className="grid grid-cols-3 p-4 items-center">
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(a.performance_satisfaction.score)}>
                {a.performance_satisfaction.formatted}
              </span>
            </div>
            <div className="text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
              Performance Stability
            </div>
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(b.performance_satisfaction.score)}>
                {b.performance_satisfaction.formatted}
              </span>
            </div>
          </div>

          {/* Software */}
          <div className="grid grid-cols-3 p-4 items-center">
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(a.software_satisfaction.score)}>
                {a.software_satisfaction.formatted}
              </span>
            </div>
            <div className="text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
              Software & Updates
            </div>
            <div className="text-center font-black text-lg text-slate-900">
              <span className={getScoreColor(b.software_satisfaction.score)}>
                {b.software_satisfaction.formatted}
              </span>
            </div>
          </div>

          {/* Would Buy Again */}
          <div className="grid grid-cols-3 p-4 items-center">
            <div className="text-center font-black text-lg text-emerald-600">
              {a.would_buy_again_percentage != null ? `${a.would_buy_again_percentage}%` : 'N/A'}
            </div>
            <div className="text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
              "Would Buy Again"
            </div>
            <div className="text-center font-black text-lg text-emerald-600">
              {b.would_buy_again_percentage != null ? `${b.would_buy_again_percentage}%` : 'N/A'}
            </div>
          </div>

          {/* Repair Rate */}
          <div className="grid grid-cols-3 p-4 items-center">
            <div className="text-center font-bold text-sm text-slate-800">
              {a.repair_rate_percentage}%
            </div>
            <div className="text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
              Repair Rate
            </div>
            <div className="text-center font-bold text-sm text-slate-800">
              {b.repair_rate_percentage}%
            </div>
          </div>

          {/* Top Issues */}
          <div className="grid grid-cols-3 p-4 items-start">
            <div className="text-center space-y-1">
              {a.top_issues.length > 0 ? (
                a.top_issues.map((iss, i) => (
                  <span key={i} className="inline-block text-[11px] px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 border border-slate-200 m-0.5 font-medium">
                    {iss}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-400">None reported</span>
              )}
            </div>
            <div className="text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
              Common Issue Areas
            </div>
            <div className="text-center space-y-1">
              {b.top_issues.length > 0 ? (
                b.top_issues.map((iss, i) => (
                  <span key={i} className="inline-block text-[11px] px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 border border-slate-200 m-0.5 font-medium">
                    {iss}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-400">None reported</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
