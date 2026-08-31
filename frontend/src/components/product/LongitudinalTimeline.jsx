import React from 'react';
import { Calendar, BatteryCharging, AlertCircle, ArrowRight, TrendingDown } from 'lucide-react';
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {milestones.map((m, idx) => (
          <div key={idx} className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm relative overflow-hidden flex flex-col justify-between">
            {/* Top Accent line in Mint */}
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-[#00D09C]" />

            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="font-extrabold text-sm text-slate-900">
                  {m.tenure_bucket}
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                  n={m.reports_count}
                </span>
              </div>

              {/* Metric Breakdown for this tenure */}
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-200/60">
                  <span className="text-slate-500 font-medium">Overall Score</span>
                  <span className={`font-black ${getScoreColor(m.avg_overall_satisfaction)}`}>
                    {m.avg_overall_satisfaction ? `${m.avg_overall_satisfaction.toFixed(1)}/5.0` : 'N/A'}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-200/60">
                  <span className="text-slate-500 font-medium">Battery Score</span>
                  <span className={`font-black ${getScoreColor(m.avg_battery_satisfaction)}`}>
                    {m.avg_battery_satisfaction ? `${m.avg_battery_satisfaction.toFixed(1)}/5.0` : 'N/A'}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-200/60">
                  <span className="text-slate-500 font-medium">Performance</span>
                  <span className={`font-black ${getScoreColor(m.avg_performance_satisfaction)}`}>
                    {m.avg_performance_satisfaction ? `${m.avg_performance_satisfaction.toFixed(1)}/5.0` : 'N/A'}
                  </span>
                </div>
              </div>

              {/* Degradation perception if available */}
              {m.battery_degradation_breakdown && Object.keys(m.battery_degradation_breakdown).length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-slate-100">
                  <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block mb-1">
                    Battery Degradation Reported:
                  </span>
                  <div className="flex items-center gap-1.5 flex-wrap text-[11px]">
                    {Object.entries(m.battery_degradation_breakdown).map(([deg, pct]) => (
                      <span key={deg} className={`px-2 py-0.5 rounded-md border text-[10px] font-medium ${
                        deg === 'NONE' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' :
                        deg === 'MINOR' ? 'bg-teal-50 text-teal-800 border-teal-200' :
                        'bg-amber-50 text-amber-800 border-amber-200'
                      }`}>
                        {deg}: {pct}%
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {m.common_issues && m.common_issues.length > 0 && (
              <div className="mt-3 pt-2.5 text-[11px] text-slate-500 italic line-clamp-2 border-t border-slate-100">
                "{m.common_issues[0]}"
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
