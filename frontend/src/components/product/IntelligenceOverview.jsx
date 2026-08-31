import React from 'react';
import { Battery, Cpu, Terminal, Camera, Shield, ThumbsUp, Wrench, Sparkles } from 'lucide-react';
import { formatCurrency, getScoreColor } from '../../utils/formatters';

export default function IntelligenceOverview({ insights }) {
  if (!insights) return null;

  const wba = insights.would_buy_again;

  return (
    <div className="space-y-6">
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Overall</span>
            <Shield className="w-4 h-4 text-emerald-600" />
          </div>
          <div className={`text-2xl font-black ${getScoreColor(insights.overall_satisfaction.score)}`}>
            {insights.overall_satisfaction.formatted}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">
            {insights.overall_satisfaction.sample_size} reports
          </span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Battery</span>
            <Battery className="w-4 h-4 text-emerald-600" />
          </div>
          <div className={`text-2xl font-black ${getScoreColor(insights.battery_satisfaction.score)}`}>
            {insights.battery_satisfaction.formatted}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">
            {insights.battery_satisfaction.sample_size} reports
          </span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Performance</span>
            <Cpu className="w-4 h-4 text-teal-600" />
          </div>
          <div className={`text-2xl font-black ${getScoreColor(insights.performance_satisfaction.score)}`}>
            {insights.performance_satisfaction.formatted}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">
            {insights.performance_satisfaction.sample_size} reports
          </span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Software</span>
            <Terminal className="w-4 h-4 text-slate-700" />
          </div>
          <div className={`text-2xl font-black ${getScoreColor(insights.software_satisfaction.score)}`}>
            {insights.software_satisfaction.formatted}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">
            {insights.software_satisfaction.sample_size} reports
          </span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Camera</span>
            <Camera className="w-4 h-4 text-amber-500" />
          </div>
          <div className={`text-2xl font-black ${getScoreColor(insights.camera_satisfaction.score)}`}>
            {insights.camera_satisfaction.formatted}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">
            {insights.camera_satisfaction.sample_size} reports
          </span>
        </div>

        <div className="bg-emerald-50/50 rounded-2xl p-4 border border-emerald-200 shadow-sm">
          <div className="flex items-center justify-between text-emerald-800 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">12M+ Score</span>
            <Sparkles className="w-4 h-4 text-[#00D09C]" />
          </div>
          <div className={`text-2xl font-black ${getScoreColor(insights.satisfaction_at_12m.score)}`}>
            {insights.satisfaction_at_12m.formatted}
          </div>
          <span className="text-[11px] text-emerald-700 block mt-0.5 font-semibold">
            {insights.satisfaction_at_12m.sample_size} long-term owners
          </span>
        </div>
      </div>

      {/* Would Buy Again & Repair Rate Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Would Buy Again */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ThumbsUp className="w-4 h-4 text-[#00D09C]" />
              "Would You Buy It Again?" Repurchase Verdict
            </h4>
            <span className="text-xs text-slate-500 font-mono bg-slate-100 px-2 py-0.5 rounded-md">
              n={wba.total_responses}
            </span>
          </div>

          {wba.total_responses > 0 ? (
            <div>
              {/* Progress bar */}
              <div className="h-4 w-full bg-slate-100 rounded-full overflow-hidden flex shadow-inner">
                <div
                  className="bg-[#00D09C] transition-all duration-500"
                  style={{ width: `${wba.yes_percentage || 0}%` }}
                  title={`Yes: ${wba.yes_percentage}%`}
                />
                <div
                  className="bg-amber-400 transition-all duration-500"
                  style={{ width: `${wba.unsure_percentage || 0}%` }}
                  title={`Unsure: ${wba.unsure_percentage}%`}
                />
                <div
                  className="bg-rose-400 transition-all duration-500"
                  style={{ width: `${wba.no_percentage || 0}%` }}
                  title={`No: ${wba.no_percentage}%`}
                />
              </div>

              <div className="flex items-center justify-between text-xs mt-2.5 font-bold">
                <span className="text-emerald-700 flex items-center gap-1">
                  ● Yes ({wba.yes_percentage || 0}%)
                </span>
                <span className="text-amber-700 flex items-center gap-1">
                  ● Unsure ({wba.unsure_percentage || 0}%)
                </span>
                <span className="text-rose-700 flex items-center gap-1">
                  ● No ({wba.no_percentage || 0}%)
                </span>
              </div>

              {wba.top_reasons_positive.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-100">
                  <span className="text-[11px] uppercase font-bold text-slate-500 tracking-wider block mb-1">
                    What Long-Term Owners Praise:
                  </span>
                  <p className="text-xs text-slate-700 italic bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    "{wba.top_reasons_positive[0]}"
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500">No repurchase sentiment data logged yet.</p>
          )}
        </div>

        {/* Repair & Failure Reality */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Wrench className="w-4 h-4 text-emerald-600" />
              Real-World Repair & Service Center Stats
            </h4>
            <span className="text-xs text-slate-500 font-mono bg-slate-100 px-2 py-0.5 rounded-md">
              {insights.repair_stats.total_repairs_reported} reported
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200/70">
              <span className="text-[11px] text-slate-500 block font-semibold uppercase tracking-wider">Repair Rate</span>
              <span className="text-xl font-black text-slate-900">
                {insights.repair_stats.repair_rate_percentage}%
              </span>
            </div>
            <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200/70">
              <span className="text-[11px] text-slate-500 block font-semibold uppercase tracking-wider">Median Cost</span>
              <span className="text-xl font-black text-emerald-700">
                {insights.repair_stats.median_repair_cost
                  ? formatCurrency(insights.repair_stats.median_repair_cost, insights.repair_stats.currency)
                  : '₹0 (Free / Warranty)'}
              </span>
            </div>
          </div>

          {insights.repair_stats.common_parts.length > 0 && (
            <div className="pt-2 border-t border-slate-100">
              <span className="text-[11px] uppercase font-bold text-slate-500 tracking-wider block mb-1.5">
                Most Replaced Hardware:
              </span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {insights.repair_stats.common_parts.map((p, idx) => (
                  <span key={idx} className="text-xs px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-slate-700 font-medium">
                    {p.part}: <strong className="text-slate-900">{p.count}</strong>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
