import {
  AnalysisResponse,
  PaginatedHistoryResponse,
  ProviderItem
} from '../types';

const API_BASE = '/api';

export async function checkBackendHealth(): Promise<{ status: string; version: string; database: string }> {
  const resp = await fetch(`${API_BASE}/health`);
  if (!resp.ok) {
    throw new Error(`Health check failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function fetchProvidersStatus(): Promise<{ providers: ProviderItem[] }> {
  const resp = await fetch(`${API_BASE}/providers/status`);
  if (!resp.ok) {
    throw new Error(`Failed to load providers status`);
  }
  return resp.json();
}

export async function submitVerification(formData: FormData): Promise<AnalysisResponse> {
  const resp = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({ detail: `HTTP error ${resp.status}` }));
    throw new Error(errorData.detail || `Verification failed (${resp.status})`);
  }

  return resp.json();
}

export async function fetchAnalysisReport(id: string): Promise<AnalysisResponse> {
  const resp = await fetch(`${API_BASE}/analyses/${id}`);
  if (!resp.ok) {
    throw new Error(`Analysis report '${id}' not found`);
  }
  return resp.json();
}

export async function fetchHistory(page = 1, pageSize = 10): Promise<PaginatedHistoryResponse> {
  const resp = await fetch(`${API_BASE}/history?page=${page}&page_size=${pageSize}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch history`);
  }
  return resp.json();
}

export async function deleteHistoryRecord(id: string): Promise<void> {
  const resp = await fetch(`${API_BASE}/history/${id}`, {
    method: 'DELETE',
  });
  if (!resp.ok) {
    throw new Error(`Failed to delete record ${id}`);
  }
}
