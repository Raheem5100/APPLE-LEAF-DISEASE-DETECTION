import os
import json
import uuid
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from PIL import Image
import tensorflow as tf

app = Flask(__name__)
app.secret_key = 'apple_leaf_disease_secret_key_2024'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['HISTORY_FILE'] = os.path.join('instance', 'history.json')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

CLASS_NAMES = [
    'Apple___Cedar_apple_rust',
    'Apple___Apple_scab',
    'Apple___healthy',
    'Apple___Black_rot'
]

DISEASE_INFO = {
    'Apple___Cedar_apple_rust': {
        'display_name': 'Cedar Apple Rust',
        'severity': 'Moderate',
        'severity_level': 2,
        'description': 'Cedar apple rust is a fungal disease caused by Gymnosporangium juniperi-virginianae. It produces striking orange or yellow spots on the upper surface of apple leaves, with tube-like structures on the undersides. The disease requires two host plants — apple and eastern red cedar — to complete its lifecycle.',
        'symptoms': [
            'Bright orange-yellow spots (1–10 mm) on upper leaf surfaces',
            'Pale yellow halos surrounding spots',
            'Tube-like structures (aecia) on leaf undersides',
            'Premature leaf drop in severe cases',
            'Occasional fruit spotting and distortion'
        ],
        'cures': [
            {
                'title': 'Fungicide Application',
                'detail': 'Apply myclobutanil (Eagle, Rally) or propiconazole at pink bud stage. Repeat every 7–10 days during wet spring periods. Mancozeb is effective as a protectant when applied before infection.'
            },
            {
                'title': 'Remove Alternate Hosts',
                'detail': 'Eliminate eastern red cedar and other juniper species within 1–2 miles if possible. Remove galls from cedars in late winter before orange spore horns form in spring.'
            },
            {
                'title': 'Resistant Varieties',
                'detail': 'Plant resistant apple varieties such as Liberty, Redfree, or Enterprise for long-term management. Avoid Fuji, Gala, and Golden Delicious which are highly susceptible.'
            },
            {
                'title': 'Cultural Practices',
                'detail': 'Improve air circulation by proper pruning. Avoid overhead irrigation. Collect and destroy fallen infected leaves in autumn to reduce overwintering spores.'
            }
        ],
        'color': '#F59E0B',
        'icon': '🟡'
    },
    'Apple___Apple_scab': {
        'display_name': 'Apple Scab',
        'severity': 'High',
        'severity_level': 3,
        'description': 'Apple scab is one of the most economically damaging diseases of apple trees worldwide, caused by the fungus Venturia inaequalis. It thrives in cool, wet spring conditions and can defoliate trees entirely if left unmanaged, severely reducing fruit quality and yield.',
        'symptoms': [
            'Olive-green to dark brown, velvety lesions on leaves',
            'Angular lesions often bounded by leaf veins',
            'Yellowing and premature leaf drop',
            'Scabby, cracked lesions on fruit surface',
            'Deformed or stunted fruit in severe infections'
        ],
        'cures': [
            {
                'title': 'Preventive Fungicide Program',
                'detail': 'Begin applications at green tip stage using captan, mancozeb, or sulfur. Follow a 7–14 day spray schedule during primary infection periods (pink through petal fall). Use sterol inhibitors (myclobutanil, trifloxystrobin) for curative action within 72–96 hours of infection.'
            },
            {
                'title': 'Sanitation',
                'detail': 'Rake and destroy fallen leaves in autumn — this is the primary overwintering site of the fungus. Mow and shred leaves to accelerate decomposition. Apply urea (5%) to fallen leaves to reduce viable spore production.'
            },
            {
                'title': 'Pruning for Airflow',
                'detail': 'Open the canopy with annual pruning to reduce humidity and leaf wetness duration. Train trees to central leader or open vase forms. Remove water sprouts and crossing branches.'
            },
            {
                'title': 'Biological Control',
                'detail': 'Apply Bacillus subtilis (Serenade) or Trichoderma-based products as supplementary management. These are best used within organic programs or to reduce chemical load in low-pressure years.'
            }
        ],
        'color': '#EF4444',
        'icon': '🔴'
    },
    'Apple___healthy': {
        'display_name': 'Healthy',
        'severity': 'None',
        'severity_level': 0,
        'description': 'Your apple leaf appears to be in excellent health. No signs of fungal, bacterial, or viral disease are detected. Healthy apple leaves are characterized by uniform green coloration, smooth surfaces, and intact margins. Continue your current orchard management practices.',
        'symptoms': [
            'Uniform bright to deep green coloration',
            'Smooth, waxy leaf surface',
            'No spots, lesions, or discoloration',
            'Intact leaf margins without browning',
            'Normal leaf size and shape'
        ],
        'cures': [
            {
                'title': 'Preventive Maintenance',
                'detail': 'Continue regular scouting (weekly during growing season). Monitor for early signs of pest or disease pressure. Maintain a spray calendar even when no disease is present to prevent infections.'
            },
            {
                'title': 'Optimal Nutrition',
                'detail': 'Maintain balanced soil nutrition with NPK fertilization based on annual soil tests. Ensure adequate calcium to strengthen cell walls. Apply micronutrients (boron, zinc) as deficiencies are identified.'
            },
            {
                'title': 'Irrigation Management',
                'detail': 'Use drip or under-tree irrigation to keep foliage dry. Water in early morning if overhead irrigation is used. Maintain consistent soil moisture to prevent stress-related susceptibility.'
            },
            {
                'title': 'Integrated Pest Management',
                'detail': 'Maintain a full IPM program including beneficial insect conservation, pheromone traps for codling moth, and regular pruning. A healthy tree is naturally more resistant to disease.'
            }
        ],
        'color': '#22C55E',
        'icon': '🟢'
    },
    'Apple___Black_rot': {
        'display_name': 'Black Rot',
        'severity': 'Severe',
        'severity_level': 4,
        'description': 'Black rot is a serious fungal disease caused by Botryosphaeria obtusa, affecting leaves, bark, and fruit. Known as "frogeye leaf spot" in its leaf phase, it can cause significant economic loss. The fungus overwinters in cankers, dead wood, and mummified fruit, releasing spores during wet spring weather.',
        'symptoms': [
            'Circular "frogeye" spots: purple border with tan/brown center',
            'Concentric rings visible in lesion centers',
            'Leaf yellowing around lesions, leading to defoliation',
            'Black, shriveled (mummified) fruit',
            'Reddish-brown cankers on branches and trunk'
        ],
        'cures': [
            {
                'title': 'Canker Removal',
                'detail': 'Prune out all dead, cankered, and infected wood at least 15 cm beyond visible infection. Sterilize pruning tools between cuts with 70% isopropyl alcohol or 10% bleach solution. Burn or remove all prunings from the orchard.'
            },
            {
                'title': 'Fungicide Treatments',
                'detail': 'Apply captan, thiophanate-methyl (Topsin-M), or ziram beginning at petal fall and continuing every 10–14 days. Strobilurin fungicides (azoxystrobin, trifloxystrobin) provide excellent curative and preventive control. Rotate chemical classes to prevent resistance.'
            },
            {
                'title': 'Mummified Fruit Removal',
                'detail': 'Remove all mummified fruit from trees and ground immediately — these are primary inoculum sources. Do not leave fruit in the orchard through winter. Sanitation is the single most effective practice for reducing disease pressure.'
            },
            {
                'title': 'Wound Management',
                'detail': 'Protect all pruning wounds, fire blight strikes, and insect injuries with wound sealant. Black rot commonly enters through wounds. Minimize mechanical damage during harvest. Apply protectant fungicide after hail events.'
            }
        ],
        'color': '#8B5CF6',
        'icon': '🟣'
    }
}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Load model
model = r'D:\Games\apple_leaf_disease_dec\model_fine_tuned.keras'
def load_model():
    global model
    try:
        model = tf.keras.models.load_model(model)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"⚠️  Model not found or error: {e}")
        model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(image_path):
    if model is None:
        # Demo mode: return random prediction for testing UI
        import random
        probs = np.random.dirichlet(np.ones(4) * 2)
        predicted_idx = np.argmax(probs)
        return CLASS_NAMES[predicted_idx], float(probs[predicted_idx]) * 100, {
            CLASS_NAMES[i]: float(probs[i]) * 100 for i in range(len(CLASS_NAMES))
        }
    
    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array, verbose=0)
    probs = predictions[0]
    predicted_idx = np.argmax(probs)
    predicted_class = CLASS_NAMES[predicted_idx]
    confidence = float(probs[predicted_idx]) * 100
    all_probs = {CLASS_NAMES[i]: float(probs[i]) * 100 for i in range(len(CLASS_NAMES))}
    return predicted_class, confidence, all_probs

def load_history():
    if os.path.exists(app.config['HISTORY_FILE']):
        with open(app.config['HISTORY_FILE'], 'r') as f:
            return json.load(f)
    return []

def save_to_history(entry):
    history = load_history()
    history.insert(0, entry)
    history = history[:100]  # Keep last 100
    with open(app.config['HISTORY_FILE'], 'w') as f:
        json.dump(history, f, indent=2)

def get_stats():
    history = load_history()
    if not history:
        return {
            'total': 0, 'healthy': 0, 'diseased': 0,
            'disease_counts': {d: 0 for d in CLASS_NAMES},
            'avg_confidence': 0, 'recent_trend': []
        }
    
    disease_counts = {d: 0 for d in CLASS_NAMES}
    total_confidence = 0
    healthy_count = 0
    
    for entry in history:
        disease_counts[entry['predicted_class']] = disease_counts.get(entry['predicted_class'], 0) + 1
        total_confidence += entry['confidence']
        if entry['predicted_class'] == 'Apple___healthy':
            healthy_count += 1
    
    recent = history[:10]
    recent_trend = [{'date': e['timestamp'][:10], 'disease': e['predicted_class'], 'conf': e['confidence']} for e in recent]
    
    return {
        'total': len(history),
        'healthy': healthy_count,
        'diseased': len(history) - healthy_count,
        'disease_counts': disease_counts,
        'avg_confidence': round(total_confidence / len(history), 1),
        'recent_trend': recent_trend
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('index'))
    
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    predicted_class, confidence, all_probs = predict_disease(filepath)
    disease_info = DISEASE_INFO[predicted_class]
    
    entry = {
        'id': uuid.uuid4().hex[:8],
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        'predicted_class': predicted_class,
        'display_name': disease_info['display_name'],
        'confidence': round(confidence, 2),
        'severity': disease_info['severity'],
        'all_probs': {k: round(v, 2) for k, v in all_probs.items()}
    }
    save_to_history(entry)
    session['last_prediction'] = entry['id']
    
    chart_data = {
        'labels': [DISEASE_INFO[c]['display_name'] for c in CLASS_NAMES],
        'values': [round(all_probs[c], 2) for c in CLASS_NAMES],
        'colors': [DISEASE_INFO[c]['color'] for c in CLASS_NAMES]
    }
    
    return render_template('result.html',
        prediction=entry,
        disease_info=disease_info,
        chart_data=json.dumps(chart_data),
        image_url=url_for('static', filename=f'uploads/{filename}')
    )

@app.route('/history')
def history():
    history_data = load_history()
    return render_template('history.html', history=history_data, disease_info=DISEASE_INFO)

@app.route('/stats')
def stats():
    stats_data = get_stats()
    history_data = load_history()
    
    # Prepare chart data
    disease_chart = {
        'labels': [DISEASE_INFO[c]['display_name'] for c in CLASS_NAMES],
        'values': [stats_data['disease_counts'].get(c, 0) for c in CLASS_NAMES],
        'colors': [DISEASE_INFO[c]['color'] for c in CLASS_NAMES]
    }
    
    # Monthly trend (last 30 entries grouped by date)
    from collections import defaultdict
    daily_counts = defaultdict(lambda: {'healthy': 0, 'diseased': 0})
    for entry in history_data[:30]:
        date = entry['timestamp'][:10]
        if entry['predicted_class'] == 'Apple___healthy':
            daily_counts[date]['healthy'] += 1
        else:
            daily_counts[date]['diseased'] += 1
    
    sorted_dates = sorted(daily_counts.keys())[-14:]
    trend_chart = {
        'labels': sorted_dates,
        'healthy': [daily_counts[d]['healthy'] for d in sorted_dates],
        'diseased': [daily_counts[d]['diseased'] for d in sorted_dates]
    }
    
    return render_template('stats.html',
        stats=stats_data,
        disease_chart=json.dumps(disease_chart),
        trend_chart=json.dumps(trend_chart),
        disease_info=DISEASE_INFO,
        class_names=CLASS_NAMES
    )

@app.route('/delete_history', methods=['POST'])
def delete_history():
    with open(app.config['HISTORY_FILE'], 'w') as f:
        json.dump([], f)
    return redirect(url_for('history'))

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

if __name__ == '__main__':
    load_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
