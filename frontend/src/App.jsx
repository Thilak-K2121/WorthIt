import React, { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import HomePage from './pages/HomePage';
import ProductListPage from './pages/ProductListPage';
import ProductDetailPage from './pages/ProductDetailPage';
import ComparePage from './pages/ComparePage';
import SubmitExperiencePage from './pages/SubmitExperiencePage';
import SuggestProductPage from './pages/SuggestProductPage';
import AdminDiscoveryPage from './pages/AdminDiscoveryPage';
import AboutTrustPage from './pages/AboutTrustPage';

function ScrollToTop() {
  const { pathname, search } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [pathname, search]);
  return null;
}

export default function App() {
  const location = useLocation();

  return (
    <div className="flex flex-col min-h-screen bg-white text-slate-900 selection:bg-[#00D09C] selection:text-white">
      <ScrollToTop />
      <Navbar />
      <main key={`${location.pathname}${location.search}`} className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 page-entrance">
        <Routes location={location}>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/products/:id" element={<ProductDetailPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/submit" element={<SubmitExperiencePage />} />
          <Route path="/suggest" element={<SuggestProductPage />} />
          <Route path="/admin" element={<AdminDiscoveryPage />} />
          <Route path="/about" element={<AboutTrustPage />} />
        </Routes>
      </main>
      {location.pathname === '/' && <Footer />}
    </div>
  );
}
