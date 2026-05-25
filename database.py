# database.py
import sqlite3
from config import DB_NAME

def init_db():
    """تهيئة قاعدة البيانات وإنشاء جدول السجلات التنبؤية وجدول المستخدمين"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 1. جدول سجلات التنبؤ الذكي الخاص بنموذج الذكاء الاصطناعي
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                age INTEGER,
                gender INTEGER,
                height REAL,
                current_weight REAL,
                target_weight REAL,
                activity_level INTEGER,
                sports_days INTEGER,
                sleep_hours INTEGER,
                avg_caloric_intake REAL,
                water_intake REAL,
                night_eating INTEGER,
                stress_level INTEGER,
                commitment INTEGER,
                motivation INTEGER,
                bmi REAL,
                success_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. جدول الحسابات لتخزين مستخدمي تطبيق فلاتر
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("📁 Database & Tables (Logs + Users) initialized successfully!")
    except Exception as e:
        print(f"⚠️ Failed to initialize database: {str(e)}")
    finally:
        if conn:
            conn.close()

def log_prediction(data, bmi, probability):
    """حفظ مدخلات المستخدم ونسبة النجاح المحسوبة بأمان"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        calories = data.get('Avg_Caloric_Intake') or data.get('avg_caloric_intake') or 0.0

        cursor.execute('''
            INSERT INTO analysis_logs (
                age, gender, height, current_weight, target_weight,
                activity_level, sports_days, sleep_hours, avg_caloric_intake,
                water_intake, night_eating, stress_level, commitment, motivation, bmi, success_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(data.get('age', 0)), 
            int(data.get('gender', 0)), 
            float(data.get('height', 0.0)), 
            float(data.get('current_weight', 0.0)), 
            float(data.get('target_weight', 0.0)),
            int(data.get('activity_level', 1)), 
            int(data.get('sports_days', 0)), 
            int(data.get('sleep_hours', 0)), 
            float(calories), 
            float(data.get('water_intake', 0.0)), 
            int(data.get('night_eating', 0)), 
            int(data.get('stress_level', 1)), 
            int(data.get('commitment', 1)), 
            int(data.get('motivation', 1)),
            round(bmi, 1), 
            round(probability, 1)
        ))
        conn.commit()
        print("💾 New prediction logged into database successfully!")
    except Exception as db_error:
        print(f"⚠️ Database insertion failed: {str(db_error)}")
    finally:
        if conn:
            conn.close()

def add_user(username, full_name, password):
    """إضافة مستخدم جديد إلى قاعدة البيانات والتحقق من عدم تكرار اسم المستخدم"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, full_name, password) 
            VALUES (?, ?, ?)
        ''', (username, full_name, password))
        
        conn.commit()
        print(f"👤 Account created successfully for user: {username}")
        return True, "Account created successfully!"
        
    except sqlite3.IntegrityError:
        print(f"⚠️ Registration failed: Username '{username}' already exists.")
        return False, "Username is already registered, please choose another name."
    except Exception as e:
        print(f"⚠️ Error during registration query: {str(e)}")
        return False, f"Database error: {str(e)}"
    finally:
        if conn:
            conn.close()

# 🌟 هذه هي الدالة التي كانت مفقودة وتسببت في ظهور الـ ImportError
def verify_user(username, password):
    """التحقق من صحة اسم المستخدم وكلمة المرور عند تسجيل الدخول"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT full_name FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        
        user = cursor.fetchone()
        
        if user:
            print(f"🔓 Successful login for user: {username}")
            return True, user[0]
        else:
            print(f"🔒 Failed login attempt for user: {username}")
            return False, "Incorrect username or password"
            
    except Exception as e:
        print(f"⚠️ Error during login query: {str(e)}")
        return False, f"Database error: {str(e)}"
    finally:
        if conn:
            conn.close()