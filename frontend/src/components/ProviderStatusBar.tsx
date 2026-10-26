import React from 'react';
import { ProviderItem } from '../types';
import { CheckCircle2, AlertCircle, Cpu, Globe, Search, Layers, Image as ImageIcon } from 'lucide-react';

interface Props {
  providers: ProviderItem[];
}

export const ProviderStatusBar: React.FC<Props> = ({ providers }) => {
  const getIcon = (name: string) => {
    if (name.includes('Gemini')) return <Cpu className="w-3.5 h-3.5 text-blue-400" />;
    if (name.includes('Fact Check')) return <Search className="w-3.5 h-3.5 text-emerald-400" />;
    if (name.includes('GDELT')) return <Globe className="w-3.5 h-3.5 text-indigo-400" />;
    if (name.includes('Vision') || name.includes('Image')) return <ImageIcon className="w-3.5 h-3.5 text-purple-400" />;
    return <Layers className="w-3.5 h-3.5 text-amber-400" />;
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3 sm:p-4 mb-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Integrated Verification Providers & Engine Status
        </h3>
        <span className="text-[11px] text-slate-500 font-mono">Live Configuration</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
        {providers.map((p, idx) => (
          <div 
            key={idx}
            className="flex items-start space-x-2.5 p-2 rounded-lg bg-slate-950/50 border border-slate-800/80 text-xs"
          >
            <div className="mt-0.5">{getIcon(p.name)}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-medium text-slate-200 truncate">{p.name}</span>
                {p.configured ? (
                  <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0 ml-1" />
                ) : (
                  <AlertCircle className="w-3 h-3 text-amber-400 shrink-0 ml-1" />
                )}
              </div>
              <p className="text-[10px] text-slate-400 truncate mt-0.5" title={p.status}>
                {p.status}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
