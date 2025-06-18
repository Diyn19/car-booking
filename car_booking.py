from flask import Flask, render_template, request, redirect, url_for
from datetime import date, datetime
import collections

app = Flask(__name__)

# 簡易模擬資料庫：字典 key=日期，value=清單（多筆登記）
records = collections.defaultdict(list)
# id 自動遞增
next_id = 1

def get_next_id():
    global next_id
    nid = next_id
    next_id += 1
    return nid

@app.route('/')
def calendar_view():
    # 示範當月，產生簡單的日期清單(1~30)
    year = 2025
    month = 6
    days = [date(year, month, d) for d in range(1, 31)]
    return render_template('calendar.html', days=days, records=records)

@app.route('/submit', methods=['POST'])
def submit():
    d_str = request.form['date']
    purpose = request.form['purpose']
    car_number = request.form['car_number']
    department = request.form['department']

    d = datetime.strptime(d_str, '%Y-%m-%d').date()
    rec = {
        'id': get_next_id(),
        'purpose': purpose,
        'car_number': car_number,
        'department': department,
    }
    records[d].append(rec)
    return redirect(url_for('calendar_view'))

@app.route('/edit/<int:record_id>', methods=['POST'])
def edit_record(record_id):
    purpose = request.form['purpose']
    car_number = request.form['car_number']
    department = request.form['department']
    # 找出該紀錄並更新
    for rec_list in records.values():
        for rec in rec_list:
            if rec['id'] == record_id:
                rec['purpose'] = purpose
                rec['car_number'] = car_number
                rec['department'] = department
                break
    return redirect(url_for('calendar_view'))

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    for d, rec_list in records.items():
        for rec in rec_list:
            if rec['id'] == record_id:
                rec_list.remove(rec)
                break
    return redirect(url_for('calendar_view'))

if __name__ == '__main__':
    app.run(debug=True)
