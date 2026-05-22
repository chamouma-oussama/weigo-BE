# model_trainer.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from config import FEATURE_COLUMNS

model_accuracy = 0.0

def train_model():
    global model_accuracy
    try:
        # 1. قراءة ملف البيانات
        data = pd.read_csv('advanced_weight_loss_data.csv')
        
        # 🌟 خطوة حماية: توحيد مسمى عمود السعرات الحرارية ليطابق الـ config تماماً في حال اختلاف حالة الأحرف بالـ CSV
        if 'avg_caloric_intake' in data.columns and 'Avg_Caloric_Intake' not in data.columns:
            data.rename(columns={'avg_caloric_intake': 'Avg_Caloric_Intake'}, inplace=True)
            
        # 2. هندسة الميزات الجانبية (Feature Engineering)
        data['bmi'] = data['current_weight'] / ((data['height'] / 100) ** 2)
        data['weight_gap'] = data['current_weight'] - data['target_weight']
        
        # 🌟 خطوة حماية: التخلص من أي سجلات تحتوي على قيم مفقودة لضمان استقرار Scikit-Learn
        data = data.dropna(subset=FEATURE_COLUMNS + ['success'])
        
        # 3. فصل المتغيرات المستقلة والتابعة
        X = data[FEATURE_COLUMNS]
        y = data['success']
        
        # 4. تقسيم البيانات لقياس دقة النموذج بشكل حقيقي ومحايد
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 5. بناء وتدريب نموذج الـ Random Forest بالمعاملات المحددة للمشروع
        rf_model = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # 6. حساب دقة النموذج وحفظها لاستعراضها في واجهة الفلاتر أمام اللجنة
        predictions = rf_model.predict(X_test)
        calculated_accuracy = accuracy_score(y_test, predictions) * 100
        
        model_accuracy = calculated_accuracy
        rf_model.saved_accuracy = calculated_accuracy  
        
        # 7. 🌟 إعادة تدريب النموذج على كامل الداتا لرفع الكفاءة التشغيلية داخل التطبيق
        rf_model.fit(X, y)
        print(f"✅ Model trained successfully! Precision Accuracy: {model_accuracy:.2f}%")
        return rf_model, model_accuracy
        
    except FileNotFoundError:
        print("❌ Error: Dataset file 'advanced_weight_loss_data.csv' not found. Please ensure it exists in the root directory.")
        return None, 0.0
    except KeyError as ke:
        print(f"❌ Error: Missing feature column in the dataset. {str(ke)}")
        return None, 0.0
    except Exception as e:
        print(f"❌ Unexpected Error during model training: {str(e)}")
        return None, 0.0