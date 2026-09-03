import React from 'react';
import { AlertTriangle, Wrench, ShieldAlert, Clock, AlertOctagon } from 'lucide-react';

export default function IssueBreakdown({ issues }) {
  if (!issues || issues.length === 0) {
    return (
      <div className="p-6 text-center bg-white rounded-3xl border border-slate-200 shadow-sm">
        <p className="text-xs text-slate-500">
          No hardware or software failure patterns reported by owners yet.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-500" />
            Reported Hardware & Software Issues
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Structured problem taxonomy aggregated across owner reports. (Distinguished from laboratory failure rates).
          </p>
        </div>
      </div>

      {/* Horizontal Stack of Issue Cards */}
      <div className="space-y-3">
        {issues.map((iss, idx) => (
          <div
            key={idx}
            className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-sm relative overflow-hidden flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:border-amber-400 transition-all"
          >
            {/* Left Amber/Rose Accent Bar */}
            <div
              className={`absolute top-0 left-0 bottom-0 w-1.5 ${
                iss.percentage_of_owners > 15 ? 'bg-rose-500' : 'bg-amber-500'
              }`}
            />

            {/* Left: Issue Category & User Quote */}
            <div className="space-y-1 min-w-[220px]">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-500 shrink-0" />
                <span className="font-black text-base text-slate-900 capitalize">
                  {iss.category_name}
                </span>
              </div>
              {iss.most_common_complaint && (
                <p className="text-xs text-slate-600 italic pl-6 line-clamp-1">
                  "{iss.most_common_complaint}"
                </p>
              )}
            </div>

            {/* Middle: Horizontal Metrics Chips */}
            <div className="flex items-center gap-3 flex-wrap">
              <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-600 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>Avg month: <strong className="text-slate-900 font-bold">{iss.average_occurred_month || 'N/A'}</strong></span>
              </div>

              {iss.repair_required_count > 0 && (
                <div className="px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 font-bold flex items-center gap-1.5">
                  <Wrench className="w-3.5 h-3.5 text-amber-600" />
                  <span>{iss.repair_required_count} required repair</span>
                </div>
              )}
            </div>

            {/* Right: Prominent Percentage Badge */}
            <div className="shrink-0 lg:text-right">
              <span
                className={`text-xs font-black px-3 py-1.5 rounded-full inline-flex items-center gap-1 shadow-sm ${
                  iss.percentage_of_owners > 15
                    ? 'bg-rose-50 text-rose-700 border border-rose-200'
                    : iss.percentage_of_owners > 8
                    ? 'bg-amber-50 text-amber-700 border border-amber-200'
                    : 'bg-slate-100 text-slate-700 border border-slate-200'
                }`}
              >
                {iss.percentage_of_owners}% of owners
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
