from flask import Flask, render_template, request, redirect, url_for, session
from models import User, ShoppingItem
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Измените на что-то свое!

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User()
        if user.create(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Пользователь уже существует')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User()
        user_data = user.authenticate(username, password)
        
        if user_data:
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Личный кабинет со списком покупок"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    shopping = ShoppingItem()
    items = shopping.get_user_items(session['user_id'])
    
    # Группировка товаров по категориям
    categories = {}
    for item in items:
        if item['category'] not in categories:
            categories[item['category']] = []
        categories[item['category']].append(item)
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         categories=categories)

@app.route('/add_item', methods=['POST'])
def add_item():
    """Добавление нового товара"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    quantity = request.form.get('quantity', 1)
    category = request.form.get('category', 'Другое')
    
    shopping = ShoppingItem()
    shopping.add(session['user_id'], name, quantity, category)
    
    return redirect(url_for('dashboard'))

@app.route('/toggle_item/<int:item_id>')
def toggle_item(item_id):
    """Изменение статуса товара"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    shopping = ShoppingItem()
    shopping.toggle_purchased(item_id, session['user_id'])
    
    return redirect(url_for('dashboard'))

@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    """Удаление товара"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    shopping = ShoppingItem()
    shopping.delete(item_id, session['user_id'])
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':

    app.run(debug=True)
else:
    # Для продакшена на Render
    app.run(host='0.0.0.0', port=5000)
