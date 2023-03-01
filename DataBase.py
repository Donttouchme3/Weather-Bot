import sqlite3

DataBase = sqlite3.connect('WeatherDataBase.db')
cursor = DataBase.cursor()
cursor.execute('''
DROP TABLE IF EXISTS history;
''')
DataBase.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS history(
    historyId INTEGER PRIMARY KEY AUTOINCREMENT,
    chatId BIGINT,
    city TEXT,
    temp FLOAT,
    feelsLike FLOAT,
    weather TEXT,
    wind FLOAT
);
''')
