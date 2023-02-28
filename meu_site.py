from flask import Flask, render_template, redirect, request, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "tccpuc"

# connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://Bruno1981bh:tccpuc@cluster0.6ztnjlx.mongodb.net/?retryWrites=true&w=majority")
db = client['database']
usuarios_collection = db['usuarios']
atividades_collection = db['atividades']
resultado_collection = db['resultado']


# index route - displays login form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if email and password are correct
        email = request.form['email']
        password = request.form['password']
        user = usuarios_collection.find_one({'email': email, 'password': password})
        if user:
            session['user'] = email
            return redirect('/dashboard')
        else:
            return render_template('index.html', message="Invalid login credentials")
    else:
        return render_template('index.html')


# register route - displays registration form
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # create new user
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        usuarios_collection.insert_one({'nome': nome, 'email': email, 'password': password})
        return redirect('/')
    else:
        return render_template('register.html')


# dashboard route - displays dashboard page with user's activities and results
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        email = session['user']
        atividades = atividades_collection.find({'email': email})
        resultados = resultado_collection.find({'email': email})
        return render_template('dashboard.html', atividades=atividades, resultados=resultados)
    else:
        return redirect('/')


# create activity route - displays form to create new activity
@app.route('/create-activity', methods=['GET', 'POST'])
def create_activity():
    if 'user' in session:
        if request.method == 'POST':
            # create new activity
            atividade = request.form['atividade']
            palavras = request.form['palavras']
            email = session['user']
            atividades_collection.insert_one({'email': email, 'atividade': atividade, 'palavras': palavras})
            return redirect('/dashboard')
        else:
            return render_template('create-activity.html')
    else:
        return redirect('/')


# edit activity route - displays form to edit activity
@app.route('/edit-activity/<id>', methods=['GET', 'POST'])
def edit_activity(id):
    if 'user' in session:
        atividade = atividades_collection.find_one({'_id': ObjectId(id)})
        if request.method == 'POST':
            # update activity
            atividades_collection.update_one({'_id': ObjectId(id)}, {'$set': {'atividade': request.form['atividade'], 'palavras': request.form['palavras']}})
            return redirect('/dashboard')
        else:
            return render_template('edit-activity.html', atividade=atividade)
    else:
        return redirect('/')


# delete activity route - deletes activity
@app.route('/delete-activity/<id>', methods=['POST'])
def delete_activity(id):
    if 'user' in session:
        atividades_collection.delete_one({'_id': ObjectId(id)})
        return redirect('/dashboard')
    else:
        return redirect('/')


# create result route - displays form to create new result
@app.route('/create-result', methods=['GET', 'POST'])
def create_result():
    if 'user' in session:
        if request.method == 'POST':
            # create new result
            aluno = request.form['aluno']
            nome_atividade = request.form['nome_atividade']
            nota = request.form['nota']
            email = session['user']
            resultado_collection.insert_one({'email': email, 'aluno': aluno, 'nome_atividade': nome_atividade, 'nota': nota})
            return redirect('/dashboard')
        else:
            atividades = atividades_collection.find({'email': session['user']})
            return render_template('create-result.html', atividades=atividades)
    else:
        return redirect('/')


# edit result route - displays form to edit result
@app.route('/edit-result/<id>', methods=['GET', 'POST'])
def edit_result(id):
    if 'user' in session:
        resultado = resultado_collection.find_one({'_id': ObjectId(id)})
        atividades = atividades_collection.find({'email': session['user']})
        if request.method == 'POST':
            # update result
            resultado_collection.update_one({'_id': ObjectId(id)}, {'$set': {'aluno': request.form['aluno'], 'nome_atividade': request.form['nome_atividade'], 'nota': request.form['nota']}})
            return redirect('/dashboard')
        else:
            return render_template('edit-result.html', resultado=resultado, atividades=atividades)
    else:
        return redirect('/')


# delete result route - deletes result
@app.route('/delete-result/<id>', methods=['POST'])
def delete_result(id):
    if 'user' in session:
        resultado_collection.delete_one({'_id': ObjectId(id)})
        return redirect('/dashboard')
    else:
        return redirect('/')


# logout route - logs user out
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
