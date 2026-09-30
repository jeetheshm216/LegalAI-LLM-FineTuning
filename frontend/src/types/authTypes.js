/**
 * authTypes.js
 * 
 * Domain types, enums, and constants for LegalAI Authentication &
 * Professional Advocate Verification.
 */

export const AuthState = {
  INITIALIZING: 'initializing',
  UNAUTHENTICATED: 'unauthenticated',
  AUTHENTICATED: 'authenticated',
  PROFESSIONAL_VERIFICATION_PENDING: 'professional_verification_pending',
  PROFESSIONAL_VERIFICATION_FAILED: 'professional_verification_failed',
  PROFESSIONAL_VERIFICATION_REVIEW: 'professional_verification_review',
  VERIFIED: 'verified',
  TWO_FACTOR_REQUIRED: 'two_factor_required',
  AUTHORIZED: 'authorized'
};

export const VerificationStatus = {
  PENDING: 'PENDING',
  VERIFIED: 'VERIFIED',
  NEEDS_REVIEW: 'NEEDS_REVIEW',
  FAILED: 'FAILED'
};

export const UserRole = {
  LAWYER: 'LAWYER',
  ADMIN: 'ADMIN',
  VERIFICATION_REVIEWER: 'VERIFICATION_REVIEWER'
};

export const STATE_BAR_COUNCILS = [
  'Bar Council of Tamil Nadu & Puducherry',
  'Bar Council of Delhi',
  'Bar Council of Maharashtra & Goa',
  'Bar Council of Karnataka',
  'Bar Council of West Bengal',
  'Bar Council of Kerala',
  'Bar Council of Uttar Pradesh',
  'Bar Council of Gujarat',
  'Bar Council of Punjab & Haryana',
  'Bar Council of Andhra Pradesh',
  'Bar Council of Telangana',
  'Bar Council of Rajasthan',
  'Bar Council of Madhya Pradesh',
  'Bar Council of Bihar'
];
