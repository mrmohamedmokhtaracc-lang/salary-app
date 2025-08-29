import streamlit as st
import sqlite3
from datetime import datetime, date
from main import calculate_net_salary, initialize_database

# إعداد الصفحة
st.set_page_config(page_title="نظام الرواتب", layout="centered")

# التأكد من إنشاء قاعدة البيانات
initialize_database()

# الاتصال بقاعدة البيانات
@st.cache_resource
def get_database_connection():
    return sqlite3.connect("payrolljawhahr.db", check_same_thread=False)

conn = get_database_connection()
cursor = conn.cursor()

st.title("🧮 نظام حساب الرواتب")

# اختيار نوع العملية
operation = st.selectbox("اختر العملية", ["حساب راتب جديد", "عرض السجلات"])

if operation == "حساب راتب جديد":
    # --- بيانات الموظف ---
    st.header("بيانات الموظف")
    
    # عرض الموظفين المتاحين
    cursor.execute("SELECT ID, name FROM employees")
    employees = cursor.fetchall()
    
    if employees:
        employee_options = {f"{emp[1]} (ID: {emp[0]})": emp[0] for emp in employees}
        selected_employee = st.selectbox("اختر الموظف", list(employee_options.keys()))
        employee_id = employee_options[selected_employee]
        
        # الحصول على الراتب الأساسي
        cursor.execute("SELECT base_salary FROM employees WHERE ID = ?", (employee_id,))
        base_salary = cursor.fetchone()[0]
        
        st.info(f"الراتب الأساسي: {base_salary} ريال")
    else:
        st.error("لا توجد موظفين في النظام. يرجى إضافة موظف أولاً.")
        st.stop()
    
    # --- البدلات ---
    st.header("البدلات")
    col1, col2 = st.columns(2)
    
    with col1:
        site_allowance = st.number_input("🏗️ بدل موقع", min_value=0.0, format="%.2f")
        meals_allowance = st.number_input("🍱 بدل وجبات", min_value=0.0, format="%.2f")
        vacation_allowance = st.number_input("🏖️ بدل إجازات", min_value=0.0, format="%.2f")
        ticket_allowance = st.number_input("✈️ بدل تذاكر", min_value=0.0, format="%.2f")
    
    with col2:
        bonus = st.number_input("🎁 مكافأة", min_value=0.0, format="%.2f")
        incentive = st.number_input("💹 حوافز", min_value=0.0, format="%.2f")
        housing_allowance = st.number_input("🏠 بدل سكن", min_value=0.0, format="%.2f")
        transport_allowance = st.number_input("🚗 بدل مواصلات", min_value=0.0, format="%.2f")
    
    # --- الخصومات ---
    st.header("الخصومات")
    col3, col4 = st.columns(2)
    
    with col3:
        absence_deduction = st.number_input("🚫 خصم غياب", min_value=0.0, format="%.2f")
        penalty = st.number_input("⚠️ جزاءات", min_value=0.0, format="%.2f")
    
    with col4:
        loan = st.number_input("💸 سلف", min_value=0.0, format="%.2f")
        other_deductions = st.number_input("📝 خصومات أخرى", min_value=0.0, format="%.2f")
    
    # الشهر
    month = st.text_input("📆 الشهر (مثال: 2024-08)", value=datetime.now().strftime("%Y-%m"))
    
    # --- حساب الراتب ---
    allowances = {
        "site": site_allowance,
        "meals": meals_allowance,
        "vacation": vacation_allowance,
        "ticket": ticket_allowance,
        "bonus": bonus,
        "incentive": incentive,
        "housing": housing_allowance,
        "transport": transport_allowance
    }
    
    deductions = {
        "absence": absence_deduction,
        "penalty": penalty,
        "loan": loan,
        "other": other_deductions
    }
    
    net_salary = calculate_net_salary(base_salary, allowances, deductions)
    
    # عرض النتيجة
    st.markdown("---")
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.metric("💰 الراتب الأساسي", f"{base_salary:.2f} ريال")
    
    with col6:
        total_allowances = sum(allowances.values())
        st.metric("➕ إجمالي البدلات", f"{total_allowances:.2f} ريال")
    
    with col7:
        total_deductions = sum(deductions.values())
        st.metric("➖ إجمالي الخصومات", f"{total_deductions:.2f} ريال")
    
    st.markdown(f"### 💵 الراتب الصافي: `{net_salary:.2f}` ريال")
    
    # حفظ البيانات
    if st.button("💾 حفظ البيانات"):
        try:
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
                housing_allowance, transport_allowance, 0.0,  # phone_allowance
                site_allowance, meals_allowance, vacation_allowance,
                ticket_allowance, bonus, incentive,
                absence_deduction, penalty, loan,
                net_salary
            ))
            conn.commit()
            st.success("✅ تم حفظ البيانات بنجاح!")
        except Exception as e:
            st.error(f"خطأ في حفظ البيانات: {str(e)}")

elif operation == "عرض السجلات":
    st.header("📋 السجلات المحفوظة")
    
    try:
        # عرض السجلات مع أسماء الموظفين
        cursor.execute("""
            SELECT 
                sr.id,
                e.name,
                sr.month,
                sr.net_salary,
                sr.housing_allowance + sr.transport_allowance + sr.phone_allowance + 
                sr.site_allowance + sr.food_allowance + sr.leave_allowance + 
                sr.ticket_allowance + sr.bonus + sr.incentive as total_allowances,
                sr.absence_deduction + sr.penalty + sr.loan as total_deductions
            FROM salary_records sr
            LEFT JOIN employees e ON sr.employee_id = e.ID
            ORDER BY sr.id DESC
        """)
        records = cursor.fetchall()
        
        if records:
            st.write("🔍 آخر السجلات:")
            
            # تحويل البيانات لعرض أفضل
            import pandas as pd
            df = pd.DataFrame(records, columns=[
                "رقم السجل", "اسم الموظف", "الشهر", "الراتب الصافي", 
                "إجمالي البدلات", "إجمالي الخصومات"
            ])
            
            # تنسيق الأرقام
            df["الراتب الصافي"] = df["الراتب الصافي"].round(2)
            df["إجمالي البدلات"] = df["إجمالي البدلات"].round(2)
            df["إجمالي الخصومات"] = df["إجمالي الخصومات"].round(2)
            
            st.dataframe(df, use_container_width=True)
            
            # إحصائيات سريعة
            st.markdown("📊 **إحصائيات سريعة:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_salary = df["الراتب الصافي"].mean()
                st.metric("متوسط الراتب الصافي", f"{avg_salary:.2f} ريال")
            
            with col2:
                total_records = len(df)
                st.metric("عدد السجلات", total_records)
            
            with col3:
                max_salary = df["الراتب الصافي"].max()
                st.metric("أعلى راتب", f"{max_salary:.2f} ريال")
                
        else:
            st.info("لا توجد سجلات محفوظة حتى الآن.")
            
    except Exception as e:
        st.error(f"خطأ في استرجاع البيانات: {str(e)}")

# إضافة معلومات في الشريط الجانبي
with st.sidebar:
    st.markdown("### 📝 معلومات النظام")
    st.markdown("**نظام حساب الرواتب**")
    st.markdown("إصدار 1.0")
    
    # عرض عدد الموظفين
    cursor.execute("SELECT COUNT(*) FROM employees")
    employee_count = cursor.fetchone()[0]
    st.metric("عدد الموظفين", employee_count)
    
    # عرض عدد السجلات
    cursor.execute("SELECT COUNT(*) FROM salary_records")
    record_count = cursor.fetchone()[0]
    st.metric("عدد سجلات الرواتب", record_count)
    
    if st.button("🔄 إعادة تشغيل"):
        st.rerun()