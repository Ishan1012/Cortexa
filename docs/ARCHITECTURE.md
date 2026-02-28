# Cortexa - Multimodal Clinical Risk Assessment Framework
## Architecture Documentation

## Executive Summary

Cortexa is a pioneering, unified multimodal deep learning framework designed to revolutionize clinical diagnostics by seamlessly integrating disparate biomedical data streams. Unlike traditional siloed diagnostic approaches that analyze physiological signals (ECG, SpO2, HRV, EDA, TEMP) and medical imaging (MRI, CT) independently, Cortexa's architecture recognizes and leverages the intricate synergistic relationships between different physiological systems.

The platform enables simultaneous prediction of multiple high-impact clinical conditions through a state-of-the-art deep neural network architecture deployed across a modern, decoupled microservice infrastructure. This innovative approach promises earlier disease detection, more personalized risk stratification, and ultimately, improved patient outcomes.

### Target Clinical Conditions
- **Cardiopulmonary**: Sleep Apnea, Atrial Fibrillation (AFib)
- **Metabolic/Endocrine**: Early-stage Diabetes Risk Assessment
- **Psychological/Neurological**: Chronic Stress, Burnout Detection, Brain Tumor Identification
- **Automated Clinical Reporting**: Structured, human-readable diagnostic narratives

## Overview

Cortexa is engineered as a comprehensive, web-centric multimodal analysis system that bridges the critical gap between raw biomedical sensor data and truly actionable medical insights. The system is built with a resilient microservices architecture, combining a Next.js frontend with specialized backend services (Express Orchestrator, FastAPI Inference Engine, and Encryption API), a sophisticated team-based ML pipeline, and analytics dashboards for clinical decision support.

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Clinical User Interface                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │              Next.js Web Application (Frontend)                    │  │
│  │  • Data Stream Initialization & Real-Time Visualization            │  │
│  │  • Secure Clinical Reporting & Alert Management                    │  │
│  │  • React 19 + TypeScript + Tailwind CSS                            │  │
│  └──────────────────────────┬─────────────────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────────────┘
                              │ HTTPS/Encrypted
                              │
        ┌─────────────────────▼───────────────────────┐
        │   Express.js Orchestrator (API Gateway)     │
        │  • Authentication & Authorization (RBAC)    │
        │  • User & Session Management                │
        │  • Feedback & Alerts Service                │
        │  • Database Interface Layer                 │
        │  • Load Balancing & Traffic Management      │
        └─────────┬─────────────────────┬─────────────┘
                  │                     │
        ┌─────────▼──────────┐  ┌───────▼────────────┐
        │  FastAPI Inference │  │  Encryption API    │
        │  Engine (ML Core)  │  │  • Data Hardening  │
        │                    │  │  • AES-256 Encrypt │
        │ • CNN Encoders     │  │  • SHA-256 Hash    │
        │ • LSTM Models      │  │  • Credential Mgmt │
        │ • Fusion Layer     │  └────────────────────┘
        │ • Tracery NLG      │
        │ • 5 Team Pipelines │
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────────┐
        │   PostgreSQL Database  │
        │  (Secure, HIPAA-Ready) │
        │  • Patient Records     │
        └────────────────────────┘
```

## Project Objectives

### 1. Data Unification: Secure Multi-Modal Data Ingestion and Synchronization
**Objective**: Establish a robust, secure ingestion pipeline capable of unifying heterogeneous biomedical data streams.

**Key Modalities**:
- **Physiological Time-Series Signals**:
  - Electrocardiogram (ECG): Cardiac rhythm and arrhythmia detection
  - Blood Oxygen Saturation (SpO2): Oxygenation and desaturation events
  - Heart Rate Variability (HRV): Autonomic nervous system function
  - Electrodermal Activity (EDA): Sympathetic arousal and stress response
  - Peripheral Temperature (TEMP): Thermophysiological response
  - Accelerometer (ACC): Movement, activity, and sleep staging

- **Medical Imaging Data**:
  - Magnetic Resonance Imaging (MRI): Structural brain analysis
  - Computed Tomography (CT): Detailed anatomical imaging
  - Photo-Plethysmography (PPG): Non-invasive vascular response

**Temporal Harmonization Strategy**:
- Linear/cubic spline interpolation to standardized sampling rates (100-125Hz)
- Timestamp alignment across all modalities for synchronized feature vectors
- Intelligent missing data imputation for wireless sensor dropout

### 2. Multi-Task Risk Prediction: Integrated Deep Learning for Simultaneous Pathologies
**Objective**: Utilize unified data for simultaneous, early prediction of multiple inter-related medical conditions.

**Architecture Strategy**:
- Modality-specific encoders (1D-CNN for time-series, 2D/3D-CNN for imaging)
- Late-fusion strategy using attention-weighted concatenation
- Multi-task prediction head for concurrent risk assessment

### 3. Automated Clinical Narratives: Bridging Prediction and Documentation
**Objective**: Transform abstract mathematical outputs into clinically usable, structured medical documentation.

**Implementation**:
- Structured Natural Language Generation (NLG) via Tracery framework
- Contextually a.js Orchestrator (`services/express-api`)

**Technology Stack:**
- Framework: Express.js
- Language: TypeScript
- Type: CommonJS module
- Role: API Gateway & Load Balancer

**Core Responsibilities**:

1. **Authentication & Authorization**:
   - Secure sign-in and session management
   - Role-Based Access Control (RBAC) for clinicians and administrators
   - JWT token validation and refresh mechanisms
   - Audit logging for all authentication events

2. **Feedback Service**:
   - Capture patient-reported outcomes (PROs)
   - Subjective clinical observations and symptoms
   - Model validation and clinical context enrichment

3. **Alerting & Notifications**:
   - Real-time critical vital sign alerts
   - SMS/Email notification delivery
   - Alert threshold management and customization
   - Alert acknowledgment and escalation workflows

4. **Relational Database Interface**:
   - Sole secure interface to PostgreSQL persistence layer
   - CRUD operations for user profiles and configuration
   - Clinical report storage and retrieval
   - Transaction management and data consistency

5. **Load Balancing & Traffic Management**:
   - Request routing to FastAPI inference engine
   - Connection pooling and resource management
   - Rate limiting and DDoS protection
   - Graceful degradation under high load

**Directory Structure:**
- `src/app.ts` - Application initialization with middleware
- `src/server.ts` - Server configuration and port binding
- `src/controllers/` - Request handlers for auth, feedback, alerts
- `src/routes/` - API route definitions
- `src/middlewares/` - Authentication, logging, error handling, encryption
- `src/services/` - Business logic for clinical operations
- `src/models/` - TypeScript interfaces and database schemas
- `src/validators/` - Pydantic-style input validation
- `src/utils/` - Encryption/decryption helpers, JWT utilities
- `src/config/` - Environment-based configuration management
- `tests/` - Unit and integration tr Interface Functions**:
- **Data Stream Initialization**: Secure selection and initialization of physiological data streams from patient monitoring devices
- **Real-Time Visualization**: Dynamic trend charts for ECG, SpO2, HRV, EDA, TEMP signals with clinical thresholds
- **Alert Management**: Real-time notifications for critical vital sign deviations
- **Secure Clinical Reporting**: Retrieval, filtering, and viewing of comprehensive diagnostic summaries
- **User Authentication**: Clinician and administrator login with session management

**Structure:**
- `src/app/` - Next.js app directory with clinical workflows
- `pages/dashboard/` - Real-time signal visualization
- `pages/reports/` - Clinical report generation and retrieval
- `pages/alerts/` - Alert management and historical tracking
- `public/` - Clinical UI assets and icon
- Styling: Tailwind CSS 4
- Runtime: Node.js (CommonJS)

**Key Features:**
- Server-side rendering and static generation
- Modern React components with hooks
- Responsive design with utility-first CSS
- Type-safe development environment

**Structure:**
- `src/app/` - Next.js app directory with layouts and pages
- `public/` - Static assets
- Root configuration files (tsconfig, next.config, eslint.config)

---

### 2. Backend Services

#### 2.1 Express Inference Engine (`services/fast-api`)

**Technology Stack:**
- Framework: FastAPI (Python)
- Python Version: >=3.11
- ML Framework: PyTorch
- Package Manager: UV (via pyproject.toml)
- Role: High-Performance Deep Learning Backend

**Core Responsibilities**:

1. **Data Validation & Schema Enforcement**:
   - Pydantic models for strict data integrity
   - Multi-modal signal schema validation
   - Temporal consistency verification
   - Missing value detection and handling

2. **Signal Preprocessing Pipeline**:
   - Noise reduction (Butterworth filtering)
   - Baseline wander correction (high-pass filtering)
   - Signal normalization (z-score standardization)
   - Temporal interpolation for sampling rate harmonization

- Cryptography: OpenSSL, crypto-js

**Responsibilities**:

1. **Data Encryption/Decryption**:
   - AES-256 encryption for all Protected Health Information (PHI)
   - Dual-layer encryption for maximum security (data at rest + in transit)
   - Key rotation and management
   - Secure initialization vector (IV) generation

2. **Data Integrity**:
   - SHA-256 digital fingerprinting for all clinical records
   - Non-repudiation through cryptographic signatures
   - Tamper detection and alerting

3. **Credential Management**:
   - Secure storage of database credentials
   - API key rotation and validation
   - Encryption of sensitive configuration parameters

4. **Compliance & Audit**:
   - HIPAA compliance verification
   - Encrypted audit log generation
   - Data integrity certificates/Overtraining**: Hybrid CNN-LSTM for chronic trend detection
   - **Team 5 - Tumor Prediction**: 2D-CNN for medical image classification

4. **Feature Fusion & Multi-Task Prediction**:
   - Attention-weighted late fusion of modality-specific features
   - Multi-task prediction head for simultaneous risk assessment
   - Confidence scoring and uncertainty quantification

5. **Natural Language Generation**:
   - Tracery-based structured narrative generation
   - Clinical context-aware report templating
   - Confidence score interpretation and explanation

6.Strategic Team-Based Organization**:

The ML pipeline is organized across five specialized engineering teams, each focusing on distinct pathologies and optimized deep learning architectures:

#### 3.1 Team 1: Sleep Apnea & Stress Detection

**Essential Modalities**:
- SpO2 dips (desaturation event detection)
- HRV drops (autonomic nervous system response)
- Accelerometer (ACC) (sleep stage and restless limb tracking)
- Electrodermal Activity (EDA) (sympathetic arousal)
- Temperature (TEMP) (thermophysiological response)

**Key Datasets**:
- Apnea-ECG Database
- Sleep-EDF Dataset
- Wearable Exam Stress Dataset

**Deep Learning Architecture**:
- 1D-CNN with 30-second temporal windowing (AASM-aligned sleep staging epochs)
- Local feature extraction for rapid desaturation onset detection
- EDA spike corre& Reporting Layer (`analytics`)

#### 4.1 Streamlit Dashboards (`analytics/dashboards/`)

**`streamlit_app.py`** - Interactive clinical dashboard:
- **Real-Time Signal Monitoring**: Live ECG, SpO2, HRV, EDA, TEMP streams
- **Predictive Risk Dashboard**: Team-specific risk scores and trends
- **Alert Management Console**: Historical and active clinical alerts
- **Report Generation Interface**: Automated clinical narrative generation
- **Performance Metrics**: Model accuracy, sensitivity, specificity by condition
- **Patient Cohort Analysis**: Trend analysis across patient populations

#### 4.2 Jupyter Notebooks (`analytics/notebooks/`)

**`eda.ipynb`** - Exploratory Data Analysis:
- Multi-modal signal distribution analysis
- Missing data pattern investigation
- Cross-modal correlation heatmaps
- Temporal pattern discovery
- Team-specific feature importance analysis

**`performance_analysis.ipynb`** - Model Performance Metrics:
- Team-wise model performance comparison
- Confusion matrices and ROC curves
- Sensitivity/specificity trade-off analysis
- Threshold optimization studies
- Generalization performance assessment

#### 4.3 Reports (`analytics/reports/`)

**`report.ipynb`** - Comprehensive Clinical Analysis:
- Aggregated clinical findings across modalities
- Multi-condition risk stratification summaries
- Longitudinal trend analysis for patient cohorts
- Operational metrics and system performance reports
- Security and compliance auditd rest cycles)
- HRV Patterns (sympathetic/parasympathetic balance)
- Sleep Irregularity (circadian disruption indicators)

**Key Datasets**:
- BIDMC PPG and Respiration Dataset
- PhysioNet MIMIC (clinical correlation)

**Deep Learning Architecture**:
- CNNs for spectral feature extraction from SpO2/PPG signals
- RNNs/Hidden Markov Models for temporal dependency modeling
- Long-term progression pattern recognition for diabetes risk stratification

**Location**: `ml/experiments/exp_02/`

---

#### 3.3 Team 3: Atrial Fibrillation & Cardiovascular Risk

**Essential Modalities& Security (`infra`)

#### 5.1 Docker (`infra/docker/`)

**`express.Dockerfile`** - Express Orchestrator container:
- Node.js LTS runtime
- Express.js with TypeScript compilation
- Security middleware and health checks
- Multi-stage build for minimal image size

**Fast-API Dockerfile** (to be created):
- Python 3.11+ runtime
- PyTorch ML framework
- Secure Python environment isolation
- Signal processing libraries (NumPy, SciPy, librosa)

**`encrypt.sh`** - Data encryption utility script:
- AES-256 encryption for backup and archival data
- Key management and rotation
- Integrity verification via SHA-256 hashing

#### 5.2 Deployment (`infra/scripts/`)

**`deploy.sh`** - Automated deployment orchestration:
- Service orchestration (start/stop/restart)
- Database migration execution
- Environment-specific configuration loading
- Health check verification
- Graceful rolling updates
- Rollback mechanisms
- MIT-BIH Normal Sinus Rhythm Database

**Deep Learning Architecture**:
- 1D-CNN or ResNet-18 for high-fidelity ECG signal analysis
- Signal alignment and centering (baseline wandering removal, R-peak alignment)
- Robust feature maps for distinguishing true fibrillation from noise

**Location**: `ml/experiments/exp_03/`

---

#### 3.4 Team 4: Burnout & Overtraining Detection

**Essential Modalities**:
- Long-term  Architectures

### Clinical User Request Flow

```
1. Clinician Authentication
   │
   ├→ Next.js Frontend (web-app)
   │  • Login via Express Auth endpoint
   │  • Session token generation (JWT)
   │  • RBAC verification
   │
2. Data Stream Selection or Clinical Query
   │
   ├→ Express Orchestrator (API Gateway)
   │  • Token validation
   │  • Request routing to appropriate service
   │  • Rate limiting and DDoS protection
   │
3. Service Routing
   │
   ├→ Option A: Clinical Report Retrieval
   │  ├→ Express → PostgreSQL
   │  ├→ Encryption API (decrypt PHI)
   │  └→ Return to Frontend
   │
   ├→ Option B: Real-Time Signal Visualization
   │  ├→ Express → Data Stream Service
   │  ├→ FastAPI (signal preprocessing)
   │  └→ WebSocket stream to Frontend
   │
   └→ Option C: Predictive Risk Assessment
      ├→ Express → FastAPI Inference
      ├→ Multi-modal Feature Extraction
      ├→ Team-Specific Model Inference
      ├→ Fusion & Prediction
      ├→ NLG Report Generation
      ├→ Encryption API (encrypt PHI)
      ├→ PostgreSQL (store report)
      └→ Return to Frontend

4. Frontend Rendering
   │
   ├→ Display clinical findings
   ├→ Real-time visualization of signals
   ├→ Alert acknowledgment if applicable
   │
5. Audit Logging
   │
   └→ All transactions logged with timestamps and user context
```

### Multimodal ML Inference Pipeline

``` Purpose

1. Parallelized Team-Specific Feature Extraction
   │
   ├→ Team 1 (Sleep Apnea & Stress)
   │  └→ 30s sliding window CNN feature extraction
   │
   ├→ Team 2 (Anemia & Diabetes)
   │  └→ Spectral analysis (FFT) + RNN temporal features
   │
   ├→ Team 3 (AFib & Cardiovascular)
   │  └→ R-peak aligned 1D-CNN features
   │
   ├→ Team 4 (Burnout & Overtraining)
   │  └→ CNN daily patterns + LSTM weekly trends
   │
   └→ Team 5 (Tumor Prediction)
      └→ 2D-CNN spatial feature maps

2. Feature Fusion Layer
   │
   ├→ Attention Mechanism
   │  └→ Weighted aggregation of team-specific features
   │
   ├→ Late Fusion Concatenation
   │  └→ Combine multi-task encoded vectors
   │
   └→ Dimensionality Reduction (optional)
      └→ PCA or AutoEncoder compression

3. Multi-Task Prediction Head
   │
   ├→ Sleep Apnea Risk Score (0-100%)
   ├→ Atrial Fibrillation Risk Score (0-100%)
   ├→ Diabetes Risk Score (0-100%)
   ├→ Chronic Stress Score (0-100%)
   ├→ Burnout Index (0-100%)
   └→ Brain Tumor Classification (benign/malignant/type)

4. Confidence & Uncertainty Quantification
   │
   ├→ Monte Carlo Dropout for Bayesian uncertainty
   ├→ Ensemble disagreement metrics
   └→ Threshold-based flagging for low-confidence predictions

5. Natural Language Report Generation (Tracery NLG)
   │
   ├→ Template Selection (based on risk profile)
   ├→ Dynamic Content Generation
   │  ├→ Risk scores and severity interpretation
   │  ├→ Contributing modalities and key features
   │  ├→ Clinical recommendations
   │  └→ Follow-up action items
   │
   └→ Structured Clinical Narrative Output

6. Security & Storage
   │
   ├→ Encryption API (AES-256 encryption)
   ├→ SHA-256 integrity hash generation
   ├→ PostgreSQL storage with audit trail
   └→ Return to Express for frontend delivery

7. Alert Triggering (if applicable)
   │
   ├→ High-risk predictions trigger alerts
   ├→ Alert Service via Express
   └→ Notifications to clinicians (in-app, SMS, Email)
```

### Training & Experimentation Pipeline

```
1. Data Preparation
   │
   ├→ Load curated clinical datasets
   ├→ Train/validation/test split
   └→ Team-specific dataset filtering

2. Preprocessing
   │
   ├→ Execute ml/pipelines/preprocess.py
   ├→ Temporal interpolation to standardized rates
   └→ Feature normalization

3. Feature Engineering
   │
   ├→ Execute ml/pipelines/feature_engineering.py
   ├→ Generate team-specific features
   └→ Cross-modal feature combinations

4. Team-Specific Training (ml/training/train.py)
   │
   ├→ Architecture initialization
   ├→ Hyperparameter configuration loading (ml/config.yaml)
   ├→ Multi-epoch training with validation
   ├→ Checkpoint saving on best performance
   ├→ Early stopping on validation plateau
   └→ Metrics logging (sensitivity, specificity, AUC)

5. Experimentation & Ablation Studies
   │
   ├→ Team experiment notebooks (exp_01 to exp_05)
   ├→ Alternative architectures comparison
   ├→ Modality importance analysis
   └→ Threshold optimization studies

6. Model Artifact Generation
   │
   ├→ Serialize final model weights (ml/models/model.pt)
   ├→ Configuration snapshot
   └→ Performance metrics documentation

7. Integration & Validation
   │
   ├→ Load model.pt into FastAPI service
   ├→ Inference speed benchmarking
   ├→ Cross-modal feature validation
   └→ Clinical validation on held-out test setres (FFT, spectral power)
```

- Wavelet transform features for time-frequency analysis
- Team-specific feature engineering overrides

#### 3.7 Training (`ml/training/`)

**`train.py`**:
- Multi-task learning framework
- Cross-validation strategies
- Hyperparameter optimization
- Model checkpointing and early stopping
- Performance metric tracking (sensitivity, specificity, ROC-AUC)
- Experiment metadata logging

#### 3.8 Experiments (`ml/experiments/`)

Five specialized experiment notebooks organized by clinical focus:
- `exp_01/exp.ipynb` - Sleep Apnea & Stress experiments
- `exp_02/exp.ipynb` - Anemia & Diabetes Risk experiments
- `exp_03/exp.ipynb` - AFib & Cardiovascular experiments
- `exp_04/exp.ipynb` - Burnout & Overtraining experiments
- `exp_05/exp.ipynb` - Tumor Prediction experiments

Each notebook contains:
- Data exploration and visualization
- Model architecture prototyping
- Performance validation
- Team-specific findings and recommendations

#### 3.9 Models (`ml/models/`)

**`model.pt`** - Serialized PyTorch multi-task model:
- Ensemble of team-specific sub-models
- Fused prediction heads
- Pre-trained weights for rapid inference

#### 3.10 Configuration (`ml/config.yaml`)

**Pipeline Parameters**:
- Sampling rates for each modality (e.g., 100Hz for signals, appropriate resolution for images)
- Interpolation method (linear or cubic spline)
- Model architecture hyperparameters
- Team-specific thresholds and sensitivity parameters
- Training configuration (batch size, learning rate, epochs)
- Validation split ratio
- `src/middlewares/` - Express middleware (auth, logging, etc.)
- `src/services/` - Business logic
- `src/models/` - Data models and schemas
- `src/validators/` - Input validation schemas
- `src/utils/` - Utility functions
- `src/config/` - Configuration management
- `tests/` - Test suite

#### 2.2 FastAPI (`services/fast-api`)

**Technology Stack:**
- Framework: FastAPI (Python)
- Python Version: >=3.11
- Package Manager: UV (via pyproject.toml)

**Responsibilities:**
- Advanced data processing
- ML model serving endpoints
- Async request handling
- High-performance data operations

**Directory Structure:**
- `app/main.py` - Application entry point
- Additional modules for API endpoints and ML integration

#### 2.3 Encryption API (`services/encrypt-api`)

**Technology Stack:**
- Framework: Express.js
- Language: JavaScript/TypeScript
- Type: CommonJS module

**Responsibilities:**
- Encryption/decryption operations
- Secure data handling
- Credential management

---

### 3. Machine Learning Pipeline (`ml`)

**Components:**

#### 3.1 Data Processing (`ml/pipelines/`)
- `preprocess.py` - Data cleaning and normalization
- `feature_engineering.py` - Feature extraction and transformation

#### 3.2 Training (`ml/training/`)
- `train.py` - Model training logic and experiment tracking

#### 3.3 Experiments (`ml/experiments/`)
- Five separate experiment notebooks (exp_01 to exp_05)
- Exploration and validation of different model architectures

#### 3.4 Models (`ml/models/`)
- `model.pt` - Trained PyTorch model artifact

#### 3.5 Configuration (`ml/config.yaml`)
- Pipeline parameters and hyperparameters

---

### 4. Analytics Layer (`analytics`)

#### 4.1 Streamlit Dashboards (`analytics/dashboards/`)
- `streamlit_app.py` - Interactive dashboard for data visualization

#### 4.2 Jupyter Notebooks (`analytics/notebooks/`)
- `eda.ipynb` - Exploratory Data Analysis
- `performance_analysis.ipynb` - Model performance metrics

#### 4.3 Reports (`analytics/reports/`)
- `report.ipynb` - Comprehensive analysis reports

---

### 5. Infrastructure (`infra`)

#### 5.1 Docker (`infra/docker/`)
- `express.Dockerfile` - Container image for Express API
- `encrypt.sh` - Encryption script for sensitive data

#### 5.2 Deployment (`infra/scripts/`)
- `deploy.sh` - Automated deployment script

---

### 6. Shared Assets (`shared`)

#### 6.1 Type Definitions (`shared/types/`)
- `prediction.types.ts` - ML prediction-related types
- `users.types.ts` - User and authentication types

#### 6.2 Reports (`shared/reports/`)
- Shared report templates and components

#### 6.3 Constants (`shared/contants/`)
- Application-wide constants and enumerations

---

## Data Flow

### User Request Flow

```
1. User Browser
   ↓
2. Next.js Frontend (web-app)
   ↓
3. API Request Routing
   ├→ Express API (business logic)
   ├→ FastAPI (data processing/ML serving)
   └→ Encrypt API (security operations)
   ↓
4. Backend Processing
   ├→ Data validation
   ├→ Business logic execution
   └→ ML inference (if needed)
   ↓
5. Response to Frontend
   ↓
6. Rendered in Browser
```

### ML Pipeline Flow

```
1. Raw Data Input
   ↓
2. Preprocessing (preprocess.py)
   ├→ Cleaning
   ├→ Normalization
   └→ Validation
   ↓
3. Feature Engineering (feature_engineering.py)
   ├→ Feature extraction
   └→ Feature transformation
   ↓
4. Model Training (train.py)
   ├→ Experiment tracking
   ├→ Hyperparameter tuning
   └→ Model evaluation
   ↓
5. Model Artifact (model.pt)
   ↓
6. Serving via FastAPI
   ↓
7. Analytics & Reporting
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16.1.6, React 19, TypeScript 5, Tailwind CSS 4 |
| **Express API** | Node.js, Express.js, TypeScript |
| **FastAPI** | Python 3.11+, FastAPI, PyTorch |
| **Encryption** | Node.js, Express.js, Cryptography Libraries |
| **ML Framework** | PyTorch |
| **Analytics** | Streamlit, Jupyter, Pandas, NumPy |
| **Containerization** | Docker |
| **Deployment** | Shell scripts, Docker Compose |

---

## Directory Structure Guide

```
Cortexa/
├── apps/                              # Frontend & Mobile applications
│   ├── web-app/                       # Next.js clinical web interface
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── dashboard/         # Real-time signal visualization
│   │   │   │   ├── reports/           # Clinical report viewing/retrieval
│   │   │   │   ├── alerts/            # Alert management interface
│   │   │   │   ├── auth/              # Authentication pages
│   │   │   │   └── layout.tsx         # Root layout with navigation
│   │   │   └── components/            # React components
│   │   └── public/                    # Clinical logos and icons
│   │
│   └── mobile-app/                    # Mobile client (Future)
│
├── services/                          # Microservice backends
│   ├── express-api/                   # Express Orchestrator (API Gateway)
│   │   ├── src/
│   │   │   ├── app.ts                 # Middleware & initialization
│   │   │   ├── server.ts              # Server binding
│   │   │   ├── controllers/           # Auth, Feedback, Alerts
│   │   │   ├── routes/                # API endpoint definitions
│   │   │   ├── middlewares/           # Auth, logging, encryption
│   │   │   ├── services/              # Business logic
│   │   │   ├── models/                # TypeScript schemas & interfaces
│   │   │   ├── validators/            # Input validation
│   │   │   ├── utils/                 # JWT, encryption helpers
│   │   │   └── config/                # Environment configuration
│   │   └── tests/                     # Unit & integration tests
│   │
│   ├── fast-api/                      # FastAPI Inference Engine
│   │   ├── app/
│   │   │   ├── main.py                # FastAPI app initialization
│   │   │   ├── routes/                # API endpoints (/predict, /preprocess)
│   │   │   ├── schemas/               # Pydantic validation models
│   │   │   ├── models/                # PyTorch model definitions
│   │   │   ├── services/              # ML inference, preprocessing
│   │   │   ├── nlg/                   # Tracery templates & generation
│   │   │   └── utils/                 # Signal processing utilities
│   │   ├── ml/
│   │   │   └── team_specific/         # Modular feature extraction
│   │   └── tests/                     # Pytest suite
│   │
│   └── encrypt-api/                   # Encryption Service
│       ├── src/
│       │   ├── routes/                # /encrypt, /decrypt, /hash endpoints
│       │   ├── services/              # Crypto operations
│       │   └── utils/                 # Key management
│       └── tests/
│
├── ml/                                # Machine Learning Pipeline
│   ├── pipelines/
│   │   ├── preprocess.py              # Cleaning, interpolation, normalization
│   │   └── feature_engineering.py     # Modality-specific feature extraction
│   │
│   ├── training/
│   │   └── train.py                   # Multi-task training harness
│   │
│   ├── experiments/                   # Team-specific exploration
│   │   ├── exp_01/exp.ipynb           # Sleep Apnea & Stress
│   │   ├── exp_02/exp.ipynb           # Anemia & Diabetes
│   │   ├── exp_03/exp.ipynb           # AFib & Cardiovascular
│   │   ├── exp_04/exp.ipynb           # Burnout & Overtraining
│   │   └── exp_05/exp.ipynb           # Tumor Prediction
│   │
│   ├── models/
│   │   └── model.pt                   # Serialized multi-task PyTorch model
│   │
│   └── config.yaml                    # Hyperparameters, feature names, thresholds
│
├── analytics/                         # Analytics & Clinical Dashboards
│   ├── dashboards/
│   │   └── streamlit_app.py           # Interactive clinical dashboard
│   │
│   ├── notebooks/
│   │   ├── eda.ipynb                  # Multi-modal signal exploration
│   │   └── performance_analysis.ipynb # Model validation metrics
│   │
│   └── reports/
│       └── report.ipynb               # Comprehensive clinical/operational reports
│
├── infra/                             # Infrastructure & Deployment
│   ├── docker/
│   │   ├── express.Dockerfile         # Express service containerization
│   │   ├── fastapi.Dockerfile         # FastAPI service containerization
│   │   ├── encrypt.Dockerfile         # Encryption service containerization
│   │   ├── docker-compose.yml         # Local dev orchestration
│   │   ├── docker-compose.prod.yml    # Production orchestration
│   │   └── encrypt.sh                 # Data encryption utility
│   │
│   └── scripts/
│       ├── deploy.sh                  # Automated deployment orchestration
│       ├── health-check.sh            # Service health verification
│       ├── backup.sh                  # Database & model backup
│       └── rollback.sh                # Emergency rollback mechanism
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md                # This document
│   ├── API_CONTRACTS.md               # API specifications & OpenAPI schemas
│   ├── ENCRYPTION.md                  # Security protocols & key management
│   ├── ML_PIPELINE.md                 # Detailed ML methodology
│   ├── DEPLOYMENT.md                  # Deployment procedures
│   ├── HIPAA_COMPLIANCE.md            # HIPAA adherence checklist
│   └── README.md                      # Project overview
│
└── shared/                            # Shared cross-service resources
    ├── types/
    │   ├── prediction.types.ts        # ML prediction output types
    │   ├── users.types.ts             # User, roles, permissions types
    │   ├── clinical.types.ts          # Clinical data types
    │   └── signals.types.ts           # Physiological signal types
    │
    ├── reports/
    │   └── templates/                 # NLG report templates
    │
    ├── constants/
    │   ├── diseases.ts                # Disease thresholds & definitions
    │   ├── signals.ts                 # Signal metadata & ranges
    │   └── roles.ts                   # RBAC role definitions
    │
    └── utils/
        └── validation.ts              # Cross-service validators
```

---

## Communication Patterns

### Frontend to Backend Communication

| Channel | Protocol | Format | Purpose |
|---------|----------|--------|---------|
| **REST API** | HTTPS | JSON | Standard clinical queries, reporting |
| **WebSocket** | WSS | JSON | Real-time signal streaming, alerts |
| **GraphQL** (Future) | HTTPS | GraphQL | Flexible query construction |

**Authentication & Authorization**:
- Token-based authentication via JWT
- Payload signing for data integrity
- Role-Based Access Control (RBAC):
  - `admin` - Full system access
  - `clinician` - Patient data access + report generation
  - `technician` - System monitoring only
  - `patient` (future) - Limited personal data access

### Inter-Service Communication

| Sender | Receiver | Protocol | Purpose | Security |
|--------|----------|----------|---------|----------|
| Express | FastAPI | HTTP | ML inference requests | HTTPS + Service-to-service token |
| Express | Encrypt API | HTTP | PHI encryption/decryption | HTTPS + Internal CA |
| Express | PostgreSQL | TCP | CRUD operations | SSL/TLS + connection pooling |
| FastAPI | Encrypt API | HTTP | Result encryption before storage | HTTPS |
| Analytics | PostgreSQL | TCP | Report data retrieval | SSL/TLS + read-only creds |

### Asynchronous Operations

- **Long-running ML Inferences**: Queued via celery/Bull, status poll via WebSocket
- **Batch Processing Strategy

**Service Containers**:
1. **Express Orchestrator**
   - Base: Node.js 20 LTS
   - Includes: TypeScript compiler, middleware, auth logic
   - Health Check: /health endpoint (returns 200 if all services connected)
   - Ports: 3000 (main), 3001 (admin)

2. **FastAPI Inference Engine**
   - Base: Python 3.11-slim with GPU support
   - Includes: PyTorch, signal processing libraries, ML models
   - Health Check: /health endpoint (checks model availability)
   - Ports: 8000, 8001 (uvicorn workers)

3. **Encryption Service**
   - Base: Node.js 20 LTS (minimal, security-focused)
   - Includes: Cryptography libraries, key management
   - Health Check: /health endpoint
   - Port: 3002

4. **PostgreSQL Database**
   - Base: postgres:16-alpine (official image)
   - Security: User-specific credentials, SSL enforced
   - Port: 5432
   - Volumes: Persistent named volume for data

### Docker Compose Configuration

**Development** (`docker-compose.yml`):
```yaml
- Single-machine orchestration
- Environment variables for non-production settings
- Volume mounts for hot-reloading
- Service dependencies and health checks
- Network: Isolated internal network
```

**Production** (`docker-compose.prod.yml`):
```yaml
- Multi-machine deployment ready (Swarm/K8s preparation)
- Replicas for service redundancy
- Resource limits and reservations
- Logging drivers (centralized)
- Secret management via environment variables
- Restart policies with backoff
```

### Deployment Process

```
1. Build Stage
   ├→ Docker build all services in isolation
   ├→ Tag images with version and commit SHA
   └→ Push to Docker registry (Docker Hub / private registry)

2. Pre-deployment Checks
   ├→ Database migrations (Flyway / Alembic)
   ├→ Configuration validation
   ├→ Secret availability verification
   └→ Resource capacity assessment

3. Deployment Execution
   ├→ Pull latest images from registry
   ├→ Stop old containers (graceful)
   ├→ Start new containers with health checks
   ├→ Verify all services are operational
   └→ Run smoke tests

4. Post-deployment Validation
   ├→ Health check endpoints respond 200
   ├→ Database connectivity verified
   ├→ ML model loading confirmed
   ├→ End-to-end test (signal → prediction → report)
   └→ Log aggregation operational

5. Monitoring & Rollback
   ├→ Continuous health monitoring (first 30 min)
   ├→ Error rate thresholds trigger alerts
   ├→ Automatic rollback if error rate > 5%
   └→ Manual rollback via rollback.sh script
```

### Scaling Strategy

**Horizontal Scaling**:
- **Express Orchestrator**: Stateless, scale up to handle request load
- **FastAPI Engine**: Multiple workers via gunicorn/uvicorn, GPU affinity
- **PostgreSQL**: Replication with read replicas (future), connection pooling

**Vertical Scaling**:
- **FastAPI**: Add GPU nodes for inference acceleration
- **PostgreSQL**: SSD storage, increased memory for caching

---

## Development Workflow & Local Setup

### Frontend Development

```bash
# Navigate to web-app
cd apps/web-app

# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

**Development Features**:
- Hot-reloading on file changes
- TypeScript compilation in-memory
- Next.js built-in API mocking
- Debug mode integration with VS Code

### Express Orchestrator Development

```bash
# Navigate to Express service
cd services/express-api

# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev

# Run tests
npm run test

# Build TypeScript
npm run build
```

**Development Setup**:
- TypeScript compilation watching
- Nodemon for auto-restart
- .env.local for local secrets (never commit)
- Database connection string configuration

### FastAPI Engine Development

```bash
# Navigate to FastAPI service
cd services/fast-api

# Create virtual environment (Python 3.11+)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # or pyproject.toml with `pip install -e .`

# Start development server (http://localhost:8000)
uvicorn app.main:app --reload

# Run tests
pytest

# Run specific team's experiment
jupyter notebook ml/experiments/exp_01/exp.ipynb
```

**Development Setup**:
- Virtual environment isolation
- Hot-reloading via Uvicorn --reload
- Pydantic validation in real-time
- Model loading from local ml/models/

### ML Training & Experimentation

```bash
# Navigate to ML directory
cd ml

# Run preprocessing
python pipelines/preprocess.py --input raw_data/ --output processed_data/

# Run feature engineering
python pipelines/feature_engineering.py --input processed_data/ --output features/

# Execute training
python training/train.py --config config.yaml --output models/

# Jupyter experimentation (team-specific)
jupyter notebook experiments/exp_01/exp.ipynb
```

### Docker Compose Local Development

```bash
# Build all service images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec express npm run migrate

# Stop all services
docker-compose down
```

---

## 7-Week Development Roadmap

### Phase I: System Design & Planning (Week 1)

**Tasks**:
1. **Database Schema Finalization** (2 days)
   - Relational mapping of multi-modal signals
   - Anatomical metadata structure
   - Clinical report storage schema
   - HIPAA-compliant audit table design

2. **API Contract Definition** (2 days)
   - OpenAPI/Swagger specification
   - Express ↔ FastAPI contract
   - Request/response signatures with examples
   - Error code standardization

3. **Interpolation Protocol Specification** (1 day)
   - Linear vs. cubic spline trade-offs
   - Sampling rate standardization (100Hz, 125Hz options)
   - Missing data handling procedures

4. **Security Architecture Review** (2 days)
   - Encryption key management plan
   - HIPAA compliance matrix
   - Data retention policy documentation
   - Threat modeling and mitigation strategies

**Deliverables**:
- Database schema (SQL scripts)
- API OpenAPI v3.0 specification
- Signal preprocessing algorithm document
- Security hardening checklist

---

### Phase II: Core Infrastructure (Weeks 2-3)

**Week 2: Frontend & Express Setup**

1. **Next.js Frontend Scaffolding** (2 days)
   - Project initialization with TypeScript
   - Tailwind CSS setup and theming
   - Layout components (header, sidebar, footer)
   - Authentication flow implementation

2. **Express Orchestrator Setup** (2 days)
   - Project scaffold with TypeScript
   - Middleware stack (auth, logging, encryption, error handling)
   - Database connection pool with SSL/TLS
   - JWT token generation and validation

3. **User Management System** (1 day)
   - User model and RBAC schema
   - Authentication endpoints (/login, /logout, /refresh)
   - Session management logic

**Week 3: FastAPI & Encryption Service**

1. **FastAPI Initialization** (1 day)
   - Project setup with Pydantic models
   - OpenAPI documentation auto-generation
   - Asyncio worker pool configuration

2. **Encryption API Setup** (1 day)
   - AES-256 encryption/decryption endpoints
   - SHA-256 hashing service
   - Key management interface

3. **ML Model Porting** (3 days)
   - Load baseline CNN, LSTM, ResNet models
   - Create PyTorch model wrapper class
   - Implement model loading and inference pipeline
   - Optimization for inference speed

**Deliverables**:
- Functional Next.js frontend shell
- Express API with working database integration
- FastAPI inference engine with baseline models
- Encryption service endpoints exposed
- Docker images building successfully

---

### Phase III: Deep Learning Integration (Weeks 4-5)

**Week 4: Team-Specific Model Development**

1. **Team 1 - Sleep Apnea & Stress** (1 day per team member)
   - 1D-CNN implementation with 30s windows
   - Feature extraction from SpO2, HRV, EDA
   - Model training and validation

2. **Team 2 - Anemia & Diabetes** (1 day)
   - CNN for spectral analysis
   - RNN/HMM for temporal progression
   - Dataset preparation and training

3. **Team 3 - AFib & Cardiovascular** (1 day)
   - ECG signal preprocessing (R-peak detection)
   - ResNet-18 architecture customization
   - Threshold optimization studies

4. **Team 4 - Burnout & Overtraining** (1 day)
   - CNN-LSTM hybrid architecture
   - Week-over-week trend extraction
   - Chronic degradation modeling

5. **Team 5 - Tumor Prediction** (1 day)
   - Medical image preprocessing
   - 2D-CNN classification model
   - Tumor type and severity classification

**Week 5: Feature Fusion & Multi-Task Integration**

1. **Feature Fusion Layer** (1.5 days)
   - Attention mechanism implementation
   - Late-stage feature concatenation
   - Multi-task prediction head

2. **Tracery NLG Engine** (1.5 days)
   - Template design for each condition
   - Dynamic content generation from model outputs
   - Confidence score interpretation rules

3. **Alert & Feedback Services** (1 day)
   - Express feedback endpoint development
   - Alert triggering logic based on thresholds
   - Notification routing (in-app, SMS, email)

4. **Integration Testing** (1 day)
   - End-to-end signal → prediction → report flow
   - Cross-team model compatibility
   - Performance benchmarking

**Deliverables**:
- Five team-specific models trained and validated
- Feature fusion layer with attention mechanism
- NLG report generation functional
- Alert system operational
- Complete ML pipeline integration

---

### Phase IV: Security Hardening (Week 6)

**Tasks**:

1. **Encryption Implementation** (2 days)
   - AES-256 encryption for all patient records (at rest)
   - TLS 1.3 for all network communication (in transit)
   - Key management via KMS or HSM integration
   - Automatic backup encryption

2. **Digital Fingerprinting** (1 day)
   - SHA-256 HMAC generation for all clinical reports
   - Integrity verification on data retrieval
   - Tamper-evident logging

3. **Access Control Hardening** (1.5 days)
   - RBAC policy enforcement in all services
   - Attribute-based access control (ABAC) rules
   - Audit logging for all data access
   - Multi-factor authentication setup (optional)

4. **HIPAA Compliance Audit** (1.5 days)
   - Compliance checklist verification
   - Penetration testing (basic)
   - Security vulnerability scanning
   - Documentation generation

**Deliverables**:
- All data encrypted at rest and in transit
- Digital fingerprint system operational
- HIPAA compliance documentation completed
- Security audit report
- No critical vulnerabilities identified

---

### Phase V: Optimization, Testing & Delivery (Week 7)

**Tasks**:

1. **High-Concurrency Stress Testing** (2 days)
   - Load testing on Express gateway (1000+ concurrent requests)
   - ML inference latency benchmarking
   - Database connection pool optimization
   - Identify and fix bottlenecks

2. **UI/UX Polish** (1 day)
   - Clinical workflow optimization
   - Real-time dashboard refinement
   - Alert interface user testing
   - Accessibility compliance (WCAG 2.1 AA)

3. **Documentation & Knowledge Transfer** (1 day)
   - Deployment procedures manual
   - Troubleshooting guide
   - Team training sessions
   - Runbooks for operations

4. **Production Readiness** (1 day)
   - Blue-green deployment setup
   - Monitoring and alerting configuration
   - Disaster recovery plan
   - Final integration tests

5. **Launch Preparation** (1 day)
   - Release notes compilation
   - Go-live checklist
   - Backup and rollback procedures
   - Stakeholder communications

**Deliverables**:
- System passes high-load stress tests
- UI/UX fully polished and user-tested
- Complete documentation package
- Production deployment pipeline ready
- Final sign-off and release approval

---

## Deployment Architecture

### Containerization
- **Docker**: Services containerized for consistent deployment
- **Images**: 
  - Express API Docker image (`express.Dockerfile`)
  - FastAPI containerized (PyProject-based)

### Deployment Process
1. Build Docker images
2. Push to registry
3. Deploy via `deploy.sh` script
4. Environment-specific configuration

---

## Development Workflow

### Frontend Development
```bash
cd apps/web-app
npm run dev              # Start dev server
npm run build            # Production build
npm run lint             # Run ESLint
```

### Express API Development
```bash
cd services/express-api
# Development depends on setup (tsconfig configured)
npm test                 # Run tests
```

### FastAPI Development
```bash
cd services/fast-api
# Python environment setup (requires Python 3.11+)
# Execute ML operations and API endpoints
```

### ML Development
```bash
cd ml
# Training, experimentation, and model development
python training/train.py             # Train models
jupyter notebook experiments/        # Run experiments
```

## Scalability & Performance Considerations

### Horizontal Scalability

**Express Orchestrator (Stateless)**:
- Multiple instances behind load balancer
- Session state stored in Redis (future)
- Scales to handle thousands of concurrent clinicians
- Database connection pooling across instances

**FastAPI Inference Engine**:
- Multiple worker processes via Gunicorn/Uvicorn
- GPU affinity for optimal CUDA resource utilization
- Queue-based request batching for inference
- Model caching in shared memory (Ray or similar)
- Auto-scaling based on queue depth

**PostgreSQL Database**:
- Read replicas for query load distribution
- Connection pooling via PgBouncer
- Partitioning by patient ID for large datasets
- Archival of historical reports (future)

### Vertical Scalability

**GPU Acceleration**:
- CUDA support for FastAPI PyTorch models
- Batch inference optimization on tensor cores
- Mixed-precision (FP16) inference for memory efficiency

**Memory Optimization**:
- Model quantization (INT8) for reduced footprint
- Selective feature loading for memory-constrained environments
- Streaming preprocessing for large image files

### Performance Optimization

**Caching Strategy**:
- Redis cache for frequently accessed patient records
- Model prediction caching with TTL (5-15 minutes)
- Pre-computed report templates caching

**Batch Processing**:
- Nightly batch inference for non-urgent analyses
- Queue-based deferred processing during peak hours
- Parallel processing of multiple patients

**Inference Optimization**:
- TorchScript compilation for faster execution
- ONNX export for runtime-independent deployment
- Quantization-aware training for production models
- Mobile-optimized model variants (future)

### Monitoring & Metrics

**Key Performance Indicators (KPIs)**:
- Inference latency: p50 < 500ms, p95 < 2s
- API response time: p50 < 100ms (non-ML endpoints)
- System throughput: >1000 requests/min
- ML model accuracy: >95% on validation set per condition
- Availability target: 99.9% uptime (SLA)

**Observability Stack** (Future Enhancement):
- Prometheus metrics collection
- ELK Stack (Elasticsearch, Logstash, Kibana) for logging
- Jaeger distributed tracing for multi-service debugging
- Custom dashboards for clinical team oversight

---

## Production & Compliance Checklist

### Pre-Production Validation

- [ ] **Data Security**:
  - [ ] All PHI encrypted at rest (AES-256)
  - [ ] All network traffic encrypted (TLS 1.3)
  - [ ] Digital fingerprinting implemented (SHA-256)
  - [ ] Key management system operational

- [ ] **HIPAA Compliance**:
  - [ ] BAA signed with all vendors
  - [ ] Audit logging comprehensive (all data access)
  - [ ] Breach notification plan documented
  - [ ] Data retention policy enforced
  - [ ] Access control verification

- [ ] **Clinical Validation**:
  - [ ] Model performance >95% on test set per condition
  - [ ] Clinician review and sign-off on reports
  - [ ] False positive/negative analysis completed
  - [ ] Recommendation thresholds clinically validated

- [ ] **System Reliability**:
  - [ ] 99.9% uptime demonstrated (28-day test)
  - [ ] Disaster recovery plan tested
  - [ ] Rollback procedures verified
  - [ ] Database backup and restore functional

- [ ] **Performance**:
  - [ ] ML inference <2s p95 latency
  - [ ] API endpoints <100ms response time
  - [ ] Concurrent user load tested (1000+)
  - [ ] Database query optimization verified

- [ ] **Documentation**:
  - [ ] Deployment procedures documented
  - [ ] Troubleshooting guides comprehensive
  - [ ] Team training completed
  - [ ] Change management procedures established

---

## Future Enhancements

### Near-Term (3-6 Months)

- [ ] **GraphQL API Layer**: Flexible query construction for frontend
- [ ] **Redis Caching**: Performance optimization for frequently accessed data
- [ ] **Mobile Application**: Clinician alerts on mobile devices
- [ ] **Multiple Language Support**: Reporting in different languages
- [ ] **Advanced Monitoring**: Prometheus + Grafana dashboards
- [ ] **Automated Testing**: CI/CD pipeline with comprehensive test coverage
- [ ] **Model Versioning**: Track and compare model performance over time
- [ ] **A/B Testing Framework**: For evaluating model updates in production

### Medium-Term (6-12 Months)

- [ ] **Kubernetes Deployment**: Container orchestration at scale
- [ ] **Multi-Task Learning Enhancement**: Cross-condition knowledge transfer
- [ ] **Federated Learning**: Privacy-preserving model training across clinics
- [ ] **Real-time WebSocket**: Live signal streaming and alerts
- [ ] **Advanced NLG**: Context-aware narrative generation with citations
- [ ] **Blockchain Audit Trail**: Immutable record of all clinical decisions
- [ ] **Multi-modal Attention Visualization**: Interpretability for clinicians
- [ ] **Electronic Health Record (EHR) Integration**: Bi-directional HL7/FHIR exchange

### Long-Term (12+ Months)

- [ ] **Quantum Computing Integration**: For complex optimization problems
- [ ] **Advanced Privacy**: Differential privacy for dataset training
- [ ] **7xML Model Ensemble**: Diversity-based uncertainty quantification
- [ ] **Causal Inference**: Understanding disease causal relationships
- [ ] **Transfer Learning Across Diseases**: Knowledge transfer between conditions
- [ ] **Global Telemedicine Integration**: Multi-clinic federated predictions
- [ ] **Regulatory Approval**: FDA 510(k) clearance for clinical device
- [ ] **Insurance Integration**: Real-time claims and risk prediction

---

## Troubleshooting & Common Issues

### ML Inference Problems

**Issue**: Model inference latency exceeds 2 seconds
- **Solution**: Check GPU utilization via `nvidia-smi`. Enable mixed-precision inference (FP16). Reduce batch size or model complexity. Consider model quantization.

**Issue**: NaN (Not a Number) predictions
- **Solution**: Verify input signal preprocessing. Check for extreme value outliers. Validate feature normalization. Review model training logs for numerical instability.

### Database Issues

**Issue**: Connection pool exhaustion
- **Solution**: Increase pool size in Express config. Monitor long-running queries. Implement read replicas. Use connection pooling middleware (PgBouncer).

**Issue**: Database growth exceeds capacity
- **Solution**: Implement archival policy for old reports. Partition tables by patient ID. Enable point-in-time recovery with aged backups.

### Security Issues

**Issue**: Decryption failures
- **Solution**: Verify encryption key availability. Check key rotation logs. Ensure IV is properly stored. Validate AES-256 implementation.

**Issue**: Audit log tampering detected
- **Solution**: Implement immutable logging (append-only). Review access control logs. Investigate breach timeline. Activate incident response protocol.

---

## References & Related Documentation

- [API Contracts](./API_CONTRACTS.md) - OpenAPI specifications, endpoint documentation, request/response examples
- [Encryption Details](./ENCRYPTION.md) - Security implementation, key management, encryption algorithms
- [ML Pipeline Documentation](./ML_PIPELINE.md) - Detailed methodology, team assignments, dataset information
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment procedures, troubleshooting steps
- [HIPAA Compliance](./HIPAA_COMPLIANCE.md) - Compliance checklist, audit procedures, regulatory requirements
- [README.md](./README.md) - Project overview, quick start guide, contribution guidelines

---

## Contributing & Development Guidelines

### Code Standards
- **TypeScript**: Strict mode, ESLint configuration enforced
- **Python**: PEP 8 compliance, type hints via mypy
- **Documentation**: Inline comments for complex logic, README.md in each directory
- **Testing**: Unit tests for all new features, >80% code coverage

### Git Workflow
1. Create feature branch from `develop`: `git checkout -b feature/your-feature`
2. Make changes with descriptive commits
3. Push to remote: `git push origin feature/your-feature`
4. Open Pull Request with detailed description
5. Pass automated tests and code review
6. Merge to `develop` (requires 2 approvals)

### Commit Message Convention
```
[TYPE]: Short description (50 chars max)

Detailed explanation of the change, why it was made, and any relevant
context. Link related issues with #123. This section is optional for
simple changes but required for complex ones.
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Team Contacts & Support

### Project Leadership
- **Project Lead**: [Name] - Architecture & Strategic Planning
- **ML Lead**: [Name] - Team Coordination & Model Development
- **DevOps Lead**: [Name] - Infrastructure & Deployment

### Team Assignments
- **Team 1** (Sleep Apnea & Stress): [Members]
- **Team 2** (Anemia & Diabetes): [Members]
- **Team 3** (AFib & Cardiovascular): [Members]
- **Team 4** (Burnout & Overtraining): [Members]
- **Team 5** (Tumor Prediction): [Members]

### Support & Questions
- For technical issues: Open GitHub issue with `[TECHNICAL]` prefix
- For security concerns: Email security@cortexa.clinical (confidential)
- For deployment assistance: Contact DevOps team on Slack #deployments

---

**Document Version**: 2.0  
**Last Updated**: February 28, 2026  
**Status**: Ready for Development  
**Approval**: [Pending Sign-off]