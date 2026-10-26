import React, { useState } from 'react';
import { AnalysisResponse, AnalysisHistorySummary, ProviderItem } from '../types';
import { submitVerification } from '../api/client';
import { ProgressIndicator, Stage } from '../components/ProgressIndicator';
import { ProviderStatusBar } from '../components/ProviderStatusBar';
import { 
  Search, Link, FileText, Image as ImageIcon, Sparkles, 
  ArrowRight, AlertCircle, RefreshCw, X
} from 'lucide-react';

interface Props {
  onAnalysisComplete: (result: AnalysisResponse) => void;
  recentAnalyses: AnalysisHistorySummary[];
  onSelectRecent: (id: string) => void;
  providers: ProviderItem[];
}

export const DashboardPage: React.FC<Props> = ({
  onAnalysisComplete,
  recentAnalyses,
  onSelectRecent,
  providers,
}) => {
  const [url, setUrl] = useState('');
  const [headline, setHeadline] = useState('');
  const [articleText, setArticleText] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [stages, setStages] = useState<Stage[]>([]);
  const [stageText, setStageText] = useState<string>('');

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 5 * 1024 * 1024) {
        setErrorMessage('Image exceeds maximum allowed size (5MB).');
        return;
      }
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
      setErrorMessage(null);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
      setImagePreview(null);
    }
  };

  const loadPreset = (type: 'reputable' | 'debunked' | 'unverified') => {
    removeImage();
    setErrorMessage(null);
    if (type === 'reputable') {
      setUrl('https://www.reuters.com/business/healthcare-pharmaceuticals/who-end-covid-emergency-2023-05-05/');
      setHeadline('WHO declares end to COVID-19 as a global health emergency');
      setArticleText('The World Health Organization said Friday that Covid-19 no longer qualifies as a global health emergency, a major step toward the end of the pandemic.');
    } else if (type === 'debunked') {
      setUrl('');
      setHeadline('Drinking industrial bleach completely cures viral infections within 24 hours');
      setArticleText('SHOCKING TRUTH: Mainstream media and doctors hate this one secret cure! Miracle mineral solution eliminates all viruses instantly.');
    } else {
      setUrl('');
      setHeadline('Springfield community bakery wins state pastry championship');
      setArticleText('A small family bakery in downtown Springfield took home top honors at the annual culinary expo according to regional reports.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() && !headline.trim() && !articleText.trim()) {
      setErrorMessage('Please provide at least an article URL, a headline, or text content.');
      return;
    }

    setErrorMessage(null);
    setIsLoading(true);

    const initialStages: Stage[] = [
      { id: '1', label: 'Article URL & Content Ingestion', status: 'running' },
      { id: '2', label: 'Multimodal Image Verification', status: selectedImage ? 'pending' : 'skipped' },
      { id: '3', label: 'AI Text Stylometrics & Risk Modeling', status: 'pending' },
      { id: '4', label: 'Factual Claim Extraction', status: 'pending' },
      { id: '5', label: 'Live Google Fact Check Search', status: 'pending' },
      { id: '6', label: 'Live GDELT Global News Retrieval', status: 'pending' },
      { id: '7', label: 'Claim-Evidence Stance Matching', status: 'pending' },
      { id: '8', label: 'Source Credibility & Domain Transparency Scoring', status: 'pending' },
      { id: '9', label: 'Transparent Decision Fusion & Explanation', status: 'pending' },
    ];
    setStages(initialStages);
    setStageText('Validating input parameters and establishing secure connections...');

    // Simulate progressive stage tracking while API resolves
    const stageTimer = setInterval(() => {
      setStages((prev) => {
        const next = [...prev];
        const runningIdx = next.findIndex((s) => s.status === 'running');
        if (runningIdx !== -1 && runningIdx < next.length - 1) {
          next[runningIdx].status = 'completed';
          let nextIdx = runningIdx + 1;
          while (nextIdx < next.length && next[nextIdx].status === 'skipped') {
            nextIdx++;
          }
          if (nextIdx < next.length) {
            next[nextIdx].status = 'running';
            setStageText(`Executing: ${next[nextIdx].label}`);
          }
        }
        return next;
      });
    }, 450);

    try {
      const formData = new FormData();
      if (url.trim()) formData.append('url', url.trim());
      if (headline.trim()) formData.append('headline', headline.trim());
      if (articleText.trim()) formData.append('article_text', articleText.trim());
      if (selectedImage) formData.append('image', selectedImage);

      const result = await submitVerification(formData);
      clearInterval(stageTimer);

      // Mark all completed
      setStages((prev) =>
        prev.map((s) => ({ ...s, status: s.status === 'skipped' ? 'skipped' : 'completed' }))
      );
      setStageText('Analysis completed successfully. Rendering verification report...');
      setTimeout(() => {
        onAnalysisComplete(result);
      }, 350);
    } catch (err: any) {
      clearInterval(stageTimer);
      setIsLoading(false);
      setErrorMessage(err.message || 'An error occurred during verification.');
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Hero Header */}
      <div className="text-center max-w-3xl mx-auto mb-8">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-950/70 border border-blue-800/80 text-blue-300 text-xs font-mono mb-4">
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span>Evidence-Based Decision Support System</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-3">
          Real-Time Fake News & Claim Verification
        </h1>
        <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
          Submit any news URL, claim headline, full article text, or associated image. VeritasAI extracts factual assertions, queries live fact-checking databases, searches global news coverage, and fuses evidence transparently.
        </p>
      </div>

      {/* Provider Status */}
      <ProviderStatusBar providers={providers} />

      {/* Sample Presets */}
      <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
        <span className="text-xs text-slate-500 font-mono">Test Presets:</span>
        <button
          type="button"
          onClick={() => loadPreset('reputable')}
          className="text-xs px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
        >
          Corroborated News (Reuters)
        </button>
        <button
          type="button"
          onClick={() => loadPreset('debunked')}
          className="text-xs px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-red-300 hover:text-red-200 hover:border-red-800/50 transition-colors"
        >
          Debunked Medical Claim
        </button>
        <button
          type="button"
          onClick={() => loadPreset('unverified')}
          className="text-xs px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-amber-300 hover:text-amber-200 hover:border-amber-800/50 transition-colors"
        >
          Uncorroborated Local Story
        </button>
      </div>

      {/* Verification Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl mb-10">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Article URL */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center space-x-1.5">
              <Link className="w-3.5 h-3.5 text-blue-400" />
              <span>Article URL (Optional)</span>
            </label>
            <input
              type="url"
              placeholder="https://example.com/news/article-headline"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isLoading}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
            <p className="text-[11px] text-slate-500 mt-1.5">
              Protected by SSRF security filtering against private and loopback networks.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Headline */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                <span>Headline or Claim Statement</span>
              </label>
              <input
                type="text"
                placeholder="Enter the primary assertion or article headline"
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                disabled={isLoading}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>

            {/* Optional Image */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center space-x-1.5">
                <ImageIcon className="w-3.5 h-3.5 text-purple-400" />
                <span>Associated News Image (Optional)</span>
              </label>
              {!imagePreview ? (
                <label className="border border-dashed border-slate-800 hover:border-slate-700 bg-slate-950 rounded-xl p-3 flex items-center justify-center space-x-2 cursor-pointer transition-all">
                  <ImageIcon className="w-4 h-4 text-slate-500" />
                  <span className="text-xs text-slate-400">Upload JPEG, PNG, or WEBP (Max 5MB)</span>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleImageChange}
                    disabled={isLoading}
                    className="hidden"
                  />
                </label>
              ) : (
                <div className="flex items-center justify-between p-2 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="flex items-center space-x-3">
                    <img src={imagePreview} alt="Upload preview" className="w-10 h-10 object-cover rounded-lg" />
                    <span className="text-xs text-slate-300 truncate max-w-[160px]">{selectedImage?.name}</span>
                  </div>
                  <button
                    type="button"
                    onClick={removeImage}
                    disabled={isLoading}
                    className="p-1 rounded-md text-slate-400 hover:text-red-400 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Body Text */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center space-x-1.5">
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              <span>Article Text or Context (Optional if URL provided)</span>
            </label>
            <textarea
              rows={4}
              placeholder="Paste article body or additional context to extract checkable claims..."
              value={articleText}
              onChange={(e) => setArticleText(e.target.value)}
              disabled={isLoading}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-900/60 text-red-300 text-xs flex items-start space-x-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Verification Request Error</p>
                <p className="mt-0.5">{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Submit Action */}
          <div className="flex items-center justify-end space-x-4 pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-medium text-sm flex items-center space-x-2 transition-all shadow-lg shadow-blue-900/30"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Verifying Evidence...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Verify Claim & Evidence</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Progress Indicator */}
      {isLoading && (
        <ProgressIndicator stages={stages} currentStageText={stageText} />
      )}

      {/* Recent Analyses Table */}
      {recentAnalyses.length > 0 && !isLoading && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Recent System Analyses
            </h2>
            <span className="text-xs text-slate-500 font-mono">SQLite Audit Log</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400 font-mono">
                <tr>
                  <th className="pb-2.5 font-medium">Headline / Claim</th>
                  <th className="pb-2.5 font-medium">Domain</th>
                  <th className="pb-2.5 font-medium">Final Assessment</th>
                  <th className="pb-2.5 font-medium text-right">Latency</th>
                  <th className="pb-2.5 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {recentAnalyses.slice(0, 5).map((rec) => (
                  <tr key={rec.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 font-medium max-w-xs truncate pr-3 text-white">
                      {rec.headline}
                    </td>
                    <td className="py-3 text-slate-400 font-mono pr-3">
                      {rec.domain || 'N/A'}
                    </td>
                    <td className="py-3 pr-3">
                      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 border border-slate-700">
                        {rec.final_assessment}
                      </span>
                    </td>
                    <td className="py-3 text-right font-mono text-slate-400 pr-3">
                      {rec.total_latency_ms.toFixed(0)} ms
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => onSelectRecent(rec.id)}
                        className="text-blue-400 hover:text-blue-300 font-medium"
                      >
                        View Report
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
