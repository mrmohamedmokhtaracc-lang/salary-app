import sqlite3

# الاتصال بقاعدة البيانات أو إنشاؤها
conn = sqlite3.connect("payrolljawhahr.db")
cursor = conn.cursor()

# حذف الجدول لو موجود مسبقًا
cursor.execute("DROP TABLE IF EXISTS employees")

# إنشاء جدول الموظفين بكل الأعمدة المطلوبة
cursor.execute("""
CREATE TABLE employees (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,        -- رقم الموظف
    name TEXT NOT NULL,                          -- الاسم
    job_title TEXT,                              -- المسمى الوظيفي
    department TEXT,                             -- القسم
    base_salary REAL NOT NULL,                   -- الراتب الأساسي
    start_date TEXT,                             -- تاريخ التعيين
    residency_id TEXT,                           -- رقم الإقامة
    residency_expiry_date TEXT,                  -- تاريخ انتهاء الإقامة
    nationality TEXT,                            -- الجنسية
    medical_insurance_type TEXT,                 -- نوع التأمين الطبي
    work_start_date TEXT,                        -- تاريخ بداية العمل
    housing_allowance_percent REAL,              -- بدل السكن (كنسبة من الراتب الأساسي)
    transportation_allowance REAL,               -- بدل المواصلات
    phone_allowance REAL                         -- بدل الهاتف
)
""")

# حفظ التغييرات
conn.commit()
conn.close()

print("✅ تم إنشاء جدول الموظفين الجديد بالكامل بنجاح.")
import sqlite3

conn = sqlite3.connect("payrolljawhahr.db")
cursor = conn.cursor()

# جدول البدلات
cursor.execute("""
CREATE TABLE IF NOT EXISTS allowances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    period TEXT,
    housing REAL DEFAULT 0,
    transportation REAL DEFAULT 0,
    phone REAL DEFAULT 0,
    other REAL DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employees(ID)
)
""")

# جدول الخصومات
cursor.execute("""
CREATE TABLE IF NOT EXISTS deductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    period TEXT,
    absence REAL DEFAULT 0,
    insurance REAL DEFAULT 0,
    loan REAL DEFAULT 0,
    other REAL DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employees(ID)
)
""")

# جدول الرواتب
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

conn.commit()
conn.close()

print("✅ تم إنشاء جداول البدلات والخصومات والرواتب بنجاح.")
import sqlite3

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("payrolljawhahr.db")
cursor = conn.cursor()

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

conn.commit()
conn.close()

print("✅ تم إنشاء جدول البدلات والخصومات بنجاح.")
import sqlite3

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("payrolljawhahr.db")
cursor = conn.cursor()

# إنشاء جدول الرواتب الشهرية إن لم يكن موجود
cursor.execute("""
CREATE TABLE IF NOT EXISTS salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    period TEXT,
    base_salary REAL,
    total_allowances REAL,
    total_deductions REAL,
    net_salary REAL,
    FOREIGN KEY (employee_id) REFERENCES employees(ID)
)
""")

# استرجاع كل الموظفين
cursor.execute("SELECT ID, base_salary FROM employees")
employees = cursor.fetchall()

# تحديد الفترة
period = "2025-08"  # غيّرها حسب الشهر الحالي

for emp in employees:
    emp_id = emp[0]
    base_salary = emp[1]

    # إجمالي البدلات
    cursor.execute("""
        SELECT 
            COALESCE(site_allowance,0) + COALESCE(meals_allowance,0) + 
            COALESCE(vacation_allowance,0) + COALESCE(ticket_allowance,0) + 
            COALESCE(bonus,0) + COALESCE(incentive,0) + COALESCE(other,0)
        FROM allowances 
        WHERE employee_id = ? AND period = ?
    """, (emp_id, period))
    total_allowances = cursor.fetchone()[0] or 0

    # إجمالي الخصومات
    cursor.execute("""
        SELECT 
            COALESCE(absence,0) + COALESCE(penalties,0) + 
            COALESCE(loans,0) + COALESCE(other,0)
        FROM deductions 
        WHERE employee_id = ? AND period = ?
    """, (emp_id, period))
    total_deductions = cursor.fetchone()[0] or 0

    # حساب الراتب الصافي
    net_salary = base_salary + total_allowances - total_deductions

    # تخزينه في جدول الرواتب
    cursor.execute("""
        INSERT INTO salaries (employee_id, period, base_salary, total_allowances, total_deductions, net_salary)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (emp_id, period, base_salary, total_allowances, total_deductions, net_salary))

# حفظ التغييرات
conn.commit()

# عرض النتائج
print(f"\n📊 الرواتب المحسوبة لشهر {period}:")
cursor.execute("""
    SELECT e.name, s.base_salary, s.total_allowances, s.total_deductions, s.net_salary
    FROM salaries s
    JOIN employees e ON s.employee_id = e.ID
    WHERE s.period = ?
""", (period,))
rows = cursor.fetchall()

for row in rows:
    print(f"👤 {row[0]} | 💰 أساسي: {row[1]} | ➕ بدلات: {row[2]} | ➖ خصومات: {row[3]} | 🧾 صافي: {row[4]}")

conn.close()
import streamlit as st
import sqlite3
from datetime import date

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("payrolljawhahr.db", check_same_thread=False)
cursor = conn.cursor()

# إعداد الصفحة
st.title("📋 إدخال البدلات والخصومات الشهرية")

# اختيار الموظف والشهر
employee_id = st.number_input("🔢 رقم الموظف", min_value=1)
month = st.selectbox("📆 الشهر", range(1, 13))
year = st.number_input("📅 السنة", min_value=2000, max_value=2100, value=date.today().year)

# إدخال البدلات
st.header("💰 البدلات")
allow_site = st.number_input("بدل موقع", min_value=0.0, value=0.0)
allow_meals = st.number_input("بدل وجبات", min_value=0.0, value=0.0)
allow_leave = st.number_input("بدل إجازات", min_value=0.0, value=0.0)
allow_tickets = st.number_input("بدل تذاكر", min_value=0.0, value=0.0)
bonus = st.number_input("مكافأة", min_value=0.0, value=0.0)
incentive = st.number_input("حوافز", min_value=0.0, value=0.0)

# إدخال الخصومات
st.header("🧾 الخصومات")
absence = st.number_input("غياب", min_value=0.0, value=0.0)
penalty = st.number_input("جزاءات", min_value=0.0, value=0.0)
advance = st.number_input("سلف", min_value=0.0, value=0.0)

if st.button("💾 حفظ البيانات"):
    cursor.execute("""
        INSERT INTO monthly_adjustments (
            employee_id, year, month, 
            allow_site, allow_meals, allow_leave, allow_tickets,
            bonus, incentive, 
            absence, penalty, advance
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id, year, month,
        allow_site, allow_meals, allow_leave, allow_tickets,
        bonus, incentive,
        absence, penalty, advance
    ))
    conn.commit()
    st.success("✅ تم حفظ البدلات والخصومات بنجاح")

import streamlit as st
import sqlite3
from datetime import datetime

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("payrolljawhahr.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء جدول الرواتب لو مش موجود
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

# واجهة Streamlit
st.title("💰 نظام الرواتب - الإدخال الشهري")

# إدخال بيانات الموظف
employee_id = st.number_input("🆔 رقم الموظف", min_value=1, step=1)
month = st.text_input("📆 الشهر (مثال: 2025-08)", value=datetime.now().strftime("%Y-%m"))

# البدلات
st.subheader("📈 البدلات:")
housing = st.number_input("🏠 بدل سكن", value=0.0)
transport = st.number_input("🚗 بدل موصلات", value=0.0)
phone = st.number_input("📞 بدل هاتف", value=0.0)
site = st.number_input("🏗️ بدل موقع", value=0.0)
food = st.number_input("🍱 بدل وجبات", value=0.0)
leave = st.number_input("🏖️ بدل إجازات", value=0.0)
ticket = st.number_input("✈️ بدل تذاكر", value=0.0)
bonus = st.number_input("🎁 مكافأة", value=0.0)
incentive = st.number_input("💹 حوافز", value=0.0)

# الخصومات
st.subheader("📉 الخصومات:")
absence = st.number_input("🚫 خصم غياب", value=0.0)
penalty = st.number_input("⚠️ جزاءات", value=0.0)
loan = st.number_input("💸 سلف", value=0.0)

# حساب الراتب الصافي
net_salary = (
    housing + transport + phone + site + food + leave + ticket + bonus + incentive
    - absence - penalty - loan
)

st.markdown(f"### 💵 الراتب الصافي: `{net_salary:.2f}` ريال")

# حفظ البيانات
if st.button("💾 حفظ البيانات"):
    cursor.execute("""
        INSERT INTO salary_records (
            employee_id, month,
            housing_allowance, transport_allowance, phone_allowance,
            site_allowance, food_allowance, leave_allowance,
            ticket_allowance, bonus, incentive,
            absence_deduction, penalty, loan,
            net_salary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id, month,
        housing, transport, phone,
        site, food, leave,
        ticket, bonus, incentive,
        absence, penalty, loan,
        net_salary
    ))
    conn.commit()
    st.success("✅ تم حفظ البيانات بنجاح!")

# عرض السجلات
if st.checkbox("📋 عرض السجلات المحفوظة"):
    records = cursor.execute("SELECT * FROM salary_records ORDER BY id DESC").fetchall()
    if records:
        st.write("🔍 عرض آخر السجلات:")
        st.dataframe(records)
    else:
        st.info("لا توجد بيانات حتى الآن.")
def calculate_net_salary(base_salary, allowances, deductions):
    total_allowances = sum(allowances.values())
    total_deductions = sum(deductions.values())
    return base_salary + total_allowances - total_deductions
