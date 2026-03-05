# Cortexa Security & Encryption Documentation

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Security Philosophy](#security-philosophy)
3. [Data Classification](#data-classification)
4. [Encryption at Rest](#encryption-at-rest)
5. [Encryption in Transit](#encryption-in-transit)
6. [Key Management](#key-management)
7. [Digital Signatures & Integrity](#digital-signatures--integrity)
8. [Authentication & Authorization](#authentication--authorization)
9. [HIPAA Compliance](#hipaa-compliance)
10. [Implementation Guide](#implementation-guide)
11. [Security Protocols](#security-protocols)
12. [Incident Response](#incident-response)
13. [Audit Logging](#audit-logging)

---

## Executive Summary

Cortexa is engineered with security as a foundational principle, not an afterthought. The system implements **military-grade encryption** (AES-256), **cryptographic integrity verification** (SHA-256 HMAC), and **HIPAA-compliant access controls** to protect sensitive patient health information (PHI).

### Security Pillars

1. **Confidentiality**: Only authorized personnel can access patient data
2. **Integrity**: Data cannot be modified without detection
3. **Availability**: System remains operational and accessible to authorized users
4. **Accountability**: All data access is audited and traceable
5. **Non-Repudiation**: Clinical decisions are digitally signed and undeniable

### Encryption Standards

| Component | Standard | Key Size | Mode | Purpose |
|-----------|----------|----------|------|---------|
| **Data at Rest** | AES | 256-bit | GCM | Database encryption |
| **Data in Transit** | TLS | 2048-bit (RSA) | 1.3 | Network communication |
| **Hashing** | SHA | 256-bit | HMAC | Integrity verification |
| **Digital Signatures** | RSA | 2048-bit | PKCS#1 v2.1 | Non-repudiation |

---

## Security Philosophy

### Defense in Depth

Cortexa employs **layered security** to ensure that even if one layer is compromised, others remain intact:

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Network Perimeter Security                │
│  • DDoS protection                                  │
│  • Firewall rules, VPC isolation                    │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│  Layer 2: Transport Layer Security                  │
│  • TLS 1.3, Certificate pinning                     │
│  • Mutual TLS (mTLS) for service-to-service         │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│  Layer 3: Application Layer Security                │
│  • Authentication (JWT tokens), Session management  │
│  • RBAC, attribute-based access control             │
│  • Input validation, SQL injection prevention       │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│  Layer 4: Data Layer Security                       │
│  • AES-256 encryption at rest                       │
│  • Field-level encryption for sensitive columns     │
│  • Database user roles and credentials              │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│  Layer 5: Cryptographic Layer                       │
│  • SHA-256 data integrity hashing                   │
│  • HMAC for authentication                          │
│  • Digital signatures for non-repudiation           │
└─────────────────────────────────────────────────────┘
```

### Zero Trust Architecture

Cortexa implements **Zero Trust** principles:
- Never trust, always verify
- Every request requires authentication
- Every connection requires authorization
- Assume breach mentality

---

## Data Classification

### Sensitivity Levels

All patient data is classified into sensitivity tiers, with encryption and access controls matched to sensitivity:

#### Level 1: Public Data ⚪
**Definition**: Non-identifiable, aggregate data safe for public disclosure

**Examples**:
- Anonymized statistical summaries
- De-identified research findings
- Public API documentation

**Encryption**: Standard encryption at rest, HTTP/HTTPS acceptable
**Access Control**: Public-facing (minimal restrictions)

#### Level 2: Internal Data 🟡
**Definition**: Organizational data not directly related to patient care, but not public

**Examples**:
- System performance metrics
- Non-patient administrative logs
- Internal documentation

**Encryption**: AES-256 at rest, HTTPS required
**Access Control**: Employees and contractors only

#### Level 3: Sensitive Data 🟠
**Definition**: Patient-identifiable information requiring special handling

**Examples**:
- De-identified ECG waveforms
- Aggregated risk scores
- Clinical research datasets

**Encryption**: AES-256 at rest, TLS 1.3 in transit, field-level encryption
**Access Control**: Clinicians and authorized researchers only
**Audit**: All access logged and monitored

#### Level 4: Highly Sensitive (PHI) 🔴
**Definition**: Protected Health Information requiring maximum security (HIPAA Restricted Data)

**Examples**:
- Patient names, MRNs (Medical Record Numbers)
- Full ECG waveforms with timestamps
- Medical imaging (MRI/CT) with patient identifiers
- Complete health histories and recommendations

**Encryption**: 
- **At Rest**: AES-256-GCM with field-level encryption
- **In Transit**: TLS 1.3 with certificate pinning
- **Key Storage**: Hardware Security Module (HSM) or Cloud KMS

**Access Control**: 
- Strict RBAC (Role-Based Access Control)
- Multi-factor authentication required
- Time-limited access tokens

**Audit**: 
- All access attempts logged (successful and failed)
- Real-time anomaly detection
- Immediately escalated to security team

**Deletion**: 
- Cryptographic deletion (key destruction)
- Verified erasure after clinical retention period

---

## Encryption at Rest

### Database Encryption Strategy

#### 1. Transparent Data Encryption (TDE)

PostgreSQL uses PgCrypto extension for transparent encryption:

```sql
-- Create encrypted columns for sensitive data
CREATE TABLE patient_records (
    id UUID PRIMARY KEY,
    patient_mrn TEXT NOT NULL,
    patient_name TEXT NOT NULL,
    -- Encrypted fields
    encrypted_ecg BYTEA NOT NULL,  -- Contains AES-256 encrypted signal
    encrypted_spo2 BYTEA NOT NULL,
    encrypted_clinical_notes BYTEA NOT NULL,
    
    -- Integrity verification
    ecg_hash BYTEA NOT NULL,  -- SHA-256 HMAC of plaintext
    spo2_hash BYTEA NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    encryption_key_id TEXT NOT NULL,  -- Reference to key version
    
    CONSTRAINT valid_ecg_hash CHECK (length(ecg_hash) = 32)
);

-- Create index on MRN (encrypted via pgcrypto)
CREATE INDEX idx_patient_mrn ON patient_records(patient_mrn);
```

#### 2. Field-Level Encryption

```python
"""
Field-level encryption for highly sensitive data.
Encryption happens at application layer before database storage.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import hmac
import hashlib

class FieldEncryptor:
    def __init__(self, master_key: bytes, key_id: str = "default"):
        """
        Args:
            master_key: 32-byte key for AES-256
            key_id: Identifier for key rotation tracking
        """
        self.master_key = master_key
        self.key_id = key_id
        self.backend = default_backend()
    
    def encrypt_field(self, plaintext: bytes) -> tuple[bytes, bytes, str]:
        """
        Encrypt a field using AES-256-GCM.
        
        Args:
            plaintext: Raw field data
        
        Returns:
            (ciphertext, iv, tag): Encrypted data with components
        """
        # Generate random 96-bit IV (Initialization Vector)
        iv = os.urandom(12)
        
        # Create cipher with AES-256-GCM
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # GCM provides built-in authentication tag
        tag = encryptor.tag
        
        # Format: [key_id (1 byte)] + [iv (12 bytes)] + [tag (16 bytes)] + [ciphertext]
        encrypted_payload = (
            self.key_id.encode('utf-8')[:32].ljust(32, b'\x00') +  # Padded key ID
            iv +
            tag +
            ciphertext
        )
        
        return encrypted_payload, iv, tag
    
    def decrypt_field(self, encrypted_payload: bytes) -> bytes:
        """
        Decrypt a field using AES-256-GCM.
        
        Args:
            encrypted_payload: Encrypted data with metadata
        
        Returns:
            Plaintext: Decrypted field data
        """
        # Extract components
        key_id = encrypted_payload[:32].rstrip(b'\x00').decode('utf-8')
        iv = encrypted_payload[32:44]
        tag = encrypted_payload[44:60]
        ciphertext = encrypted_payload[60:]
        
        # Verify key_id matches (prevents using wrong key)
        if key_id != self.key_id:
            raise ValueError(f"Key ID mismatch: {key_id} != {self.key_id}")
        
        # Create decipher with same parameters
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def compute_hmac(self, plaintext: bytes) -> bytes:
        """
        Compute HMAC-SHA256 for integrity verification.
        
        Args:
            plaintext: Original plaintext
        
        Returns:
            32-byte HMAC digest
        """
        h = hmac.new(self.master_key, plaintext, hashlib.sha256)
        return h.digest()
    
    def verify_integrity(self, plaintext: bytes, expected_hmac: bytes) -> bool:
        """
        Verify HMAC matches expected value.
        
        Args:
            plaintext: Original plaintext
            expected_hmac: Expected HMAC value
        
        Returns:
            True if HMAC matches (data unmodified)
        """
        computed_hmac = self.compute_hmac(plaintext)
        return hmac.compare_digest(computed_hmac, expected_hmac)
```

#### 3. Backup Encryption

All database backups are encrypted with a separate key:

```bash
#!/bin/bash
# Backup encryption script

# Database backup with encryption
pg_dump cortexa_db | \
  gzip | \
  openssl enc -aes-256-cbc -salt -pass pass:$BACKUP_KEY -out backup_$(date +%Y%m%d).sql.gz.enc

# Backup integrity verification
openssl dgst -sha256 backup_$(date +%Y%m%d).sql.gz.enc > backup_$(date +%Y%m%d).sql.gz.enc.sha256

# Store backup off-site (AWS S3 with encryption)
aws s3 cp backup_$(date +%Y%m%d).sql.gz.enc \
  s3://cortexa-backups/encrypted/ \
  --sse aws:kms \
  --sse-kms-key-id $AWS_KMS_KEY_ID
```

---

## Encryption in Transit

### TLS 1.3 Implementation

#### 1. Server Configuration (Express.js)

```javascript
/**
 * Express.js HTTPS server with TLS 1.3 configuration
 */

const https = require('https');
const fs = require('fs');
const express = require('express');
const helmet = require('helmet');

const app = express();

// TLS 1.3 configuration
const httpsOptions = {
  key: fs.readFileSync('./certs/server.key'),
  cert: fs.readFileSync('./certs/server.crt'),
  // Enforce TLS 1.3
  minVersion: 'TLSv1.3',
  maxVersion: 'TLSv1.3',
  
  // Cipher suites (TLS 1.3 specific)
  ciphers: [
    'TLS_AES_256_GCM_SHA384',      // Preferred
    'TLS_CHACHA20_POLY1305_SHA256',
    'TLS_AES_128_GCM_SHA256',
  ].join(':'),
  
  // Perfect Forward Secrecy
  honorCipherOrder: true,
  
  // OCSP stapling (certificate validation)
  ca: fs.readFileSync('./certs/ca-bundle.crt'),
};

// Security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'"],
      imgSrc: ["'self'", 'data:'],
    },
  },
  strictTransportSecurity: {
    maxAge: 31536000,  // 1 year in seconds
    includeSubDomains: true,
    preload: true,  // For HSTS preload list
  },
  frameguard: { action: 'deny' },  // Prevent clickjacking
  xssFilter: true,
  noSniff: true,  // Prevent MIME type sniffing
}));

// HTTPS redirect middleware
app.use((req, res, next) => {
  if (req.header('x-forwarded-proto') !== 'https') {
    res.redirect(301, `https://${req.header('host')}${req.url}`);
  } else {
    next();
  }
});

// Start HTTPS server
https.createServer(httpsOptions, app).listen(3000, () => {
  console.log('HTTPS server listening on port 3000 (TLS 1.3)');
});
```

#### 2. Client Configuration (Next.js Frontend)

```typescript
/**
 * Next.js client with TLS certificate pinning
 */

import fetch from 'node-fetch';
import https from 'https';
import fs from 'fs';

// Load certificates for client-side TLS verification
const clientCert = fs.readFileSync('./certs/client.crt');
const clientKey = fs.readFileSync('./certs/client.key');
const caCert = fs.readFileSync('./certs/ca-bundle.crt');

// Create HTTPS agent with certificate pinning
const httpsAgent = new https.Agent({
  cert: clientCert,
  key: clientKey,
  ca: caCert,
  rejectUnauthorized: true,  // Verify server certificate
  
  // Certificate pinning (pin specific certificate)
  // This prevents man-in-the-middle attacks
  checkServerIdentity: (host, cert) => {
    // Verify subject alternative names
    const subjectAltName = cert.subjectaltname || '';
    if (!subjectAltName.includes(`DNS:${host}`)) {
      throw new Error(`Certificate CN does not match host: ${host}`);
    }
    
    // Verify certificate fingerprint (SHA-256 of cert)
    const crypto = require('crypto');
    const expectedFingerprint = process.env.CERT_FINGERPRINT;
    const certFingerprint = crypto
      .createHash('sha256')
      .update(cert.raw)
      .digest('hex');
    
    if (certFingerprint !== expectedFingerprint) {
      throw new Error(`Certificate fingerprint mismatch`);
    }
  },
});

// Secure API requests
export async function secureApiCall(endpoint: string, options = {}) {
  const response = await fetch(`https://api.cortexa.local${endpoint}`, {
    ...options,
    agent: httpsAgent,
    headers: {
      ...options.headers,
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  });
  
  return response.json();
}
```

#### 3. Certificate Management

```bash
#!/bin/bash
# Script to generate and rotate TLS certificates

# Generate private key (4096-bit RSA)
openssl genrsa -out server.key 4096

# Create Certificate Signing Request (CSR)
openssl req -new \
  -key server.key \
  -out server.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=cortexa.local/SAN=DNS:cortexa.local,DNS:*.cortexa.local"

# Self-sign for development (or use CA for production)
openssl x509 -req \
  -days 365 \
  -in server.csr \
  -signkey server.key \
  -out server.crt \
  -extensions SAN \
  -extfile <(printf "subjectAltName=DNS:cortexa.local,DNS:*.cortexa.local")

# For production, use proper CA certificate chain
# This example uses Let's Encrypt (Certbot)
certbot certonly --standalone \
  -d cortexa.local \
  -d api.cortexa.local \
  --email security@cortexa.clinical

# Certificate pinning hash (for client-side verification)
openssl x509 -in server.crt -noout -fingerprint -sha256
```

---

## Key Management

### Master Key Hierarchy

```
┌─────────────────────────────────────────────┐
│  Master Key (Stored in HSM / AWS KMS)       │
│  AES-256, 256-bit, stored in Hardware       │
│  Security Module for maximum protection     │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴──────────┬──────────────────┐
      │                   │                  │
┌──────────────┐   ┌────────────────┐   ┌──────────────┐
│ Data Key 1   │   │ Data Key 2     │   │ Backup Key   │
│ (Database)   │   │ (Backups)      │   │ (Archives)   │
└──────────────┘   └────────────────┘   └──────────────┘
      │                   │                  │
      └───────────┬───────┴──────────────────┘
                  │
         ┌────────────────────┐
         │ Data Encryption    │
         │ (Transparent)      │
         └────────────────────┘
```

### AWS KMS Integration

```python
"""
AWS Key Management Service (KMS) for key storage and encryption
"""

import boto3
import json
from base64 import b64encode, b64decode

class KMSKeyManager:
    def __init__(self, region='us-east-1', key_id='arn:aws:kms:...:key/...'):
        self.kms_client = boto3.client('kms', region_name=region)
        self.key_id = key_id
    
    def encrypt_with_kms(self, plaintext: bytes) -> str:
        """
        Encrypt data using AWS KMS master key.
        
        Args:
            plaintext: Data to encrypt
        
        Returns:
            Base64-encoded ciphertext
        """
        response = self.kms_client.encrypt(
            KeyId=self.key_id,
            Plaintext=plaintext,
        )
        
        ciphertext = response['CiphertextBlob']
        return b64encode(ciphertext).decode('utf-8')
    
    def decrypt_with_kms(self, ciphertext_b64: str) -> bytes:
        """
        Decrypt data using AWS KMS master key.
        
        Args:
            ciphertext_b64: Base64-encoded ciphertext from KMS
        
        Returns:
            Decrypted plaintext
        """
        ciphertext = b64decode(ciphertext_b64.encode('utf-8'))
        
        response = self.kms_client.decrypt(
            CiphertextBlob=ciphertext,
        )
        
        plaintext = response['Plaintext']
        return plaintext
    
    def rotate_key(self, old_ciphertext_b64: str) -> str:
        """
        Re-encrypt data with latest KMS key (key rotation).
        
        Args:
            old_ciphertext_b64: Data encrypted with old key
        
        Returns:
            Data encrypted with new key
        """
        # Decrypt with old key
        plaintext = self.decrypt_with_kms(old_ciphertext_b64)
        
        # Encrypt with new key (automatic via KMS key rotation)
        return self.encrypt_with_kms(plaintext)
    
    def generate_data_key(self) -> tuple[bytes, str]:
        """
        Generate a data key for local encryption/decryption.
        
        Returns:
            (plaintext_key, encrypted_key)
        """
        response = self.kms_client.generate_data_key(
            KeyId=self.key_id,
            KeySpec='AES_256',
        )
        
        plaintext_key = response['Plaintext']
        encrypted_key = b64encode(response['CiphertextBlob']).decode('utf-8')
        
        return plaintext_key, encrypted_key
```

### Key Rotation Policy

```python
"""
Automatic key rotation policy to minimize impact of key compromise
"""

class KeyRotationManager:
    ROTATION_INTERVAL_DAYS = 90  # Rotate keys every 90 days
    
    def __init__(self, kms_manager, db_connection):
        self.kms_manager = kms_manager
        self.db = db_connection
    
    def should_rotate(self, key_id: str) -> bool:
        """
        Check if key needs rotation based on age.
        """
        query = """
            SELECT created_at FROM encryption_keys 
            WHERE key_id = %s
        """
        
        result = self.db.execute(query, (key_id,))
        created_at = result.fetchone()[0]
        
        from datetime import datetime, timedelta
        rotation_deadline = created_at + timedelta(days=self.ROTATION_INTERVAL_DAYS)
        
        return datetime.now() > rotation_deadline
    
    def rotate_key(self, old_key_id: str) -> str:
        """
        Rotate encryption key: create new key and re-encrypt all data.
        
        Args:
            old_key_id: Current key ID
        
        Returns:
            New key ID
        """
        # Generate new data key from KMS master key
        new_plaintext_key, new_encrypted_key = self.kms_manager.generate_data_key()
        
        # Store new key in database
        new_key_id = self._store_new_key(new_encrypted_key)
        
        # Re-encrypt all data encrypted with old key
        self._reencrypt_data(old_key_id, new_key_id, new_plaintext_key)
        
        # Mark old key as rotated
        query = "UPDATE encryption_keys SET status = 'rotated' WHERE key_id = %s"
        self.db.execute(query, (old_key_id,))
        
        return new_key_id
    
    def _reencrypt_data(self, old_key_id: str, new_key_id: str, new_key: bytes):
        """
        Re-encrypt all sensitive fields with new key.
        """
        # Fetch all records encrypted with old key
        query = """
            SELECT id, encrypted_ecg, encrypted_spo2, encrypted_clinical_notes
            FROM patient_records
            WHERE encryption_key_id = %s
        """
        
        records = self.db.execute(query, (old_key_id,)).fetchall()
        
        for record_id, enc_ecg, enc_spo2, enc_notes in records:
            # Decrypt with old key, encrypt with new key
            # ... decryption and encryption logic ...
            
            # Update record with new encrypted values
            update = """
                UPDATE patient_records
                SET encrypted_ecg = %s, encrypted_spo2 = %s, 
                    encrypted_clinical_notes = %s,
                    encryption_key_id = %s
                WHERE id = %s
            """
            self.db.execute(update, (enc_ecg, enc_spo2, enc_notes, new_key_id, record_id))
        
        self.db.commit()
```

---

## Digital Signatures & Integrity

### HMAC-SHA256 Implementation

```python
"""
HMAC-SHA256 for message authentication and integrity verification
"""

import hmac
import hashlib
import json
from datetime import datetime

class DataIntegrityManager:
    def __init__(self, signing_key: bytes):
        """
        Args:
            signing_key: 32-byte key for HMAC-SHA256
        """
        self.signing_key = signing_key
    
    def compute_signature(self, data: dict) -> str:
        """
        Compute HMAC-SHA256 signature of data.
        
        Args:
            data: Dictionary to sign (e.g., clinical predictions)
        
        Returns:
            Hex-encoded HMAC signature
        """
        # Canonical JSON serialization (deterministic ordering)
        canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # Compute HMAC
        h = hmac.new(self.signing_key, canonical_json.encode('utf-8'), hashlib.sha256)
        
        return h.hexdigest()
    
    def verify_signature(self, data: dict, expected_signature: str) -> bool:
        """
        Verify HMAC signature of data.
        
        Args:
            data: Dictionary to verify
            expected_signature: Expected HMAC value
        
        Returns:
            True if signature matches (data authentic and unmodified)
        """
        computed_signature = self.compute_signature(data)
        
        # Constant-time comparison (prevents timing attacks)
        return hmac.compare_digest(computed_signature, expected_signature)
    
    def create_signed_report(self, clinical_data: dict, clinician_id: str) -> dict:
        """
        Create digitally signed clinical report.
        
        Args:
            clinical_data: Predictions and findings
            clinician_id: ID of reviewing clinician
        
        Returns:
            Report with signature and metadata
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'clinician_id': clinician_id,
            'findings': clinical_data,
        }
        
        # Sign report
        signature = self.compute_signature(report)
        
        return {
            'report': report,
            'signature': signature,
            'signature_algorithm': 'HMAC-SHA256',
        }
    
    def verify_report(self, signed_report: dict) -> bool:
        """
        Verify clinical report signature.
        
        Args:
            signed_report: Report with embedded signature
        
        Returns:
            True if report authentic (not tampered)
        """
        return self.verify_signature(
            signed_report['report'],
            signed_report['signature']
        )
```

### Digital Certificates (RSA)

```python
"""
RSA digital signatures for non-repudiation (stronger than HMAC)
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class ClinicalSignatureManager:
    def __init__(self, private_key_path: str, public_key_path: str):
        """
        Load clinician's RSA key pair.
        """
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
            )
        
        with open(public_key_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(f.read())
    
    def sign_clinical_decision(self, clinical_data: dict) -> bytes:
        """
        Digitally sign a clinical decision using RSA.
        
        Args:
            clinical_data: Clinical findings and recommendations
        
        Returns:
            Digital signature (256 bytes for RSA-2048)
        """
        # Serialize data
        data_json = json.dumps(clinical_data, sort_keys=True).encode('utf-8')
        
        # Sign with private key
        signature = self.private_key.sign(
            data_json,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def verify_signature(self, clinical_data: dict, signature: bytes) -> bool:
        """
        Verify clinical decision signature using public key.
        
        Args:
            clinical_data: Original findings
            signature: RSA signature to verify
        
        Returns:
            True if signature valid (clinician did sign this decision)
        """
        data_json = json.dumps(clinical_data, sort_keys=True).encode('utf-8')
        
        try:
            self.public_key.verify(
                signature,
                data_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False  # Signature invalid
```

---

## Authentication & Authorization

### JWT Token Implementation

```python
"""
JWT (JSON Web Token) for stateless authentication
"""

import jwt
import json
from datetime import datetime, timedelta
from typing import Optional

class AuthTokenManager:
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry_minutes = 30  # Access token valid for 30 minutes
    
    def create_access_token(self, user_id: str, role: str, permissions: list[str]) -> str:
        """
        Create JWT access token with claims.
        
        Args:
            user_id: Unique user identifier
            role: User role (admin, clinician, technician)
            permissions: List of granted permissions
        
        Returns:
            Signed JWT token
        """
        now = datetime.utcnow()
        expiry = now + timedelta(minutes=self.token_expiry_minutes)
        
        payload = {
            'sub': user_id,  # Subject (user ID)
            'role': role,
            'permissions': permissions,
            'iat': now,  # Issued at
            'exp': expiry,  # Expiration
            'aud': 'cortexa-clinical',  # Audience
        }
        
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return token
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify JWT token and extract claims.
        
        Args:
            token: JWT token to verify
        
        Returns:
            Claims dictionary if valid, None if invalid/expired
        """
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience='cortexa-clinical',
                options={'verify_exp': True}
            )
            return claims
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Token invalid
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create long-lived refresh token for obtaining new access tokens.
        
        Args:
            user_id: User identifier
        
        Returns:
            Refresh token valid for 7 days
        """
        now = datetime.utcnow()
        expiry = now + timedelta(days=7)
        
        payload = {
            'sub': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': expiry,
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )
```

### Role-Based Access Control (RBAC)

```python
"""
RBAC for fine-grained authorization
"""

from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"  # Full system access
    CLINICIAN = "clinician"  # Patient data access, report generation
    TECHNICIAN = "technician"  # System monitoring only
    PATIENT = "patient"  # (Future) Personal data access only

class Permission(Enum):
    # Patient data access
    READ_PATIENT_DATA = "read:patient_data"
    WRITE_PATIENT_DATA = "write:patient_data"
    DELETE_PATIENT_DATA = "delete:patient_data"
    
    # Report generation
    GENERATE_REPORT = "generate:report"
    APPROVE_REPORT = "approve:report"
    EXPORT_REPORT = "export:report"
    
    # System administration
    MANAGE_USERS = "manage:users"
    VIEW_AUDIT_LOGS = "view:audit_logs"
    CONFIGURE_SYSTEM = "configure:system"
    MANAGE_ENCRYPTION_KEYS = "manage:keys"
    
    # Analytics
    VIEW_DASHBOARDS = "view:dashboards"
    EXPORT_ANALYTICS = "export:analytics"

# RBAC Matrix
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,
        Permission.DELETE_PATIENT_DATA,
        Permission.GENERATE_REPORT,
        Permission.APPROVE_REPORT,
        Permission.EXPORT_REPORT,
        Permission.MANAGE_USERS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.CONFIGURE_SYSTEM,
        Permission.MANAGE_ENCRYPTION_KEYS,
        Permission.VIEW_DASHBOARDS,
        Permission.EXPORT_ANALYTICS,
    ],
    UserRole.CLINICIAN: [
        Permission.READ_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,
        Permission.GENERATE_REPORT,
        Permission.APPROVE_REPORT,
        Permission.EXPORT_REPORT,
        Permission.VIEW_DASHBOARDS,
    ],
    UserRole.TECHNICIAN: [
        Permission.VIEW_DASHBOARDS,
        Permission.VIEW_AUDIT_LOGS,
    ],
    UserRole.PATIENT: [
        Permission.READ_PATIENT_DATA,  # Own data only
        Permission.EXPORT_REPORT,  # Own reports only
    ],
}

class AccessControl:
    def __init__(self, user_role: UserRole):
        self.user_role = user_role
        self.permissions = ROLE_PERMISSIONS[user_role]
    
    def has_permission(self, required_permission: Permission) -> bool:
        """Check if user has required permission."""
        return required_permission in self.permissions
    
    def can_access_patient_data(self, patient_id: str, user_id: str, 
                                user_role: UserRole) -> bool:
        """
        Check if user can access patient data.
        
        Implements attribute-based access control (ABAC):
        - Admins: Can access all patient data
        - Clinicians: Can access assigned patients
        - Patients: Can access only their own data
        """
        if user_role == UserRole.ADMIN:
            return True  # Admin access all data
        
        if user_role == UserRole.CLINICIAN:
            # Check if clinician is assigned to this patient
            return self._is_clinician_assigned(user_id, patient_id)
        
        if user_role == UserRole.PATIENT:
            # Patient can only access their own data
            return patient_id == user_id
        
        return False
    
    def _is_clinician_assigned(self, clinician_id: str, patient_id: str) -> bool:
        """Query database to check clinician-patient assignment."""
        # Implementation would check database
        pass
```

---

## HIPAA Compliance

### HIPAA Security Rule Checklist

#### Administrative Safeguards ✅

- [ ] **Assign Security Responsibility**: Designated Security Officer
- [ ] **Workforce Security**: Authorization/authentication for all users
- [ ] **Information Access Management**: Minimum necessary principle
- [ ] **Security Awareness/Training**: Annual HIPAA training mandatory
- [ ] **Security Incident Log**: All incidents documented and tracked
- [ ] **Contingency Planning**: Disaster recovery and business continuity
- [ ] **Business Partner Agreements**: BAA with all vendors

#### Physical Safeguards ✅

- [ ] **Facility Access Control**: Limited access to server rooms
- [ ] **Workstation Use Policy**: Clear guidelines for hardware usage
- [ ] **Workstation Security**: Screen locks, automatic logoff
- [ ] **Device/Media Control**: Encrypted device storage and destruction

#### Technical Safeguards ✅

- [ ] **Access Control**: Authentication, encryption, RBAC
- [ ] **Audit Logging**: All PHI access logged immutably
- [ ] **Encryption**: AES-256 at rest, TLS 1.3 in transit
- [ ] **Transmission Security**: Secure network protocols
- [ ] **Integrity Controls**: HMAC-SHA256 for data integrity

### HIPAA Breach Notification

```python
"""
Breach notification protocol per HIPAA 45 CFR §164.400
"""

class BreachNotificationManager:
    NOTIFICATION_DEADLINE_DAYS = 60  # Must notify within 60 days
    
    def __init__(self, db_connection, email_service):
        self.db = db_connection
        self.email_service = email_service
    
    def report_breach(self, breach_details: dict) -> str:
        """
        Report a suspected PHI breach.
        
        Args:
            breach_details: {
                'affected_patients': [list of patient IDs],
                'data_types': [list of PHI types exposed],
                'discovery_date': datetime,
                'description': str,
            }
        
        Returns:
            Breach ID for tracking
        """
        # Log breach in immutable audit log
        breach_id = self._log_breach(breach_details)
        
        # Immediately notify security officer
        self._notify_security_officer(breach_id, breach_details)
        
        # Begin investigation
        self._initiate_investigation(breach_id)
        
        # Schedule patient notifications (within 60 days)
        self._schedule_patient_notifications(breach_id, breach_details)
        
        # Report to HHS (if more than 500 people affected)
        if len(breach_details['affected_patients']) > 500:
            self._report_to_hhs(breach_id)
        
        return breach_id
    
    def send_breach_notification(self, patient_id: str, breach_id: str):
        """
        Send breach notification letter to affected individual.
        
        Per HIPAA, must include:
        - Description of breach
        - Types of information involved
        - Steps individual should take
        - What organization is doing
        - Contact information for questions
        """
        patient = self.db.fetch_patient(patient_id)
        breach = self.db.fetch_breach(breach_id)
        
        notification = f"""
Dear {patient['name']},

We are writing to inform you of a breach of your protected health information.
We take the security of your information seriously.

DESCRIPTION: {breach['description']}
DATE: {breach['discovery_date']}
INFORMATION AFFECTED: {', '.join(breach['data_types'])}

STEPS YOU SHOULD TAKE:
1. Monitor your accounts for unauthorized activity
2. Consider identity theft protection services
3. Contact us with any questions

CONTACT: security@cortexa.clinical, 1-800-XXX-XXXX

Sincerely,
Cortexa Security Team
"""
        
        # Send via secure channel
        self.email_service.send_encrypted_email(
            to=patient['email'],
            subject=f"Important Security Notice - Breach Notification (ID: {breach_id})",
            body=notification,
            encrypt=True,  # Send encrypted email
        )
```

---

## Implementation Guide

### Step-by-Step Encryption Setup

#### 1. Installation

```bash
# Install Python cryptography library
pip install cryptography

# Install PyOpenSSL for SSL/TLS
pip install pyopenssl

# Install boto3 for AWS KMS integration
pip install boto3
```

#### 2. Generate Master Key

```python
from cryptography.hazmat.primitives import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import hashlib

def generate_master_key(password: str, salt: bytes = None) -> bytes:
    """Generate 256-bit master key from password."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2(
        algorithm=hashlib.sha256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = kdf.derive(password.encode('utf-8'))
    return key, salt
```

#### 3. Initialize Encryption Service

```python
from src.security.encryption import FieldEncryptor, KMSKeyManager

# For development (local encryption)
encryptor = FieldEncryptor(master_key=b'0'*32, key_id='dev-key-001')

# For production (AWS KMS)
kms_manager = KMSKeyManager(
    region='us-east-1',
    key_id='arn:aws:kms:us-east-1:123456789:key/12345678-1234'
)
```

#### 4. Encrypt Patient Data

```python
# Encrypt ECG signal
plaintext_ecg = get_ecg_signal()
encrypted_ecg, iv, tag = encryptor.encrypt_field(plaintext_ecg)

# Compute integrity hash
ecg_hash = encryptor.compute_hmac(plaintext_ecg)

# Store in database
store_encrypted_signal(
    encrypted_data=encrypted_ecg,
    iv=iv,
    tag=tag,
    hash=ecg_hash,
    key_id='dev-key-001'
)
```

---

## Security Protocols

### Session Management

```python
"""
Secure session management with automatic timeouts
"""

class SessionManager:
    def __init__(self, session_timeout_minutes: int = 30):
        self.session_timeout = session_timeout_minutes
    
    def create_session(self, user_id: str, ip_address: str) -> str:
        """Create secure session after authentication."""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'session_id': session_id,
        }
        
        # Store in Redis with expiration
        redis_client.setex(
            f"session:{session_id}",
            self.session_timeout * 60,
            json.dumps(session_data)
        )
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str) -> bool:
        """Validate session and prevent session hijacking."""
        session_data = redis_client.get(f"session:{session_id}")
        
        if not session_data:
            return False  # Session expired
        
        session = json.loads(session_data)
        
        # IP address should match (prevents session hijacking)
        if session['ip_address'] != ip_address:
            return False
        
        # Check idle timeout
        last_activity = datetime.fromisoformat(session['last_activity'])
        if (datetime.utcnow() - last_activity).seconds > (self.session_timeout * 60):
            return False  # Session idle timeout
        
        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
        redis_client.setex(
            f"session:{session_id}",
            self.session_timeout * 60,
            json.dumps(session)
        )
        
        return True
```

### Multi-Factor Authentication (MFA)

```python
"""
Optional MFA for enhanced security
"""

import pyotp  # Time-based One-Time Password

class MFAManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def enable_mfa(self, user_id: str) -> str:
        """
        Enable TOTP (Time-based OTP) for user account.
        
        Returns:
            QR code image URI for scanning with authenticator app
        """
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Store secret in database (encrypted)
        self.db.update_user(user_id, {'mfa_secret': encrypt(secret)})
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provision_uri = totp.provisioning_uri(
            name=user_id,
            issuer_name='Cortexa'
        )
        
        # Return QR code for scanning
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(provision_uri)
        qr.make()
        
        return qr.get_image()
    
    def verify_mfa_code(self, user_id: str, code: str) -> bool:
        """Verify MFA code from authenticator app."""
        user = self.db.fetch_user(user_id)
        secret = decrypt(user['mfa_secret'])
        
        totp = pyotp.TOTP(secret)
        
        # Verify code (allow 30-second window for clock drift)
        return totp.verify(code, valid_window=1)
```

---

## Incident Response

### Security Incident Classification

| Severity | Impact | Response Time | Examples |
|----------|--------|----------------|----------|
| **Critical** 🔴 | Widespread PHI exposure | Immediate (1 hour) | Master key compromise, wholesale database breach |
| **High** 🟠 | Significant PHI exposure | 4 hours | Unauthorized access to 100+ patient records |
| **Medium** 🟡 | Limited PHI exposure | 1 day | Unauthorized access to <10 patient records |
| **Low** 🟢 | No/minimal PHI exposure | 3 days | Invalid login attempts, configuration errors |

### Incident Response Playbook

```python
"""
Automated incident response procedures
"""

class IncidentResponseManager:
    def __init__(self, db, email_service, logging_service):
        self.db = db
        self.email = email_service
        self.logger = logging_service
    
    def report_security_incident(self, incident: dict):
        """
        Report a security incident with automatic response.
        
        Args:
            incident: {
                'type': 'unauthorized_access',
                'severity': 'high',
                'affected_systems': ['database'],
                'description': str,
                'detected_by': str,
            }
        """
        incident_id = str(uuid.uuid4())
        
        # Log incident immutably
        self.logger.critical_log({
            'incident_id': incident_id,
            'timestamp': datetime.utcnow(),
            'incident': incident,
        })
        
        # Classify severity
        severity = incident['severity']
        
        # Immediate actions based on severity
        if severity == 'critical':
            self._handle_critical_incident(incident_id, incident)
        elif severity == 'high':
            self._handle_high_severity_incident(incident_id, incident)
        elif severity == 'medium':
            self._handle_medium_severity_incident(incident_id, incident)
        else:
            self._handle_low_severity_incident(incident_id, incident)
        
        return incident_id
    
    def _handle_critical_incident(self, incident_id: str, incident: dict):
        """Critical incident: Immediate escalation."""
        # 1. Isolate affected systems
        self._isolate_systems(incident['affected_systems'])
        
        # 2. Notify security team immediately (SMS + email)
        self.email.send_critical_alert(
            to=['security-team@cortexa.clinical'],
            subject=f"[CRITICAL] Security Incident {incident_id}",
            body=json.dumps(incident, indent=2),
            sms=True,  # Also send SMS
        )
        
        # 3. Begin root cause analysis
        self._initiate_root_cause_analysis(incident_id, incident)
        
        # 4. Compile evidence for forensics
        self._collect_forensic_evidence(incident_id)
        
        # 5. Notify legal and compliance
        self.email.notify_legal_compliance(incident_id)
        
        # 6. Prepare breach notification (if applicable)
        self._prepare_breach_notification(incident_id, incident)
    
    def _collect_forensic_evidence(self, incident_id: str):
        """Collect forensic evidence for investigation."""
        evidence = {
            'audit_logs': self._extract_relevant_logs(incident_id),
            'system_state': self._snapshot_system_state(),
            'network_traffic': self._capture_network_traffic(),
            'file_integrity': self._verify_file_hashes(),
        }
        
        # Store evidence in secure, immutable location
        self.db.store_forensic_evidence(incident_id, evidence)
```

---

## Audit Logging

### Comprehensive Audit Trail

```python
"""
Immutable audit logging for accountability and compliance
"""

class AuditLogger:
    def __init__(self, db_connection, kms_manager=None):
        self.db = db_connection
        self.kms = kms_manager
    
    def log_data_access(self, access_event: dict):
        """
        Log all PHI access for audit trails.
        
        Args:
            access_event: {
                'user_id': str,
                'patient_id': str,
                'data_type': 'ecg' | 'spo2' | 'image' | 'report',
                'action': 'read' | 'write' | 'delete',
                'timestamp': datetime,
                'ip_address': str,
                'result': 'success' | 'denied',
                'reason': str (if denied),
            }
        """
        # Compute integrity hash
        integrity_hash = self._compute_audit_hash(access_event)
        
        # Store in append-only audit log
        audit_record = {
            'event_id': str(uuid.uuid4()),
            'timestamp': access_event['timestamp'],
            'user_id': access_event['user_id'],
            'patient_id': access_event['patient_id'],
            'action': access_event['action'],
            'data_type': access_event['data_type'],
            'ip_address': access_event['ip_address'],
            'result': access_event['result'],
            'integrity_hash': integrity_hash,
            'pk_signature': self._sign_audit_record(access_event),
        }
        
        # Insert into append-only table (no updates/deletes allowed)
        self.db.insert_audit_log(audit_record)
    
    def query_audit_trail(self, patient_id: str, 
                         start_date: datetime, 
                         end_date: datetime) -> list:
        """
        Query audit trail for given patient and date range.
        Useful for complying with patient access requests.
        """
        query = """
            SELECT * FROM audit_logs
            WHERE patient_id = %s
            AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp ASC
        """
        
        return self.db.execute(query, (patient_id, start_date, end_date)).fetchall()
    
    def verify_audit_integrity(self) -> bool:
        """
        Verify integrity of entire audit log.
        Detects any tampering or modification.
        """
        records = self.db.fetch_all_audit_logs()
        
        for record in records:
            # Recompute integrity hash
            event = {
                'user_id': record['user_id'],
                'patient_id': record['patient_id'],
                'action': record['action'],
                'data_type': record['data_type'],
                'timestamp': record['timestamp'],
                'ip_address': record['ip_address'],
                'result': record['result'],
            }
            
            expected_hash = self._compute_audit_hash(event)
            
            # Verify matches stored hash
            if record['integrity_hash'] != expected_hash:
                return False  # Tampering detected!
        
        return True  # Audit log intact
    
    def _compute_audit_hash(self, event: dict) -> str:
        """Compute SHA-256 hash of audit event for integrity."""
        event_json = json.dumps(event, sort_keys=True, default=str)
        return hashlib.sha256(event_json.encode()).hexdigest()
```

### Audit Log Retention

```python
# HIPAA requires 6-year audit log retention
AUDIT_LOG_RETENTION_YEARS = 6

# Archival schedule
AUDIT_LOG_ARCHIVAL_POLICY = {
    '0-1 months': 'Hot storage (fast access)',
    '1-3 months': 'Warm storage (medium access)',
    '3-months-6years': 'Cold storage (encrypted archival)',
}

# Automatic archival job
def archive_old_audit_logs():
    """Move audit logs older than 3 months to cold storage."""
    cutoff_date = datetime.now() - timedelta(days=90)
    
    # Query logs older than 3 months
    old_logs = db.query("""
        SELECT * FROM audit_logs WHERE timestamp < %s
    """, (cutoff_date,))
    
    # Compress and encrypt to cold storage
    for log_batch in batch(old_logs, batch_size=10000):
        compressed = gzip.compress(json.dumps(log_batch).encode())
        encrypted = kms_manager.encrypt_with_kms(compressed)
        
        # Store in S3 with long-term retention
        s3_client.put_object(
            Bucket='cortexa-audit-cold-storage',
            Key=f'audit-logs/{cutoff_date.isoformat()}/',
            Body=encrypted,
            ServerSideEncryption='aws:kms',
            StorageClass='GLACIER',  # Cost-effective long-term storage
        )
    
    # Delete from hot storage after archival
    db.delete_old_logs(cutoff_date)
```

---

## Security Testing

### Penetration Testing Checklist

- [ ] **SQL Injection**: Attempt to inject malicious SQL
- [ ] **Cross-Site Scripting (XSS)**: Try JavaScript payload injection
- [ ] **Cross-Site Request Forgery (CSRF)**: Unauthorized cross-site requests
- [ ] **Authentication Bypass**: Attempt to access protected resources
- [ ] **Authorization Bypass**: Try to escalate privileges
- [ ] **Encryption Weakness**: Brute-force key recovery
- [ ] **Insufficient Logging**: Check audit trails completeness

### Security Scanning

```bash
# OWASP Dependency Check for vulnerable libraries
dependency-check --project Cortexa --scan --format HTML

# Bandit for Python security issues
bandit -r services/fast-api/ -f json -o bandit-report.json

# ESLint with security plugins for JavaScript
eslint --plugin security apps/web-app/ --format json > eslint-report.json

# SQLMap for SQL injection testing
sqlmap -u "https://api.cortexa.local/api/patients" --dbs --batch

# OWASP ZAP for web application scanning
zaproxy -cmd -quickurl https://cortexa.local -quickout zap-report.html
```

---

## References & Standards

### Regulatory Frameworks

- [HIPAA Security Rule (45 CFR Part 164)](https://www.hhs.gov/hipaa/for-professionals/security/)
- [HIPAA Breach Notification Rule](https://www.hhs.gov/hipaa/for-professionals/breach-notification/)
- [GDPR Data Protection Requirements](https://gdpr-info.eu/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Cryptography Standards

- [NIST Approved Algorithms](https://nvlpubs.nist.gov/pubsfiles/FIPS/NIST.FIPS.140-2.pdf)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [TLS 1.3 Specification (RFC 8446)](https://tools.ietf.org/html/rfc8446)

### Security Best Practices

- [OWASP Top 10 Web Application Security Risks](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [CWE/SANS Top 25 Most Dangerous Software Errors](https://cwe.mitre.org/top25/)

---

## Support & Contact

**Security Issues**: security@cortexa.clinical  
**Responsible Disclosure**: Report security issues confidentially  
**Compliance Questions**: compliance@cortexa.clinical

---

**Last Updated**: February 28, 2026  
**Status**: Active Development  
**Review Schedule**: Quarterly security audits