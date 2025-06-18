from flask import Flask, render_template, request, redirect, url_for
from datetime import date, datetime
import mysql.connector

app = Flask(__name__)

# MySQL 設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'foxdie83356',
    'database': 'vehicle_db',
    'auth_plugin': 'mysql_native_password'  # 視情況加上
}

# 建立資料庫連線
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def calendar_view():
    # 顯示 2025/6 月曆
    year = 2025
    month = 6
    days = [date(year, month, d) for d in range(1, 31)]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM records")
    rows = cursor.fetchall()
    conn.close()

    # 整理成以日期為 key 的 dict
    records = {}
    for row in rows:
        d = row['record_date']
        records.setdefault(d, []).append(row)

    return render_template('calendar.html', days=days, records=records)

@app.route('/submit', methods=['POST'])
def submit():
    d_str = request.form['date']
    purpose = request.form['purpose']
    car_number = request.form['car_number']
    department = request.form['department']
    d = datetime.strptime(d_str, '%Y-%m-%d').date()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO records (record_date, purpose, car_number, department)
        VALUES (%s, %s, %s, %s)
    """, (d, purpose, car_number, department))
    conn.commit()
    conn.close()
    return redirect(url_for('calendar_view'))

@app.route('/edit/<int:record_id>', methods=['POST'])
def edit_record(record_id):
    purpose = request.form['purpose']
    car_number = request.form['car_number']
    department = request.form['department']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE records
        SET purpose = %s, car_number = %s, department = %s
        WHERE id = %s
    """, (purpose, car_number, department, record_id))
    conn.commit()
    conn.close()
    return redirect(url_for('calendar_view'))

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = %s", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('calendar_view'))

if __name__ == '__main__':
    app.run(debug=True)
