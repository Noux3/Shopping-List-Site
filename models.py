import sqlite3
import hashlib
from database import Database

class User:
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password):
        """Хэширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create(self, username, password):
        """Создание нового пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            hashed_pw = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Пользователь уже существует
        finally:
            conn.close()
    
    def authenticate(self, username, password):
        """Проверка логина и пароля"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        hashed_pw = self.hash_password(password)
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_pw)
        )
        user = cursor.fetchone()
        conn.close()
        return user

class ShoppingItem:
    def __init__(self):
        self.db = Database()
    
    def get_user_items(self, user_id):
        """Получение всех покупок пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM items WHERE user_id = ? ORDER BY purchased, created_at DESC",
            (user_id,)
        )
        items = cursor.fetchall()
        conn.close()
        return items
    
    def add(self, user_id, name, quantity, category):
        """Добавление новой покупки"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (user_id, name, quantity, category) VALUES (?, ?, ?, ?)",
            (user_id, name, quantity, category)
        )
        conn.commit()
        conn.close()
    
    def toggle_purchased(self, item_id, user_id):
        """Отметить товар как купленный/не купленный"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE items SET purchased = NOT purchased WHERE id = ? AND user_id = ?",
            (item_id, user_id)
        )
        conn.commit()
        conn.close()
    
    def delete(self, item_id, user_id):
        """Удаление товара"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM items WHERE id = ? AND user_id = ?",
            (item_id, user_id)
        )
        conn.commit()
        conn.close()