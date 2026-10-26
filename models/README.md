# VeritasAI Models Directory

## Model Artifacts & Architecture

### 1. Stylometric & Linguistic Misinformation Classifier
- **Artifact**: `models/stylistic_classifier.joblib`
- **Architecture**: N-gram Term Frequency - Inverse Document Frequency (TF-IDF) feature extraction coupled with a calibrated Logistic Regression classifier.
- **Features Extracted**:
  - Unigrams and bigrams
  - Punctuation & capitalization density (exclamation ratio, uppercase word ratio)
  - Clickbait syntactical pattern matching
  - Journalistic attribution marker density
- **Performance on Held-Out Test Split**:
  - Accuracy: 90.00%
  - F1-Score: 0.9091
  - Misinformation Risk Recall: 100%
- **Crucial Limitation**: The classifier identifies *stylistic and rhetorical markers* associated with manipulative or sensationalist text. It cannot verify factual truth or real-world events without external evidence retrieval.

### 2. Multimodal Vision Pipeline
- **Module**: `backend/app/services/image_analyzer.py`
- **Framework**: PIL (Python Imaging Library) + PyTorch / TorchVision.
- **Capabilities**:
  - Image validation and decompression bomb prevention
  - Lighting, brightness, and contrast extraction
  - Multimodal contextual consistency checking (comparing text assertions against visual parameters)
- **Ethical & Technical Disclaimer**: Image-text relevance assesses whether an image matches the described scene. It does not certify historical capture dates or claim deepfake detection without forensic watermarking models.
