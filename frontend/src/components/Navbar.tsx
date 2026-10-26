import React from 'react';
import { ShieldCheck, History, BookOpen, ExternalLink, Activity } from 'lucide-react';

interface NavbarProps {
  activeTab: 'dashboard' | 'history' | 'methodology' | 'report';
  setActiveTab: (tab: 'dashboard' | 'history' | 'methodology') => void;
  isBackendHealthy: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, isBackendHealthy }) => {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          className="flex items-center space-x-3 cursor-pointer group"
          onClick={() => setActiveTab('dashboard')}
        >
          <div className="p-2 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 group-hover:bg-blue-600/30 transition-all">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-white">Veritas<span className="text-blue-400">AI</span></span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                v1.2
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Multimodal News Verification & Source Credibility Engine</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === 'dashboard' || activeTab === 'report'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Activity className="w-4 h-4 text-blue-400" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === 'history'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <History className="w-4 h-4 text-purple-400" />
            <span>History</span>
          </button>

          <button
            onClick={() => setActiveTab('methodology')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === 'methodology'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <BookOpen className="w-4 h-4 text-emerald-400" />
            <span className="hidden sm:inline">Methodology</span>
            <span className="sm:hidden">Docs</span>
          </button>

          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="px-2.5 py-1.5 rounded-md text-xs font-mono text-slate-400 hover:text-slate-200 hover:bg-slate-900 flex items-center space-x-1 transition-colors border border-slate-800"
            title="OpenAPI Swagger Documentation"
          >
            <span>API</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </nav>

        {/* Live Backend Indicator */}
        <div className="hidden md:flex items-center space-x-2 text-xs font-mono">
          <span className={`w-2 h-2 rounded-full ${isBackendHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
          <span className="text-slate-400">{isBackendHealthy ? 'API Connected' : 'Connecting API...'}</span>
        </div>
      </div>
    </header>
  );
};
