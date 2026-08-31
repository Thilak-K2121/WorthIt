import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Sparkles, CheckCircle2, AlertCircle, PlusCircle } from 'lucide-react';
import { api } from '../services/api';
import OwnershipForm from '../components/forms/OwnershipForm';

export default function SubmitExperiencePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const requestedBrand = searchParams.get('brand') || '';
  const requestedProductId = searchParams.get('product_id') || '';

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    async function loadProducts() {
      try {
        const res = await api.getProducts({ page_size: 50 });
        let allItems = res.items || [];
        if (requestedBrand && !allItems.some(p => p.brand.toLowerCase() === requestedBrand.toLowerCase())) {
          try {
            const brandRes = await api.getProducts({ brand: requestedBrand, page_size: 50 });
            if (brandRes?.items?.length) {
              allItems = [...brandRes.items, ...allItems];
            }
          } catch (e) {
            console.warn('Brand specific load failed:', e);
          }
        }
        setProducts(allItems);
      } catch (err) {
        console.error('Failed to load products for submission:', err);
      } finally {
        setLoading(false);
      }
    }
    loadProducts();
  }, [requestedBrand]);

  const handleSubmit = async (payload) => {
    setSubmitting(true);
    try {
      const res = await api.registerOwnership(payload);
      setSuccess(true);
      setTimeout(() => {
        navigate(`/products/${res.product_id}`);
      }, 2000);
    } catch (err) {
      alert(`Submission failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-sm text-slate-500">Loading catalog...</div>;
  }

  return (
    <div className="py-8 max-w-3xl mx-auto space-y-8">
      {/* Header with Pop-In */}
      <div className="hero-animate-title text-center sm:text-left">
        <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight flex items-center justify-center sm:justify-start gap-2.5">
          <Sparkles className="w-8 h-8 text-[#00D09C]" />
          Log Smartphone Ownership
        </h1>
        <p className="text-base text-slate-500 mt-2 hero-animate-subtitle">
          {requestedBrand ? `Share your real-world ${requestedBrand} ownership experience.` : 'Share what your phone is actually like after months of real daily wear, software updates, and battery drain.'}
        </p>
      </div>

      {success ? (
        <div className="p-10 rounded-3xl bg-emerald-50 border border-emerald-200 text-center space-y-3 shadow-sm animate-fade-in-up">
          <CheckCircle2 className="w-14 h-14 text-[#00D09C] mx-auto" />
          <h3 className="text-2xl font-black text-slate-900">Experience Report Published!</h3>
          <p className="text-xs text-slate-600">
            Thank you for contributing verified longitudinal data. Redirecting to device intelligence dashboard...
          </p>
        </div>
      ) : (
        <div className="hero-animate-cards">
          <OwnershipForm
            products={products}
            requestedBrand={requestedBrand}
            requestedProductId={requestedProductId}
            onSubmit={handleSubmit}
            isSubmitting={submitting}
          />
        </div>
      )}
    </div>
  );
}
