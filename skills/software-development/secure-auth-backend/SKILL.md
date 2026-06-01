---
name: secure-auth-backend
description: Build secure authentication backends with WebAuthn passkeys, email whitelists, JWT sessions, and SQLite storage
category: software-development
triggers:
  - auth backend
  - passkey auth
  - webauthn
  - secure login
  - user authentication
  - jwt sessions
  - email whitelist
---

# Secure Auth Backend

Build authentication backends for confidential apps (data rooms, investor portals, internal tools).

## Stack
Node.js/Express + SQLite + `@simplewebauthn/server` + `jsonwebtoken` + `bcryptjs`

## Architecture

```
Frontend → Express API → SQLite
     ↑              ↓
   WebAuthn    JWT Sessions
```

**Flow:**
1. User enters email → `/check-email` validates against whitelist
2. If new user → `/register/options` → browser biometric prompt → `/register/complete`
3. If returning → `/login/options` → browser biometric prompt → `/login/complete`
4. On success → JWT access token (1h) + refresh token (7d)
5. Frontend stores tokens, sends `Authorization: Bearer <token>` on subsequent requests

## Quick Start

```bash
# Scaffold
mkdir backend && cd backend
npm init -y
npm install express better-sqlite3 @simplewebauthn/server jsonwebtoken bcryptjs cors helmet express-rate-limit uuid

# Files needed:
# - server.js (Express app)
# - config.js (env config)
# - db.js (SQLite schema + statements)
# - routes/auth.js (WebAuthn endpoints)
# - middleware/auth.js (JWT verification)
```

## SQLite Schema

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,          -- UUID
  email TEXT UNIQUE NOT NULL,
  access_level INTEGER DEFAULT 1,  -- 1=auth, 2=NDA, 3=full
  nda_signed INTEGER DEFAULT 0,
  investor_declaration INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE passkeys (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  credential_id TEXT UNIQUE NOT NULL,  -- base64
  public_key TEXT NOT NULL,            -- base64
  counter INTEGER NOT NULL,
  sign_count INTEGER NOT NULL,
  algorithm TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  refresh_token_hash TEXT UNIQUE NOT NULL,  -- SHA-256
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Investor declarations (for tier 3 access)
CREATE TABLE investor_declarations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  investor_type TEXT NOT NULL,  -- 'accredited', 'qualified', 'professional'
  declaration TEXT NOT NULL,   -- free-text declaration details
  declared_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Layered Access Tiers

For investor data rooms, implement tiered access. Customize sections per project:

| Tier | Level | Requirement | Typical Access |
|------|-------|-------------|--------|
| 1 | 1 | Authenticated | Overview, Pitch Deck, Team, Product, Contact |
| 2 | 2 | NDA signed | + Financials, Roadmap |
| 3 | 3 | Investor declaration | + Documents, Legal Agreements, IP Details, Cap Table |

**Two-tier variant (8Bit Data Room):** Investor declaration remains a mandatory legal KYC gate but does NOT create a separate access tier. NDA + declaration both required for full access.

| Tier | Level | Requirement | Typical Access |
|------|-------|-------------|--------|
| 1 | 1 | Authenticated | Overview, Pitch Deck, Team, Product, Contact |
| 2 | 2 | NDA signed + investor declaration | ALL sections (Financials, Roadmap, Legal, IP, Cap Table, Documents) |

**Note:** Pitch Deck often belongs in Tier 1 (marketing material, not confidential). Choose 2-tier vs 3-tier based on whether you need graduated access or just a binary gate.

**Investor declaration form options:**
- Dropdown: `Accredited Investor`, `Qualified Purchaser`, `Professional Institution`
- Textarea: free-text declaration details
- Store in `investor_declarations` table

**Backend enforcement:**
- `GET /api/auth/me` returns `accessLevel`, `ndaSigned`, `investorDeclaration`
- `POST /api/auth/nda/sign` — signs NDA, bumps user to tier 2 (or tier 3 in 3-tier model)
- `POST /api/auth/investor-declaration` — submits HNWI/professional status, bumps to tier 3 (or tier 2 in 2-tier model)

**Frontend gating:**
- Nav items greyed out for restricted sections (opacity 0.3, pointer-events none)
- Clicking restricted nav shows alert explaining what's needed
- Session restore checks access level on page load
- Never rely on frontend alone — backend enforces access too

**Flow (3-tier):** Auth → NDA Gate → Investor Declaration Gate → Data Room (sections unlocked per tier)
**Flow (2-tier):** Auth → NDA Gate → Investor Declaration Gate → Data Room (all sections unlocked)

## Key Implementation Details

### WebAuthn v9 API (`@simplewebauthn/server@9.x`)

```javascript
const { generateRegistrationOptions, verifyRegistrationResponse } = require('@simplewebauthn/server');

// Generate options
const options = await generateRegistrationOptions({
  rpName: 'App Name',
  rpID: '{{DOMAIN}}',  // domain in production
  userID: Buffer.from(userId),
  userName: email,
  timeout: 60000,
});

// Verify registration — v9 returns { verified, registrationInfo }
const verification = await verifyRegistrationResponse({
  response: { id: body.id, rawId: body.rawId, ...body.response },
  expectedChallenge: req.session.webauthnChallenge,
  expectedOrigin: 'http://localhost:{{BACKEND_PORT}}',
});

// Store credential
const { credentialID, publicKey, counter, fmt, alg } = verification.registrationInfo;
```

### Frontend Base64 Encoding

WebAuthn returns `Uint8Array` — must convert properly:

```javascript
// WRONG: btoa(credential.rawId.toString()) — produces comma-separated numbers
// CORRECT:
function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  bytes.forEach(b => binary += String.fromCharCode(b));
  return btoa(binary);
}

// Send to backend:
body: JSON.stringify({
  id: credential.id,
  rawId: arrayBufferToBase64(credential.rawId),
  response: {
    clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
    authenticatorData: arrayBufferToBase64(credential.response.authenticatorData),
    signature: arrayBufferToBase64(credential.response.signature),
    userHandle: credential.response.userHandle ? arrayBufferToBase64(credential.response.userHandle) : null,
  }
});
```

### JWT Session Management

```javascript
// Generate tokens
const accessToken = jwt.sign({ userId, email }, config.jwtSecret, { expiresIn: '1h' });
const refreshToken = jwt.sign({ userId }, config.jwtRefreshSecret, { expiresIn: '7d' });

// Store refresh token hash
const tokenHash = crypto.createHash('sha256').update(refreshToken).digest('hex');
db.statements.createSession.run(userId, tokenHash, new Date(Date.now() + 7*24*60*60*1000).toISOString());

// Verify on requests
function authenticateToken(req, res, next) {
  const token = req.headers['authorization']?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    req.user = jwt.verify(token, config.jwtSecret);
    next();
  } catch { return res.status(403).json({ error: 'Invalid token' }); }
}
```

### Email Whitelist

```javascript
// config.js
authorizedEmails: (process.env.{{AUTH_EMAILS_VAR}} || 'admin@example.com').split(',')

// Check before registration
function isAuthenticatedEmail(email) {
  return config.authorizedEmails
    .map(e => e.toLowerCase().trim())
    .includes(email.toLowerCase().trim());
}
```

## Security Checklist

- [ ] Rate limiting on auth endpoints (10 attempts/15min)
- [ ] CORS restricted to allowed origins
- [ ] Helmet security headers
- [ ] JWT secrets in env vars (not hardcoded)
- [ ] Refresh tokens hashed (SHA-256) before storage
- [ ] WebAuthn challenge stored in session, verified on completion
- [ ] `expectedOrigin` matches deployment URL
- [ ] `rpID` set to actual domain in production (not `localhost`)

## Pitfalls

- **WebAuthn v9 API returns `registrationInfo`, not `authenticationInfo`** — wrong property name causes undefined errors
- **Frontend `btoa(Uint8Array.toString())` is wrong** — produces comma-separated numbers, not binary. Use `arrayBufferToBase64()` helper
- **`@simplewebauthn/server` v9 vs v10+** — v10+ changed API significantly. Lock to `^9.0.0` in package.json
- **SQLite `better-sqlite3` is synchronous** — use prepared statements, not raw queries
- **JWT `Authorization` header format** — must be `Bearer <token>`, not just `<token>`
- **Refresh token rotation** — old tokens stay valid until expiry. For revocation, add `revoked` column to sessions table
- **WebAuthn `userID` must be Buffer** — pass `Buffer.from(userId)`, not string
- **`expectedOrigin` must match** — if frontend runs on `http://localhost:3000`, set origin to that. Mismatch causes verification failure
- **Investor declaration must complete before tier 3** — don't skip the declaration step even for whitelisted admins. The declaration is a legal record, not just an access gate.

## Testing

```bash
# Start server
cd backend && npm start

# Test health
curl http://localhost:3001/health

# Test email check
curl -X POST http://localhost:3001/api/auth/check-email \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com"}'
```

## References
- [WebAuthn v9 API docs](references/webauthn-v9-api.md)
- [Full backend template](templates/backend-template/)
