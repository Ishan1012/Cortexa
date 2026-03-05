# Cortexa ML Pipeline Documentation

## Table of Contents

1. [Overview](#overview)
2. [Data Architecture](#data-architecture)
3. [Preprocessing & Temporal Harmonization](#preprocessing--temporal-harmonization)
4. [Team-Based ML Organization](#team-based-ml-organization)
5. [Feature Engineering](#feature-engineering)
6. [Model Architectures](#model-architectures)
7. [Training & Validation](#training--validation)
8. [Inference Pipeline](#inference-pipeline)
9. [Model Evaluation](#model-evaluation)
10. [Deployment & Integration](#deployment--integration)

---

## Overview

The Cortexa ML Pipeline is a sophisticated, team-based ensemble system designed to process heterogeneous biomedical data and perform simultaneous prediction of multiple clinically relevant conditions. The pipeline is organized around **five specialized engineering teams**, each focusing on distinct pathologies with optimized deep learning architectures tailored to their specific signal characteristics and clinical requirements.

### Core Principles

- **Multimodal Integration**: Seamless fusion of physiological time-series and medical imaging
- **Temporal Synchronization**: All modalities aligned to standardized sampling rates
- **Team Specialization**: Domain expertise for each clinical condition
- **Late-Stage Feature Fusion**: Information-rich aggregation at the decision layer
- **Clinically Validated**: All metrics designed for real-world healthcare application
- **Scalable & Efficient**: Parallelized processing for high-throughput inference

### Data Flow Summary

```
Raw Patient Data (Multimodal)
        │
        ├→ Team-Specific Data Validation
        │
        ├→ Preprocessing (Standardized)
        │  ├→ Noise Reduction
        │  ├→ Baseline Correction
        │  ├→ Temporal Interpolation
        │  └→ Normalization
        │
        ├→ Team-Specific Feature Extraction (Parallel)
        │  ├→ Team 1: ECG/HRV Analysis
        │  ├→ Team 2: SpO2/Activity Analysis
        │  ├→ Team 3: Cardiac Rhythm Analysis
        │  ├→ Team 4: Long-term Trend Analysis
        │  └→ Team 5: Medical Image Analysis
        │
        ├→ Feature Fusion (Attention-Weighted)
        │
        ├→ Multi-Task Prediction Head
        │  ├→ Sleep Apnea Risk
        │  ├→ AFib Risk
        │  ├→ Diabetes Risk
        │  ├→ Stress/Burnout Score
        │  └→ Tumor Classification
        │
        ├→ Confidence Quantification
        │
        ├→ Natural Language Report Generation
        │
        └→ Clinical Output (Predictions + Narrative)
```

---

## Data Architecture

### Input Data Types

#### 1. Physiological Time-Series Signals

**Characteristics**:
- High-frequency continuous measurements
- Variable sampling rates (typically 100-1000 Hz)
- Possible missing data due to wireless transmission
- Irregular timestamps requiring alignment

**Supported Modalities**:

| Signal | Symbol | Sampling Rate | Range | Clinical Relevance |
|--------|--------|---------------|-------|-------------------|
| Electrocardiogram | ECG | 250-1000 Hz | ±5 mV | Cardiac rhythm, arrhythmias |
| Blood Oxygen Saturation | SpO2 | 1 Hz | 0-100% | Oxygenation, desaturation events |
| Heart Rate Variability | HRV | 1 Hz (computed from ECG) | 40-200 bpm | Autonomic function, stress |
| Electrodermal Activity | EDA | 4 Hz | 0-100 μS | Sympathetic arousal, emotional state |
| Body Temperature | TEMP | 0.5 Hz | 35-40 °C | Thermophysiological response |
| Accelerometer | ACC | 10-50 Hz | ±16 g | Movement, activity, sleep staging |
| Photoplethysmography | PPG | 100 Hz | 0-2V | Vascular response, pulse rate |

#### 2. Medical Imaging Data

**Types**:
- **Magnetic Resonance Imaging (MRI)**: 
  - 2D/3D T1, T2, FLAIR sequences
  - High resolution (1mm³ voxels typical)
  - Primary diagnostic imaging modality

- **Computed Tomography (CT)**:
  - 2D/3D sequential slices
  - 0.5-1mm slice thickness
  - Secondary structural imaging confirmation

**Processing Requirements**:
- DICOM format parsing and standardization
- Intensity normalization across patients
- Affine registration to template space (optional)
- Artifact removal and quality assessment

#### 3. Metadata

- **Patient Demographics**: Age, sex, medical history
- **Timestamps**: Precise recording start times with timezone info
- **Device Information**: Sensor model, firmware version
- **Clinical Context**: Chief complaints, previous diagnoses

### Data Format Specifications

**Signal Data (JSON)**:
```json
{
  "patient_id": "PT_12345",
  "session_id": "SESS_001",
  "timestamp": "2026-02-15T14:30:00Z",
  "signals": {
    "ecg": {
      "data": [0.5, 0.6, 0.4, ...],
      "sampling_rate": 250,
      "units": "mV",
      "quality": "good"
    },
    "spo2": {
      "data": [95, 95, 94, ...],
      "sampling_rate": 1,
      "units": "%",
      "quality": "acceptable"
    }
  },
  "metadata": {
    "device": "Wearable_v2.1",
    "environment": "home"
  }
}
```

**Image Data**:
- **Format**: DICOM or NIfTI
- **Dimensions**: Variable (typically 256×256×256 for volumetric)
- **Metadata**: DICOM headers preserved for clinical context
- **Quality**: Artifact-free, diagnostic grade

---

## Preprocessing & Temporal Harmonization

### Principle

All heterogeneous, asynchronously sampled biomedical data must be transformed into strictly uniform, temporally consistent feature vectors suitable for deep learning models. This is achieved through rigorous preprocessing and temporal synchronization.

### Step 1: Data Validation

**Input Checks**:
```python
def validate_signal_data(signal, modality_config):
    # Check for correct data type
    assert isinstance(signal, (list, np.ndarray))
    
    # Verify length meets minimum requirements
    min_duration_sec = modality_config['min_duration']
    min_samples = modality_config['sampling_rate'] * min_duration_sec
    assert len(signal) >= min_samples, f"Signal too short: {len(signal)} < {min_samples}"
    
    # Check for NaN values
    nan_ratio = np.isnan(signal).sum() / len(signal)
    assert nan_ratio < 0.5, f"Too many NaN values: {nan_ratio:.1%}"
    
    # Verify range plausibility
    min_val, max_val = modality_config['valid_range']
    assert signal.min() >= min_val and signal.max() <= max_val, \
        f"Out of range: [{signal.min()}, {signal.max()}] vs [{min_val}, {max_val}]"
    
    return True
```

### Step 2: Baseline Correction & Noise Reduction

**Baseline Wander Removal** (High-pass filtering):
```python
def remove_baseline_wander(signal, fs, cutoff=0.5):
    """
    Remove low-frequency drift using Butterworth high-pass filter.
    
    Args:
        signal: Raw input signal
        fs: Sampling frequency (Hz)
        cutoff: High-pass cutoff frequency (Hz)
    
    Returns:
        Corrected signal without baseline drift
    """
    from scipy import signal as sp_signal
    
    # Normalize cutoff frequency
    nyquist = fs / 2
    normalized_cutoff = cutoff / nyquist
    
    # Design Butterworth filter
    b, a = sp_signal.butter(4, normalized_cutoff, btype='high')
    
    # Apply zero-phase filtering (forward-backward)
    corrected = sp_signal.filtfilt(b, a, signal)
    
    return corrected
```

**Noise Reduction** (Low-pass filtering + denoising):
```python
def denoise_signal(signal, fs, modality):
    """
    Denoise using Butterworth low-pass filter appropriate to modality.
    """
    # Modality-specific cutoff frequencies
    cutoff_freqs = {
        'ecg': 40,      # Hz (removes high-frequency noise)
        'spo2': 0.5,    # Hz (slowly varying)
        'hrv': 1.0,     # Hz
        'eda': 2.0,     # Hz
        'acc': 10.0,    # Hz
        'ppg': 20.0,    # Hz
        'temp': 0.1,    # Hz (very slow)
    }
    
    cutoff = cutoff_freqs.get(modality, 1.0)
    
    from scipy import signal as sp_signal
    nyquist = fs / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    
    # Design Butterworth filter
    b, a = sp_signal.butter(3, normalized_cutoff, btype='low')
    denoised = sp_signal.filtfilt(b, a, signal)
    
    return denoised
```

### Step 3: Temporal Interpolation to Standardized Sampling Rate

**Objective**: Resample all signals to a unified sampling rate (default: 100 Hz) for synchronized processing.

**Linear Interpolation** (Fast, suitable for high-frequency signals):
```python
def interpolate_linear(signal, fs_original, fs_target=100):
    """
    Linearly interpolate signal to target sampling rate.
    
    Args:
        signal: Original signal array
        fs_original: Original sampling frequency (Hz)
        fs_target: Target sampling frequency (Hz)
    
    Returns:
        Interpolated signal at target rate
    """
    from scipy.interpolate import interp1d
    
    # Create original time vector
    duration = len(signal) / fs_original
    t_original = np.linspace(0, duration, len(signal))
    
    # Create target time vector
    n_samples_target = int(duration * fs_target)
    t_target = np.linspace(0, duration, n_samples_target)
    
    # Linear interpolation
    f = interp1d(t_original, signal, kind='linear', bounds_error=False, fill_value='extrapolate')
    interpolated = f(t_target)
    
    return interpolated
```

**Cubic Spline Interpolation** (Smoother, suitable for signals with non-linear dynamics):
```python
def interpolate_cubic_spline(signal, fs_original, fs_target=100):
    """
    Cubic spline interpolation for smoother representation.
    
    Args:
        signal: Original signal array
        fs_original: Original sampling frequency (Hz)
        fs_target: Target sampling frequency (Hz)
    
    Returns:
        Interpolated signal with smoother transitions
    """
    from scipy.interpolate import CubicSpline
    
    duration = len(signal) / fs_original
    t_original = np.linspace(0, duration, len(signal))
    n_samples_target = int(duration * fs_target)
    t_target = np.linspace(0, duration, n_samples_target)
    
    # Cubic spline interpolation
    cs = CubicSpline(t_original, signal)
    interpolated = cs(t_target)
    
    return interpolated
```

### Step 4: Missing Data Imputation

**K-Nearest Neighbors Imputation**:
```python
def impute_missing_values(signal, method='knn', k=5):
    """
    Impute missing values (NaN) using KNN or forward-fill.
    
    Args:
        signal: Signal with potential NaN values
        method: 'knn' or 'forward_fill'
        k: Number of nearest neighbors
    
    Returns:
        Signal with imputed values
    """
    if method == 'knn':
        from sklearn.impute import KNNImputer
        
        signal_2d = signal.reshape(-1, 1)
        imputer = KNNImputer(n_neighbors=k)
        imputed = imputer.fit_transform(signal_2d).ravel()
        
    elif method == 'forward_fill':
        import pandas as pd
        
        series = pd.Series(signal)
        imputed = series.fillna(method='ffill').fillna(method='bfill').values
    
    return imputed
```

### Step 5: Normalization & Standardization

**Z-score Standardization** (Recommended for most modalities):
```python
def normalize_zscore(signal, computed_mean=None, computed_std=None):
    """
    Normalize signal to zero mean, unit variance.
    
    Args:
        signal: Input signal
        computed_mean: Pre-computed mean (e.g., from training set)
        computed_std: Pre-computed std (e.g., from training set)
    
    Returns:
        Normalized signal
    """
    if computed_mean is None:
        computed_mean = signal.mean()
    if computed_std is None:
        computed_std = signal.std()
    
    # Avoid division by zero
    if computed_std == 0:
        computed_std = 1.0
    
    normalized = (signal - computed_mean) / computed_std
    
    return normalized
```

**Min-Max Scaling** (For signals with meaningful bounds):
```python
def normalize_minmax(signal, min_val=None, max_val=None):
    """
    Normalize signal to range [0, 1].
    
    Args:
        signal: Input signal
        min_val: Minimum value (e.g., from training set)
        max_val: Maximum value (e.g., from training set)
    
    Returns:
        Normalized signal in [0, 1]
    """
    if min_val is None:
        min_val = signal.min()
    if max_val is None:
        max_val = signal.max()
    
    normalized = (signal - min_val) / (max_val - min_val + 1e-8)
    
    return np.clip(normalized, 0, 1)
```

### Complete Preprocessing Pipeline

```python
def preprocess_signal(raw_signal, fs_original, modality, config=None):
    """
    Complete preprocessing pipeline for a single signal.
    
    Args:
        raw_signal: Raw input signal
        fs_original: Original sampling frequency (Hz)
        modality: Type of signal ('ecg', 'spo2', etc.)
        config: Optional configuration overrides
    
    Returns:
        Preprocessed, normalized signal at standardized rate
    """
    if config is None:
        config = get_default_config(modality)
    
    # 1. Validation
    validate_signal_data(raw_signal, config)
    
    # 2. Handle missing values (before filtering)
    signal = impute_missing_values(raw_signal, method='forward_fill')
    
    # 3. Baseline correction
    signal = remove_baseline_wander(signal, fs_original, 
                                   cutoff=config['baseline_cutoff'])
    
    # 4. Noise reduction
    signal = denoise_signal(signal, fs_original, modality)
    
    # 5. Temporal interpolation
    signal = interpolate_cubic_spline(signal, fs_original, 
                                      fs_target=config['target_fs'])
    
    # 6. Normalization
    signal = normalize_zscore(signal)
    
    return signal
```

---

## Team-Based ML Organization

The ML pipeline is strategically organized across **five specialized engineering teams**, each with deep domain expertise in specific clinical conditions and optimization for unique signal characteristics.

### Team Assignments Matrix

| Team | Clinical Focus | Primary Modalities | Deep Learning Architecture | Lead Model | Status |
|------|----------------|------------------|---------------------------|-----------|--------|
| **Team 1** | Sleep Apnea & Stress | SpO2, HRV, EDA, TEMP, ACC | 1D-CNN (30s windows) | AASM-Epoch CNN | In Dev |
| **Team 2** | Anemia & Diabetes | SpO2, HR, Activity, Sleep | CNN + RNN/HMM | Spectral CNN + Temporal RNN | In Dev |
| **Team 3** | AFib & Cardiovascular | ECG, HR, BVP | ResNet-18 / 1D-CNN | ECG-ResNet | In Dev |
| **Team 4** | Burnout & Overtraining | HRV Trends, Activity, Sleep | CNN-LSTM Hybrid | Degradation LSTM | In Dev |
| **Team 5** | Tumor Prediction | MRI/CT Images | 2D-CNN | Classification CNN | In Dev |

---

## Team 1: Sleep Apnea & Stress Detection

### Clinical Objectives

**Sleep Apnea**: Detect obstructive sleep apnea through desaturation events and breathing anomalies
**Stress**: Identify acute and chronic stress through autonomic markers

### Essential Modalities

| Modality | Role | Key Features |
|----------|------|-------------|
| **SpO2** | Primary | Desaturation events (dips >3%), baseline decline |
| **HRV** | Secondary | Heart rate variability patterns, parasympathetic tone |
| **EDA** | Secondary | Sympathetic arousal spikes, baseline elevation |
| **TEMP** | Tertiary | Thermophysiological response to stress |
| **ACC** | Tertiary | Sleep stage classification (REM vs. NREM) |

### Datasets

- **Apnea-ECG Database** (PhysioNet): 100 patients, 10 hours each
- **Sleep-EDF** (PhysioNet): Polysomnography data with sleep annotations
- **Wearable Exam Stress Dataset**: Induced stress sessions with labeled stress levels

### Model Architecture

```
Input: 30-second windows (AASM sleep staging epoch)
       ├─ SpO2 (100 samples @ 100 Hz)
       ├─ HRV (100 samples @ 1 Hz resampled)
       ├─ EDA (100 samples @ 4 Hz resampled)
       └─ TEMP (100 samples @ 0.5 Hz resampled)
       
       │
       ├─ Conv1D(32 filters, 5-kernel) → BatchNorm → ReLU → MaxPool
       ├─ Conv1D(64 filters, 5-kernel) → BatchNorm → ReLU → MaxPool
       ├─ Conv1D(128 filters, 3-kernel) → BatchNorm → ReLU → GlobalAvgPool
       │
       └─ Fully Connected (256) → Dropout(0.5) → ReLU
          → Output: [Sleep Apnea Risk, Stress Level]
```

### Training Configuration

```yaml
# Train parameters
batch_size: 32
epochs: 100
learning_rate: 0.001
optimizer: Adam
loss: Binary Crossentropy (for apnea), MSE (for stress)

# Data split
train: 70%
validation: 15%
test: 15%

# Augmentation
temporal_shift: ±0.5 sec
amplitude_jitter: ±5%
dropout: 0.5
```

### Team 1 Location

`ml/experiments/exp_01/exp.ipynb` - Experimentation and validation notebook

---

## Team 2: Anemia & Diabetes Risk Assessment

### Clinical Objectives

**Anemia**: Detect iron-deficiency anemia through sustained SpO2/PPG deviations
**Diabetes**: Predict early-stage Type 2 diabetes risk through HRV patterns and metabolic indicators

### Essential Modalities

| Modality | Role | Key Features |
|----------|------|-------------|
| **SpO2** | Primary | Baseline oxygenation, chronotropic response |
| **HR/Activity** | Secondary | Physical exertion capacity, fatigue patterns |
| **HRV** | Secondary | Morning HRV levels, parasympathetic balance |
| **Sleep** | Tertiary | Circadian regularity, sleep quality metrics |

### Datasets

- **BIDMC PPG and Respiration Dataset**: 53 patients with PPG and respiratory data
- **PhysioNet MIMIC**: 40,000+ ICU records with laboratory values
- **Internal Diabetes Registry**: 500+ longitudinal patient records

### Model Architecture

**Two-Stage Approach**:

**Stage 1 - Spectral Feature Extraction (CNN)**:
```
Input: 1-hour SpO2/PPG window (3600 samples)
       │
       ├─ FFT → Frequency spectrum
       ├─ Conv1D(32, 7) → BatchNorm → ReLU
       ├─ Conv1D(64, 5) → BatchNorm → ReLU
       ├─ Conv1D(128, 3) → BatchNorm → ReLU
       └─ GlobalAvgPool → Dense(64)
       
Output: Spectral feature vector (64-dim)
```

**Stage 2 - Temporal Progression (RNN/HMM)**:
```
Input: Sequence of daily feature vectors (30 days)
       │
       ├─ LSTM(128, return_sequences=True) → Dropout(0.5)
       ├─ LSTM(64) → Dropout(0.5)
       ├─ Dense(32) → ReLU
       └─ Dense(2) → Softmax
       
Output: [Anemia Risk, Diabetes Risk]
```

### Training Configuration

```yaml
# Two-stage training
stage1:
  batch_size: 64
  epochs: 50
  pretrain: Spectral reconstruction autoencoder
  
stage2:
  batch_size: 32
  epochs: 80
  sequence_length: 30 (days)
  learning_rate: 0.0005

# Loss function
stage1: MSE (reconstruction) + Contrastive loss
stage2: Focal loss (class imbalance)
```

### Team 2 Location

`ml/experiments/exp_02/exp.ipynb` - Experimentation and validation notebook

---

## Team 3: Atrial Fibrillation & Cardiovascular Risk

### Clinical Objectives

**AFib**: Detect paroxysmal and persistent atrial fibrillation through irregular ECG patterns
**Cardiovascular Risk**: Assess risk of myocardial infarction and stroke

### Essential Modalities

| Modality | Role | Key Features |
|----------|------|-------------|
| **ECG** | Primary | P-wave morphology, R-R interval variability, QT duration |
| **HR** | Secondary | Heart rate stability, response to exertion |
| **BVP** | Tertiary | Pulse regularity, vascular stiffness indicators |

### Datasets

- **MIT-BIH Atrial Fibrillation Database**: 25 records, 10 hours each
- **MIT-BIH Normal Sinus Rhythm Database**: 18 healthy controls (24 hours each)
- **Long Term AF Database**: 84 subjects, 38 hours each

### Model Architecture

```
Input: 10-second ECG window (2500 samples @ 250 Hz)
       │
       ├─ Preprocessing
       │  ├─ R-peak detection (Pan-Tompkins algorithm)
       │  ├─ Centering on R-peaks
       │  └─ Baseline wander removal (high-pass @ 0.5 Hz)
       │
       ├─ ResNet-18 CNN
       │  ├─ Conv2D(64, 7, stride=2) → BatchNorm → ReLU
       │  ├─ ResBlock(64) × 2
       │  ├─ ResBlock(128, stride=2) × 2
       │  ├─ ResBlock(256, stride=2) × 2
       │  ├─ ResBlock(512, stride=2) × 2
       │  ├─ GlobalAvgPool
       │  └─ Dense(2) → Softmax
       │
Output: [AFib Risk, Cardiovascular Risk]
```

### Key Implementation Details

**R-Peak Detection** (Pan-Tompkins Algorithm):
```python
def detect_r_peaks(ecg_signal, fs=250):
    """
    Detect R-peaks in ECG using Pan-Tompkins algorithm.
    
    Returns:
        Indices of R-peaks in the signal
    """
    from scipy.signal import find_peaks
    
    # Bandpass filter (5-15 Hz)
    filtered = bandpass_filter(ecg_signal, 5, 15, fs)
    
    # Differentiate
    differentiated = np.diff(filtered)
    
    # Square
    squared = differentiated ** 2
    
    # Moving window integration (200ms window)
    window_size = int(0.2 * fs)
    integrated = np.convolve(squared, np.ones(window_size) / window_size)
    
    # Find peaks with adaptive threshold
    threshold = 0.6 * integrated.max()
    r_peaks, _ = find_peaks(integrated, height=threshold, distance=fs//2)
    
    return r_peaks
```

### Training Configuration

```yaml
batch_size: 32
epochs: 150
learning_rate: 0.001 (with cosine annealing)
optimizer: SGD with momentum 0.9

# Data augmentation
temporal_shift: ±50ms
amplitude_scaling: 0.95-1.05
heart_rate_variation: Simulate different RR intervals

# Class weighting (handle AFib rarity)
positive_weight: 5.0
negative_weight: 1.0
```

### Team 3 Location

`ml/experiments/exp_03/exp.ipynb` - Experimentation and validation notebook

---

## Team 4: Burnout & Overtraining Detection

### Clinical Objectives

**Burnout**: Identify professional burnout through sustained HRV decline and inadequate recovery
**Overtraining**: Detect overtraining syndrome through maladaptive training response

### Essential Modalities

| Modality | Role | Key Features |
|----------|------|-------------|
| **HRV Trends** | Primary | Week-over-week decline, reduced parasympathetic tone |
| **Resting HR** | Primary | Morning HR elevation, baseline creep |
| **Activity** | Secondary | Physical exertion level, recovery patterns |
| **Sleep** | Secondary | Sleep duration, quality metrics |

### Datasets

- **Wearable Stress Dataset**: Longitudinal wearable data (30+ days)
- **Structured Exercise Dataset**: Athletes with induced overtraining
- **Occupational Burnout Study**: Healthcare workers (100+ subjects, 3+ months)

### Model Architecture

**Hybrid CNN-LSTM for Dual Temporal Scales**:

```
Input: 30-day time series
       ├─ Daily windows: [Morning HRV, Resting HR, Sleep score, Activity]
       │                  (30 samples, 4 features each)
       │
       │─ Local Pattern Extraction (CNN)
       │  ├─ Conv1D(32 filters, 3-kernel, dilation=1)
       │  ├─ Conv1D(32 filters, 3-kernel, dilation=2)
       │  ├─ Conv1D(32 filters, 3-kernel, dilation=4)
       │  └─ MaxPool → Output: (30, 32)
       │
       │─ Long-term Trend Modeling (LSTM)
       │  ├─ Bidirectional LSTM(64) → Dropout(0.5)
       │  ├─ LSTM(32) → Dropout(0.5)
       │  └─ Dense(16) → ReLU
       │
Output: [Burnout Risk, Overtraining Risk]
```

### Key Concepts

**Morning HRV Decline Pattern**:
```python
def detect_hrv_decline(daily_hrv_values, window_days=7):
    """
    Detect sustained HRV decline indicative of fatigue.
    
    Args:
        daily_hrv_values: Daily HRV measurements (30+ days)
        window_days: Rolling window for trend detection
    
    Returns:
        Decimal percentage decline per week
    """
    from scipy.stats import linregress
    
    declines = []
    for i in range(window_days, len(daily_hrv_values)):
        window = daily_hrv_values[i-window_days:i]
        
        x = np.arange(len(window))
        slope, _, _, _, _ = linregress(x, window)
        
        declines.append(slope)
    
    # Average decline per week
    avg_decline = np.mean(declines)
    
    return avg_decline
```

### Training Configuration

```yaml
batch_size: 16
epochs: 100
learning_rate: 0.0005
optimizer: Adam

# Sequence configuration
sequence_length: 30 (days)
prediction_horizon: 7 (days ahead)

# Class imbalance handling
pos_weight: 2.0 (burnout/overtraining less frequent)

# Temporal augmentation
time_warp: Scale different days' durations (0.9-1.1x)
window_shift: Slide arbitrary start dates
```

### Team 4 Location

`ml/experiments/exp_04/exp.ipynb` - Experimentation and validation notebook

---

## Team 5: Brain Tumor Identification

### Clinical Objectives

**Tumor Detection**: Identify presence of brain tumor in MRI/CT scans
**Tumor Classification**: Classify tumor type (glioma, meningioma, pituitary)
**Severity Assessment**: Determine malignancy (benign vs. malignant)

### Essential Modalities

| Modality | Role | Key Features |
|----------|------|-------------|
| **MRI T2** | Primary | Best for brain tissue differentiation |
| **MRI FLAIR** | Primary | Optimal for lesion detection |
| **MRI T1 + Gadolinium** | Secondary | Tumor vascularity, blood-brain barrier breakdown |
| **CT** | Tertiary | Bone involvement, additional confirmation |

### Datasets

- **Kaggle Brain Tumor MRI Dataset**: 3,000+ T2/FLAIR sequences
- **BraTS Challenge Dataset**: 500 subjects with segmentation annotations
- **TCGA Radiogenomics**: Molecular subtyping correlates

### Model Architecture

```
Input: 2D MRI Slice (256 × 256 pixels, single-channel)
       │
       ├─ Conv2D(32, 3×3, padding='same') → BatchNorm → ReLU
       ├─ Conv2D(32, 3×3) → BatchNorm → ReLU → MaxPool(2×2)
       │
       ├─ Conv2D(64, 3×3, padding='same') → BatchNorm → ReLU
       ├─ Conv2D(64, 3×3) → BatchNorm → ReLU → MaxPool(2×2)
       │
       ├─ Conv2D(128, 3×3, padding='same') → BatchNorm → ReLU
       ├─ Conv2D(128, 3×3) → BatchNorm → ReLU → MaxPool(2×2)
       │
       ├─ Conv2D(256, 3×3, padding='same') → BatchNorm → ReLU
       ├─ Conv2D(256, 3×3) → BatchNorm → ReLU → MaxPool(2×2)
       │
       ├─ GlobalAvgPool → Dense(512) → Dropout(0.5) → ReLU
       ├─ Dense(256) → Dropout(0.5) → ReLU
       └─ Dense(4) → Softmax
       
Output: [No Tumor, Glioma, Meningioma, Pituitary, Malignant Score]
```

**Multi-Slice Aggregation** (For full 3D context):
```python
def aggregate_3d_predictions(slice_predictions, aggregation='attention'):
    """
    Combine predictions from multiple 2D slices for 3D context.
    
    Args:
        slice_predictions: (N_slices, 4) array of class probabilities
        aggregation: 'attention', 'max', 'mean'
    
    Returns:
        Final tumor probability
    """
    if aggregation == 'mean':
        return slice_predictions.mean(axis=0)
    
    elif aggregation == 'max':
        # Use maximum across slices (assume worst-case for safety)
        return slice_predictions.max(axis=0)
    
    elif aggregation == 'attention':
        # Learn which slices are most informative
        weights = attention_pooling(slice_predictions)  # (N_slices, 1)
        return (slice_predictions * weights).sum(axis=0) / weights.sum()
    
    return slice_predictions.mean(axis=0)
```

### Training Configuration

```yaml
batch_size: 64
epochs: 200
learning_rate: 0.001
optimizer: AdamW (with weight decay)

# Data augmentation (critical for medical imaging)
rotation: ±20°
elastic_deformation: sigma=10
intensity_shift: ±20%
brightness_contrast: 0.2-1.8
gaussian_noise: σ = 0.01

# Class weights
tumor_present: 2.0
tumor_absent: 1.0

# Loss function
Focal loss (γ=2.0) for class imbalance
Dice coefficient for segmentation overlap
```

### Preprocessing for Medical Images

```python
def preprocess_medical_image(image_path, target_shape=(256, 256)):
    """
    Preprocess DICOM or NIfTI medical image.
    """
    # Load DICOM
    if image_path.endswith('.dcm'):
        import pydicom
        dcm = pydicom.dcmread(image_path)
        image = dcm.pixel_array.astype(float)
    else:
        import nibabel as nib
        nib_data = nib.load(image_path)
        image = nib_data.get_fdata()
    
    # Hounsfield Unit normalization (for CT)
    image = np.clip(image, -1000, 3000)
    
    # Intensity normalization
    image = (image - image.mean()) / (image.std() + 1e-8)
    
    # Resize to target
    from skimage.transform import resize
    image = resize(image, target_shape, mode='constant')
    
    return image.astype(np.float32)
```

### Team 5 Location

`ml/experiments/exp_05/exp.ipynb` - Experimentation and validation notebook

---

## Feature Engineering

### Modality-Agnostic Features

Computed for all time-series signals:

```python
def extract_statistical_features(signal):
    """Extract basic statistical features."""
    return {
        'mean': signal.mean(),
        'std': signal.std(),
        'min': signal.min(),
        'max': signal.max(),
        'median': np.median(signal),
        'q25': np.percentile(signal, 25),
        'q75': np.percentile(signal, 75),
        'iqr': np.percentile(signal, 75) - np.percentile(signal, 25),
        'skewness': pd.Series(signal).skew(),
        'kurtosis': pd.Series(signal).kurtosis(),
    }

def extract_frequency_features(signal, fs=100):
    """Extract frequency-domain features via FFT."""
    from scipy import signal as sp_signal
    
    # Compute power spectral density
    freqs, pxx = sp_signal.welch(signal, fs=fs, nperseg=256)
    
    return {
        'spectral_centroid': np.sum(freqs * pxx) / np.sum(pxx),
        'spectral_entropy': pd.Series(pxx).entropy(),
        'power_low_freq': pxx[freqs < 1].sum(),
        'power_mid_freq': pxx[(freqs >= 1) & (freqs < 5)].sum(),
        'power_high_freq': pxx[freqs >= 5].sum(),
    }

def extract_entropy_features(signal):
    """Extract complexity measures."""
    # Approximate entropy (regularity measure)
    m, r = 2, 0.2 * signal.std()
    
    def _maxdist(x_i, x_j):
        return max([abs(ua - va) for ua, va in zip(x_i, x_j)])
    
    def _phi(m):
        x = [[signal[j] for j in range(i, i + m)] for i in range(len(signal) - m + 1)]
        c = [len([1 for x_j in x if _maxdist(x_i, x_j) <= r]) / (len(signal) - m + 1.0)
             for x_i in x]
        return (len(signal) - m + 1.0) ** (-1) * sum(np.log(c))
    
    apen = abs(_phi(m + 1) - _phi(m))
    
    return {'approximate_entropy': apen}
```

### Modality-Specific Features

**ECG/HRV Features**:
```python
def extract_ecg_features(ecg_signal, fs=250):
    """Extract ECG-specific morphological features."""
    from scipy.signal import find_peaks
    
    # R-peak detection
    r_peaks = detect_r_peaks(ecg_signal, fs)
    
    # RR intervals (in milliseconds)
    rr_intervals = np.diff(r_peaks) / fs * 1000
    
    return {
        'mean_rr': rr_intervals.mean(),
        'std_rr': rr_intervals.std(),
        'rmssd': np.sqrt(np.mean(np.diff(rr_intervals) ** 2)),  # Root Mean Sq of Successive Diffs
        'nn50': np.sum(np.abs(np.diff(rr_intervals)) > 50),      # Count of RR diffs > 50ms
        'pnn50': nn50 / len(rr_intervals) * 100,                  # Percentage of NN50
        'lfhf_ratio': compute_lfhf_ratio(rr_intervals),          # LF/HF power ratio
        'heart_rate_variability_index': len(rr_intervals) / (rr_intervals.max() - rr_intervals.min()),
    }
```

**SpO2/PPG Features**:
```python
def extract_spo2_features(spo2_signal, window_sec=30):
    """Extract SpO2-specific features for apnea detection."""
    
    # Desaturation events (dips > 3%)
    baseline = np.percentile(spo2_signal, 95)
    dips = spo2_signal[spo2_signal < (baseline - 3)]
    
    return {
        'baseline_spo2': baseline,
        'min_spo2': spo2_signal.min(),
        'num_desaturation_events': len(dips),
        'mean_dip_depth': (baseline - dips).mean() if len(dips) > 0 else 0,
        'time_below_90pct': (spo2_signal < 90).sum() / len(spo2_signal) * 100,
        'oxygen_variability': spo2_signal.std(),
    }
```

**Image Features**:
```python
def extract_image_features(image):
    """Extract hand-crafted image features for explainability."""
    # Texture analysis (Haralick features, LBP, GLCM)
    from skimage.feature import local_binary_pattern, greycomatrix, greycoprops
    
    # Local Binary Pattern (texture descriptor)
    lbp = local_binary_pattern(image, P=8, R=1)
    lbp_hist, _ = np.histogram(lbp, bins=256, range=(0, 256))
    
    # Gray-Level Co-occurrence Matrix (GLCM)
    glcm = greycomatrix(image.astype(np.uint8), [1], [0], 256, symmetric=True, normed=True)
    contrast = greycoprops(glcm, 'contrast')[0, 0]
    dissimilarity = greycoprops(glcm, 'dissimilarity')[0, 0]
    homogeneity = greycoprops(glcm, 'homogeneity')[0, 0]
    
    return {
        'lbp_histogram': lbp_hist,
        'glcm_contrast': contrast,
        'glcm_dissimilarity': dissimilarity,
        'glcm_homogeneity': homogeneity,
    }
```

---

## Model Architectures

### Common Building Blocks

**ResBlock (Residual Connection)**:
```python
class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1):
        super().__init__()
        
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size, 
                               stride=stride, padding=(kernel_size-1)//2)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size, 
                               padding=(kernel_size-1)//2)
        self.bn2 = nn.BatchNorm1d(out_channels)
        
        # Skip connection
        self.skip = nn.Identity()
        if stride != 1 or in_channels != out_channels:
            self.skip = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, 1, stride=stride),
                nn.BatchNorm1d(out_channels)
            )
    
    def forward(self, x):
        residual = self.skip(x)
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        out += residual
        out = self.relu(out)
        
        return out
```

**Attention Mechanism**:
```python
class AttentionModule(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.query = nn.Linear(dim, dim)
        self.key = nn.Linear(dim, dim)
        self.value = nn.Linear(dim, dim)
        self.scale = np.sqrt(dim)
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, dim)
        
        Returns:
            weighted_sum: (batch, dim)
        """
        q = self.query(x)  # (batch, seq_len, dim)
        k = self.key(x)
        v = self.value(x)
        
        # Attention weights
        scores = torch.matmul(q, k.transpose(-2, -1)) / self.scale
        weights = torch.softmax(scores, dim=-1)
        
        # Weighted values
        out = torch.matmul(weights, v)  # (batch, seq_len, dim)
        
        # Global aggregation
        out = out.mean(dim=1)  # (batch, dim)
        
        return out
```

---

## Training & Validation

### Training Loop

```python
def train_model(model, train_loader, val_loader, num_epochs, device):
    """
    Training loop with validation and early stopping.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 
                                                           mode='min', 
                                                           factor=0.5, 
                                                           patience=10)
    
    best_val_loss = float('inf')
    patience = 20
    patience_counter = 0
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            # Forward pass
            output = model(data)
            loss = compute_loss(output, target)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation phase
        model.eval()
        val_loss = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                loss = compute_loss(output, target)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            # Save checkpoint
            torch.save({
                'epoch': epoch,
                'model_state': model.state_dict(),
                'optimizer_state': optimizer.state_dict(),
                'best_val_loss': best_val_loss,
            }, 'best_model.pth')
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}")
    
    return model
```

### Cross-Validation Strategy

```python
def stratified_kfold_validation(dataset, model_class, num_folds=5):
    """
    Stratified K-Fold cross-validation with separate test set.
    """
    from sklearn.model_selection import StratifiedKFold
    
    skf = StratifiedKFold(n_splits=num_folds, shuffle=True, random_state=42)
    
    fold_scores = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(dataset, dataset.labels)):
        # Create fold datasets
        train_data = torch.utils.data.Subset(dataset, train_idx)
        val_data = torch.utils.data.Subset(dataset, val_idx)
        
        train_loader = torch.utils.data.DataLoader(train_data, batch_size=32, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_data, batch_size=32)
        
        # Train model
        model = model_class()
        train_model(model, train_loader, val_loader, num_epochs=100, device='cuda')
        
        # Evaluate
        metrics = evaluate_model(model, val_loader, device='cuda')
        fold_scores.append(metrics)
        
        print(f"Fold {fold}: AUC = {metrics['auc']:.4f}, F1 = {metrics['f1']:.4f}")
    
    # Aggregate results
    mean_auc = np.mean([m['auc'] for m in fold_scores])
    std_auc = np.std([m['auc'] for m in fold_scores])
    
    return mean_auc, std_auc
```

---

## Model Evaluation

### Classification Metrics

**For Binary Classification** (e.g., Apnea: Yes/No):

```python
def compute_metrics(predictions, targets, threshold=0.5):
    """
    Compute comprehensive classification metrics.
    """
    from sklearn.metrics import (
        confusion_matrix, roc_auc_score, roc_curve,
        precision_recall_curve, f1_score, cohen_kappa_score
    )
    
    # Binary predictions (threshold at 0.5)
    preds_binary = (predictions >= threshold).astype(int)
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(targets, preds_binary).ravel()
    
    # Sensitivity (Recall / True Positive Rate)
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    # Specificity
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    # Precision
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    
    # F1-Score
    f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
    
    # AUC-ROC
    auc_roc = roc_auc_score(targets, predictions)
    
    # Cohen's Kappa
    kappa = cohen_kappa_score(targets, preds_binary)
    
    return {
        'sensitivity': sensitivity,      # How many actual positives identified
        'specificity': specificity,      # How many actual negatives identified
        'precision': precision,          # How many positive predictions correct
        'f1_score': f1,
        'auc_roc': auc_roc,
        'kappa': kappa,
        'true_positives': tp,
        'false_positives': fp,
        'true_negatives': tn,
        'false_negatives': fn,
    }
```

### Visualization

```python
def plot_roc_curve(predictions, targets):
    """Plot ROC curve for model evaluation."""
    from sklearn.metrics import roc_curve, auc
    import matplotlib.pyplot as plt
    
    fpr, tpr, thresholds = roc_curve(targets, predictions)
    roc_auc = auc(fpr, tpr)
    
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    plt.show()
```

---

## Inference Pipeline

### Real-Time Prediction Flow

```python
class InferenceEngine:
    def __init__(self, model_path, device='cuda'):
        self.device = torch.device(device)
        self.model = self.load_model(model_path)
        self.model.eval()
    
    def predict(self, patient_data):
        """
        End-to-end prediction for new patient data.
        
        Args:
            patient_data: {
                'ecg': np.array,
                'spo2': np.array,
                'hrv': np.array,
                'eda': np.array,
                'image': np.array (optional),
            }
        
        Returns:
            Multi-task predictions and interpretability features
        """
        # Preprocessing
        processed_signals = self.preprocess_multimodal_data(patient_data)
        
        # Feature extraction
        features = self.extract_features(processed_signals)
        
        # Convert to tensors
        feature_tensor = torch.from_numpy(features).unsqueeze(0).to(self.device)
        
        # Model inference
        with torch.no_grad():
            predictions = self.model(feature_tensor)
        
        # Post-processing
        output = self.postprocess_predictions(predictions)
        
        # Confidence quantification
        confidence = self.compute_confidence(predictions)
        
        return {
            'sleep_apnea_risk': output['apnea_prob'],
            'afib_risk': output['afib_prob'],
            'diabetes_risk': output['diabetes_prob'],
            'stress_level': output['stress_score'],
            'burnout_index': output['burnout_score'],
            'tumor_classification': output['tumor_class'],
            'confidence_scores': confidence,
            'uncertainty_estimate': 1 - confidence.max(),
        }
    
    def preprocess_multimodal_data(self, data):
        """Apply preprocessing pipeline to all modalities."""
        processed = {}
        
        for modality, signal in data.items():
            if signal is not None:
                config = get_modality_config(modality)
                processed[modality] = preprocess_signal(
                    signal, 
                    fs_original=config['original_fs'],
                    modality=modality,
                    config=config
                )
        
        return processed
    
    def extract_features(self, signals):
        """Extract team-specific features in parallel."""
        features = []
        
        # Team 1 features
        t1_features = self.extract_team1_features(signals)
        features.append(t1_features)
        
        # Team 2 features
        t2_features = self.extract_team2_features(signals)
        features.append(t2_features)
        
        # ... Teams 3, 4, 5 ...
        
        return np.concatenate(features, axis=-1)
    
    def postprocess_predictions(self, raw_predictions):
        """Apply clinical thresholds and interpretations."""
        return {
            'apnea_prob': torch.sigmoid(raw_predictions[0, 0]).item(),
            'afib_prob': torch.sigmoid(raw_predictions[0, 1]).item(),
            'diabetes_prob': torch.sigmoid(raw_predictions[0, 2]).item(),
            'stress_score': torch.sigmoid(raw_predictions[0, 3]).item() * 100,
            'burnout_score': torch.sigmoid(raw_predictions[0, 4]).item() * 100,
            'tumor_class': torch.argmax(raw_predictions[0, 5:9]).item(),
        }
```

---

## Deployment & Integration

### Model Serialization

```python
# Save trained model
checkpoint = {
    'model_state_dict': model.state_dict(),
    'model_architecture': model.__class__.__name__,
    'hyperparameters': config,
    'training_metrics': metrics,
    'feature_scaler': scaler,  # For normalization during inference
    'class_labels': ['No Tumor', 'Glioma', 'Meningioma', 'Pituitary'],
}

torch.save(checkpoint, 'ml/models/model.pt')
```

### Integration with FastAPI

```python
from fastapi import FastAPI, File, UploadFile
import torch
import numpy as np

app = FastAPI()

# Load model on startup
inference_engine = None

@app.on_event("startup")
def load_models():
    global inference_engine
    inference_engine = InferenceEngine('ml/models/model.pt', device='cuda')

@app.post("/predict")
async def predict(
    ecg: UploadFile = File(...),
    spo2: UploadFile = File(...),
    image: UploadFile = File(None),
):
    """
    Multimodal prediction endpoint.
    """
    # Load files
    ecg_data = np.load(await ecg.read())
    spo2_data = np.load(await spo2.read())
    
    # Predict
    result = inference_engine.predict({
        'ecg': ecg_data,
        'spo2': spo2_data,
        'image': image if image else None,
    })
    
    return result
```

---

## Configuration Management

### `ml/config.yaml`

```yaml
# Global Configuration

preprocessing:
  target_sampling_rate: 100  # Hz
  standardization_method: 'zscore'  # or 'minmax'
  interpolation_method: 'cubic_spline'  # or 'linear'
  filter_order: 4

# Team-Specific Configuration

teams:
  team_1:
    name: "Sleep Apnea & Stress"
    primary_modalities: [spo2, hrv, eda, temp, acc]
    model_type: "CNN_1D"
    window_size_sec: 30
    overlap_pct: 50
    batch_size: 32
    learning_rate: 0.001
    epochs: 100
    thresholds:
      apnea_risk_high: 0.7
      stress_level_high: 80
  
  team_2:
    name: "Anemia & Diabetes"
    primary_modalities: [spo2, hr, activity, sleep]
    model_type: "CNN_RNN"
    window_size_sec: 3600
    sequence_length_days: 30
    batch_size: 64
    learning_rate: 0.0005
    epochs: 80
    thresholds:
      anemia_risk_high: 0.75
      diabetes_risk_high: 0.65
  
  # ... teams 3-5 configurations ...

models:
  ensemble_strategy: 'weighted_voting'  # Combine team predictions
  team_weights:
    team_1: 1.0
    team_2: 1.0
    team_3: 1.2  # AFib detection weighted higher
    team_4: 0.9
    team_5: 1.1  # Tumor detection weighted higher

inference:
  device: 'cuda'
  batch_size: 32
  confidence_threshold: 0.6
  uncertainty_method: 'monte_carlo_dropout'
  uncertainty_samples: 10
```

---

## Version Control & Model Registry

### Model Versioning

```python
class ModelRegistry:
    """Track and manage model versions."""
    
    def __init__(self, registry_path='ml/models/registry.json'):
        self.registry = self.load_registry(registry_path)
        self.registry_path = registry_path
    
    def register_model(self, model_path, metrics, train_config):
        """Register new trained model."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'model_path': model_path,
            'metrics': metrics,
            'config': train_config,
            'version': len(self.registry) + 1,
            'status': 'candidate',  # pending review
        }
        
        self.registry.append(entry)
        self.save_registry()
        
        return entry['version']
    
    def promote_to_production(self, version):
        """Promote model version to production."""
        # Mark old production as archived
        for entry in self.registry:
            if entry['status'] == 'production':
                entry['status'] = 'archived'
        
        # Promote new version
        for entry in self.registry:
            if entry['version'] == version:
                entry['status'] = 'production'
        
        self.save_registry()
```

---

## Continuous Improvement

### Retraining Pipeline

```python
def schedule_retraining(
    frequency_days=30,
    min_new_samples=1000,
    performance_threshold=0.95
):
    """
    Scheduled retraining based on new clinical data and performance drift.
    """
    import schedule
    
    def retrain_job():
        # Check performance on recent data
        recent_metrics = evaluate_on_recent_data()
        
        if recent_metrics['auc'] < performance_threshold:
            print("Performance drift detected, initiating retraining...")
            
            # Collect new training data
            new_data = collect_recent_clinical_data(min_samples=min_new_samples)
            
            # Retrain models
            for team_id in range(1, 6):
                retrain_team_model(team_id, new_data)
            
            # Validate before promotion
            validate_new_models(new_data)
    
    schedule.every(frequency_days).days.do(retrain_job)
```

---

## References & Further Reading

- [PyTorch Documentation](https://pytorch.org/docs/)
- [Signal Processing with SciPy](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [Medical Image Analysis Review](https://www.sciencedirect.com/journal/medical-image-analysis)
- [Deep Learning for Healthcare (MIT Press)](https://mitpress.mit.edu/)

---

**Last Updated**: February 28, 2026  
**Status**: Active Development  
**Next Review**: April 2026
