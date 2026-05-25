# main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

# استيراد الإعدادات والوظائف من ملفاتك
from config import SERVER_HOST, SERVER_PORT
from database import init_db, log_prediction, add_user, verify_user 
from model_trainer import train_model

app = Flask(__name__)
CORS(app)

# تهيئة قاعدة البيانات وتدريب الذكاء الاصطناعي عند إقلاع السيرفر
init_db()
model, model_accuracy = train_model()


# 1️⃣ مسار إنشاء الحساب (الذي عمل عندك بنجاح 🎉)
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        password = data.get('password')

        if not username or not password or not first_name or not last_name:
            return jsonify({
                "status": "validation_error", 
                "message": "Please fill in all the required fields on the server"
            }), 400

        full_name = f"{first_name} {last_name}"
        success, message = add_user(str(username).strip(), str(full_name).strip(), str(password))
        
        if success:
            return jsonify({"status": "success", "message": "Account created successfully and securely"}), 200
        else:
            return jsonify({"status": "validation_error", "message": message}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500


# 2️⃣ 🌟 مسار تسجيل الدخول المفقود (الذي حل مشكلة الـ 404)
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data was received"}), 400
            
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                "status": "validation_error", 
                "message": "Username and password required"
            }), 400

        # استدعاء دالة التحقق من قاعدة البيانات
        success, result_msg = verify_user(str(username).strip(), str(password))
        
        if success:
            return jsonify({
                "status": "success", 
                "message": "Login successful",
                "full_name": result_msg
            }), 200
        else:
            return jsonify({"status": "validation_error", "message": result_msg}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500


# 3️⃣ مسار التنبؤ الذكي الخاص بمشروعك (مستقر تماماً)
@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"status": "error", "message": "Model not trained"}), 500
        
    try:
        data = request.json
        
        required_fields = [
            'age', 'gender', 'height', 'current_weight', 'target_weight',
            'activity_level', 'sports_days', 'sleep_hours', 
            'Avg_Caloric_Intake', 'water_intake', 'night_eating', 
            'stress_level', 'commitment', 'motivation'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                return jsonify({
                    "status": "validation_error", 
                    "message": f"The field '{field}' cannot be empty."
                }), 400

        age = int(data['age'])
        gender = int(data['gender'])
        height = float(data['height'])
        weight = float(data['current_weight'])
        target = float(data['target_weight'])
        calories = float(data['Avg_Caloric_Intake'])
        water = float(data['water_intake'])
        sleep = int(data['sleep_hours'])
        stress = int(data['stress_level'])
        sports = int(data['sports_days'])
        night_eat = int(data['night_eating'])
        activity = int(data['activity_level'])
        commitment = int(data['commitment'])
        motivation = int(data['motivation'])
        
        if target >= weight:
            return jsonify({
                "status": "validation_error", 
                "message": "Target weight must be less than your current weight for a weight loss application."
            }), 400

        bmi_calc = weight / ((height / 100) ** 2)
        weight_gap_calc = weight - target
        
        features = np.array([[
            age, gender, height, weight, target,
            activity, sports, sleep, 
            calories, water, night_eat, stress, 
            commitment, motivation,
            bmi_calc, weight_gap_calc
        ]])

        probability = model.predict_proba(features)[0][1] * 100
        current_model_accuracy = getattr(model, 'saved_accuracy', model_accuracy)
        
        log_prediction(data, bmi_calc, probability)

        warnings = []
        recommendations = []

        if gender == 1:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
        activity_multipliers = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
        daily_needs = bmr * activity_multipliers.get(activity, 1.2)
        
        if calories > daily_needs + 200:
            warnings.append(f"Your caloric intake ({int(calories)} kcal) is high compared to your daily needs ({int(daily_needs)} kcal).")
            safe_target = max(1200, int(daily_needs - 500))
            recommendations.append(f"Try to target around {int(daily_needs - 500)} kcal for steady and safe fat loss.")
        
        elif calories < 1200:
            warnings.append("Extremely low calorie consumption detected. This can collapse your metabolism.")
            recommendations.append("Ensure your intake stays above 1200 kcal by including nutrient-dense foods.")
            
        if water < 2.0:
            warnings.append(f"Low hydration ({water}L) slows down your metabolic rate.")
            recommendations.append("Drink at least 3 liters of water daily to optimize fat burning.")

        elif water > 4.5:
            warnings.append(f"Excessive water intake ({water}L) can strain your kidneys and risk Hyponatremia (water intoxication).")
            recommendations.append("Moderate your intake to 3.0 - 3.5 liters daily, distributed evenly throughout the day.")    
            
        if stress >= 4:
            warnings.append("High stress levels can cause emotional eating and fat storage.")
            recommendations.append("Incorporate 10 mins of meditation or deep breathing daily.")
        if sports <= 1:
            warnings.append("Sedentary lifestyle: Physical activity is too low.")
            recommendations.append("Start with 20 minutes of brisk walking 4 times a week.")
        if sleep < 7:
            warnings.append(f"Sleeping only {sleep} hours triggers high cortisol (stress) and hunger.")
            recommendations.append("Prioritize 7-8 hours of sleep to stabilize your biological rhythm.")
        elif sleep > 9.5:
        
            warnings.append(f"Over-sleeping ({sleep} hours) slows down your metabolic rate and triggers daytime lethargy.")
            recommendations.append("Aim for a consistent 7-8 hour sleep window and increase your daytime physical activity.")    
        
        if data.get('night_eating') == 1:
            warnings.append("Night eating syndrome delays your metabolic rest and impairs insulin sensitivity.")
            recommendations.append("Close your eating window at least 3 hours before sleep. Shift your calories to daytime.")    
        
        if motivation <= 4:
            # 🌟 معالجة التحفيز المنخفض 
            warnings.append(f"Low motivation ({motivation}/10) indicates mental fatigue from previous failed attempts.")
            recommendations.append("Focus on non-scale victories (like better sleep or higher energy) rather than just the weight number to rebuild your momentum.")
        elif motivation >= 9:
            # 🌟 فرملة التحفيز المفرط (حماية من الانتكاسة)
            warnings.append(f"Extreme motivation ({motivation}/10) can trap you in the 'honeymoon phase', leading to burnout or crash dieting.")
            recommendations.append("Stay patient. Weight loss is a marathon, not a sprint. Do not cut your calories drastically to chase fast results.")    

        if probability > 75:
            msg = "Excellent! You have a high chance of reaching your goal. Keep it up!"
        elif probability > 50:
            msg = "You are on the right track, but minor adjustments will speed up your results."
        else:
            msg = "Success is possible! Focus on calorie control and consistency to improve your odds."

        return jsonify({
            "status": "success",
            "success_rate": round(probability, 1),
            "model_accuracy": round(current_model_accuracy, 1),
            "analysis": {
                "warnings": warnings,
                "recommendations": recommendations,
                "message": msg,
                "bmi": round(bmi_calc, 1)
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"System Error: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)