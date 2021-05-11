from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'faithfulData'
mysql.init_app(app)


@app.route('/', methods=['GET'])
def index():
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
    cursor.execute('SELECT fldEruptionLengthInMins FROM tblFaithfulImport ORDER BY fldEruptionLengthInMins ASC LIMIT 50')
    for fldEruptionLengthInMins in cursor.fetchall():
        eruption_labels.append(list(fldEruptionLengthInMins.values())[0])
    eruption_values = []
    cursor.execute('SELECT fldEruptionWaitInMins FROM tblFaithfulImport')
    for fldEruptionWaitInMins in cursor.fetchall():
        eruption_values.append(list(fldEruptionWaitInMins.values())[0])
    cursor.execute('SELECT * FROM tblFaithfulImport')
    result = cursor.fetchall()
    return render_template('chart.html', title='Home', user=user, faithful=result, eruption_labels=eruption_labels, eruption_legend=eruption_legend,
                           eruption_values=eruption_values)

@app.route('/view/<int:index_id>', methods=['GET'])
def record_view(index_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblFaithfulImport WHERE id=%s', index_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', index=result[0])


@app.route('/edit/<int:index_id>', methods=['GET'])
def form_edit_get(index_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblFaithfulImport WHERE id=%s', index_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', index=result[0])


@app.route('/edit/<int:index_id>', methods=['POST'])
def form_update_post(index_id):
    cursor = mysql.get_db().cursor()
    input_data = (request.form.get('fldIndex'), request.form.get('fldEruptionLengthInMins'),
                  request.form.get('fldEruptionWaitInMins'), index_id)
    sql_update_query = """UPDATE tblFaithfulImport t SET t.fldIndex = %s, t.fldEruptionLengthInMins = %s, 
    t.fldEruptionWaitInMins = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, input_data)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/faithful/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Entry Form')


@app.route('/faithful/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    input_data = (request.form.get('fldIndex'), request.form.get('fldEruptionLengthInMins'),
                  request.form.get('fldEruptionWaitInMins'))
    sql_insert_query = """INSERT INTO tblFaithfulImport (fldIndex,fldEruptionLengthInMins,fldEruptionWaitInMins) 
    VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, input_data)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/delete/<int:index_id>', methods=['POST'])
def form_delete_post(index_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblFaithfulImport WHERE id = %s """
    cursor.execute(sql_delete_query, index_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


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