import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Smartphone, ExternalLink, Scale, PlusCircle, Filter, Users, ArrowLeft } from 'lucide-react';
import { api } from '../services/api';
import ConfidenceBanner from '../components/common/ConfidenceBanner';
import IntelligenceOverview from '../components/product/IntelligenceOverview';
import LongitudinalTimeline from '../components/product/LongitudinalTimeline';
import IssueBreakdown from '../components/product/IssueBreakdown';
import ExperienceReportCard from '../components/product/ExperienceReportCard';
import { formatDate, formatCurrency } from '../utils/formatters';

export default function ProductDetailPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [insights, setInsights] = useState(null);
  const [experiences, setExperiences] = useState([]);
  const [durationFilter, setDurationFilter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadProductData() {
      setLoading(true);
      setError(null);
      try {
        const [prodData, insData, expData] = await Promise.all([
          api.getProduct(id),
          api.getProductInsights(id),
          api.getProductExperiences(id, { min_months: durationFilter || undefined })
        ]);
        setProduct(prodData);
        setInsights(insData);
        setExperiences(expData || []);
      } catch (err) {
        console.error('Failed to load product details:', err);
        setError(err.message || 'Failed to fetch product details.');
      } finally {
        setLoading(false);
      }
    }
    loadProductData();
  }, [id, durationFilter]);

  if (loading) {
    return (
      <div className="py-12 space-y-6 animate-pulse max-w-6xl mx-auto">
        <div className="h-8 w-48 bg-slate-100 rounded-lg" />
        <div className="h-64 bg-slate-100 rounded-3xl" />
        <div className="h-96 bg-slate-100 rounded-3xl" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="py-16 text-center max-w-md mx-auto space-y-4">
        <h2 className="text-xl font-bold text-slate-900">Device Not Found</h2>
        <p className="text-xs text-slate-500">{error || 'This smartphone record does not exist.'}</p>
        <Link to="/products" className="inline-block px-5 py-2.5 rounded-xl btn-lexi-mint text-xs font-bold">
          Back to Catalog
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-10 py-6 max-w-6xl mx-auto">
      {/* Back breadcrumb */}
      <Link to="/products" className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-emerald-700 transition-colors hero-animate-title">
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Smartphone Catalog</span>
      </Link>

      {/* Main Header Hero Card with Pop-In */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm relative overflow-hidden hero-animate-subtitle">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-black uppercase tracking-wider text-emerald-700">
                {product.brand}
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-xs text-slate-500 font-medium">
                Released {formatDate(product.release_date)}
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-slate-100 text-[11px] font-semibold text-slate-700 border border-slate-200">
                {product.country_market || 'Global'}
              </span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight">
              {product.model_name}
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
              {product.description || 'Longitudinal owner experience tracking battery health, software stability, and hardware durability.'}
            </p>

            {/* Known Variants */}
            {product.variants && product.variants.length > 0 && (
              <div className="flex items-center gap-2 pt-2 flex-wrap">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Variants:
                </span>
                {product.variants.map(v => (
                  <span key={v.id} className="text-xs px-2.5 py-1 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 font-medium">
                    {v.ram ? `${v.ram} / ` : ''}{v.storage} {v.launch_price ? `(${formatCurrency(v.launch_price, v.currency)})` : ''}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Quick Action CTAs */}
          <div className="flex flex-col sm:flex-row md:flex-col gap-3 shrink-0">
            <Link
              to={`/submit`}
              className="px-5 py-2.5 rounded-xl btn-lexi-mint text-xs font-bold flex items-center justify-center gap-2"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Share Your Experience</span>
            </Link>

            <Link
              to={`/compare?product_a=${product.id}`}
              className="px-5 py-2.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-subtle"
            >
              <Scale className="w-4 h-4 text-emerald-600" />
              <span>Compare with Another Phone</span>
            </Link>

            {product.official_url && (
              <a
                href={product.official_url}
                target="_blank"
                rel="noreferrer"
                className="text-center text-[11px] font-semibold text-slate-500 hover:text-emerald-700 flex items-center justify-center gap-1 transition-colors"
              >
                <span>Official Specs Page</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>

        {/* Source Evidence Provocations */}
        {product.sources && product.sources.length > 0 && (
          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 flex-wrap text-[11px] text-slate-500">
            <span className="font-bold text-slate-700">Discovery Provenance:</span>
            <span>Discovered via {product.sources[0].provider} search ({product.sources.length} sources linked)</span>
            <a href={product.sources[0].source_url} target="_blank" rel="noreferrer" className="text-emerald-700 font-semibold hover:underline">
              [View Source]
            </a>
          </div>
        )}
      </div>

      {/* Sample Size Confidence Disclaimer */}
      {insights?.confidence && (
        <div className="hero-animate-btn">
          <ConfidenceBanner confidence={insights.confidence} />
        </div>
      )}

      {/* 1. Longitudinal Intelligence Overview */}
      {insights && (
        <section className="space-y-3 hero-animate-cards">
          <h2 className="text-xl font-black text-slate-900 tracking-tight">
            Aggregated Longitudinal Intelligence
          </h2>
          <IntelligenceOverview insights={insights} />
        </section>
      )}

      {/* 2. Longitudinal Timeline Curve */}
      {insights?.tenure_summary && insights.tenure_summary.length > 0 && (
        <section className="animate-fade-in-up delay-200">
          <LongitudinalTimeline milestones={insights.tenure_summary} />
        </section>
      )}

      {/* 3. Structured Hardware/Software Issues */}
      {insights?.issue_breakdown && (
        <section className="animate-fade-in-up delay-300">
          <IssueBreakdown issues={insights.issue_breakdown} />
        </section>
      )}

      {/* 4. Real Owner Experience Reports Stream */}
      <section className="space-y-6 pt-4 animate-fade-in-up delay-400">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <Users className="w-5 h-5 text-emerald-600" />
              Owner Experience Reports ({experiences.length})
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Chronological ownership logs submitted by real users across varying ownership intervals.
            </p>
          </div>

          {/* Tenure Filter Buttons */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 mr-1 flex items-center gap-1 text-[11px] font-bold uppercase">
              <Filter className="w-3 h-3" /> Filter:
            </span>
            <button
              onClick={() => setDurationFilter(null)}
              className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
                durationFilter == null ? 'bg-[#00D09C] text-white shadow-mint' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              All Reports
            </button>
            <button
              onClick={() => setDurationFilter(6)}
              className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
                durationFilter === 6 ? 'bg-[#00D09C] text-white shadow-mint' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              6M+
            </button>
            <button
              onClick={() => setDurationFilter(12)}
              className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
                durationFilter === 12 ? 'bg-[#00D09C] text-white shadow-mint' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              12M+
            </button>
          </div>
        </div>

        {experiences.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {experiences.map(exp => (
              <ExperienceReportCard key={exp.id} report={exp} />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-white rounded-3xl border border-slate-200 shadow-sm">
            <p className="text-xs text-slate-500">
              No experience reports match the selected tenure filter.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
