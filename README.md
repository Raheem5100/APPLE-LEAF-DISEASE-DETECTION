# 🍃 Apple Leaf Disease Detection

A professional Flask web application for detecting apple leaf diseases using deep learning.

## 📁 Project Structure

```
apple_leaf_disease/
├── app.py                  # Main Flask application
├── model_Aa.keras          # ← Place your model here
├── requirements.txt
├── instance/
│   └── history.json        # Auto-created: prediction history
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/            # Auto-created: uploaded images
└── templates/
    ├── base.html
    ├── index.html           # Upload page
    ├── result.html          # Prediction results + charts
    ├── history.html         # All past scans
    └── stats.html           # Analytics dashboard
```

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Place your model
Copy `model_Aa.keras` into the project root directory.

### 3. Run the app
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

## 🌿 Disease Classes

| Class | Display Name | Severity |
|-------|-------------|----------|
| `Apple___Cedar_apple_rust` | Cedar Apple Rust | Moderate |
| `Apple___Apple_scab` | Apple Scab | High |
| `Apple___healthy` | Healthy | None |
| `Apple___Black_rot` | Black Rot | Severe |

## 📄 Pages

- **`/`** — Upload leaf image for disease detection
- **`/predict`** — POST endpoint, processes image and shows result
- **`/history`** — Browse all previous scans with filter buttons
- **`/stats`** — Analytics dashboard with charts and KPI metrics

## 📊 Features

- Deep learning inference with TensorFlow/Keras
- Probability distribution bar & donut charts (Chart.js)
- Professional disease cure/treatment information
- Persistent scan history (JSON storage)
- Analytics dashboard with trend charts
- Dark agricultural theme
- Responsive design
- Drag & drop image upload
- Demo mode (if model not found, uses random predictions for UI testing)

## ⚙️ Configuration

Edit `app.py` to change:
- `app.secret_key` — Change for production
- `app.config['MAX_CONTENT_LENGTH']` — Max upload size (default 16MB)
- Image input size (default 224×224) in `preprocess_image()`
