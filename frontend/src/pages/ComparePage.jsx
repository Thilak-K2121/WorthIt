import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Scale, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import ComparisonMatrix from '../components/compare/ComparisonMatrix';

export default function ComparePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [productAId, setProductAId] = useState(searchParams.get('product_a') || '');
  const [productBId, setProductBId] = useState(searchParams.get('product_b') || '');
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadCatalog() {
      try {
        const res = await api.getProducts({ page_size: 50 });
        const items = res.items || [];
        setProducts(items);

        if (!productAId && items.length > 0) {
          setProductAId(items[0].id);
        }
        if (!productBId && items.length > 1) {
          setProductBId(items[1].id);
        }
      } catch (err) {
        console.error('Failed to load products for comparison:', err);
      }
    }
    loadCatalog();
  }, []);

  useEffect(() => {
    if (!productAId || !productBId || productAId === productBId) {
      setComparisonData(null);
      return;
    }

    async function runComparison() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.compareProducts(productAId, productBId);
        setComparisonData(data);
      } catch (err) {
        console.error('Comparison error:', err);
        setError(err.message || 'Failed to compare devices.');
      } finally {
        setLoading(false);
      }
    }
    runComparison();
  }, [productAId, productBId]);

  const handleSwap = () => {
    const temp = productAId;
    setProductAId(productBId);
    setProductBId(temp);
  };

  return (
    <div className="space-y-8 py-8 max-w-5xl mx-auto">
      {/* Header with Pop-In */}
      <div className="hero-animate-title">
        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight flex items-center gap-3">
          <Scale className="w-9 h-9 text-[#00D09C]" />
          Longitudinal Smartphone Comparison
        </h1>
        <p className="text-base text-slate-500 mt-2 hero-animate-subtitle">
          Compare real 12-month satisfaction, battery endurance curves, repair frequencies, and repurchase sentiment side-by-side.
        </p>
      </div>

      {/* Selectors Bar */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm hero-animate-cards">
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 items-center">
          {/* Device 1 Select */}
          <div className="sm:col-span-2">
            <label className="text-xs font-bold text-emerald-800 uppercase tracking-wider block mb-1">
              Primary Smartphone
            </label>
            <select
              value={productAId}
              onChange={(e) => setProductAId(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl bg-slate-50 border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-[#00D09C] focus:bg-white font-medium"
            >
              {products.map(p => (
                <option key={p.id} value={p.id}>
                  {p.brand} {p.model_name}
                </option>
              ))}
            </select>
          </div>

          {/* Swap Button */}
          <div className="flex justify-center">
            <button
              onClick={handleSwap}
              className="p-3 rounded-full bg-slate-100 border border-slate-200 hover:border-[#00D09C] text-slate-600 hover:text-emerald-700 transition-colors shadow-sm"
              title="Swap Devices"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {/* Device 2 Select */}
          <div className="sm:col-span-2">
            <label className="text-xs font-bold text-teal-800 uppercase tracking-wider block mb-1">
              Comparison Smartphone
            </label>
            <select
              value={productBId}
              onChange={(e) => setProductBId(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl bg-slate-50 border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-[#00D09C] focus:bg-white font-medium"
            >
              {products.map(p => (
                <option key={p.id} value={p.id} disabled={p.id === productAId}>
                  {p.brand} {p.model_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Comparison Results Area */}
      {loading ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-sm animate-pulse">
          <p className="text-sm text-slate-500">Computing longitudinal comparison intelligence...</p>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
          {error}
        </div>
      ) : comparisonData ? (
        <div className="animate-fade-in-up delay-200">
          <ComparisonMatrix comparisonData={comparisonData} />
        </div>
      ) : null}
    </div>
  );
}
