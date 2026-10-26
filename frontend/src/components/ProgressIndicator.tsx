import React from 'react';
import { Loader2, CheckCircle2, Circle } from 'lucide-react';

export interface Stage {
  id: string;
  label: string;
  status: 'pending' | 'running' | 'completed' | 'skipped';
}

interface Props {
  stages: Stage[];
  currentStageText?: string;
}

export const ProgressIndicator: React.FC<Props> = ({ stages, currentStageText }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 my-6 shadow-xl">
      <div className="flex items-center space-x-3 mb-4">
        <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
        <h3 className="text-base font-semibold text-white">
          Executing Verification Pipeline...
        </h3>
      </div>
      {currentStageText && (
        <p className="text-xs text-blue-300 font-mono mb-6 bg-blue-950/40 border border-blue-900/50 rounded-lg px-3 py-2">
          {currentStageText}
        </p>
      )}

      <div className="space-y-3">
        {stages.map((stage, idx) => (
          <div key={stage.id} className="flex items-center space-x-3 text-sm">
            {stage.status === 'completed' && (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            )}
            {stage.status === 'running' && (
              <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
            )}
            {stage.status === 'pending' && (
              <Circle className="w-4 h-4 text-slate-600 shrink-0" />
            )}
            {stage.status === 'skipped' && (
              <Circle className="w-4 h-4 text-slate-500 shrink-0 opacity-40" />
            )}

            <span
              className={`font-mono text-xs ${
                stage.status === 'running'
                  ? 'text-blue-300 font-semibold'
                  : stage.status === 'completed'
                  ? 'text-slate-300'
                  : 'text-slate-500'
              }`}
            >
              Step {idx + 1}: {stage.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
