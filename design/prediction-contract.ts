/** Design sketch only: no provider integration or deployment is claimed. */
export type EvidenceRef = { id: string; source: 'creator_input' | 'verified_import' | 'simulation'; version: string };
export type Decision =
  | { status: 'abstain'; reason: 'unsupported_language' | 'insufficient_evidence' | 'invalid_output'; missing: string[] }
  | { status: 'ok'; ranking: string[]; evidence: EvidenceRef[];
      // Populate only if the model contract defines a calibrated probability target.
      probability?: { event: string; value: number; calibration_version: string } };
export interface PredictionEnvelope {
  run_id: string;
  input_hash: string;
  contract_version: string;
  prompt_version: string;
  provider: string;
  model: string;
  model_version: string | null;
  audience_version: string;
  decision: Decision;
  attempt: number;
  latency_ms: number;
  usage: { input_tokens: number | null; output_tokens: number | null; cost_usd: number | null };
  raw_output_ref: string;
  created_at: string;
}
// Unknown usage is null, never zero. Persist every failed attempt and final selection.
// Validate finite probability in [0,1], known variant IDs, unique rank entries and
// referenced evidence ownership before accepting an adapter's output.
// A ranking preference is not a CTR estimate; never reinterpret it as one.
