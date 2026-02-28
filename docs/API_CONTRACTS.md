# Cortexa API Contracts & OpenAPI Specification

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs & Versioning](#base-urls--versioning)
4. [Express Orchestrator API](#express-orchestrator-api)
5. [File Upload API](#file-upload-api)
6. [FastAPI Inference Engine](#fastapi-inference-engine)
7. [Encryption Service API](#encryption-service-api)
8. [PDF Report Generation](#pdf-report-generation)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)
11. [OpenAPI 3.0 Specification](#openapi-30-specification)

---

## Overview

Cortexa exposes three REST APIs serving distinct roles:

| Service | Purpose | Port | Primary Use |
|---------|---------|------|-------------|
| **Express Orchestrator** | API Gateway, authentication, user/patient management | 3000 | Frontend integration, request routing |
| **FastAPI Inference Engine** | ML model inference, signal preprocessing | 8000 | Real-time clinical predictions |
| **Encryption Service** | Data encryption/decryption | 3001 | Sensitive data protection |

### API Communication Flow

```
Frontend (Next.js)
         │
         ▼
┌─────────────────────────────────────┐
│  Express Orchestrator (Port 3000)   │
│  - Authentication & authorization   │
│  - Request validation               │
│  - PDF report generation            │
│  - Database CRUD operations         │
└──────────┬──────────────┬───────────┘
           │              │
           ▼              ▼
    ┌─────────────┐ ┌─────────────────┐
    │ FastAPI     │ │ Encryption API  │
    │ Inference   │ │ (Port 3001)     │
    │ (Port 8000) │ └─────────────────┘
    └─────────────┘
```

---

## Authentication

### JWT Bearer Token

All endpoints (except login) require JWT authentication via `Authorization` header:

```http
GET /api/v1/patients/123 HTTP/1.1
Host: api.cortexa.local
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Format

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "clinician-001",
  "role": "clinician",
  "permissions": ["read:patient_data", "generate:report"],
  "iat": 1709080000,
  "exp": 1709081800,
  "aud": "cortexa-clinical"
}
```

### Token Lifetime

- **Access Token**: 30 minutes
- **Refresh Token**: 7 days (for obtaining new access tokens)

---

## Base URLs & Versioning

### Endpoints

```
Express Orchestrator:  https://api.cortexa.local/api/v1
FastAPI Inference:     https://inference.cortexa.local/api/v1
Encryption Service:    https://crypto.cortexa.local/api/v1
```

### API Versioning Strategy

- Version in URL path: `/api/v1/` (current), `/api/v2/` (future)
- Backward compatible for 1 year after new version release
- Deprecation notices included in response headers

---

## Express Orchestrator API

### Authentication & Sessions

#### POST /auth/login

Authenticate user and obtain JWT tokens.

**Request:**
```http
POST /auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "clinician@cortexa.clinical",
  "password": "SecurePassword123!",
  "mfa_code": "123456"  // Optional, required if MFA enabled
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": "clinician-001",
    "email": "clinician@cortexa.clinical",
    "role": "clinician",
    "name": "Dr. Jane Smith",
    "mfa_enabled": true
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Invalid credentials",
  "error_code": "AUTH_INVALID_CREDENTIALS",
  "timestamp": "2026-02-28T12:00:00Z"
}
```

#### POST /auth/refresh

Obtain new access token using refresh token.

**Request:**
```http
POST /auth/refresh HTTP/1.1
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

#### POST /auth/logout

Invalidate current session and tokens.

**Request:**
```http
POST /auth/logout HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully",
  "timestamp": "2026-02-28T12:00:00Z"
}
```

---

### Patient Management

#### GET /patients

List all patients accessible to current user (with optional filtering).

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Results per page (default: 20, max: 100) |
| `search` | string | Search by name or MRN |
| `status` | string | Filter by status: `active`, `discharged`, `archived` |
| `condition` | string | Filter by condition: `sleep_apnea`, `diabetes`, `afib`, `burnout`, `tumor` |

**Request:**
```http
GET /patients?page=1&limit=20&condition=diabetes HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "patient-001",
      "mrn": "MRN-2024-001",
      "name": "John Doe",
      "age": 45,
      "gender": "M",
      "status": "active",
      "conditions": ["diabetes", "afib"],
      "created_at": "2024-01-15T10:30:00Z",
      "last_assessment": "2026-02-27T14:22:00Z"
    },
    {
      "id": "patient-002",
      "mrn": "MRN-2024-002",
      "name": "Jane Smith",
      "age": 52,
      "gender": "F",
      "status": "active",
      "conditions": ["sleep_apnea"],
      "created_at": "2024-02-20T09:15:00Z",
      "last_assessment": "2026-02-28T08:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 127,
    "pages": 7
  }
}
```

#### GET /patients/{patientId}

Retrieve detailed patient information.

**Request:**
```http
GET /patients/patient-001 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": "patient-001",
  "mrn": "MRN-2024-001",
  "name": "John Doe",
  "age": 45,
  "gender": "M",
  "contact": {
    "email": "john.doe@example.com",
    "phone": "+1-555-0100"
  },
  "medical_history": {
    "conditions": ["diabetes", "afib"],
    "medications": ["Metformin 500mg", "Amiodarone 100mg"],
    "allergies": ["Penicillin"]
  },
  "vital_signs": {
    "blood_pressure": "120/80",
    "heart_rate": 72,
    "temperature": 98.6,
    "respiratory_rate": 16
  },
  "assessments": [
    {
      "id": "assessment-001",
      "timestamp": "2026-02-28T08:45:00Z",
      "type": "diabetes_risk",
      "status": "completed",
      "risk_score": 0.72
    }
  ],
  "reports": [
    {
      "id": "report-001",
      "timestamp": "2026-02-28T09:30:00Z",
      "type": "clinical_summary",
      "status": "ready",
      "url": "/api/v1/reports/report-001/pdf"
    }
  ]
}
```

#### POST /patients

Create new patient record.

**Request:**
```http
POST /patients HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "mrn": "MRN-2026-100",
  "name": "Alice Johnson",
  "age": 58,
  "gender": "F",
  "contact": {
    "email": "alice.johnson@example.com",
    "phone": "+1-555-0101"
  },
  "medical_history": {
    "conditions": ["burnout"],
    "medications": [],
    "allergies": []
  }
}
```

**Response (201 Created):**
```json
{
  "id": "patient-003",
  "mrn": "MRN-2026-100",
  "name": "Alice Johnson",
  "age": 58,
  "gender": "F",
  "status": "active",
  "created_at": "2026-02-28T12:00:00Z"
}
```

---

## File Upload API

### Overview

Cortexa supports two types of file uploads for clinical data:

1. **Timeseries Data CSV Files** - Physiological signals and vital signs
2. **Medical Imaging** - MRI/CT scan images in DICOM or standard formats

### File Format Specifications

#### CSV Timeseries Format

**Required Columns:**
```csv
timestamp,ecg,spo2,hrv,eda,temperature,activity_score,respiratory_rate
2026-02-28T08:00:00Z,0.45,95,45000,0.5,36.8,2.1,16
2026-02-28T08:01:00Z,0.48,94,48000,0.6,36.9,2.3,16
2026-02-28T08:02:00Z,0.42,95,42000,0.55,36.8,1.9,15
```

**Column Specifications:**

| Column | Data Type | Unit | Range | Required |
|--------|-----------|------|-------|----------|
| `timestamp` | ISO 8601 | - | - | ✓ Yes |
| `ecg` | Float | mV | -1.0 to 1.0 | Optional* |
| `spo2` | Integer | % | 70-100 | Optional* |
| `hrv` | Integer | ms² | 10,000-500,000 | Optional* |
| `eda` | Float | μS | 0.0-10.0 | Optional* |
| `temperature` | Float | °C | 35.0-40.0 | Optional* |
| `activity_score` | Float | - | 0.0-10.0 | Optional* |
| `respiratory_rate` | Integer | breaths/min | 8-40 | Optional* |

*At least 2 signals required per CSV file

**CSV Validation Rules:**
- Maximum file size: 50 MB
- Maximum rows: 1,000,000 samples
- Timestamp must be monotonic increasing
- All numeric values must be valid numbers (no NaN or Inf)
- Duplicate timestamps are merged (averaged)
- Time format: RFC 3339 (ISO 8601)

**Example CSV (10 seconds @ 1 Hz):**
```csv
timestamp,ecg,spo2,hrv,temperature
2026-02-28T08:00:00Z,0.45,95,45000,36.8
2026-02-28T08:00:01Z,0.48,94,48000,36.8
2026-02-28T08:00:02Z,0.42,95,42000,36.8
2026-02-28T08:00:03Z,0.50,95,50000,36.9
2026-02-28T08:00:04Z,0.46,94,46000,36.8
2026-02-28T08:00:05Z,0.44,95,44000,36.8
2026-02-28T08:00:06Z,0.49,95,49000,36.8
2026-02-28T08:00:07Z,0.43,94,43000,36.8
2026-02-28T08:00:08Z,0.47,95,47000,36.9
2026-02-28T08:00:09Z,0.45,95,45000,36.8
```

#### Medical Imaging Format

**Supported Image Formats:**

| Format | Extension | Bit Depth | Dimensions | Max Size | Use Case |
|--------|-----------|-----------|------------|----------|----------|
| **DICOM** | .dcm | 16-bit | 512×512-1024×1024 | 100 MB | MRI/CT primary format |
| **NIfTI** | .nii, .nii.gz | 8/16/32-bit | 3D volumes | 500 MB | Medical imaging standard |
| **JPEG** | .jpg | 8-bit RGB | Any | 25 MB | Quick visual reference |
| **PNG** | .png | 8/16-bit | Any | 50 MB | Lossless reference images |
| **TIFF** | .tiff | 16/32-bit | Any | 100 MB | High-quality scans |

**DICOM Metadata Requirements:**
- Patient ID (must match MRN)
- Study Date/Time
- Modality (MR for MRI, CT for CT)
- Slice Thickness
- Series Number
- Instance Number

### File Upload Endpoints

#### GET /upload-templates

Download CSV template files for different signal types.

**Request:**
```http
GET /upload-templates?type=physiological_signals HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Query Parameters:**
| Parameter | Type | Options |
|-----------|------|---------|
| `type` | string | `physiological_signals`, `sleep_apnea`, `diabetes`, `afib`, `burnout` |
| `format` | string | `csv` (default), `json` |

**Response (200 OK):**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="template_physiological_signals.csv"

timestamp,ecg,spo2,hrv,eda,temperature,activity_score,respiratory_rate
2026-02-28T08:00:00Z,0.45,95,45000,0.5,36.8,2.1,16
2026-02-28T08:00:01Z,0.48,94,48000,0.6,36.9,2.3,16
```

#### POST /patients/{patientId}/signals/upload

Upload timeseries CSV file for patient.

**Request:**
```http
POST /patients/patient-001/signals/upload HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="patient_signals_2026-02-28.csv"
Content-Type: text/csv

timestamp,ecg,spo2,hrv,temperature
2026-02-28T08:00:00Z,0.45,95,45000,36.8
2026-02-28T08:00:01Z,0.48,94,48000,36.8
...
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="metadata"

{
  "signal_source": "wearable_device",
  "device_type": "Apple_Watch_Series_7",
  "collection_date_start": "2026-02-28T08:00:00Z",
  "collection_date_end": "2026-02-28T09:00:00Z",
  "sampling_rate_hz": 1
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (202 Accepted):**
```json
{
  "upload_id": "upload-001",
  "patient_id": "patient-001",
  "file_name": "patient_signals_2026-02-28.csv",
  "file_size": 125000,
  "status": "processing",
  "rows_detected": 3600,
  "signals_found": ["ecg", "spo2", "hrv", "temperature"],
  "validation_status": "in_progress",
  "progress": 0,
  "created_at": "2026-02-28T12:00:00Z",
  "estimated_completion": "2026-02-28T12:02:00Z",
  "webhook_url": "https://api.cortexa.local/webhooks/uploads/upload-001"
}
```

#### GET /uploads/{uploadId}

Poll file upload status and validation results.

**Request:**
```http
GET /uploads/upload-001 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK) - Processing:**
```json
{
  "upload_id": "upload-001",
  "patient_id": "patient-001",
  "file_name": "patient_signals_2026-02-28.csv",
  "status": "validating",
  "progress": 65,
  "rows_processed": 2340,
  "rows_total": 3600,
  "errors": [],
  "warnings": [
    "Row 1250: Missing temperature value (will be imputed)"
  ],
  "started_at": "2026-02-28T12:00:00Z",
  "estimated_completion": "2026-02-28T12:02:00Z"
}
```

**Response (200 OK) - Completed:**
```json
{
  "upload_id": "upload-001",
  "patient_id": "patient-001",
  "file_name": "patient_signals_2026-02-28.csv",
  "status": "ready",
  "progress": 100,
  "rows_processed": 3600,
  "rows_total": 3600,
  "validation_result": {
    "is_valid": true,
    "error_count": 0,
    "warning_count": 1,
    "quality_score": 0.98,
    "data_completeness": 0.99,
    "timestamp_continuity": "valid",
    "signal_ranges": {
      "ecg": {"min": 0.35, "max": 0.95, "status": "valid"},
      "spo2": {"min": 92, "max": 98, "status": "valid"},
      "hrv": {"min": 38000, "max": 52000, "status": "valid"},
      "temperature": {"min": 36.5, "max": 37.2, "status": "valid"}
    }
  },
  "signals_summary": {
    "ecg": {"samples": 3600, "missing": 0, "mean": 0.46, "std": 0.08},
    "spo2": {"samples": 3600, "missing": 0, "mean": 95, "std": 1.2},
    "hrv": {"samples": 3600, "missing": 1, "mean": 45200, "std": 3100},
    "temperature": {"samples": 3599, "missing": 1, "mean": 36.8, "std": 0.15}
  },
  "storage_path": "s3://cortexa-signals/patient-001/upload-001/",
  "completed_at": "2026-02-28T12:02:15Z",
  "can_create_assessment": true
}
```

**Response (400 Bad Request) - Validation Failed:**
```json
{
  "upload_id": "upload-001",
  "status": "failed",
  "validation_result": {
    "is_valid": false,
    "error_count": 5,
    "warning_count": 3,
    "errors": [
      {
        "row": 1,
        "field": "timestamp",
        "error": "Invalid timestamp format (expected ISO 8601)",
        "value": "2026/02/28 08:00:00"
      },
      {
        "row": 250,
        "field": "ecg",
        "error": "Value out of range: 2.5 (expected -1.0 to 1.0)",
        "value": "2.5"
      },
      {
        "row_range": "500-600",
        "field": "spo2",
        "error": "Non-monotonic timestamp detected",
        "value": "Timestamps decreased: 12:05:23 → 12:05:22"
      }
    ]
  },
  "failed_at": "2026-02-28T12:02:00Z"
}
```

#### POST /patients/{patientId}/imaging/upload

Upload medical imaging files (MRI/CT scans).

**Request:**
```http
POST /patients/patient-001/imaging/upload HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="patient_mri_brain_T1.dcm"
Content-Type: application/dicom

[DICOM binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="metadata"

{
  "imaging_type": "MRI",
  "modality": "MR",
  "body_part": "brain",
  "sequence": "T1_weighted",
  "scan_date": "2026-02-28",
  "study_id": "STUDY-2026-001",
  "series_number": 1,
  "clinical_indication": "Rule out tumor",
  "radiologist_notes": "Incidental finding noted"
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (202 Accepted):**
```json
{
  "upload_id": "img-upload-001",
  "patient_id": "patient-001",
  "file_name": "patient_mri_brain_T1.dcm",
  "file_size": 15728640,
  "imaging_type": "MRI",
  "modality": "MR",
  "body_part": "brain",
  "status": "processing",
  "validation_status": "in_progress",
  "progress": 0,
  "created_at": "2026-02-28T12:00:00Z",
  "estimated_completion": "2026-02-28T12:05:00Z",
  "webhook_url": "https://api.cortexa.local/webhooks/imaging/img-upload-001"
}
```

#### GET /imaging/{uploadId}

Poll medical imaging upload status and DICOM validation.

**Request:**
```http
GET /imaging/img-upload-001 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK) - Processing:**
```json
{
  "upload_id": "img-upload-001",
  "status": "validating",
  "progress": 45,
  "validation_steps": [
    {"step": "File integrity check", "status": "completed"},
    {"step": "DICOM header parsing", "status": "completed"},
    {"step": "Image decompression", "status": "in_progress"},
    {"step": "Metadata validation", "status": "pending"},
    {"step": "AI preprocessor", "status": "pending"}
  ]
}
```

**Response (200 OK) - Completed:**
```json
{
  "upload_id": "img-upload-001",
  "patient_id": "patient-001",
  "file_name": "patient_mri_brain_T1.dcm",
  "imaging_type": "MRI",
  "modality": "MR",
  "body_part": "brain",
  "status": "ready",
  "progress": 100,
  "validation_result": {
    "is_valid": true,
    "file_integrity": "verified",
    "dicom_compliant": true,
    "patient_id_matches": true
  },
  "dicom_metadata": {
    "patient_id": "MRN-2024-001",
    "patient_name": "John Doe",
    "study_date": "2026-02-28",
    "study_time": "08:30:00",
    "series_number": 1,
    "instance_number": 1,
    "slice_thickness": 1.5,
    "pixel_spacing": [1.0, 1.0],
    "rows": 512,
    "columns": 512,
    "bits_allocated": 16
  },
  "image_quality": {
    "signal_to_noise_ratio": 45.2,
    "contrast": "good",
    "artifacts": "minimal",
    "quality_score": 0.96
  },
  "preprocessing": {
    "dimensions": [512, 512],
    "data_type": "uint16",
    "range": [0, 4095],
    "normalized": false,
    "thumbnail_url": "https://api.cortexa.local/imaging/img-upload-001/thumbnail.jpg"
  },
  "storage_path": "s3://cortexa-imaging/patient-001/img-upload-001/",
  "completed_at": "2026-02-28T12:04:30Z",
  "can_create_assessment": true
}
```

#### POST /validate-csv

Validate CSV file before upload (dry-run validation).

**Request:**
```http
POST /validate-csv HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="patient_signals_sample.csv"
Content-Type: text/csv

timestamp,ecg,spo2,hrv
2026-02-28T08:00:00Z,0.45,95,45000
2026-02-28T08:00:01Z,0.48,94,48000
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (200 OK):**
```json
{
  "validation_id": "val-001",
  "file_name": "patient_signals_sample.csv",
  "is_valid": true,
  "quality_score": 0.97,
  "summary": {
    "rows": 2,
    "columns": 4,
    "signals_found": ["timestamp", "ecg", "spo2", "hrv"],
    "missing_signals": [],
    "duration_seconds": 1,
    "time_range": {
      "start": "2026-02-28T08:00:00Z",
      "end": "2026-02-28T08:00:01Z"
    }
  },
  "column_analysis": {
    "timestamp": {
      "type": "datetime",
      "format": "ISO8601",
      "valid_count": 2,
      "invalid_count": 0,
      "status": "valid"
    },
    "ecg": {
      "type": "float",
      "unit": "mV",
      "range": [0.45, 0.48],
      "valid_count": 2,
      "invalid_count": 0,
      "status": "valid"
    },
    "spo2": {
      "type": "integer",
      "unit": "%",
      "range": [94, 95],
      "valid_count": 2,
      "invalid_count": 0,
      "status": "valid"
    },
    "hrv": {
      "type": "integer",
      "unit": "ms²",
      "range": [45000, 48000],
      "valid_count": 2,
      "invalid_count": 0,
      "status": "valid"
    }
  },
  "errors": [],
  "warnings": [],
  "recommendations": [
    "CSV contains only 2 data points; minimum 60 samples recommended for meaningful analysis"
  ]
}
```

---

### Clinical Assessments

#### POST /patients/{patientId}/assessments

Initiate ML-based clinical assessment for patient (supports uploaded files or direct signal input).

**Request Option 1: Using Uploaded File IDs**
```http
POST /patients/patient-001/assessments HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "assessment_type": "diabetes_risk",
  "data_source": "uploaded_files",
  "uploaded_files": {
    "signals_upload_id": "upload-001",
    "imaging_upload_id": "img-upload-001"
  },
  "additional_context": {
    "symptoms": ["fatigue", "increased_thirst"],
    "blood_glucose": 185,
    "notes": "Patient reports recent weight gain"
  }
}
```

**Request Option 2: Direct Signal Input (for small datasets)**
```http
POST /patients/patient-001/assessments HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "assessment_type": "diabetes_risk",
  "signals": {
    "ecg": [0.1, 0.2, 0.15, ...],
    "spo2": [95, 94, 95, 96, ...],
    "hrv": [45000, 48000, 42000, ...],
    "temperature": 36.8,
    "activity_score": 7.2
  },
  "additional_context": {
    "symptoms": ["fatigue", "increased_thirst"],
    "blood_glucose": 185,
    "notes": "Patient reports recent weight gain"
  }
}
```

**Response (202 Accepted):**
```json
{
  "assessment_id": "assessment-001",
  "patient_id": "patient-001",
  "assessment_type": "diabetes_risk",
  "status": "processing",
  "data_source": "uploaded_files",
  "data_summary": {
    "signals_used": ["ecg", "spo2", "hrv", "temperature"],
    "signal_samples": 3600,
    "signal_duration_seconds": 3600,
    "imaging_included": true,
    "imaging_type": "MRI",
    "imaging_volume_slices": 128
  },
  "submitted_at": "2026-02-28T12:00:00Z",
  "estimated_completion": "2026-02-28T12:05:00Z",
  "webhook_url": "https://api.cortexa.local/webhooks/assessments/assessment-001"
}
```

#### GET /assessments/{assessmentId}

Poll assessment status and results.

**Request:**
```http
GET /assessments/assessment-001 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK) - Processing:**
```json
{
  "assessment_id": "assessment-001",
  "patient_id": "patient-001",
  "assessment_type": "diabetes_risk",
  "status": "processing",
  "progress": 65,
  "started_at": "2026-02-28T12:00:00Z",
  "estimated_completion": "2026-02-28T12:02:00Z"
}
```

**Response (200 OK) - Completed:**
```json
{
  "assessment_id": "assessment-001",
  "patient_id": "patient-001",
  "assessment_type": "diabetes_risk",
  "status": "completed",
  "results": {
    "risk_score": 0.72,
    "risk_category": "high",
    "confidence": 0.91,
    "key_indicators": [
      {
        "indicator": "fasting_glucose",
        "value": 185,
        "unit": "mg/dL",
        "risk_contribution": 0.35
      },
      {
        "indicator": "hrv_variability",
        "value": 45000,
        "unit": "ms²",
        "risk_contribution": 0.28
      }
    ],
    "recommendations": [
      "Schedule endocrinology consultation",
      "Monitor glucose levels daily",
      "Implement dietary changes"
    ],
    "nlg_summary": "Patient presents elevated diabetes risk (72%) based on fasting glucose of 185 mg/dL and reduced heart rate variability. Immediate endocrinology referral recommended."
  },
  "completed_at": "2026-02-28T12:02:15Z"
}
```

---

### Report Generation

#### POST /reports/generate

Generate clinical PDF report from assessment results.

**Request:**
```http
POST /reports/generate HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "assessment_id": "assessment-001",
  "report_type": "clinical_summary",
  "format": "pdf",
  "include_sections": [
    "executive_summary",
    "risk_assessment",
    "key_findings",
    "recommendations",
    "clinical_notes"
  ],
  "template": "standard",
  "recipient_type": "clinician",
  "signature_requested": true,
  "delivery_method": "email"
}
```

**Response (202 Accepted):**
```json
{
  "report_id": "report-001",
  "assessment_id": "assessment-001",
  "patient_id": "patient-001",
  "status": "generating",
  "report_type": "clinical_summary",
  "format": "pdf",
  "created_at": "2026-02-28T12:03:00Z",
  "estimated_completion": "2026-02-28T12:05:00Z",
  "download_url": "https://api.cortexa.local/api/v1/reports/report-001/pdf",
  "webhook_event": "report.generation.completed"
}
```

#### GET /reports/{reportId}

Get report status and metadata.

**Request:**
```http
GET /reports/report-001 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "report_id": "report-001",
  "assessment_id": "assessment-001",
  "patient_id": "patient-001",
  "report_type": "clinical_summary",
  "status": "ready",
  "format": "pdf",
  "file_size": 245000,
  "page_count": 8,
  "created_at": "2026-02-28T12:03:00Z",
  "completed_at": "2026-02-28T12:04:30Z",
  "signed": false,
  "signatures": [],
  "download_url": "https://api.cortexa.local/api/v1/reports/report-001/pdf",
  "metadata": {
    "title": "Clinical Assessment Report - John Doe",
    "author": "Dr. Sarah Wilson",
    "subject": "Diabetes Risk Assessment",
    "keywords": ["diabetes", "risk_assessment", "clinical"]
  }
}
```

#### GET /reports/{reportId}/pdf

Download PDF report (binary file).

**Request:**
```http
GET /reports/report-001/pdf HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="report-001.pdf"
Content-Length: 245000

[PDF binary data]
```

#### POST /reports/{reportId}/sign

Digitally sign a report (clinician approval).

**Request:**
```http
POST /reports/report-001/sign HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "clinician_id": "clinician-001",
  "signature_password": "SecurePassword123!",
  "notes": "Approved after reviewing with patient"
}
```

**Response (200 OK):**
```json
{
  "report_id": "report-001",
  "signed": true,
  "signature": {
    "clinician_id": "clinician-001",
    "clinician_name": "Dr. Sarah Wilson",
    "signed_at": "2026-02-28T12:10:00Z",
    "notes": "Approved after reviewing with patient",
    "signature_hash": "sha256_hash_of_signed_content"
  },
  "signatures": [
    {
      "clinician_id": "clinician-001",
      "signed_at": "2026-02-28T12:10:00Z"
    }
  ]
}
```

#### POST /reports/{reportId}/share

Share report with patient or other clinicians.

**Request:**
```http
POST /reports/report-001/share HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "recipients": [
    {
      "email": "john.doe@example.com",
      "recipient_type": "patient",
      "expires_in": 2592000  // 30 days in seconds
    },
    {
      "email": "specialist@hospital.com",
      "recipient_type": "clinician",
      "expires_in": 7776000  // 90 days in seconds
    }
  ],
  "message": "Please review your assessment results attached.",
  "require_mfa": true
}
```

**Response (200 OK):**
```json
{
  "report_id": "report-001",
  "shared_with": 2,
  "sharing_links": [
    {
      "recipient_email": "john.doe@example.com",
      "access_token": "share_token_abc123...",
      "expires_at": "2026-03-30T12:10:00Z",
      "shared_at": "2026-02-28T12:10:00Z"
    },
    {
      "recipient_email": "specialist@hospital.com",
      "access_token": "share_token_def456...",
      "expires_at": "2026-05-29T12:10:00Z",
      "shared_at": "2026-02-28T12:10:00Z"
    }
  ]
}
```

#### DELETE /reports/{reportId}

Archive or delete report (soft delete with 90-day retention).

**Request:**
```http
DELETE /reports/report-001 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "report_id": "report-001",
  "status": "archived",
  "archived_at": "2026-02-28T12:15:00Z",
  "retention_until": "2026-05-29T12:15:00Z",
  "message": "Report archived but remains for 90 days per HIPAA requirements"
}
```

---

## FastAPI Inference Engine

### Signal Validation & Preprocessing

#### POST /validate-signals

Validate signal quality before ML processing.

**Request:**
```http
POST /validate-signals HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "signals": {
    "ecg": [0.1, 0.2, 0.15, ...],
    "spo2": [95, 94, 95, 96, ...],
    "hrv": [45000, 48000, 42000, ...]
  },
  "sampling_rates": {
    "ecg": 100,
    "spo2": 1,
    "hrv": 1
  },
  "validation_level": "strict"
}
```

**Response (200 OK):**
```json
{
  "request_id": "val-req-001",
  "overall_quality": 0.94,
  "signals": {
    "ecg": {
      "quality": 0.96,
      "status": "valid",
      "samples": 256,
      "duration_seconds": 2.56,
      "missing_data": 0,
      "noise_level": 0.05,
      "warnings": []
    },
    "spo2": {
      "quality": 0.92,
      "status": "valid",
      "samples": 60,
      "missing_data": 0,
      "drift": false,
      "warnings": ["Low SpO2 reading at 90% baseline"]
    },
    "hrv": {
      "quality": 0.94,
      "status": "valid",
      "ectopic_beats": 2,
      "warnings": []
    }
  },
  "processing_ready": true
}
```

#### POST /preprocess

Preprocess and harmonize multimodal signals.

**Request:**
```http
POST /preprocess HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "signals": {
    "ecg": [0.1, 0.2, 0.15, ...],
    "spo2": [95, 94, 95, 96, ...],
    "hrv": [45000, 48000, 42000, ...],
    "eda": [0.5, 0.6, 0.55, ...],
    "temperature": 36.8,
    "accelerometer": [0.1, 0.2, 0.15, ...]
  },
  "preprocessing_config": {
    "normalize": true,
    "interpolate": true,
    "remove_baseline_wander": true,
    "filter_noise": true,
    "impute_missing": true,
    "target_sampling_rate": 100
  }
}
```

**Response (200 OK):**
```json
{
  "request_id": "preproc-001",
  "status": "success",
  "preprocessed_signals": {
    "ecg": [0.05, 0.15, 0.10, ...],
    "spo2": [0.92, 0.91, 0.93, ...],
    "hrv": [0.45, 0.48, 0.42, ...],
    "eda": [0.48, 0.58, 0.53, ...],
    "temperature": 0.89,
    "accelerometer": [0.08, 0.18, 0.13, ...]
  },
  "processing_steps": [
    "Baseline wander removed (Butterworth high-pass @0.5Hz)",
    "Noise filtered (signal-specific cutoff frequencies)",
    "Interpolated to 100Hz standard rate",
    "Missing values imputed (KNN, k=5)",
    "Z-score normalized (mean=0, std=1)"
  ],
  "quality_metrics": {
    "overall_quality_score": 0.94,
    "snr_improvement": 1.45,
    "missing_data_recovered": 2
  },
  "processing_time_ms": 234
}
```

#### POST /preprocess-image

Preprocess and normalize medical imaging (MRI/CT) for ML analysis.

**Request:**
```http
POST /preprocess-image HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="patient_mri_brain.dcm"
Content-Type: application/dicom

[DICOM binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="config"

{
  "imaging_type": "MRI",
  "modality": "MR",
  "body_part": "brain",
  "preprocessing_steps": [
    "skull_strip",
    "bias_field_correction",
    "normalize_intensity",
    "register_to_template",
    "extract_features"
  ],
  "normalization_method": "z-score",
  "target_dimensions": [192, 192, 192]
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (200 OK):**
```json
{
  "request_id": "img-preproc-001",
  "status": "success",
  "imaging_type": "MRI",
  "modality": "MR",
  "body_part": "brain",
  "preprocessing_result": {
    "original_dimensions": [512, 512, 128],
    "preprocessed_dimensions": [192, 192, 192],
    "voxel_spacing": [1.0, 1.0, 1.5],
    "data_type": "float32",
    "value_range": [-1.0, 1.0],
    "processing_steps_applied": [
      "Skull stripping (removed non-brain tissue)",
      "Bias field correction (N4ITK algorithm)",
      "Intensity normalization (z-score standardization)",
      "Rigid registration to MNI152 template",
      "Resampling to isotropic resolution"
    ]
  },
  "image_quality": {
    "contrast_to_noise_ratio": 42.1,
    "signal_to_noise_ratio": 38.5,
    "artifact_level": "minimal",
    "preprocessing_quality_score": 0.97
  },
  "roi_analysis": {
    "rois_detected": [
      {
        "name": "gray_matter",
        "volume_mm3": 620000,
        "mask_available": true
      },
      {
        "name": "white_matter",
        "volume_mm3": 480000,
        "mask_available": true
      },
      {
        "name": "ventricles",
        "volume_mm3": 25000,
        "mask_available": true
      }
    ]
  },
  "extracted_features": {
    "texture_features": {
      "glcm_contrast": 0.34,
      "glcm_correlation": 0.82,
      "lbp_histogram": [0.05, 0.12, 0.15, ..., 0.03]
    },
    "shape_features": {
      "volume_asymmetry": 0.08,
      "surface_area_ratio": 1.02
    }
  },
  "storage_path": "s3://cortexa-imaging/processed/img-preproc-001/mri_preprocessed.nii.gz",
  "processing_time_seconds": 125
}
```

#### POST /validate-image-quality

Validate medical imaging quality before analysis.

**Request:**
```http
POST /validate-image-quality HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="patient_mri_brain.dcm"
Content-Type: application/dicom

[DICOM binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="validation_criteria"

{
  "minimum_signal_to_noise_ratio": 35,
  "maximum_artifact_level": "moderate",
  "minimum_image_quality_score": 0.80,
  "check_motion_artifacts": true,
  "check_aliasing": true
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (200 OK):**
```json
{
  "validation_id": "img-val-001",
  "is_valid": true,
  "overall_quality_score": 0.96,
  "quality_metrics": {
    "signal_to_noise_ratio": 42.1,
    "contrast_to_noise_ratio": 38.5,
    "artifact_level": "minimal",
    "motion_artifact_detected": false,
    "aliasing_detected": false,
    "ghosting_level": "none"
  },
  "dicom_validation": {
    "is_dicom_compliant": true,
    "file_integrity": "verified",
    "required_tags_present": true,
    "missing_tags": [],
    "patient_id_matches": true
  },
  "anatomical_validation": {
    "anatomy_recognized": true,
    "modality": "MR",
    "body_part": "brain",
    "sequence_type": "T1_weighted",
    "anatomical_landmark_detection": {
      "landmarks_detected": 12,
      "landmarks_expected": 12,
      "registration_confidence": 0.98
    }
  },
  "processing_readiness": {
    "can_preprocess": true,
    "can_extract_features": true,
    "can_run_prediction": true,
    "recommended_preprocessing": [
      "Skull stripping",
      "Bias field correction",
      "Intensity normalization"
    ]
  },
  "warnings": [],
  "recommendations": ["Image quality is excellent; proceed with confidence"]
}
```

---

### ML Predictions

#### POST /predict

Generate ML predictions for clinical assessment.

**Request:**
```http
POST /predict HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "assessment_id": "assessment-001",
  "clinical_condition": "diabetes",
  "preprocessed_signals": {
    "ecg": [0.05, 0.15, 0.10, ...],
    "spo2": [0.92, 0.91, 0.93, ...],
    "hrv": [0.45, 0.48, 0.42, ...],
    "temperature": 0.89,
    "activity": 0.72
  },
  "include_interpretability": true,
  "confidence_threshold": 0.85
}
```

**Response (200 OK):**
```json
{
  "assessment_id": "assessment-001",
  "prediction_id": "pred-001",
  "clinical_condition": "diabetes",
  "status": "success",
  "prediction": {
    "risk_score": 0.72,
    "risk_category": "high",
    "confidence": 0.91,
    "probability_distribution": {
      "low_risk": 0.08,
      "moderate_risk": 0.20,
      "high_risk": 0.72
    }
  },
  "feature_importance": {
    "fasting_glucose": 0.35,
    "hrv_variability": 0.28,
    "weight_change": 0.18,
    "family_history": 0.12,
    "activity_level": 0.07
  },
  "contributing_factors": [
    {
      "factor": "HRV Variability (45,000 ms²)",
      "contribution": "Elevated risk",
      "clinical_significance": "Indicates autonomic nervous system dysfunction"
    },
    {
      "factor": "Fasting Glucose (185 mg/dL)",
      "contribution": "Primary risk indicator",
      "clinical_significance": "Above normal range (100-125 mg/dL prediabetic range)"
    }
  ],
  "model_metadata": {
    "model_name": "Team-2-CNN-LSTM-v2.3",
    "training_date": "2026-01-15",
    "n_training_samples": 5000,
    "accuracy": 0.94,
    "auc_roc": 0.96
  },
  "processing_time_ms": 145
}
```

#### POST /predict-multi-condition

Predict multiple conditions simultaneously (ensemble approach).

**Request:**
```http
POST /predict-multi-condition HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "assessment_id": "assessment-001",
  "clinical_conditions": [
    "sleep_apnea",
    "diabetes",
    "afib",
    "burnout",
    "tumor"
  ],
  "preprocessed_signals": { ... }
}
```

**Response (200 OK):**
```json
{
  "assessment_id": "assessment-001",
  "predictions": [
    {
      "clinical_condition": "sleep_apnea",
      "risk_score": 0.34,
      "risk_category": "moderate",
      "confidence": 0.88
    },
    {
      "clinical_condition": "diabetes",
      "risk_score": 0.72,
      "risk_category": "high",
      "confidence": 0.91
    },
    {
      "clinical_condition": "afib",
      "risk_score": 0.18,
      "risk_category": "low",
      "confidence": 0.94
    },
    {
      "clinical_condition": "burnout",
      "risk_score": 0.61,
      "risk_category": "high",
      "confidence": 0.82
    },
    {
      "clinical_condition": "tumor",
      "risk_score": 0.05,
      "risk_category": "very_low",
      "confidence": 0.97
    }
  ],
  "processing_time_ms": 580,
  "teams_involved": 5
}
```

#### POST /predict-image

Generate ML predictions for medical imaging (tumor classification, lesion detection).

**Request:**
```http
POST /predict-image HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="patient_mri_preprocessed.nii.gz"
Content-Type: application/gzip

[Preprocessed NIfTI image binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="prediction_config"

{
  "assessment_id": "assessment-001",
  "clinical_condition": "tumor",
  "imaging_modality": "MRI",
  "body_part": "brain",
  "model_version": "Team5-2D-CNN-v3.1",
  "include_localization": true,
  "include_attention_maps": true,
  "confidence_threshold": 0.80
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (200 OK):**
```json
{
  "assessment_id": "assessment-001",
  "prediction_id": "img-pred-001",
  "imaging_modality": "MRI",
  "body_part": "brain",
  "clinical_condition": "tumor",
  "status": "success",
  "prediction": {
    "classification": "glioblastoma",
    "risk_score": 0.87,
    "confidence": 0.94,
    "classification_probabilities": {
      "healthy_brain": 0.03,
      "benign_tumor": 0.05,
      "glioma_low_grade": 0.08,
      "glioma_high_grade": 0.87,
      "meningioma": 0.02,
      "pituitary_adenoma": 0.01
    }
  },
  "lesion_analysis": {
    "lesions_detected": 1,
    "lesions": [
      {
        "lesion_id": "lesion-001",
        "classification": "glioblastoma",
        "confidence": 0.94,
        "location": {
          "region": "right_temporal_lobe",
          "coordinates": {"x": 320, "y": 280, "z": 85},
          "volume_mm3": 12400
        },
        "characteristics": {
          "shape": "irregular",
          "boundary": "poorly_defined",
          "heterogeneity": "high",
          "central_necrosis": true,
          "edema_extent": "marked"
        },
        "enhancement_pattern": "rim_enhancement"
      }
    ]
  },
  "risk_stratification": {
    "grade": "WHO_Grade_IV",
    "prognosis": "poor",
    "recommended_action": "urgent_neurosurgery_consultation",
    "urgency_level": "critical",
    "time_to_treatment": "within_48_hours"
  },
  "feature_importance": {
    "contrast_enhancement": 0.35,
    "perilesional_edema": 0.28,
    "central_necrosis": 0.18,
    "lesion_heterogeneity": 0.12,
    "size_volume": 0.07
  },
  "spatial_localization": {
    "bounding_box": {
      "x": [280, 360],
      "y": [240, 320],
      "z": [65, 105]
    },
    "saliency_map_url": "https://api.cortexa.local/imaging/img-pred-001/saliency.nii.gz",
    "attention_map_url": "https://api.cortexa.local/imaging/img-pred-001/attention.json"
  },
  "comparative_analysis": {
    "has_prior_exam": true,
    "prior_exam_date": "2025-11-15",
    "progression_since_prior": true,
    "interval_growth_percent": 18.5,
    "growth_rate_mm3_per_day": 3.2,
    "progression_assessment": "rapid"
  },
  "model_metadata": {
    "model_name": "Team-5-2D-CNN-v3.1",
    "architecture": "3D_Convolutional_Neural_Network_with_ResNet_backbone",
    "training_data_samples": 8500,
    "training_data_institutions": 15,
    "model_accuracy": 0.97,
    "auc_roc": 0.98,
    "sensitivity": 0.96,
    "specificity": 0.98,
    "last_updated": "2026-01-20"
  },
  "clinical_recommendations": [
    "URGENT: Neurosurgery consultation within 24 hours",
    "Recommend pre-operative MRI with spectroscopy",
    "Consider functional MRI (fMRI) for motor/language mapping",
    "Baseline cognitive assessment before intervention",
    "Genetic testing (IDHE1 mutation status)"
  ],
  "processing_time_seconds": 45,
  "warning": "Early detection algorithm detected aggressive tumor characteristics requiring immediate specialist evaluation"
}
```

#### POST /predict-multi-site-imaging

Process multi-site/multi-slice medical imaging (e.g., whole brain MRI series).

**Request:**
```http
POST /predict-multi-site-imaging HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="files"; filename="slice_001.dcm"
Content-Type: application/dicom

[DICOM slice 1 binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="files"; filename="slice_002.dcm"
Content-Type: application/dicom

[DICOM slice 2 binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
...
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="config"

{
  "assessment_id": "assessment-001",
  "imaging_modality": "MRI",
  "clinical_condition": "tumor",
  "aggregation_method": "attention_weighted_pooling",
  "report_level": "detailed"
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (200 OK):**
```json
{
  "assessment_id": "assessment-001",
  "multi_site_prediction_id": "img-pred-multi-001",
  "total_slices_processed": 128,
  "volume_analysis": {
    "overall_classification": "glioblastoma",
    "overall_risk_score": 0.88,
    "overall_confidence": 0.95,
    "volume_extent_mm3": 12400,
    "percentage_brain_volume": 0.85
  },
  "slice_by_slice_analysis": [
    {
      "slice_number": 45,
      "position_mm": 67.5,
      "classification": "lesion_present",
      "confidence": 0.96,
      "tumor_area_mm2": 145.3,
      "attention_weight": 0.95
    },
    {
      "slice_number": 46,
      "position_mm": 69.0,
      "classification": "lesion_present",
      "confidence": 0.98,
      "tumor_area_mm2": 162.5,
      "attention_weight": 0.98
    },
    {
      "slice_number": 47,
      "position_mm": 70.5,
      "classification": "lesion_present",
      "confidence": 0.94,
      "tumor_area_mm2": 155.2,
      "attention_weight": 0.92
    }
  ],
  "most_suspicious_slice": {
    "slice_number": 46,
    "confidence": 0.98,
    "thumbnail_url": "https://api.cortexa.local/imaging/img-pred-multi-001/slice_46.jpg"
  },
  "volumetric_reconstruction": {
    "reconstruction_url": "https://api.cortexa.local/imaging/img-pred-multi-001/3d_reconstruction.obj",
    "visualization_format": "STL",
    "tumor_surface_area_mm2": 4520.3,
    "tumor_volume_mm3": 12400
  },
  "processing_time_seconds": 120,
  "can_generate_report": true
}
```

---

## Encryption Service API

### Data Encryption/Decryption

#### POST /encrypt

Encrypt sensitive PHI data.

**Request:**
```http
POST /encrypt HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "plaintext": "Patient name: John Doe, MRN: MRN-2024-001",
  "data_type": "patient_name",
  "key_id": "prod-key-001"
}
```

**Response (200 OK):**
```json
{
  "encrypted_data": "base64_encoded_ciphertext...",
  "iv": "base64_encoded_iv...",
  "tag": "base64_encoded_auth_tag...",
  "key_id": "prod-key-001",
  "algorithm": "AES-256-GCM",
  "encrypted_at": "2026-02-28T12:00:00Z"
}
```

#### POST /decrypt

Decrypt sensitive PHI data.

**Request:**
```http
POST /decrypt HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "encrypted_data": "base64_encoded_ciphertext...",
  "iv": "base64_encoded_iv...",
  "tag": "base64_encoded_auth_tag...",
  "key_id": "prod-key-001"
}
```

**Response (200 OK):**
```json
{
  "plaintext": "Patient name: John Doe, MRN: MRN-2024-001",
  "decrypted_at": "2026-02-28T12:00:00Z",
  "integrity_verified": true
}
```

#### POST /hash

Compute SHA-256 HMAC for integrity verification.

**Request:**
```http
POST /hash HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "data": "Patient name: John Doe, MRN: MRN-2024-001",
  "key_id": "hmac-key-001"
}
```

**Response (200 OK):**
```json
{
  "hash": "a3f2c981d50e2c4f8e9d3a1b7c6e5f4d2a1b3c5e7f9d1e3a5b7c9d1e3f5a7b",
  "algorithm": "SHA-256-HMAC",
  "hashed_at": "2026-02-28T12:00:00Z"
}
```

---

## PDF Report Generation

### Detailed Report Structure

#### Clinical Summary Report

**Sections:**
1. **Executive Summary** - High-level findings and recommendations
2. **Patient Demographics** - De-identified patient information
3. **Assessment Details** - Conditions evaluated, date/time
4. **Risk Scores** - Primary risk score with clinical interpretation
5. **Key Findings** - Top contributing factors with clinical context
6. **Recommendations** - Actionable next steps for clinician
7. **Model Information** - ML model versions and accuracy metrics
8. **Digital Signature** - Secure clinician approval
9. **Patient Consent** - Privacy acknowledgment
10. **References** - Clinical guidelines and sources

#### Report Generation Workflow

```
POST /reports/generate
        │
        ▼
┌─────────────────────────────────────┐
│ 1. Validate report request          │
│    - Check permissions              │
│    - Verify assessment exists       │
│    - Check required sections        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Extract assessment data          │
│    - Load predictions               │
│    - Retrieve vital signs           │
│    - Get medical history            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Generate report content          │
│    - NLG summaries                  │
│    - Format recommendations         │
│    - Create visualizations          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Render PDF                       │
│    - Apply template styling         │
│    - Add headers/footers            │
│    - Embed charts/images            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Sign & encrypt (optional)        │
│    - Compute digital signature      │
│    - Encrypt with recipient key     │
│    - Store signature metadata       │
└──────────────┬──────────────────────┘
               │
               ▼
        Report Ready
      (storage + retrieval)
```

#### PDF Header Example

```
╔═══════════════════════════════════════════════════════════════╗
║                    CLINICAL ASSESSMENT REPORT                 ║
║                         CORTEXA PLATFORM                      ║
║                    Multimodal Deep Learning Framework         ║
╚═══════════════════════════════════════════════════════════════╝

Report ID:           report-001
Assessment ID:       assessment-001
Generated:           February 28, 2026 12:04:30 UTC
Patient MRN:         MRN-2024-001 [ENCRYPTED]
Clinician:           Dr. Sarah Wilson (ID: clinician-001)
```

#### PDF Report Content Example

```
EXECUTIVE SUMMARY
─────────────────

John Doe (Age 45, Male) underwent a comprehensive multimodal clinical 
assessment using the Cortexa platform. Analysis of physiological signals 
and medical history indicates HIGH RISK (72%) for Type 2 Diabetes.

RISK ASSESSMENT RESULTS
──────────────────────

Primary Condition:     Diabetes Risk
Risk Score:            0.72 (HIGH RISK)
Confidence:            91%

Risk Stratification:
  • Low (0-0.33):      8%
  • Moderate (0.33-0.66):  20%
  • High (0.66-1.0):   72%

KEY CONTRIBUTING FACTORS
────────────────────────

1. Fasting Glucose: 185 mg/dL
   - Exceeds normal range (70-100 mg/dL)
   - Indicates impaired fasting glucose metabolism
   - Risk Contribution: 35%

2. Heart Rate Variability: 45,000 ms²
   - Below normal range (50,000-100,000 ms²)
   - Suggests autonomic dysfunction
   - Associated with metabolic syndrome
   - Risk Contribution: 28%

3. Recent Weight Change: +8 lbs (3.6 kg)
   - Over 6-month period
   - Accelerated weight gain is risk factor
   - Risk Contribution: 18%

CLINICAL RECOMMENDATIONS
────────────────────────

IMMEDIATE ACTIONS (Next 1-2 weeks):
✓ Schedule endocrinology consultation
✓ Order comprehensive metabolic panel (CMP)
✓ Conduct oral glucose tolerance test (OGTT)

SHORT-TERM INTERVENTIONS (1-3 months):
✓ Implement dietary modifications (Mediterranean diet)
✓ Monitor fasting glucose daily
✓ Increase physical activity to 150 min/week
✓ Follow-up assessment in 4 weeks

LONG-TERM MONITORING (3+ months):
✓ HbA1C testing every 3 months
✓ Annual comprehensive physical
✓ Metabolic panel every 6 months

MODEL INFORMATION
────────────────

Model Name:          Team-2-CNN-LSTM-v2.3
Condition Focus:     Anemia, Diabetes Risk Detection
Training Samples:    5,000 patients
Model Accuracy:      94%
AUC-ROC Score:       0.96
Last Updated:        January 15, 2026

MODEL ARCHITECTURE:
- Input: Multimodal signals (ECG, SpO2, HRV, activity)
- Layer 1: Spectral CNN (extract frequency features)
- Layer 2: LSTM (model long-term dependencies)
- Layer 3: Dense classification network
- Output: Risk probability + confidence interval

CLINICAL NOTES
──────────────

[Clinician Notes - Optional Section]
"Patient appears to be at pre-diabetes threshold. Family history 
of Type 2 Diabetes supports intervention. Recommend aggressive 
lifestyle modification before pharmaceutical intervention."

- Dr. Sarah Wilson
- February 28, 2026 12:10:00 UTC
```

---

## Error Handling

### Error Response Format

All errors follow consistent format:

```json
{
  "error": "Descriptive error message",
  "error_code": "ERROR_CODE_CONSTANT",
  "status_code": 400,
  "timestamp": "2026-02-28T12:00:00Z",
  "request_id": "req-abc123",
  "details": {
    "field": "clinical_condition",
    "issue": "Invalid condition type",
    "allowed_values": ["sleep_apnea", "diabetes", "afib", "burnout", "tumor"]
  }
}
```

### Common Error Codes

| Status | Error Code | Meaning |
|--------|-----------|---------|
| 400 | `INVALID_REQUEST` | Malformed request body |
| 400 | `VALIDATION_ERROR` | Input validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource already exists |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily down |

### Example Error Response

**Request (Missing required field):**
```http
POST /reports/generate HTTP/1.1
Content-Type: application/json

{
  "report_type": "clinical_summary"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Missing required field: assessment_id",
  "error_code": "VALIDATION_ERROR",
  "status_code": 400,
  "timestamp": "2026-02-28T12:00:00Z",
  "request_id": "req-xyz789",
  "details": {
    "field": "assessment_id",
    "issue": "Required field missing",
    "expected_type": "string (UUID format)"
  }
}
```

---

## Rate Limiting

### Rate Limit Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1709080800
X-RateLimit-RetryAfter: 3600
```

### Rate Limits by Endpoint Type

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 5 requests | 15 minutes |
| Patient queries | 100 requests | 1 hour |
| Assessment submission | 10 requests | 1 hour |
| Report generation | 20 requests | 1 hour |
| ML Predictions | 50 requests | 1 hour |
| Bulk operations | 2 requests | 1 hour |

---

## OpenAPI 3.0 Specification

### YAML Definition

```yaml
openapi: 3.0.0
info:
  title: Cortexa Clinical API
  version: 1.0.0
  description: RESTful API for multimodal clinical assessment and reporting
  contact:
    name: Cortexa Support
    email: support@cortexa.clinical
  license:
    name: Apache-2.0

servers:
  - url: https://api.cortexa.local/api/v1
    description: Production server
  - url: https://staging-api.cortexa.local/api/v1
    description: Staging server
  - url: http://localhost:3000/api/v1
    description: Development server

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []

paths:
  /auth/login:
    post:
      summary: Authenticate user
      operationId: loginUser
      tags:
        - Authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        '200':
          description: Login successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        '401':
          description: Invalid credentials

  /patients/{patientId}:
    get:
      summary: Get patient details
      operationId: getPatient
      tags:
        - Patients
      parameters:
        - name: patientId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Patient details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PatientDetails'
        '404':
          description: Patient not found

  /reports/generate:
    post:
      summary: Generate clinical PDF report
      operationId: generateReport
      tags:
        - Reports
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReportGenerationRequest'
      responses:
        '202':
          description: Report generation started
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReportGenerationResponse'
        '400':
          description: Invalid request

  /reports/{reportId}/pdf:
    get:
      summary: Download PDF report
      operationId: downloadReport
      tags:
        - Reports
      parameters:
        - name: reportId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: PDF file
          content:
            application/pdf: {}
        '404':
          description: Report not found

  /predict:
    post:
      summary: Generate ML prediction
      operationId: predict
      tags:
        - Predictions
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PredictionRequest'
      responses:
        '200':
          description: Prediction results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PredictionResponse'
        '400':
          description: Invalid signals

components:
  schemas:
    LoginRequest:
      type: object
      required:
        - email
        - password
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          format: password
        mfa_code:
          type: string
          pattern: '^\d{6}$'

    LoginResponse:
      type: object
      properties:
        access_token:
          type: string
        refresh_token:
          type: string
        token_type:
          type: string
          enum: [Bearer]
        expires_in:
          type: integer
        user:
          $ref: '#/components/schemas/User'

    PatientDetails:
      type: object
      properties:
        id:
          type: string
        mrn:
          type: string
        name:
          type: string
        age:
          type: integer
        medical_history:
          type: object
          properties:
            conditions:
              type: array
              items:
                type: string
            medications:
              type: array
              items:
                type: string

    ReportGenerationRequest:
      type: object
      required:
        - assessment_id
        - report_type
      properties:
        assessment_id:
          type: string
        report_type:
          type: string
          enum: [clinical_summary, detailed_analysis, risk_stratification]
        format:
          type: string
          enum: [pdf]
        include_sections:
          type: array
          items:
            type: string
        template:
          type: string
        signature_requested:
          type: boolean

    ReportGenerationResponse:
      type: object
      properties:
        report_id:
          type: string
        status:
          type: string
          enum: [generating, ready, error]
        download_url:
          type: string
        estimated_completion:
          type: string
          format: date-time

    PredictionRequest:
      type: object
      required:
        - assessment_id
        - clinical_condition
        - preprocessed_signals
      properties:
        assessment_id:
          type: string
        clinical_condition:
          type: string
          enum: [sleep_apnea, diabetes, afib, burnout, tumor]
        preprocessed_signals:
          type: object

    PredictionResponse:
      type: object
      properties:
        assessment_id:
          type: string
        prediction:
          type: object
          properties:
            risk_score:
              type: number
              minimum: 0
              maximum: 1
            risk_category:
              type: string
              enum: [very_low, low, moderate, high, very_high]
            confidence:
              type: number
        feature_importance:
          type: object
          additionalProperties:
            type: number

    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        role:
          type: string
        name:
          type: string
```

---

## Webhook Events

### Report Generation Completion

When report generation completes, the Express Orchestrator sends webhook notification:

```json
{
  "event": "report.generation.completed",
  "timestamp": "2026-02-28T12:05:00Z",
  "data": {
    "report_id": "report-001",
    "assessment_id": "assessment-001",
    "status": "ready",
    "file_size": 245000,
    "page_count": 8,
    "download_url": "https://api.cortexa.local/api/v1/reports/report-001/pdf"
  }
}
```

### Assessment Completion

When assessment processing completes:

```json
{
  "event": "assessment.completed",
  "timestamp": "2026-02-28T12:02:15Z",
  "data": {
    "assessment_id": "assessment-001",
    "patient_id": "patient-001",
    "status": "completed",
    "risk_score": 0.72,
    "risk_category": "high"
  }
}
```

---

## Data Upload Workflows

### CSV Timeseries Upload Workflow

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Prepare CSV File                                    │
│  - Ensure RFC 3339 timestamps (monotonic increasing)         │
│  - Include at least 2 physiological signals                  │
│  - Validate numeric values (no NaN, Inf)                     │
│  - Maximum 1,000,000 rows per file                           │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: Optional - Dry-Run Validation                       │
│  POST /validate-csv                                          │
│  Returns validation report without uploading                 │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: Upload File                                         │
│  POST /patients/{patientId}/signals/upload                   │
│  - Multipart form-data with CSV and metadata                 │
│  - Returns upload_id and status: "processing"                │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: Poll Status                                         │
│  GET /uploads/{uploadId}                                     │
│  - Query every 2-5 seconds until completion                  │
│  - Monitor progress percentage                               │
│  - Check for validation errors/warnings                      │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 5: Use in Assessment                                   │
│  POST /patients/{patientId}/assessments                      │
│  - Reference upload_id in data_source                        │
│  - Signals automatically preprocessed                        │
│  - Results available after inference                         │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
          Assessment Complete
     (results in GET /assessments/{assessmentId})
```

**CSV Upload Example:**
```bash
# 1. Validate CSV first (optional)
curl -X POST https://api.cortexa.local/api/v1/validate-csv \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_signals.csv"

# 2. Upload CSV file
UPLOAD_RESPONSE=$(curl -X POST \
  https://api.cortexa.local/api/v1/patients/patient-001/signals/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_signals.csv" \
  -F 'metadata={"signal_source":"wearable_device"}')

UPLOAD_ID=$(echo $UPLOAD_RESPONSE | jq -r '.upload_id')

# 3. Poll until complete
while true; do
  STATUS=$(curl -X GET \
    https://api.cortexa.local/api/v1/uploads/$UPLOAD_ID \
    -H "Authorization: Bearer $TOKEN")
  
  if [[ $(echo $STATUS | jq -r '.status') == "ready" ]]; then
    echo "Upload complete!"
    break
  fi
  sleep 3
done

# 4. Create assessment using uploaded file
curl -X POST https://api.cortexa.local/api/v1/patients/patient-001/assessments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_type": "diabetes_risk",
    "data_source": "uploaded_files",
    "uploaded_files": {
      "signals_upload_id": "'$UPLOAD_ID'"
    }
  }'
```

---

### Medical Imaging Upload Workflow

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Prepare Imaging Files                               │
│  - DICOM (.dcm) primary format                               │
│  - NIfTI (.nii.gz) for volumetric data                       │
│  - Maximum file size: 100 MB per file                        │
│  - Required DICOM tags: Patient ID, Study Date, Modality     │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: Optional - Quality Check                            │
│  POST /validate-image-quality                                │
│  - DICOM compliance verification                             │
│  - Signal-to-noise ratio assessment                          │
│  - Motion/artifact detection                                 │
│  - Anatomical validation                                     │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: Upload Imaging File                                 │
│  POST /patients/{patientId}/imaging/upload                   │
│  - Multipart form-data with DICOM/NIfTI and metadata         │
│  - Returns upload_id and status: "processing"                │
│  - Background processing begins automatically                │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: Poll Status & Preprocessing                         │
│  GET /imaging/{uploadId}                                     │
│  - DICOM header parsing                                      │
│  - Image decompression                                       │
│  - Preprocessing pipeline (skull strip, bias correction)     │
│  - Returns when status: "ready"                              │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 5: Run ML Prediction (Optional)                        │
│  POST /predict-image or /predict-multi-site-imaging          │
│  - High-resolution 3D analysis                               │
│  - Tumor classification, lesion detection                    │
│  - Spatial localization with attention maps                  │
│  - Risk stratification for clinical decision support         │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 6: Use in Assessment                                   │
│  POST /patients/{patientId}/assessments                      │
│  - Reference imaging_upload_id                               │
│  - Multimodal analysis (imaging + physiological signals)     │
│  - Integrated risk scores and recommendations                │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
       Assessment with Imaging Complete
   (results in GET /assessments/{assessmentId})
```

**Imaging Upload Example:**
```bash
# 1. Check image quality first
curl -X POST https://api.cortexa.local/api/v1/validate-image-quality \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_mri_brain.dcm"

# 2. Upload DICOM file
IMG_UPLOAD=$(curl -X POST \
  https://api.cortexa.local/api/v1/patients/patient-001/imaging/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_mri_brain.dcm" \
  -F 'metadata={
    "imaging_type": "MRI",
    "modality": "MR",
    "body_part": "brain",
    "clinical_indication": "Rule out tumor"
  }')

IMG_UPLOAD_ID=$(echo $IMG_UPLOAD | jq -r '.upload_id')

# 3. Poll preprocessing status
while true; do
  IMG_STATUS=$(curl -X GET \
    https://api.cortexa.local/api/v1/imaging/$IMG_UPLOAD_ID \
    -H "Authorization: Bearer $TOKEN")
  
  if [[ $(echo $IMG_STATUS | jq -r '.status') == "ready" ]]; then
    echo "Imaging preprocessing complete!"
    break
  fi
  sleep 5
done

# 4. Optional: Run tumor detection
curl -X POST https://api.cortexa.local/api/v1/predict-image \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_mri_preprocessed.nii.gz" \
  -F 'prediction_config={
    "clinical_condition": "tumor",
    "include_localization": true,
    "include_attention_maps": true
  }'

# 5. Create assessment with both signals and imaging
curl -X POST https://api.cortexa.local/api/v1/patients/patient-001/assessments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_type": "tumor",
    "data_source": "uploaded_files",
    "uploaded_files": {
      "signals_upload_id": "'$UPLOAD_ID'",
      "imaging_upload_id": "'$IMG_UPLOAD_ID'"
    }
  }'
```

---

## Combined Multimodal Analysis Workflow

```
                    Patient Data
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    Physiological    Medical Imaging   Clinical Context
    Signals (CSV)   (MRI/CT DICOM)    (Demographics)
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐   ┌─────────┐   ┌─────────────┐
    │ Upload  │   │ Upload  │   │ API Input   │
    │ CSV     │   │ DICOM   │   │ (Direct)    │
    └────┬────┘   └────┬────┘   └──────┬──────┘
         │             │               │
         ▼             ▼               ▼
    ┌──────────────────────────────────────┐
    │  Validation & Preprocessing         │
    │  - Signal quality checking          │
    │  - Image DICOM validation           │
    │  - Normalization & alignment        │
    └────────────┬─────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
         ▼               ▼
    ┌─────────┐   ┌──────────┐
    │ Feature │   │ Feature  │
    │ Extract │   │ Extract  │
    │ (Signal)│   │ (Image)  │
    └────┬────┘   └───┬──────┘
         │            │
         └──────┬─────┘
                ▼
         ┌────────────────┐
         │ Feature Fusion │
         │ (Attention-    │
         │  weighted)     │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Team-Based ML      │
         │ · Sleep Apnea      │
         │ · Diabetes         │
         │ · AFib             │
         │ · Burnout          │
         │ · Tumor Detection  │
         └────────┬───────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Ensemble        │
         │ Predictions     │
         │ (5 conditions)  │
         └────────┬────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Risk Scores &    │
         │ Recommendations  │
         │ NLG Summary      │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ PDF Report Gen   │
         │ · Clinical       │
         │ · Visualizations │
         │ · Signatures     │
         └────────┬─────────┘
                  │
                  ▼
            Clinician Report
        (for patient/expert review)
```

---

## Testing API Endpoints

### cURL Examples

**Login:**
```bash
curl -X POST https://api.cortexa.local/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "clinician@cortexa.clinical",
    "password": "SecurePassword123!"
  }'
```

**Get Patient:**
```bash
curl -X GET https://api.cortexa.local/api/v1/patients/patient-001 \
  -H "Authorization: Bearer $TOKEN"
```

**Generate Report:**
```bash
curl -X POST https://api.cortexa.local/api/v1/reports/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_id": "assessment-001",
    "report_type": "clinical_summary",
    "format": "pdf"
  }'
```

**Download PDF:**
```bash
curl -X GET https://api.cortexa.local/api/v1/reports/report-001/pdf \
  -H "Authorization: Bearer $TOKEN" \
  -o report-001.pdf
```

**Upload CSV Signals:**
```bash
curl -X POST https://api.cortexa.local/api/v1/patients/patient-001/signals/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_signals_2026-02-28.csv" \
  -F 'metadata={
    "signal_source": "wearable_device",
    "device_type": "Apple_Watch",
    "sampling_rate_hz": 1
  }'
```

**Upload MRI Image:**
```bash
curl -X POST https://api.cortexa.local/api/v1/patients/patient-001/imaging/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_mri_brain.dcm" \
  -F 'metadata={
    "imaging_type": "MRI",
    "modality": "MR",
    "body_part": "brain",
    "clinical_indication": "Rule out tumor"
  }'
```

**Check Upload Status:**
```bash
curl -X GET https://api.cortexa.local/api/v1/uploads/upload-001 \
  -H "Authorization: Bearer $TOKEN"
```

**Validate Image Quality:**
```bash
curl -X POST https://api.cortexa.local/api/v1/validate-image-quality \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_mri_brain.dcm" \
  -F 'validation_criteria={
    "minimum_signal_to_noise_ratio": 35,
    "check_motion_artifacts": true
  }'
```

**Run Image-Based Prediction:**
```bash
curl -X POST https://api.cortexa.local/api/v1/predict-image \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@patient_mri_preprocessed.nii.gz" \
  -F 'prediction_config={
    "clinical_condition": "tumor",
    "include_localization": true,
    "confidence_threshold": 0.80
  }'
```

**Create Assessment with Uploaded Files:**
```bash
curl -X POST https://api.cortexa.local/api/v1/patients/patient-001/assessments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_type": "tumor",
    "data_source": "uploaded_files",
    "uploaded_files": {
      "signals_upload_id": "upload-001",
      "imaging_upload_id": "img-upload-001"
    },
    "additional_context": {
      "symptoms": ["headaches", "vision_changes"],
      "clinical_indication": "Rule out intracranial lesion"
    }
  }'
```

---

## Support & Documentation

**API Documentation**: https://api-docs.cortexa.local  
**OpenAPI Interactive**: https://swagger-ui.cortexa.local  
**Postman Collection**: Available on request

---

**Last Updated**: February 28, 2026  
**API Version**: 1.0.0  
**Status**: Production Ready  
**SLA**: 99.9% uptime guarantee
