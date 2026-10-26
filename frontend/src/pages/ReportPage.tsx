import React from 'react';
import { AnalysisResponse } from '../types';
import { 
  ShieldCheck, AlertTriangle, XCircle, HelpCircle, CheckCircle, 
  ExternalLink, Clock, ArrowLeft, Cpu, Globe, Search, Layers, Image as ImageIcon
} from 'lucide-react';

interface Props {
  report: AnalysisResponse;
  onBack: () => void;
}

export const ReportPage: React.FC<Props> = ({ report, onBack }) => {
  // Format verdict styling
  const getVerdictBadge = (verdict: string) => {
    switch (verdict) {
      case 'Supported by available evidence':
        return {
          bg: 'bg-emerald-950/80 border-emerald-700/80 text-emerald-300',
          icon: <CheckCircle className="w-5 h-5 text-emerald-400" />
        };
      case 'Contradicted by available evidence':
        return {
          bg: 'bg-red-950/80 border-red-700/80 text-red-300',
          icon: <XCircle className="w-5 h-5 text-red-400" />
        };
      case 'Misleading or missing context':
        return {
          bg: 'bg-amber-950/80 border-amber-700/80 text-amber-300',
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />
        };
      case 'Conflicting evidence':
        return {
          bg: 'bg-purple-950/80 border-purple-700/80 text-purple-300',
          icon: <HelpCircle className="w-5 h-5 text-purple-400" />
        };
      case 'Insufficient evidence':
      default:
        return {
          bg: 'bg-slate-900 border-slate-700 text-slate-300',
          icon: <HelpCircle className="w-5 h-5 text-slate-400" />
        };
    }
  };

  const badge = getVerdictBadge(report.final_assessment);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Back button and metadata header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="text-xs font-mono text-slate-400 hover:text-white flex items-center space-x-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>
        <div className="flex items-center space-x-3 text-xs font-mono text-slate-500">
          <span>Analysis ID: {report.id.slice(0, 8)}</span>
          <span>•</span>
          <span>Latency: {report.total_latency_ms.toFixed(0)} ms</span>
        </div>
      </div>

      {/* Main Verdict Hero Card */}
      <div className={`p-6 sm:p-8 rounded-2xl border ${badge.bg} shadow-2xl relative overflow-hidden`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 flex-1">
            <div className="flex items-center space-x-2.5">
              {badge.icon}
              <span className="font-mono text-xs uppercase tracking-wider font-semibold">
                Epistemic Verdict: {report.final_assessment}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-900/60 border border-slate-700 text-slate-300 font-mono">
                Uncertainty: {report.uncertainty_level}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {report.headline}
            </h1>
            <p className="text-slate-200 text-sm sm:text-base leading-relaxed">
              {report.assessment_explanation}
            </p>
          </div>

          {/* Quick Stats Panel */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 min-w-[200px] space-y-2.5 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Coverage:</span>
              <span className="text-white font-medium">{report.decision_fusion.evidence_coverage}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Fact-Checks:</span>
              <span className="text-white font-medium">{report.fact_checks.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">News Reports:</span>
              <span className="text-white font-medium">{report.news_articles.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Source Score:</span>
              <span className="text-white font-medium">
                {report.source_credibility.overall_score !== null && report.source_credibility.overall_score !== undefined
                  ? `${report.source_credibility.overall_score}/100`
                  : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Article Origin link */}
        {report.article_url && (
          <div className="mt-4 pt-4 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-300">
            <span className="truncate max-w-md">Source URL: {report.article_url}</span>
            <a
              href={report.article_url}
              target="_blank"
              rel="noreferrer"
              className="text-blue-400 hover:text-blue-300 flex items-center space-x-1 font-medium ml-2 shrink-0"
            >
              <span>Visit Original Article</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        )}
      </div>

      {/* Grid: Extracted Claims & Source Credibility */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Extracted Claims (2 Columns) */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                Extracted Checkable Factual Claims ({report.claims.length})
              </h2>
            </div>
            <span className="text-xs text-slate-500 font-mono">Pydantic Validated</span>
          </div>

          {report.claims.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No discrete factual assertions identified in the text.</p>
          ) : (
            <div className="space-y-4">
              {report.claims.map((claim, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800/90 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-900">
                      Claim {idx + 1} • {claim.category}
                    </span>
                    <span
                      className={`text-[11px] font-mono px-2 py-0.5 rounded border ${
                        claim.verification_status === 'SUPPORTED'
                          ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                          : claim.verification_status === 'CONTRADICTED'
                          ? 'bg-red-950 text-red-300 border-red-800'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {claim.verification_status}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-slate-100">{claim.claim_text}</p>
                  {claim.explanation && (
                    <p className="text-xs text-slate-400 leading-relaxed">{claim.explanation}</p>
                  )}
                  {claim.named_entities.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {claim.named_entities.map((ent, eIdx) => (
                        <span key={eIdx} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                          {ent}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Source Credibility Gauge (1 Column) */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-indigo-400" />
                <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                  Source Credibility
                </h2>
              </div>
              <span className="text-xs font-mono text-slate-500">Heuristic Signals</span>
            </div>

            <div className="text-center py-4 bg-slate-950 rounded-xl border border-slate-800 mb-4">
              <span className="text-4xl font-extrabold text-white font-mono">
                {report.source_credibility.overall_score !== null && report.source_credibility.overall_score !== undefined
                  ? `${report.source_credibility.overall_score}`
                  : 'N/A'}
              </span>
              <span className="text-xs text-slate-500 font-mono block mt-1">
                Score (0 to 100) • {report.source_credibility.assessment_status}
              </span>
            </div>

            {/* Factors list */}
            <div className="space-y-2 text-xs">
              {report.source_credibility.factors.map((f, fIdx) => (
                <div key={fIdx} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
                  <div className="flex justify-between font-medium text-slate-300">
                    <span>{f.factor_name}</span>
                    <span className="font-mono">{f.score.toFixed(0)}/100</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{f.description}</p>
                </div>
              ))}
            </div>

            {report.source_credibility.missing_signals.length > 0 && (
              <div className="mt-4 p-2.5 rounded-lg bg-amber-950/30 border border-amber-900/40 text-[11px] text-amber-300/90 space-y-1">
                <span className="font-semibold block">Missing Source Signals:</span>
                <ul className="list-disc pl-4 space-y-0.5">
                  {report.source_credibility.missing_signals.map((m, mIdx) => (
                    <li key={mIdx}>{m}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <p className="text-[10px] text-slate-500 mt-4 leading-tight italic">
            {report.source_credibility.disclaimer}
          </p>
        </div>
      </div>

      {/* Grid: Fact Check Reviews & Live News Coverage */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Published Fact-Checks */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                Published Fact-Check Reviews ({report.fact_checks.length})
              </h2>
            </div>
            <span className="text-xs text-slate-500 font-mono">Google Fact Check API</span>
          </div>

          {report.fact_checks.length === 0 ? (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
              <p className="font-medium text-slate-300">No matching published fact-check was found.</p>
              <p className="text-slate-500">The absence of a fact-check does not establish that the claim is true or false.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {report.fact_checks.map((fc, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-300">{fc.fact_checker_publisher}</span>
                    <span
                      className={`text-[11px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                        fc.normalized_verdict === 'FALSE'
                          ? 'bg-red-950 text-red-300 border border-red-800'
                          : fc.normalized_verdict === 'TRUE'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}
                    >
                      {fc.original_rating}
                    </span>
                  </div>
                  <h3 className="text-xs font-medium text-white">{fc.review_title}</h3>
                  <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                    <span>{fc.publication_date || 'Date unavailable'}</span>
                    <a
                      href={fc.review_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                    >
                      <span>Read Fact-Check</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live News Search */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Globe className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                Corroborating News Coverage ({report.news_articles.length})
              </h2>
            </div>
            <span className="text-xs text-slate-500 font-mono">GDELT 2.0 Global News</span>
          </div>

          {report.news_articles.length === 0 ? (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
              <p className="font-medium text-slate-300">No matching independent news articles retrieved.</p>
              <p className="text-slate-500">Story may be local, hyper-recent, or fabricated.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {report.news_articles.map((na, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-slate-400">{na.publisher}</span>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded capitalize ${
                        na.stance === 'supporting'
                          ? 'bg-emerald-950/70 text-emerald-300'
                          : na.stance === 'contradicting'
                          ? 'bg-red-950/70 text-red-300'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {na.stance}
                    </span>
                  </div>
                  <h3 className="text-xs font-medium text-white">{na.title}</h3>
                  <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                    <span>{na.publication_date || 'Recent'}</span>
                    <a
                      href={na.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                    >
                      <span>Visit Outlet</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Grid: AI Model Cues & Multimodal Findings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Text Model Attribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-purple-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                AI Text Stylometrics ({report.text_analysis.model_name})
              </h2>
            </div>
            <span className="text-xs font-mono text-slate-500">
              {report.text_analysis.inference_time_ms.toFixed(1)} ms
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Stylistic Classification:</span>
              <span className="font-semibold text-white">{report.text_analysis.prediction}</span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Classifier Confidence:</span>
              <span className="font-mono text-white">{(report.text_analysis.confidence * 100).toFixed(1)}%</span>
            </div>

            {report.text_analysis.key_attribution_tokens.length > 0 && (
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-slate-400 font-medium block">Key Contributing Linguistic Tokens:</span>
                <div className="flex flex-wrap gap-1.5">
                  {report.text_analysis.key_attribution_tokens.map((tok, tIdx) => (
                    <span
                      key={tIdx}
                      className={`font-mono text-[11px] px-2 py-0.5 rounded border ${
                        tok.indicator_type === 'risk_indicator'
                          ? 'bg-red-950/70 border-red-800 text-red-300'
                          : 'bg-emerald-950/70 border-emerald-800 text-emerald-300'
                      }`}
                    >
                      {tok.token} ({tok.attribution_weight > 0 ? `+${tok.attribution_weight}` : tok.attribution_weight})
                    </span>
                  ))}
                </div>
              </div>
            )}

            <p className="text-[11px] text-slate-500 italic mt-2">
              {report.text_analysis.limitations}
            </p>
          </div>
        </div>

        {/* Multimodal Image Findings */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <ImageIcon className="w-4 h-4 text-purple-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                Multimodal Image Analysis
              </h2>
            </div>
            <span className="text-xs font-mono text-slate-500">PIL & Vision Verification</span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Image Attached:</span>
                <span className="font-mono text-white">{report.image_analysis.has_image ? 'Yes' : 'No'}</span>
              </div>
              {report.image_analysis.has_image && (
                <>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Format & Dimensions:</span>
                    <span className="font-mono text-white">
                      {report.image_analysis.image_format} ({report.image_analysis.image_dimensions})
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Image-Text Relevance:</span>
                    <span className="font-mono text-emerald-400">
                      {report.image_analysis.image_text_relevance_score
                        ? `${(report.image_analysis.image_text_relevance_score * 100).toFixed(0)}%`
                        : 'N/A'}
                    </span>
                  </div>
                </>
              )}
            </div>

            <p className="text-xs text-slate-300 leading-relaxed p-3 rounded-xl bg-slate-950 border border-slate-800">
              {report.image_analysis.visual_context_summary}
            </p>

            <p className="text-[11px] text-slate-500 italic mt-2">
              {report.image_analysis.limitations}
            </p>
          </div>
        </div>
      </div>

      {/* Latency Breakdown Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between text-xs font-mono text-slate-400 gap-4">
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-blue-400" />
          <span className="text-white font-medium">Pipeline Timing Breakdown:</span>
        </div>
        <div className="flex flex-wrap gap-4 text-[11px]">
          {Object.entries(report.latency_breakdown_ms).map(([stage, ms], idx) => (
            <span key={idx}>
              <span className="text-slate-500">{stage.replace('_ms', '')}:</span>{' '}
              <span className="text-slate-200">{ms.toFixed(0)}ms</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
