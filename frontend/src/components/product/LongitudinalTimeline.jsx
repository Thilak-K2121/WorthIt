import React from 'react';
import { Calendar, BatteryCharging, AlertCircle, ArrowRight, TrendingDown, Clock, Activity, Zap, Cpu } from 'lucide-react';
import { getScoreColor } from '../../utils/formatters';

export default function LongitudinalTimeline({ milestones }) {
  if (!milestones || milestones.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-3xl border border-slate-200 shadow-sm">
        <p className="text-sm text-slate-500">
          Not enough multi-interval ownership reports to plot the timeline curve yet.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-[#00D09C]" />
            Longitudinal Ownership Curve (Tenure Milestones)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            How satisfaction and battery resilience evolve as the device ages from unboxing to 2+ years.
          </p>
        </div>
      </div>

      {/* Horizontal Stack of Milestone Cards */}
      <div className="space-y-3">
        {milestones.map((m, idx) => (
          <div
            key={idx}
            className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-sm relative overflow-hidden flex flex-col lg:flex-row lg:items-center justify-between gap-5 hover:border-[#00D09C] transition-all"
          >
            {/* Left Accent Bar in Mint */}
            <div className="absolute top-0 left-0 bottom-0 w-1.5 bg-[#00D09C]" />

            {/* Left: Tenure Title & Sample Size */}
            <div className="space-y-1.5 min-w-[200px]">
              <div className="flex items-center gap-2.5">
                <Clock className="w-4 h-4 text-[#00D09C] shrink-0" />
                <span className="font-black text-base text-slate-900">
                  {m.tenure_bucket}
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                  n={m.reports_count}
                </span>
              </div>
              {m.common_issues && m.common_issues.length > 0 && (
                <p className="text-xs text-slate-500 italic pl-6">
                  "{m.common_issues[0]}"
                </p>
              )}
            </div>

            {/* Middle: Horizontal Metrics Chips */}
            <div className="grid grid-cols-3 gap-2.5 sm:gap-3 flex-grow max-w-xl">
              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 text-center">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Overall</span>
                <span className={`font-black text-sm sm:text-base ${getScoreColor(m.avg_overall_satisfaction)}`}>
                  {m.avg_overall_satisfaction ? `${m.avg_overall_satisfaction.toFixed(1)}/5.0` : 'N/A'}
                </span>
              </div>

              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 text-center">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Battery</span>
                <span className={`font-black text-sm sm:text-base ${getScoreColor(m.avg_battery_satisfaction)}`}>
                  {m.avg_battery_satisfaction ? `${m.avg_battery_satisfaction.toFixed(1)}/5.0` : 'N/A'}
                </span>
              </div>

              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 text-center">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Performance</span>
                <span className={`font-black text-sm sm:text-base ${getScoreColor(m.avg_performance_satisfaction)}`}>
                  {m.avg_performance_satisfaction ? `${m.avg_performance_satisfaction.toFixed(1)}/5.0` : 'N/A'}
                </span>
              </div>
            </div>

            {/* Right: Degradation Perception Tags */}
            {m.battery_degradation_breakdown && Object.keys(m.battery_degradation_breakdown).length > 0 ? (
              <div className="space-y-1 lg:text-right shrink-0">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">
                  Battery Degradation:
                </span>
                <div className="flex items-center lg:justify-end gap-1.5 flex-wrap">
                  {Object.entries(m.battery_degradation_breakdown).map(([deg, pct]) => (
                    <span
                      key={deg}
                      className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold ${
                        deg === 'NONE'
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : deg === 'MINOR'
                          ? 'bg-teal-50 text-teal-800 border-teal-200'
                          : deg === 'MODERATE'
                          ? 'bg-amber-50 text-amber-800 border-amber-200'
                          : 'bg-rose-50 text-rose-800 border-rose-200'
                      }`}
                    >
                      {deg}: {pct}%
                    </span>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
