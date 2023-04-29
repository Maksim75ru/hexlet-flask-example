from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
    session
)
import json
from uuid import uuid4
from email_validator import validate_email, EmailNotValidError


# Это callable WSGI-приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = uuid4().hex


@app.route('/courses/<int:id>')
def courses(id):
    return f'Course id: {id}'


@app.route('/users')
def get_users():
    term = request.args.get('term')
    per_page = 5
    page = request.args.get('page', default=1, type=int)
    messages = get_flashed_messages(with_categories=True)

    with open('users.json', 'r') as fr:
        users = json.load(fr)

    if term:
        filtered_users = list(filter(lambda user: term.lower() in user["nickname"].lower(), users))
        return render_template('users/index.html', users=filtered_users, search=term, messages=messages)

    users = users[(page - 1) * per_page:page*per_page]

    return render_template('users/index.html', users=users, messages=messages, page=page)


@app.post('/users')
def users_post():
    return 'Users', 302


@app.route('/users/<int:id>')
def get_user(id):
    with open('users.json', 'r') as f:
        users = json.load(f)
        target_user = list(filter(lambda user: int(user['id']) == id, users))

    if not target_user:
        return 'Page not found', 404

    return render_template('users/show.html', user=target_user)


""" Создание нового пользователя
Пользователь вводить никнейм и email. Email проходит проверку на валидность.
Если проверка пройдена, то данные пользователя записываются в файл.
Если проверка НЕ пройдена, то пользователь получает сообщение об ошибке.
"""


def validate(nickname, email):
    errors = {}
    try:
        validate_email(email)
    except EmailNotValidError as e:
        errors['email'] = e

    if len(nickname) < 2:
        errors['nickname'] = 'Nickname must be grater than 2 characters'

    return errors


@app.post('/users/new')
def user_post():
    user = request.form.to_dict()
    errors = validate(user['nickname'], user['email'])

    if errors:
        flash('Ошибка записи, проверьте корректность данных', category='error')
        messages = get_flashed_messages(with_categories=True)
        return render_template('users/form.html', user=user, errors=errors, messages=messages)

    flash('Вы успешно добавили пользователя', category='success')
    id_ = uuid4().int % 1000
    user['id'] = str(id_)

    with open('users.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        data.append(user)
        with open('users.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=4, ensure_ascii=False)

    return redirect(url_for('get_users'), code=302)


@app.get('/users/new')
def users_new():
    user = {'nickname': '',
            'email': '',
            'user_id': '',
            }
    errors = {}
    return render_template('users/form.html', user=user, errors=errors)


""" Обновление данных пользователя"""


@app.get('/users/<id>/edit')
def edit_user(id):
    errors = {}
    with open('users.json', 'r') as f:
        users = json.load(f)
        user = next(filter(lambda user_: user_['id'] == id, users))

    return render_template('users/edit.html', user=user, errors=errors)


@app.post('/users/<id>/patch')
def patch_user(id):
    with open('users.json', 'r') as f:
        users = json.load(f)
        user = next(filter(lambda user_: user_['id'] == id, users))

    data = request.form.to_dict()

    errors = validate(user['nickname'], user['email'])
    if errors:
        return render_template('users/edit.html', user=user, errors=errors), 422

    for user in users:
        if user['id'] == id:
            user['nickname'] = data['nickname']
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    flash('Вы успешно обновили никнейм пользователя', category='success')

    return redirect(url_for('get_users'), code=302)


""" Удаление пользователя пользователя"""


@app.post('/users/<id>/delete')
def delete_user(id):
    with open('users.json', 'r') as fr:
        users = json.load(fr)
        user = next(filter(lambda user_: user_['id'] == id, users))

    new_data = list(filter(lambda user_: user_ != user, users))

    with open('users.json', 'w') as fw:
        json.dump(new_data, fw, indent=4, ensure_ascii=False)

    flash('Вы успешно удалили пользователя', category='success')

    return redirect(url_for('get_users'), 302)


""" Вход пользователя по логину и сохранение доступа в сессии
Также реализовано удаление данных из сессии
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'username' in session:
            # return f'Logged in as {session["username"]}'
            users = session.values()
            return render_template('users/login_users.html', users=users)

    if request.method == 'GET':
        return render_template('users/base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return 'You logged user'
    return render_template('users/login_form.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
