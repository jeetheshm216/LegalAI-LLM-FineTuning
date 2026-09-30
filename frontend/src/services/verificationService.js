/**
 * verificationService.js
 * 
 * Professional Advocate Verification Service Abstraction.
 * 
 * In production, this service connects to authorized State Bar Council APIs
 * or certified identity providers.
 * 
 * DISCLAIMER:
 * Prototype verification — official Bar Council integration required for production.
 * Do not claim connection to real government or statutory bodies in prototype mode.
 */

import { VerificationStatus } from '../types/authTypes.js';

export const PROTOTYPE_DISCLAIMER =
  'Prototype verification — official Bar Council integration required for production.';

// Known prototype records for demonstration and automated testing
const PROTOTYPE_ADVOCATES = [
  {
    fullName: 'Elena Vance',
    stateBarCouncil: 'Bar Council of Tamil Nadu & Puducherry',
    enrollmentNumber: 'TN/1942/2018',
    status: VerificationStatus.VERIFIED
  },
  {
    fullName: 'Elena Vance',
    stateBarCouncil: 'Bar Council of Delhi',
    enrollmentNumber: 'NY-BAR-481920',
    status: VerificationStatus.VERIFIED
  },
  {
    fullName: 'Rajesh Kumar',
    stateBarCouncil: 'Bar Council of Delhi',
    enrollmentNumber: 'D/3819/2015',
    status: VerificationStatus.VERIFIED
  },
  {
    fullName: 'Priya Sharma',
    stateBarCouncil: 'Bar Council of Maharashtra & Goa',
    enrollmentNumber: 'MAH/5120/2017',
    status: VerificationStatus.VERIFIED
  },
  {
    fullName: 'K. Swaminathan',
    stateBarCouncil: 'Bar Council of Tamil Nadu & Puducherry',
    enrollmentNumber: 'TN/4012/2010',
    status: VerificationStatus.VERIFIED
  },
  {
    fullName: 'Arun Verma',
    stateBarCouncil: 'Bar Council of Delhi',
    enrollmentNumber: 'D/9999/REVIEW',
    status: VerificationStatus.NEEDS_REVIEW
  }
];

class MockVerificationProvider {
  name = 'Prototype Verification Provider';

  async verify({ fullName, stateBarCouncil, enrollmentNumber }) {
    // Simulate network latency of credential lookup
    await new Promise((resolve) => setTimeout(resolve, 600));

    const cleanEnrollment = (enrollmentNumber || '').trim().toUpperCase();
    const cleanName = (fullName || '').trim().toLowerCase();

    // Check for explicit review keyword or format
    if (cleanEnrollment.includes('REVIEW') || cleanEnrollment.endsWith('REV')) {
      return {
        status: VerificationStatus.NEEDS_REVIEW,
        verifiedName: fullName,
        stateBarCouncil,
        enrollmentNumber: cleanEnrollment,
        provider: this.name,
        verifiedAt: new Date().toISOString(),
        disclaimer: PROTOTYPE_DISCLAIMER,
        message: 'Your professional credentials require manual verification.'
      };
    }

    // Match against known prototype records
    const match = PROTOTYPE_ADVOCATES.find(
      (adv) =>
        adv.enrollmentNumber.toUpperCase() === cleanEnrollment &&
        (!stateBarCouncil || adv.stateBarCouncil === stateBarCouncil)
    );

    if (match) {
      // Use user-provided name if available, fallback to mock record name
      const effectiveName = (fullName && fullName.trim().length > 0) ? fullName.trim() : match.fullName;
      return {
        status: match.status,
        verifiedName: effectiveName,
        stateBarCouncil: stateBarCouncil || match.stateBarCouncil,
        enrollmentNumber: cleanEnrollment,
        provider: this.name,
        verifiedAt: new Date().toISOString(),
        disclaimer: PROTOTYPE_DISCLAIMER,
        message: 'Advocate identity verified against Bar roll.'
      };
    }

    // Also support any well-formed Indian bar enrolment pattern for flexible demoing:
    // e.g., STATE_CODE/NUMBER/YEAR (like TN/1942/2018, D/3819/2015, MAH/5120/2017) or any valid number
    const indianEnrollmentRegex = /^[A-Z]{1,4}\/\d{1,6}\/\d{2,4}$/;
    if ((indianEnrollmentRegex.test(cleanEnrollment) || cleanEnrollment.length >= 5) && cleanName.length >= 2) {
      return {
        status: VerificationStatus.VERIFIED,
        verifiedName: fullName.trim(),
        stateBarCouncil: stateBarCouncil || 'State Bar Council',
        enrollmentNumber: cleanEnrollment,
        provider: this.name,
        verifiedAt: new Date().toISOString(),
        disclaimer: PROTOTYPE_DISCLAIMER,
        message: 'Advocate credentials successfully verified.'
      };
    }

    // Not found
    return {
      status: VerificationStatus.FAILED,
      verifiedName: null,
      stateBarCouncil,
      enrollmentNumber: cleanEnrollment,
      provider: this.name,
      verifiedAt: null,
      disclaimer: PROTOTYPE_DISCLAIMER,
      message: "We couldn't verify the professional credentials provided. Please check the enrollment number and state bar council."
    };
  }
}

export const verificationService = {
  provider: new MockVerificationProvider(),

  /**
   * Pluggable provider setter for future official Bar Council API integration
   */
  setProvider(newProvider) {
    this.provider = newProvider;
  },

  async verifyAdvocate({ fullName, stateBarCouncil, enrollmentNumber }) {
    return this.provider.verify({ fullName, stateBarCouncil, enrollmentNumber });
  }
};
