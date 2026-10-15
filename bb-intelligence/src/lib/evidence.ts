export type VerificationStatus = 'VERIFIED' | 'UNVERIFIED' | 'NEEDS_VERIFICATION' | 'CONTRADICTED';

export interface EvidenceRecordInput {
  claimId?: number;
  primaryUrl: string;
  sourceType?: string;
  excerpt?: string;
  directQuote?: string;
  author?: string;
  secondaryUrls?: string[];
}

export interface CalculatedVerification {
  status: VerificationStatus;
  corroborationScore: number;
  contradictionFlag: boolean;
  notes: string;
}

export function evaluateEvidenceStatus(
  corroborationCount: number,
  hasOfficialSource: boolean,
  hasContradictions: boolean
): CalculatedVerification {
  if (hasContradictions) {
    return {
      status: 'CONTRADICTED',
      corroborationScore: 20,
      contradictionFlag: true,
      notes: 'Contradictory sources detected during cross-reference analysis.'
    };
  }

  if (hasOfficialSource && corroborationCount >= 1) {
    return {
      status: 'VERIFIED',
      corroborationScore: 95,
      contradictionFlag: false,
      notes: 'Verified by official brand/retailer source and secondary confirmation.'
    };
  }

  if (corroborationCount >= 2) {
    return {
      status: 'VERIFIED',
      corroborationScore: 85,
      contradictionFlag: false,
      notes: 'Corroborated across multiple independent news/review sources.'
    };
  }

  if (corroborationCount === 1) {
    return {
      status: 'NEEDS_VERIFICATION',
      corroborationScore: 60,
      contradictionFlag: false,
      notes: 'Single source reporting. Additional evidence recommended before publishing.'
    };
  }

  return {
    status: 'UNVERIFIED',
    corroborationScore: 40,
    contradictionFlag: false,
    notes: 'Unverified single mention without secondary citation.'
  };
}
