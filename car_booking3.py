from flask import Flask, render_template, request, redirect, url_for
from datetime import date, datetime
import mysql.connector
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# MySQL 設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'foxdie83356',
    'database': 'vehicle_db',
    'auth_plugin': 'mysql_native_password'
}

# Email 寄件設定
EMAIL_SENDER = 'yang.di@toshibatec.com.tw'
EMAIL_PASSWORD = 'foxdie789'
SMTP_SERVER = 'mail.toshibatec.com.tw'
SMTP_PORT = 25

# 車號對應 Email
car_emails = {
    'BKQ-2990': 'yang.di@toshibatec.com.tw',
    'BKQ-2991': 'yang.di@toshibatec.com.tw'
}

# 建立資料庫連線
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 發送 Email 函式
def send_email(subject, body, to_email):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())

@app.route('/history')
def history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM records ORDER BY record_date DESC, id DESC")
    rows = cursor.fetchall()
    conn.close()
    return render_template('history.html', records=rows)

@app.route('/')
def calendar_view():
    year = 2025
    month = 6
    days = [date(year, month, d) for d in range(1, 31)]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM records")
    rows = cursor.fetchall()
    conn.close()

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

    to_email = car_emails.get(car_number)
    if to_email:
        subject = f"[新增登記通知] {d}"
        body = f"日期: {d}\n部門: {department}\n車號: {car_number}\n用途: {purpose}"
        send_email(subject, body, to_email)

    return redirect(url_for('calendar_view'))

@app.route('/edit/<int:record_id>', methods=['POST'])
def edit_record(record_id):
    purpose = request.form['purpose']
    car_number = request.form['car_number']
    department = request.form['department']
    d_str = request.form['date']
    new_date = datetime.strptime(d_str, '%Y-%m-%d').date()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 取得原始紀錄
    cursor.execute("SELECT * FROM records WHERE id = %s", (record_id,))
    old_record = cursor.fetchone()

    # 更新資料
    cursor.execute("""
        UPDATE records
        SET purpose = %s, car_number = %s, department = %s, record_date = %s
        WHERE id = %s
    """, (purpose, car_number, department, new_date, record_id))
    conn.commit()
    conn.close()

    if old_record:
        # 發送通知給編輯後車號
        new_email = car_emails.get(car_number)
        subject = f"[編輯登記通知] ID: {record_id}"
        body = f"""編輯前:
記錄ID: {old_record['id']}
日期: {old_record['record_date']}
部門: {old_record['department']}
車號: {old_record['car_number']}
用途: {old_record['purpose']}

編輯後:
記錄ID: {record_id}
日期: {new_date}
部門: {department}
車號: {car_number}
用途: {purpose}
"""
        if new_email:
            send_email(subject, body, new_email)

        # 車號有變動時，也發通知給舊車號
        old_email = car_emails.get(old_record['car_number'])
        if old_record['car_number'] != car_number and old_email:
            send_email(subject + "（原車號通知）", body, old_email)

    return redirect(url_for('calendar_view'))

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM records WHERE id = %s", (record_id,))
    rec = cursor.fetchone()

    cursor.execute("DELETE FROM records WHERE id = %s", (record_id,))
    conn.commit()
    conn.close()

    if rec:
        to_email = car_emails.get(rec['car_number'])
        if to_email:
            subject = f"[刪除登記通知] ID: {record_id}"
            body = f"記錄ID: {record_id} 已被刪除\n日期: {rec['record_date']}\n部門: {rec['department']}\n車號: {rec['car_number']}\n用途: {rec['purpose']}"
            send_email(subject, body, to_email)

    return redirect(url_for('calendar_view'))

if __name__ == '__main__':
    app.run(debug=True)
