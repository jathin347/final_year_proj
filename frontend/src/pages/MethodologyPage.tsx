import React from 'react';
import { BookOpen, ShieldCheck, Scale, Cpu, Search, AlertTriangle, Layers, Globe } from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-10">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-950/70 border border-blue-800/80 text-blue-300 text-xs font-mono mb-3">
          <BookOpen className="w-3.5 h-3.5 text-blue-400" />
          <span>Technical Transparency Documentation</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          System Architecture, Methodology & Epistemic Boundaries
        </h1>
        <p className="text-slate-400 text-sm mt-2 leading-relaxed">
          VeritasAI is an investigative decision-support platform designed to counter misinformation by uniting linguistic AI modeling with genuine live evidence retrieval.
        </p>
      </div>

      {/* Epistemic Principle Alert */}
      <div className="p-5 rounded-2xl bg-amber-950/30 border border-amber-900/50 text-amber-200/90 text-xs leading-relaxed space-y-2">
        <div className="flex items-center space-x-2 font-bold text-amber-300 text-sm">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>Core Principle: AI Prediction vs. Factual Grounding</span>
        </div>
        <p>
          A machine-learning classifier evaluates stylistic, rhetorical, and syntactical patterns associated with misinformation. However, <strong>no language model can independently certify real-world truth</strong>. An article written in sensationalist phrasing might describe a real disaster, while a carefully phrased deceptive article might sound perfectly objective. VeritasAI explicitly separates AI text classification from live external evidence retrieval.
        </p>
      </div>

      {/* Pipeline Sections */}
      <div className="space-y-8 text-sm">
        {/* Section 1: Ingestion & Security */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            <h2>1. Article Ingestion & SSRF Protection</h2>
          </div>
          <p className="text-slate-300 text-xs leading-relaxed">
            When an article URL is submitted, the system verifies the URL scheme (<code className="text-blue-300 font-mono">http/https</code>) and performs forward DNS resolution to validate destination IP addresses. It strictly blocks private RFC 1918 networks, loopback addresses (<code className="text-blue-300 font-mono">127.0.0.0/8</code>), cloud metadata addresses (<code className="text-blue-300 font-mono">169.254.169.254</code>), and IPv6 link-locals to prevent Server-Side Request Forgery (SSRF). Content streams are bounded to 10MB with strict timeouts.
          </p>
        </div>

        {/* Section 2: Claim Extraction */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <Layers className="w-4 h-4 text-purple-400" />
            <h2>2. Factual Claim Extraction Engine</h2>
          </div>
          <p className="text-slate-300 text-xs leading-relaxed">
            News articles often combine opinion, background, and specific factual assertions. The claim extraction service isolates verifiable, checkable statements. When configured, Google Gemini API structures assertions into Pydantic models. If unconfigured or offline, an internal rule-based NLP extractor scores sentences based on named entities, quantitative data, temporal references, and assertive verb predicates to generate targeted search queries.
          </p>
        </div>

        {/* Section 3: Evidence Retrieval */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <Search className="w-4 h-4 text-emerald-400" />
            <h2>3. Multi-Channel Evidence Retrieval</h2>
          </div>
          <p className="text-slate-300 text-xs leading-relaxed">
            External evidence is gathered via two independent pathways:
          </p>
          <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1.5">
            <li>
              <strong>Google Fact Check Tools API:</strong> Queries the global repository of schema.org <code className="text-emerald-300 font-mono">ClaimReview</code> records published by verified fact-checkers (PolitiFact, Snopes, FactCheck.org, AFP, Reuters Fact Check). Original publisher ratings are preserved verbatim.
            </li>
            <li>
              <strong>GDELT Project 2.0 Global News API:</strong> Live REST queries against global news archives to identify corroborating or disputing coverage, with cross-outlet title similarity deduplication to filter syndicated reprints.
            </li>
          </ul>
        </div>

        {/* Section 4: Source Credibility */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <Globe className="w-4 h-4 text-indigo-400" />
            <h2>4. Heuristic Source Credibility Scoring</h2>
          </div>
          <p className="text-slate-300 text-xs leading-relaxed">
            The source assessment module calculates a transparent 0–100 heuristic index based only on observable signals:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-semibold text-slate-200">Domain Track Record (40%)</span>
              <p className="text-slate-400 mt-1">Cross-referenced against verified news registries and catalogued satire/discredited domains.</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-semibold text-slate-200">TLD & Domain Integrity (25%)</span>
              <p className="text-slate-400 mt-1">Institutional verification (.gov, .edu) vs low-reputation disposable TLDs and typo-squatting checks.</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-semibold text-slate-200">Author Attribution (20%)</span>
              <p className="text-slate-400 mt-1">Presence of explicit editorial bylines and journalist attribution.</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-semibold text-slate-200">Publisher Transparency (15%)</span>
              <p className="text-slate-400 mt-1">Clear self-identification and imprint transparency.</p>
            </div>
          </div>
        </div>

        {/* Section 5: Decision Fusion */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <Scale className="w-4 h-4 text-amber-400" />
            <h2>5. Epistemic Decision Fusion Hierarchy</h2>
          </div>
          <p className="text-slate-300 text-xs leading-relaxed">
            The system synthesizes all signals through an explicit, documented rule hierarchy:
          </p>
          <ol className="list-decimal pl-5 text-xs text-slate-300 space-y-1">
            <li><strong>Rule 1 (Fact-Check Refutation):</strong> If accredited fact-checkers rated the claim FALSE, the verdict is <em>Contradicted by available evidence</em> with Low uncertainty.</li>
            <li><strong>Rule 2 (Discredited Source):</strong> If the domain is documented satire or conspiracy, the verdict is <em>Misleading or missing context</em>.</li>
            <li><strong>Rule 3 (Fact-Check Affirmation):</strong> Corroborated by accredited fact-checks → <em>Supported by available evidence</em>.</li>
            <li><strong>Rule 4 (Multimodal Conflict):</strong> Image properties contradict claimed scene timing → <em>Misleading or missing context</em>.</li>
            <li><strong>Rule 5 (Conflicting Coverage):</strong> Opposing evidence streams → <em>Conflicting evidence</em>.</li>
            <li><strong>Rule 6 (Multi-Source News Corroboration):</strong> Multiple independent reputable outlets confirm → <em>Supported by available evidence</em>.</li>
            <li><strong>Rule 7 (Missing Evidence Abstention):</strong> If zero external records exist, the system returns <em>Insufficient evidence</em>. The system never forces an unverified statement into Real or Fake.</li>
          </ol>
        </div>

        {/* System Limitations */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <h2>6. Documented Limitations</h2>
          </div>
          <ul className="list-disc pl-5 text-xs text-slate-400 space-y-1.5 leading-relaxed">
            <li><strong>On-demand verification:</strong> The engine inspects articles submitted by users; it does not passively monitor the entire global web in real time.</li>
            <li><strong>Absence of Evidence:</strong> Unreported or hyper-local events will yield <em>Insufficient evidence</em> rather than a definitive confirmation.</li>
            <li><strong>Deepfake Detection:</strong> Image analysis measures image-text visual consistency; it does not certify cryptographic authenticity or detect GAN/diffusion artifacts without a dedicated forensic model.</li>
            <li><strong>Language Coverage:</strong> Primary parsing, claim extraction, and stylometric weights are calibrated for English-language news.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
