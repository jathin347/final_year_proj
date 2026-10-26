import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { ReportPage } from './pages/ReportPage';
import { HistoryPage } from './pages/HistoryPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { 
  AnalysisResponse, 
  AnalysisHistorySummary, 
  ProviderItem 
} from './types';
import { 
  checkBackendHealth, 
  fetchProvidersStatus, 
  fetchHistory, 
  fetchAnalysisReport 
} from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'history' | 'methodology' | 'report'>('dashboard');
  const [currentReport, setCurrentReport] = useState<AnalysisResponse | null>(null);
  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisHistorySummary[]>([]);
  const [providers, setProviders] = useState<ProviderItem[]>([]);
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  // Load backend status and recent runs on initial mount
  const refreshAppData = async () => {
    try {
      const health = await checkBackendHealth();
      setIsBackendHealthy(health.status === 'ok');

      const provResp = await fetchProvidersStatus();
      setProviders(provResp.providers);

      const histResp = await fetchHistory(1, 5);
      setRecentAnalyses(histResp.items);
    } catch (e) {
      console.warn('Initial data load warning:', e);
      setIsBackendHealthy(false);
    }
  };

  useEffect(() => {
    refreshAppData();
  }, []);

  const handleAnalysisComplete = (result: AnalysisResponse) => {
    setCurrentReport(result);
    setActiveTab('report');
    // Refresh recent list
    refreshAppData();
  };

  const handleSelectRecent = async (id: string) => {
    try {
      const fullReport = await fetchAnalysisReport(id);
      setCurrentReport(fullReport);
      setActiveTab('report');
    } catch (err: any) {
      alert(`Could not load report: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
        }}
        isBackendHealthy={isBackendHealthy}
      />

      <main className="flex-1">
        {activeTab === 'dashboard' && (
          <DashboardPage
            onAnalysisComplete={handleAnalysisComplete}
            recentAnalyses={recentAnalyses}
            onSelectRecent={handleSelectRecent}
            providers={providers}
          />
        )}

        {activeTab === 'report' && currentReport && (
          <ReportPage
            report={currentReport}
            onBack={() => setActiveTab('dashboard')}
          />
        )}

        {activeTab === 'history' && (
          <HistoryPage
            onSelectRecord={handleSelectRecent}
          />
        )}

        {activeTab === 'methodology' && (
          <MethodologyPage />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>VeritasAI • Real-Time Evidence Verification Platform</span>
          <span>Google Fact Check • GDELT 2.0 • Gemini AI • SQLite Engine</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
