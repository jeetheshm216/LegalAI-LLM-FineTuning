# LegalAI — Secure Lawyer Authentication & Professional Verification

## Architecture Overview
LegalAI is a dedicated workspace for verified legal professionals. It implements a strict, multi-layered security architecture:

```text
Email & Password Login (Supabase Auth)
                 │
                 ▼
        Authenticated User
                 │
                 ▼
    Professional Bar Verification
    (State Bar Council + Enrollment No.)
                 │
                 ▼
         Verification Provider
                 │
                 ▼
    Two-Factor Authentication (2FA)
                 │
                 ▼
        AUTHORIZED Session
                 │
                 ▼
       LegalAI Chambers Dashboard
```

---

## Security Principles

1. **Authentication != Authorization**:
   Successfully signing in with an email and password proves account ownership, but does **not** grant access to chambers case records, client documents, or AI tools.
2. **Professional Verification Barrier**:
   Every advocate must be verified against their State Bar Council roll. Until verified, the account remains in `verification_status: PENDING` and cannot view privileged legal work product.
3. **Dual-Factor Security (2FA)**:
   A 6-digit TOTP challenge is required for chambers access.

---

## Authorization States

| State | Description |
|---|---|
| `UNAUTHENTICATED` | User is not logged in; displays `LoginScreen`. |
| `AUTHENTICATED` | Email/password validated, awaiting professional Bar verification. |
| `PROFESSIONAL_VERIFICATION_PENDING` | Bar credentials awaiting verification; dashboard remains inaccessible. |
| `PROFESSIONAL_VERIFICATION_REVIEW` | Credentials require manual Bar Council review. |
| `PROFESSIONAL_VERIFICATION_FAILED` | Credentials failed verification against Bar rolls. |
| `TWO_FACTOR_REQUIRED` | Advocate verified; awaiting 6-digit TOTP challenge. |
| `AUTHORIZED` | Fully verified advocate with active 2FA; granted access to chambers workspace. |

---

## Environment Configuration

In `frontend/.env` (and `frontend/.env.example`):
```env
VITE_API_BASE_URL=http://localhost:8008
VITE_SUPABASE_URL=brveublsqvbulxxkgjxu
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_fo2AZ4LYA90V1N2ghE4JHw_qSTCGfix
```

> [!NOTE]
> No social login providers, Google Client IDs, or secret keys are used. Only standard Supabase publishable keys are stored on the frontend.
