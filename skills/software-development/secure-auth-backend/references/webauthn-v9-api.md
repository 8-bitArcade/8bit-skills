# WebAuthn v9 API Reference

## Package
`@simplewebauthn/server@9.0.3`

## Key Imports
```javascript
const {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
} = require('@simplewebauthn/server');
```

## Registration Flow

### 1. Generate Options
```javascript
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

const userId = uuidv4();
const options = await generateRegistrationOptions({
  rpName: 'App Name',
  rpID: '{{DOMAIN}}',  // or domain in production
  userID: Buffer.from(userId),
  userName: email,
  timeout: 60000,
});

// Store challenge in session
req.session.webauthnChallenge = options.challenge;
req.session.userId = userId;
```

### 2. Verify Registration
```javascript
const verification = await verifyRegistrationResponse({
  response: {
    id: body.id,
    rawId: body.rawId,
    type: 'webauthn.create',
    trusted: true,
    ...body.response,
  },
  expectedChallenge: req.session.webauthnChallenge,
  expectedOrigin: 'http://localhost:{{BACKEND_PORT}}',
});

if (!verification.verified) {
  // Handle error
}

// v9 returns registrationInfo (NOT authenticationInfo)
const { credentialID, publicKey, counter, fmt, alg } = verification.registrationInfo;

// Store in database
db.statements.createPasskey.run(
  userId,
  credentialID,
  publicKey,
  counter,
  counter,
  fmt,
  alg
);
```

## Authentication Flow

### 1. Generate Options
```javascript
const options = await generateAuthenticationOptions({
  rpID: '{{DOMAIN}}',
  timeout: 60000,
  allowCredentials: [],  // Empty = allow any credential for user
});

req.session.webauthnChallenge = options.challenge;
```

### 2. Verify Authentication
```javascript
const verification = await verifyAuthenticationResponse({
  response: {
    id: body.id,
    rawId: body.rawId,
    type: 'webauthn.get',
    trusted: true,
    ...body.response,
  },
  expectedChallenge: req.session.webauthnChallenge,
  expectedOrigin: 'http://localhost:{{BACKEND_PORT}}',
  credential: {
    id: passkey.credential_id,
    publicKey: Buffer.from(passkey.public_key, 'base64'),
    counter: passkey.sign_count,
  },
});

if (!verification.verified) {
  // Handle error
}

// Update sign count
db.statements.updateSignCount.run(
  verification.authenticationInfo.newCounter,
  passkey.id
);
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `registrationInfo` undefined | Using v9 API but accessing `authenticationInfo` | Use `verification.registrationInfo` |
| `expectedOrigin` mismatch | Frontend URL doesn't match | Set to actual deployment URL |
| `userID` must be Buffer | Passing string | Use `Buffer.from(userId)` |
| Challenge verification failed | Session lost/cleared | Use server-side session store |

## Frontend Integration

```javascript
// Registration
const options = await fetch('/api/auth/register/options').then(r => r.json());
const credential = await navigator.credentials.create({ publicKey: options });

// Authentication
const options = await fetch('/api/auth/login/options').then(r => r.json());
const credential = await navigator.credentials.get({ publicKey: options });
```

## Data Conversion

WebAuthn returns `Uint8Array` — must convert to base64 for JSON:

```javascript
function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  bytes.forEach(b => binary += String.fromCharCode(b));
  return btoa(binary);
}

// Send to backend
{
  id: credential.id,
  rawId: arrayBufferToBase64(credential.rawId),
  response: {
    clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
    authenticatorData: arrayBufferToBase64(credential.response.authenticatorData),
    signature: arrayBufferToBase64(credential.response.signature),
    userHandle: credential.response.userHandle 
      ? arrayBufferToBase64(credential.response.userHandle) 
      : null,
  }
}
```
