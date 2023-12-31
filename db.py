import sqlite3

class Database:
	def __init__(self, db_file):
		self.connection = sqlite3.connect(db_file)
		self.cursor = self.connection.cursor()

	def user_exists(self, user_id):
		with self.connection:
			result = self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchall()
			return bool(len(result))
	
	def add_user(self, user_id, lang):
		with self.connection:
			return self.cursor.execute('INSERT INTO users (user_id, lang) VALUES (?, ?)', (user_id, lang,))
	
	def get_lang(self, user_id):
		with self.connection:
			return self.cursor.execute('SELECT lang FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]