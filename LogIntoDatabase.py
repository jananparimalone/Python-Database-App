import mysql.connector

try:
    connection = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        database = 'university'
    )

except Exception as e:
    print("Could not establish connection to SQL server")
    print("Error",e)
    exit()
cursor = connection.cursor()
cursor.execute("SELECT * FROM instructor")
rows = cursor.fetchall()
print(rows)
