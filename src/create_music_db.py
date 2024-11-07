# coding=windows-1251
# create_music_db.py

import sqlite3

# Создаем соединение с базой данных (файл music.db будет создан, если его не существует)
conn = sqlite3.connect('data/music.db')
cursor = conn.cursor()

# Создаем таблицу для хранения музыки и звуков интерфейса
cursor.execute('''
    CREATE TABLE IF NOT EXISTS music (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        category TEXT NOT NULL
    )
''')

# Добавляем записи для музыки главного меню, основной игры и звуков интерфейса
music_tracks = [
    ('Main Menu Music', 'data/menu_music.mp3', 'menu'),
    ('Game Music', 'data/game_music.mp3', 'game'),
    ('Interface Select Sound', 'data/interface_select.mp3', 'interface'),
    ('Interface Confirm Sound', 'data/interface_confirm.mp3', 'interface')
]

# Вставляем данные в таблицу
cursor.executemany('INSERT INTO music (name, file_path, category) VALUES (?, ?, ?)', music_tracks)

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("База данных создана и заполнена музыкой и звуками интерфейса.")
