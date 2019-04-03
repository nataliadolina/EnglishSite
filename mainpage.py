import json

from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from DB import DB, UsersModel, TasksModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Enter')


base = DB()
users_base = UsersModel(base)
users_base.init_table()
print(users_base.get_all())


class RegistrateForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeatpassword = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Done')


class AddTaskForm(FlaskForm):
    sentence = TextAreaField('sentences', validators=[DataRequired()])
    choice = TextAreaField('answer choice', validators=[DataRequired()])
    correct = TextAreaField('answer choice', validators=[DataRequired()])
    submit = SubmitField('Add')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrateForm()
    if form.validate_on_submit():
        f1, f2 = form.username.data, form.password.data
        exists = users_base.exists(f1, f2)
        if exists[0]:
            form.username.data = ''
            return render_template('registration.html',
                                   text='User with such name already exists. Please change the login', form=form)
        elif f2 != form.repeatpassword.data:
            form.password.data = ''
            return render_template('registration.html',
                                   text='Passwords do not match. Please check your spelling and try again', form=form)
        else:
            session['username'] = form.username.data
            nm = UsersModel(base)
            nm.insert(form.username.data, form.password.data)
            session['user_id'] = users_base.exists(form.username.data, form.password.data)[1]
            return redirect('/index')
    return render_template('registration.html', text='', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        exists = users_base.exists(request.form['username'], request.form['password'])
        if exists[0]:
            session['username'] = request.form['username']
            session['user_id'] = exists[1]
            return redirect('/index')
        return render_template('login.html', title='Authorization', text='invalid login or password', form=form)
    return render_template('login.html', title='Authorization', text='', form=form)


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('tasks.html')


@app.route('/', methods=['GET', 'POST'])
def tasks():
    if 'username' in session:
        return render_template('tasks.html')
    else:
        return redirect('/login')


users = [x[1] for x in users_base.get_all()]
ides = [x[0] for x in users_base.get_all()]
ides_names = {}
for i in range(len(users)):
    ides_names[ides[i]] = users[i]
ides_names = sorted(list(ides_names.items()), key=lambda x: x[1])


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'username' not in session:
        return redirect('/login')
    form = AddTaskForm()
    if form.validate_on_submit():
        sentence = form.sentence.data
        choice = form.choice.data
        correct = form.correct.data
        nm = TasksModel(base)
        print(request.form['accept'])
        #nm.insert(sentence, choice, session['user_id'], correct)
        return redirect("/index")
    return render_template('add_task.html', form=form, username=session['username'], users=ides_names)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
