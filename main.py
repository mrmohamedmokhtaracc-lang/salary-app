import sqlite3
from datetime import datetime

def initialize_database():
    """إنشاء قاعدة البيانات والجداول اللازمة"""
    conn = sqlite3.connect("payrolljawhahr.db")
    cursor = conn.cursor()
    
    # إنشاء جدول الموظفين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        job_title TEXT,
        department TEXT,
        base_salary REAL NOT NULL,
        start_date TEXT,
        residency_id TEXT,
        residency_expiry_date TEXT,
        nationality TEXT,
        medical_insurance_type TEXT,
        work_start_date TEXT,
        housing_allowance_percent REAL,
        transportation_allowance REAL,
        phone_allowance REAL
    )
    """)
    
    # إنشاء جدول البدلات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allowances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        period TEXT,
        site_allowance REAL DEFAULT 0,
        meals_allowance REAL DEFAULT 0,
        vacation_allowance REAL DEFAULT 0,
        ticket_allowance REAL DEFAULT 0,
        bonus REAL DEFAULT 0,
        incentive REAL DEFAULT 0,
        other REAL DEFAULT 0,
        FOREIGN KEY (employee_id) REFERENCES employees(ID)
    )
    """)
    
    # إنشاء جدول الخصومات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deductions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        period TEXT,
        absence REAL DEFAULT 0,
        penalties REAL DEFAULT 0,
        loans REAL DEFAULT 0,
        other REAL DEFAULT 0,
        FOREIGN KEY (employee_id) REFERENCES employees(ID)
    )
    """)
    
    # إنشاء جدول الرواتب
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        period TEXT,
        base_salary REAL,
        total_allowances REAL,
        total_deductions REAL,
        net_salary REAL,
        calculation_date TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(ID)
    )
    """)
    
    # إنشاء جدول السجلات البسيط للواجهة
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salary_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        month TEXT,
        housing_allowance REAL,
        transport_allowance REAL,
        phone_allowance REAL,
        site_allowance REAL,
        food_allowance REAL,
        leave_allowance REAL,
        ticket_allowance REAL,
        bonus REAL,
        incentive REAL,
        absence_deduction REAL,
        penalty REAL,
        loan REAL,
        net_salary REAL
    )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم إنشاء قاعدة البيانات والجداول بنجاح")

def calculate_net_salary(base_salary, allowances, deductions):
    """حساب الراتب الصافي"""
    total_allowances = sum(allowances.values()) if isinstance(allowances, dict) else allowances
    total_deductions = sum(deductions.values()) if isinstance(deductions, dict) else deductions
    return base_salary + total_allowances - total_deductions

def add_sample_employee():
    """إضافة موظف نموذجي للاختبار"""
    conn = sqlite3.connect("payrolljawhahr.db")
    cursor = conn.cursor()
    
    # التحقق من وجود موظفين
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
        INSERT INTO employees (name, job_title, department, base_salary, start_date)
        VALUES (?, ?, ?, ?, ?)
        """, ("محمد أحمد", "محاسب", "المالية", 5000.0, "2024-01-01"))
        conn.commit()
        print("✅ تم إضافة موظف نموذجي")
    
    conn.close()

if __name__ == "__main__":
    # تشغيل إعداد قاعدة البيانات
    initialize_database()
    add_sample_employee()
    
    print("🎯 تم إعداد النظام بنجاح. استخدم الأمر التالي لتشغيل الواجهة:")
    print("streamlit run app.py")