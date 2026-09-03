import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Cpu, Play, RefreshCw, Clock, CheckCircle2, XCircle, 
  Smartphone, Inbox, Sparkles, ChevronDown, ChevronUp, ExternalLink, ArrowRight, Layers, Globe,
  Search, Shield, Bot, Database, Activity, Zap, Check
} from 'lucide-react';
import { api } from '../services/api';

const DISCOVERY_STAGES = [
  {
    step: 1,
    title: 'Tavily Web Search',
    desc: 'Scanning launch articles, OEM press releases & spec sheets',
    icon: Search,
    color: 'text-sky-500',
    bg: 'bg-sky-50'
  },
  {
    step: 2,
    title: 'Gemini AI Extraction',
    desc: 'Extracting clean JSON specs (SoC, RAM, battery, camera, ₹ INR price)',
    icon: Bot,
    color: 'text-purple-500',
    bg: 'bg-purple-50'
  },
  {
    step: 3,
    title: 'Jaccard Deduplication',
    desc: 'Evaluating token similarity against existing 98+ phone catalog',
    icon: Shield,
    color: 'text-amber-500',
    bg: 'bg-amber-50'
  },
  {
    step: 4,
    title: 'Database Ingestion',
    desc: 'Committing verified phones, variants, and source citations to Supabase',
    icon: Database,
    color: 'text-emerald-500',
    bg: 'bg-emerald-50'
  }
];

export default function AdminDiscoveryPage() {
  const [runs, setRuns] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [productsCount, setProductsCount] = useState(0);
  const [running, setRunning] = useState(false);
  const [queryTopic, setQueryTopic] = useState('Latest Smartphone Launches 2026');
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('runs');
  const [expandedRunId, setExpandedRunId] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [activeJobQuery, setActiveJobQuery] = useState('');

  const pollingTimerRef = useRef(null);
  const elapsedTimerRef = useRef(null);

  const refreshData = async () => {
    try {
      const [runsData, suggData, prodData] = await Promise.all([
        api.listDiscoveryRuns(1, 20),
        api.listSuggestions(),
        api.getProducts({ page_size: 1 })
      ]);
      setRuns(runsData || []);
      setSuggestions(suggData || []);
      setProductsCount(prodData?.total || 0);
      
      if (runsData && runsData.length > 0 && !expandedRunId) {
        setExpandedRunId(runsData[0].id);
      }
      return runsData || [];
    } catch (err) {
      console.error('Failed to load admin data:', err);
      return [];
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const activeStored = localStorage.getItem('worthit_active_discovery');
    if (activeStored) {
      try {
        const parsed = JSON.parse(activeStored);
        const startedAt = parsed.started_at || Date.now();
        const initialElapsed = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
        setElapsedSeconds(initialElapsed);
        setActiveJobQuery(parsed.query_topic || 'Latest Smartphone Launches');
        setRunning(true);
      } catch (e) {
        localStorage.removeItem('worthit_active_discovery');
      }
    }
    refreshData();
  }, []);

  useEffect(() => {
    if (running) {
      elapsedTimerRef.current = setInterval(() => {
        setElapsedSeconds(prev => prev + 1);
      }, 1000);

      pollingTimerRef.current = setInterval(async () => {
        const freshRuns = await refreshData();
        const activeStored = localStorage.getItem('worthit_active_discovery');
        if (activeStored) {
          const parsed = JSON.parse(activeStored);
          const latestRun = freshRuns[0];
          if (latestRun && new Date(latestRun.started_at).getTime() >= (parsed.started_at - 10000)) {
            if (latestRun.status === 'COMPLETED' || latestRun.status === 'FAILED') {
              localStorage.removeItem('worthit_active_discovery');
              setRunning(false);
              setExpandedRunId(latestRun.id);
              setActiveTab('runs');
            }
          }
        }
      }, 3500);
    } else {
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    }

    return () => {
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    };
  }, [running]);

  const handleTriggerDiscovery = async () => {
    const jobData = {
      query_topic: queryTopic,
      started_at: Date.now()
    };
    localStorage.setItem('worthit_active_discovery', JSON.stringify(jobData));
    setActiveJobQuery(queryTopic);
    setElapsedSeconds(0);
    setRunning(true);

    try {
      const newRun = await api.triggerDiscovery({
        query_topic: queryTopic,
        max_results: 5
      });
      localStorage.removeItem('worthit_active_discovery');
      setRunning(false);
      await refreshData();
      if (newRun?.id) {
        setExpandedRunId(newRun.id);
        setActiveTab('runs');
      }
    } catch (err) {
      localStorage.removeItem('worthit_active_discovery');
      setRunning(false);
      alert(`Discovery run failed: ${err.message}`);
    }
  };

  const handleReviewSuggestion = async (id, action) => {
    try {
      await api.reviewSuggestion(id, { action });
      await refreshData();
    } catch (err) {
      alert(`Review failed: ${err.message}`);
    }
  };

  const toggleRunExpand = (runId) => {
    setExpandedRunId(prev => prev === runId ? null : runId);
  };

  const currentStageIndex = elapsedSeconds < 6 ? 0 : elapsedSeconds < 14 ? 1 : elapsedSeconds < 20 ? 2 : 3;
  const pendingSuggestions = suggestions.filter(s => s.status === 'PENDING');

  return (
    <div className="space-y-10 py-8 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 hero-animate-title">
        <div className="space-y-1">
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
            <Cpu className="w-7 h-7 text-[#00D09C]" />
            Discovery & Moderation Console
          </h1>
          <p className="text-sm text-slate-500 hero-animate-subtitle">
            Automated Tavily search + Gemini extraction pipeline and user suggestion queue.
          </p>
        </div>

        <button
          onClick={refreshData}
          className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 text-xs font-bold flex items-center gap-2 self-start sm:self-auto transition-colors shadow-sm cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Data</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 hero-animate-cards">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-[#00D09C] flex items-center justify-center shrink-0">
            <Smartphone className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">Catalog Phones</span>
            <span className="text-2xl font-black text-slate-900">{productsCount} Devices</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">Discovery Runs</span>
            <span className="text-2xl font-black text-slate-900">{runs.length} Completed</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
            <Inbox className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">User Suggestions</span>
            <span className="text-2xl font-black text-slate-900">{pendingSuggestions.length} Pending</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4 hero-animate-cards">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#00D09C]" />
            Trigger Automated Web Discovery
          </h3>
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Live AI Search & Extraction
          </span>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3">
          <input
            type="text"
            value={queryTopic}
            onChange={(e) => setQueryTopic(e.target.value)}
            disabled={running}
            placeholder="e.g. Latest Smartphone Launches 2026 or Vivo X100 Pro launch"
            className="w-full px-4 py-3 rounded-2xl bg-slate-50 border border-slate-200 text-slate-900 text-sm font-medium focus:outline-none focus:border-[#00D09C] focus:bg-white transition-colors disabled:opacity-60"
          />

          <button
            onClick={handleTriggerDiscovery}
            disabled={running}
            className="w-full sm:w-auto px-7 py-3 rounded-xl btn-lexi-mint text-xs font-extrabold shadow-mint hover:shadow-mint-hover transition-all disabled:opacity-50 flex items-center justify-center gap-2 shrink-0 cursor-pointer"
          >
            <Play className="w-4 h-4" />
            <span>{running ? 'Discovery in Progress...' : 'Run Discovery'}</span>
          </button>
        </div>

        {running && (
          <div className="mt-6 p-6 rounded-3xl bg-gradient-to-br from-slate-900 via-slate-950 to-emerald-950 text-white border-2 border-[#00D09C] shadow-2xl space-y-6 relative overflow-hidden animate-fade-in-up">
            <div className="absolute top-0 right-0 w-80 h-80 bg-[#00D09C]/10 rounded-full blur-3xl pointer-events-none" />

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div className="flex items-center gap-3.5">
                <div className="relative flex items-center justify-center w-12 h-12">
                  <span className="absolute inline-flex h-full w-full rounded-full bg-[#00D09C] opacity-40 animate-ping" />
                  <span className="relative inline-flex rounded-full h-9 w-9 bg-[#00D09C] text-slate-950 items-center justify-center font-black shadow-lg">
                    <Activity className="w-5 h-5 animate-pulse" />
                  </span>
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-black text-lg text-white">
                      Live AI Extraction Radar
                    </h4>
                    <span className="text-[10px] uppercase font-black tracking-widest px-2 py-0.5 rounded-full bg-emerald-500/20 text-[#00D09C] border border-emerald-500/30 animate-pulse">
                      Active
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5 font-mono">
                    Target: "{activeJobQuery || queryTopic}"
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 self-start sm:self-auto">
                <div className="px-3.5 py-1.5 rounded-xl bg-slate-800/90 border border-slate-700/80 text-xs font-mono font-bold text-emerald-400 flex items-center gap-2 shadow-inner">
                  <Clock className="w-3.5 h-3.5 animate-spin" />
                  <span>Elapsed: {elapsedSeconds}s</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {DISCOVERY_STAGES.map((stg, idx) => {
                const isPassed = currentStageIndex > idx;
                const isCurrent = currentStageIndex === idx;
                const IconComponent = stg.icon;

                return (
                  <div
                    key={stg.step}
                    className={`p-4 rounded-2xl border transition-all relative flex flex-col justify-between min-h-[110px] ${
                      isCurrent
                        ? 'bg-slate-800/90 border-[#00D09C] shadow-lg ring-1 ring-[#00D09C]/50'
                        : isPassed
                        ? 'bg-slate-900/60 border-emerald-900/60 opacity-90'
                        : 'bg-slate-900/30 border-slate-800/50 opacity-40'
                    }`}
                  >
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                            isCurrent ? 'bg-[#00D09C] text-slate-950 font-bold' : isPassed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'
                          }`}>
                            <IconComponent className="w-4 h-4" />
                          </div>
                          <span className="text-xs font-black text-white">
                            {stg.title}
                          </span>
                        </div>

                        {isPassed ? (
                          <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : isCurrent ? (
                          <span className="w-2.5 h-2.5 rounded-full bg-[#00D09C] animate-ping" />
                        ) : null}
                      </div>

                      <p className="text-[11px] text-slate-400 leading-tight">
                        {stg.desc}
                      </p>
                    </div>

                    {isCurrent && (
                      <div className="mt-2 pt-2 border-t border-slate-700/60 flex items-center gap-1.5 text-[10px] font-bold text-[#00D09C] animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#00D09C]" />
                        <span>Processing in real time...</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-400 bg-slate-950/60 p-3 rounded-2xl border border-slate-800/80">
              <span className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400 shrink-0" />
                <span><strong>Persistent Background Worker:</strong> You can safely browse other pages; discovery will finish in the cloud.</span>
              </span>
              <span className="text-[11px] text-emerald-400 font-bold">
                Auto-syncing every 3.5s
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3 border-b border-slate-200 pb-3">
        <button
          onClick={() => setActiveTab('runs')}
          className={`px-5 py-2.5 rounded-xl text-xs font-extrabold transition-all flex items-center gap-2 ${
            activeTab === 'runs'
              ? 'bg-[#00D09C] text-white shadow-mint'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          <Cpu className="w-4 h-4" />
          <span>Automated Pipeline Logs ({runs.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('suggestions')}
          className={`px-5 py-2.5 rounded-xl text-xs font-extrabold transition-all flex items-center gap-2 ${
            activeTab === 'suggestions'
              ? 'bg-[#00D09C] text-white shadow-mint'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          <Inbox className="w-4 h-4" />
          <span>User Suggestions Queue</span>
          {pendingSuggestions.length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full bg-white text-emerald-800 text-[10px] font-black">
              {pendingSuggestions.length}
            </span>
          )}
        </button>
      </div>

      {/* 5. Tab Content: Discovery Audit Logs with Clean Phone Badges (Zero Snippet Clutter) */}
      {activeTab === 'runs' && (
        <div className="space-y-6 animate-fade-in-up">
          {runs.length > 0 ? (
            <div className="space-y-4">
              {runs.map((r, idx) => {
                const isExpanded = expandedRunId === r.id;
                const runNumber = runs.length - idx;
                const sourcesList = r.sources || [];

                return (
                  <div 
                    key={r.id} 
                    className={`bg-white rounded-3xl border transition-all ${
                      isExpanded 
                        ? 'border-[#00D09C] shadow-md ring-1 ring-emerald-400/30' 
                        : 'border-slate-200 shadow-sm hover:border-slate-300'
                    }`}
                  >
                    {/* Clickable Header Row */}
                    <div 
                      onClick={() => toggleRunExpand(r.id)}
                      className="p-6 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 select-none group"
                    >
                      <div className="space-y-2">
                        <div className="flex items-center gap-2.5">
                          <span className="font-black text-lg text-slate-900 group-hover:text-emerald-700 transition-colors">
                            Discovery Run #{runNumber}
                          </span>
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${
                            r.status === 'COMPLETED' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800'
                          }`}>
                            {r.status}
                          </span>
                        </div>

                        <div className="text-xs text-slate-500 flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          <span>{new Date(r.started_at).toLocaleString()}</span>
                        </div>
                      </div>

                      {/* Quick Metric Pills */}
                      <div className="flex items-center gap-3 flex-wrap">
                        <div className="grid grid-cols-3 gap-2 bg-slate-50 p-2.5 rounded-2xl border border-slate-200 text-xs">
                          <div className="px-2">
                            <span className="text-slate-400 block text-[10px] uppercase font-bold">Sources</span>
                            <strong className="text-slate-900 text-sm">{r.sources_searched}</strong>
                          </div>
                          <div className="px-2 border-l border-slate-200">
                            <span className="text-slate-400 block text-[10px] uppercase font-bold">Extracted</span>
                            <strong className="text-teal-700 text-sm">{r.extracted_count}</strong>
                          </div>
                          <div className="px-2 border-l border-slate-200">
                            <span className="text-slate-400 block text-[10px] uppercase font-bold">New Phones</span>
                            <strong className="text-emerald-700 text-sm font-extrabold">+{r.new_products_created}</strong>
                          </div>
                        </div>

                        <button
                          type="button"
                          className="px-3.5 py-2 rounded-xl bg-slate-100 group-hover:bg-emerald-50 group-hover:text-emerald-700 text-slate-600 text-xs font-bold flex items-center gap-1.5 transition-colors shrink-0"
                        >
                          <span>{isExpanded ? 'Hide Phones' : 'View Discovered Phones'}</span>
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>

                    {/* Expandable Drilldown: Minimalist Discovered Phone Cards */}
                    {isExpanded && (
                      <div className="p-6 pt-0 border-t border-slate-100 bg-slate-50/50 rounded-b-3xl space-y-4 animate-fade-in-up">
                        <div className="flex items-center justify-between pt-4">
                          <h4 className="text-xs uppercase font-extrabold tracking-wider text-slate-500 flex items-center gap-2">
                            <Smartphone className="w-4 h-4 text-[#00D09C]" />
                            Smartphones Discovered ({sourcesList.length} models)
                          </h4>
                          <span className="text-xs text-slate-400">
                            Duplicates recognized: <strong className="text-slate-700">{r.duplicates_detected}</strong>
                          </span>
                        </div>

                        {sourcesList.length > 0 ? (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {sourcesList.map((src, sIdx) => {
                              const spec = src.raw_extracted_json || {};
                              const variants = spec.variants || [];
                              const modelTitle = src.model_name || spec.model_name || 'Smartphone';
                              const brandName = src.brand || spec.brand || 'Device';

                              return (
                                <div 
                                  key={src.id || sIdx} 
                                  className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3 flex flex-col justify-between hover:border-[#00D09C] transition-all group/phone"
                                >
                                  <div className="space-y-2">
                                    {/* Brand & Market Header */}
                                    <div className="flex items-center justify-between">
                                      <span className="text-xs font-black uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-lg border border-emerald-100">
                                        {brandName}
                                      </span>
                                      <span className="text-[11px] font-semibold text-slate-400">
                                        {spec.country_market || 'Global'}
                                      </span>
                                    </div>

                                    {/* Model Name */}
                                    <h5 className="text-lg font-black text-slate-900 group-hover/phone:text-emerald-700 transition-colors">
                                      {modelTitle}
                                    </h5>

                                    {/* Storage & Pricing Pills (if available) */}
                                    {variants.length > 0 && (
                                      <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                                        {variants.slice(0, 2).map((v, vIdx) => (
                                          <span 
                                            key={vIdx} 
                                            className="text-[11px] px-2.5 py-0.5 rounded-xl bg-slate-50 text-slate-800 font-bold border border-slate-200"
                                          >
                                            {v.ram ? `${v.ram}/` : ''}{v.storage} {v.launch_price ? `(₹${Number(v.launch_price).toLocaleString()})` : ''}
                                          </span>
                                        ))}
                                      </div>
                                    )}
                                  </div>

                                  {/* Direct 1-Click Action Buttons */}
                                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2 text-xs">
                                    <a
                                      href={src.source_url}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="text-slate-400 hover:text-slate-700 text-[11px] font-semibold flex items-center gap-1 truncate"
                                    >
                                      <span>Source</span>
                                      <ExternalLink className="w-3 h-3 shrink-0" />
                                    </a>

                                    {src.product_id ? (
                                      <Link
                                        to={`/products/${src.product_id}`}
                                        className="px-3 py-1.5 rounded-xl btn-lexi-mint text-xs font-bold flex items-center gap-1 shadow-subtle"
                                      >
                                        <span>View in Catalog</span>
                                        <ArrowRight className="w-3.5 h-3.5" />
                                      </Link>
                                    ) : (
                                      <span className="text-[11px] font-bold text-slate-400">
                                        Cataloged
                                      </span>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="p-6 rounded-2xl bg-white border border-slate-200 text-center space-y-1">
                            <p className="text-xs font-bold text-slate-700">
                              Discovery Query: "{queryTopic}"
                            </p>
                            <p className="text-xs text-slate-500">
                              {r.new_products_created > 0 
                                ? `Created ${r.new_products_created} new smartphone models in the catalog.`
                                : `Recognized ${r.duplicates_detected} existing devices in the catalog with zero duplicates created.`}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-sm space-y-3">
              <Cpu className="w-12 h-12 text-slate-300 mx-auto" />
              <h4 className="text-base font-bold text-slate-900">No Discovery Runs Yet</h4>
              <p className="text-xs text-slate-500">
                Trigger a discovery query above to search for new smartphone launches on the web.
              </p>
            </div>
          )}
        </div>
      )}

      {/* 6. Tab Content: Suggestions Queue */}
      {activeTab === 'suggestions' && (
        <div className="space-y-4 animate-fade-in-up">
          {suggestions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {suggestions.map(s => (
                <div key={s.id} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs uppercase font-extrabold text-emerald-700">{s.brand}</span>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        s.status === 'APPROVED' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
                        s.status === 'PENDING' ? 'bg-amber-50 text-amber-800 border border-amber-200' :
                        'bg-slate-100 text-slate-600'
                      }`}>
                        {s.status}
                      </span>
                    </div>

                    <h4 className="text-xl font-black text-slate-900">{s.model_name}</h4>

                    {s.variant_details && (
                      <p className="text-xs text-slate-600 font-medium">Variant: {s.variant_details}</p>
                    )}
                    {s.notes && (
                      <p className="text-xs text-slate-500 italic bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        "{s.notes}"
                      </p>
                    )}
                  </div>

                  {s.status === 'PENDING' ? (
                    <div className="flex items-center gap-2 pt-3 border-t border-slate-100">
                      <button
                        onClick={() => handleReviewSuggestion(s.id, 'APPROVE')}
                        className="flex-1 py-2.5 rounded-xl btn-lexi-mint text-xs font-bold flex items-center justify-center gap-1.5"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Approve & Ingest</span>
                      </button>
                      <button
                        onClick={() => handleReviewSuggestion(s.id, 'REJECT')}
                        className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
                      >
                        Reject
                      </button>
                    </div>
                  ) : (
                    <div className="pt-2 border-t border-slate-100 text-xs text-slate-400 font-medium">
                      Reviewed & processed in catalog
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-sm space-y-3">
              <CheckCircle2 className="w-12 h-12 text-[#00D09C] mx-auto" />
              <h4 className="text-base font-bold text-slate-900">All Suggestions Reviewed</h4>
              <p className="text-xs text-slate-500">
                No user submitted phone models pending in the queue.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
