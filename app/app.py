from typing import List, Dict
import os
import simplejson as json
from flask import Flask, request, Response, redirect, session, url_for, flash
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'faithfulData'
mysql.init_app(app)

app.config['SECRET_KEY'] = 'data'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAIL_SENDER'] = os.environ.get('MAIL_SENDER')
mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("login.html")


@app.route('/index', methods=['GET'])
def index_homepage():
    user = {'username': 'Vaibhav'}

    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblFaithfulImport')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, faithful=result)


@app.route('/chart', methods=['GET'])
def charts_view():
    user = {'username': 'Vaibhav'}
    eruption_legend = 'Eruption Data'
    eruption_labels = []
    cursor = mysql.get_db().cursor()
    cursor.execute(
        'SELECT fldEruptionLengthInMins FROM tblFaithfulImport ORDER BY fldEruptionLengthInMins ASC LIMIT 50')
    for fldEruptionLengthInMins in cursor.fetchall():
        eruption_labels.append(list(fldEruptionLengthInMins.values())[0])
    eruption_values = []
    cursor.execute('SELECT fldEruptionWaitInMins FROM tblFaithfulImport')
    for fldEruptionWaitInMins in cursor.fetchall():
        eruption_values.append(list(fldEruptionWaitInMins.values())[0])
    cursor.execute('SELECT * FROM tblFaithfulImport')
    result = cursor.fetchall()
    return render_template('chart.html', title='Home', user=user, faithful=result, eruption_labels=eruption_labels,
                           eruption_legend=eruption_legend,
                           eruption_values=eruption_values)


@app.route('/login', methods=['POST'])
def index_login():
    if 'fldEmail' in request.form and 'fldPassword' in request.form:
        fldEmail = request.form['fldEmail']
        fldPassword = request.form['fldPassword']
        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT * FROM tblUsersImport WHERE fldEmail=%s AND fldPassword=%s", (fldEmail, fldPassword))
        info = cursor.fetchone()
        print(info)
        if info is not None:
            if info['fldEmail'] == fldEmail and info['fldPassword'] == fldPassword:
                username = info['fldName']
                string01 = "{'username': '"
                string02 = "'}"
                user = string01 + username + string02
                return render_template("profile.html", user=user)
        else:
            return render_template("login.html")


@app.route('/new', methods=['GET'])
def form_register_get():
    return render_template('register.html')


@app.route('/new', methods=['POST'])
def form_register_post():
    recipient = request.form['fldEmail']
    msg = Message('Registration for Final Web Application successful', recipients=[recipient])
    msg.body = ('Congratulations! You have successfully registered to the Final Web Application '
                'Regards,'
                'Vinit Santani and Vaibhav Pothireddy')
    msg.html = ('<h1>Final Web Application</h1>'
                '<p>Congratulations! You have successfully register to our final project '
                '<b>IS 601 - Final Web Application</b>! '
                'by '
                '<b>Vinit Santani and Vaibhav Pothireddy</b></p>')
    mail.send(msg)
    flash(f'A registration message was sent to {recipient}.')
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('fldName'), request.form.get('fldEmail'), request.form.get('fldPassword'))
    sql_insert_query = """INSERT INTO tblUsersImport (fldName, fldEmail, fldPassword) VALUES (%s,%s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/profile')
def profile():
    return render_template("profile.html")


@app.route('/view/<int:index_id>', methods=['GET'])
def record_view(index_id):
    user = {'username': 'Vaibhav'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblFaithfulImport WHERE id=%s', index_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', user=user, index=result[0])


@app.route('/edit/<int:index_id>', methods=['GET'])
def form_edit_get(index_id):
    user = {'username': 'Vaibhav'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblFaithfulImport WHERE id=%s', index_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', user=user, index=result[0])


@app.route('/edit/<int:index_id>', methods=['POST'])
def form_update_post(index_id):
    cursor = mysql.get_db().cursor()
    input_data = (request.form.get('fldIndex'), request.form.get('fldEruptionLengthInMins'),
                  request.form.get('fldEruptionWaitInMins'), index_id)
    sql_update_query = """UPDATE tblFaithfulImport t SET t.fldIndex = %s, t.fldEruptionLengthInMins = %s, 
    t.fldEruptionWaitInMins = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, input_data)
    mysql.get_db().commit()
    return redirect("/index", code=302)


@app.route('/faithful/new', methods=['GET'])
def form_insert_get():
    user = {'username': 'Vaibhav'}
    return render_template('new.html', title='New Entry Form', user=user)


@app.route('/faithful/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    input_data = (request.form.get('fldIndex'), request.form.get('fldEruptionLengthInMins'),
                  request.form.get('fldEruptionWaitInMins'))
    sql_insert_query = """INSERT INTO tblFaithfulImport (fldIndex,fldEruptionLengthInMins,fldEruptionWaitInMins) 
    VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, input_data)
    mysql.get_db().commit()
    return redirect("/index", code=302)


@app.route('/delete/<int:index_id>', methods=['POST'])
def form_delete_post(index_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblFaithfulImport WHERE id = %s """
    cursor.execute(sql_delete_query, index_id)
    mysql.get_db().commit()
    return redirect("/index", code=302)


@app.route('/api/v1/faithful', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblFaithfulImport')
    result = cursor.fetchall()
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/faithful/<int:index_id>', methods=['GET'])
def api_retrieve(index_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblFaithfulImport WHERE id=%s', index_id)
    result = cursor.fetchall()
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/faithful/<int:index_id>', methods=['PUT'])
def api_edit(index_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['fldIndex'], content['fldEruptionLengthInMins'], content['fldEruptionWaitInMins'], index_id)
    sql_update_query = """UPDATE tblFaithfulImport t SET t.fldIndex = %s, t.fldEruptionLengthInMins = %s, 
    t.fldEruptionWaitInMins = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/faithful', methods=['POST'])
def api_add() -> str:
    content = request.json
    cursor = mysql.get_db().cursor()
    inputData = (content['fldIndex'], content['fldEruptionLengthInMins'],
                 request.form.get('fldEruptionWaitInMins'))
    sql_insert_query = """INSERT INTO tblFaithfulImport (fldIndex,fldEruptionLengthInMins,fldEruptionWaitInMins) 
    VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/faithful/<int:index_id>', methods=['DELETE'])
def api_delete(index_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblFaithfulImport WHERE id = %s """
    cursor.execute(sql_delete_query, index_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
