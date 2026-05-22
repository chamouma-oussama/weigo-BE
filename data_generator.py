import pandas as pd
import numpy as np

# الإعدادات الأساسية
n_samples = 10000
np.random.seed(42)

# 1. توليد المدخلات الأساسية (بمنطق إحصائي مطور)
age = np.random.randint(18, 65, n_samples)
gender = np.random.randint(0, 2, n_samples) # 0: Female, 1: Male

# الطول بالمتر (للحسابات الطبية) ثم تحويله لسنتيمتر كما في كودك
height_m = np.random.uniform(1.55, 1.95, n_samples)
height = (height_m * 100).astype(int)

# توليد الوزن بناءً على BMI واقعي (من 20 إلى 45)
bmi = np.random.uniform(20, 45, n_samples)
current_weight = (bmi * (height_m**2)).astype(int)

# هدف الوزن (منطقي: دائماً أقل من الوزن الحالي بنسبة معقولة)
target_weight = current_weight - np.random.randint(5, 20, n_samples)

stress_level = np.random.randint(1, 11, n_samples)
commitment = np.random.randint(1, 11, n_samples)
motivation = np.random.randint(1, 11, n_samples)
water_intake = np.random.uniform(1.5, 4.5, n_samples)
night_eating = np.random.randint(0, 2, n_samples)

# 2. توليد مدخلات مترابطة (النشاط، الرياضة، النوم)
activity_level = np.random.randint(1, 5, n_samples)
sports_days = []
sleep_hours = []
avg_caloric_intake = []

for i in range(n_samples):
    # ربط الرياضة بمستوى النشاط (منطق كودك الأصلي)
    if activity_level[i] == 1: sports_days.append(np.random.randint(0, 2))
    elif activity_level[i] == 4: sports_days.append(np.random.randint(4, 8))
    else: sports_days.append(np.random.randint(1, 5))
    
    # ربط النوم بالتوتر (منطق Sleep Dataset)
    # التوتر العالي يقلل النوم ويزيد السعرات (Stress Eating)
    sleep = np.random.uniform(6, 9)
    if stress_level[i] > 7: sleep -= np.random.uniform(1, 2)
    sleep_hours.append(round(sleep, 1))
    
    # ربط السعرات بالوزن والنشاط (منطق FitBit)
    base_calories = current_weight[i] * 28 
    if activity_level[i] >= 3: base_calories += 500
    # إضافة تذبذب عشوائي في الأكل
    avg_caloric_intake.append(int(base_calories + np.random.normal(0, 300)))

# 3. حساب النجاح (Success) - المحرك الأساسي للنموذج
success = []
for i in range(n_samples):
    # حساب BMR تقريبي (Mifflin-St Jeor simplified)
    bmr = (10 * current_weight[i]) + (6.25 * height[i]) - (5 * age[i])
    calorie_diff = avg_caloric_intake[i] - bmr
    
    # بناء النقاط (Score System)
    score = (commitment[i] * 4) + (motivation[i] * 3) + (sports_days[i] * 5)
    
    # تأثير السعرات (عامل حاسم)
    if calorie_diff < 200: score += 30  # عجز أو توازن جيد
    elif calorie_diff > 600: score -= 40 # فائض كبير يعيق النجاح
    
    # تأثير النوم والماء (Lifestyle Factors)
    if sleep_hours[i] >= 7: score += 10
    if water_intake[i] >= 3: score += 10
    if night_eating[i] == 1: score -= 15
    if stress_level[i] > 7: score -= 10

    # تحديد النجاح مع إضافة "ضجيج" لجعله طبيعياً
    final_prob = score + np.random.normal(0, 10)
    success.append(1 if final_prob > 55 else 0)

# إنشاء الجدول بنفس المسميات الدقيقة التي يستخدمها الـ Flask الخاص بك
df = pd.DataFrame({
    'age': age,
    'gender': gender,
    'height': height,
    'current_weight': current_weight,
    'target_weight': target_weight,
    'activity_level': activity_level,
    'sports_days': sports_days,
    'sleep_hours': sleep_hours,
    'Avg_Caloric_Intake': avg_caloric_intake,
    'water_intake': np.round(water_intake, 1),
    'night_eating': night_eating,
    'stress_level': stress_level,
    'commitment': commitment,
    'motivation': motivation,
    'success': success
})

# حفظ الملف بنفس الاسم الذي يطلبه كود الـ Flask
df.to_csv('advanced_weight_loss_data.csv', index=False)
print(f"✅ Done! Created 10,000 records. Success Rate: {df['success'].mean()*100:.1f}%")