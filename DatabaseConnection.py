# Import the MySQL Connector library
import mysql.connector

# Set the values for HOST, PASSWORD, and DATABASE
HOST = "localhost"
PASSWORD = "password"
DATABASE = "CS350 Project 1"

# Establish initial connection with the MySQL database
try:
    # Connect to the database using the specified host, user, password, and database
    connection = mysql.connector.connect(
        host=HOST,
        user='root',  # MySQL user (you may need to change this)
        password=PASSWORD,
        database=DATABASE
    )

    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    
except Exception as e:
    # If an error occurs during the connection, print an error message and exit the program
    print("Could not establish connection to SQL server")
    print("Error", e)
    exit()

# Grants all privileges to users logging in for tables they will be accessing
cursor.execute("GRANT ALL privileges ON `CS350 Project 1`.Login_Credentials TO 'admin'@'localhost'")
cursor.execute("GRANT ALL privileges ON `CS350 Project 1`.SE_Data TO 'admin'@'localhost', 'SE'@'localhost'")
cursor.execute("GRANT ALL privileges ON `CS350 Project 1`.EMP_SE TO 'SE'@'localhost', 'HR'@'localhost', 'PR'@'localhost', 'General'@'localhost', 'admin'@'localhost'")
cursor.execute("GRANT ALL privileges ON `CS350 Project 1`.HR_Data TO 'admin'@'localhost', 'HR'@'localhost'")
cursor.execute("GRANT ALL privileges ON `CS350 Project 1`.Emp_HR TO 'admin'@'localhost', 'HR'@'localhost', 'PR'@'localhost', 'General'@'localhost'")
cursor.execute("GRANT ALL privileges ON `CS350 Project 1`.Emp_PR TO 'admin'@'localhost', 'HR'@'localhost', 'PR'@'localhost', 'General'@'localhost'")
cursor.execute("GRANT ALL privileges ON `CS350 Project 1`.PR_Data TO 'admin'@'localhost', 'PR'@'localhost'")
print("Permissions granted.\n")

# Prompt the user to enter their username and password
print("Enter Username:")
usernames = input()
print("Enter Password:")
password = input()

# Verifying login information and connecting as the desired user
try:
    # Execute a SQL query to check if the provided username and password exist in the database
    cursor.execute("SELECT * FROM LogIn_Credential WHERE usernames = %s AND password = %s", (usernames, password))

    # Fetch the result of the query
    login_info = cursor.fetchall()
    
    # Extract the user's role from the query result
    role = login_info[0][2]

    # Close the cursor and database connection
    cursor.close()
    connection.close()

    # Print a message indicating the role and database being entered
    print(f'Entering database "{DATABASE}" as role "{role}"')
    print()

    # Connect to the database using the user's role
    connection_role = mysql.connector.connect(
        host=HOST,
        user=role,
        password='',
        database=DATABASE
    )

    # Create a cursor for the role-specific connection
    cursor_role = connection_role.cursor()

    # Execute an SQL query to get a list of tables in the database
    cursor_role.execute("SHOW TABLES")

    # Fetch and print the list of tables
    tables = cursor_role.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])

    # Close the cursor and database connection for the role
    cursor_role.close()
    connection_role.close()

except Exception as e:
    # If an error occurs during the connection, print an error message and exit the program
    print("Error", e)
    print("Could not establish connection to SQL server")
    print("Invalid Username or Password")
    exit()

# Connect to the database using the user's role
connection_role = mysql.connector.connect(
    host=HOST,
    user=role,
    password='',
    database=DATABASE
)

# Function to perform a SELECT operation
def perform_select():

    # Connect to the database using the user's role
    connection_role = mysql.connector.connect(
        host=HOST,
        user=role,
        password='',  # Empty password
        database=DATABASE
    )

    # Create a cursor for the role-specific connection
    cursor_role = connection_role.cursor()

    # Execute the MySQL command for the desired table
    try:
        query = f"SELECT * FROM {usertable}"
        cursor_role.execute(query)
        result = cursor_role.fetchall()

        # Get column names from the cursor description
        column_names = [desc[0] for desc in cursor_role.description]

        # Display column names
        print("Column Names in",usertable,"are",column_names)
        print("")

        # Display the result with column names
        for row in result:
            for i in range(len(column_names)):
                print(f"{column_names[i]}: {row[i]}")
            print()
    except Exception as e:
        print("Error while executing MySQL command:", e)

    # Close the cursor and database connection for the role
    cursor_role.close()
    connection_role.close()

# Prompt the user to choose a table
print("")
usertable = input("What table would you like to view? ")
print("")
perform_select()
