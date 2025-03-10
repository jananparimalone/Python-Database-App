import sys
import mysql.connector
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDialog, QStackedWidget, QTableView
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtWidgets
#Please note - Comments are ABOVE the line of code that is being commented

#Set the values for HOST, PASSWORD, and DATABASE variables so they are global
HOST = "localhost"
PASSWORD = "password"
DATABASE = "CS350 Project 1"

#Create WelcomeScreen class, open WelcomeScreen.ui
class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        #Set a fixed size for the window
        self.setFixedSize(500,350)
        #Hide password when logging in
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        #Take user to table selection once logged in
        self.selection.clicked.connect(self.loginfunction)

    #Attempting to log in as a user from the database
    def loginfunction(self):
        global user
        global password
        user = self.usernamefield.text()
        password = self.passwordfield.text()

        #If username/password field are empty, display an error message saying that
        if len(user) == 0 or len(password) == 0:
            self.error_label.setText("Enter username and password")

        else:
            try:
                connection = mysql.connector.connect(        
                    host=HOST,
                    user='root',  #MySQL user (you may need to change this)
                    password=PASSWORD,
                    database=DATABASE
                )
            
                #Create a cursor object to interact with the database
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM LogIn_Credential WHERE usernames = %s AND password = %s", (user, password))

                #Fetch the result of the query
                login_info = cursor.fetchall()

                if login_info:
                    #Extract the user's role from the query result
                    self.role = login_info[0][2]
                    #Successful login
                    print("Successfully logged in!")
                    #Close the cursor and database connection
                    cursor.close()
                    connection.close()
                    #Call the gotoselection method to transition to the next screen
                    self.gotoselection()
                
                #If user or pass are incorrect, throw an error
                else:
                    self.error_label.setText("Invalid username or password")
                    #Close the cursor and the database connection
                    cursor.close()
                    connection.close()

            except mysql.connector.Error as err:
                #Handle MySQL errors if DB does not connect
                self.error_label.setText(f"MySQL Error: {err.msg}")

                #Close the cursor and connection in case of an error
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()

    #Bring the user to the table selection screen once logged in
    def gotoselection(self):
        #Record the inputs as variables for username and password
        user = self.usernamefield.text()
        password = self.passwordfield.text()
        #Passing my user, role, and password variables to the SelectTableScreen class
        self.select_table_screen = SelectTableScreen(user, self.role, password)
        #Establish a connection between signals and slots
        self.select_table_screen.table_selected.connect(self.show_selected_table)
        #Add a new widget to the stack of widgets managed by QStackedWidget
        widget.addWidget(self.select_table_screen)
        #Navigate to the next screen or widget in the stack
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    #Function for displaying the selected table (similar syntax to gotoselection())
    def show_selected_table(self, table_name):
        self.view_table_screen = ViewTable()
        self.view_table_screen.show_selected_table(table_name)
        widget.addWidget(self.view_table_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

#Create TableScreen class, open TableScreen.ui
class SelectTableScreen(QDialog):
    #Define a signal to pass the selected table name
    table_selected = pyqtSignal(str)
    #Pass the variables and open selection.ui + set a fixed window size again
    def __init__(self, user, role, password):
        super(SelectTableScreen, self).__init__()
        self.user = user
        self.role = role
        self.password = password
        loadUi("selection.ui", self)
        self.setFixedSize(500,350)
        self.populate_table_selection()

    def populate_table_selection(self):
        #Connect to the database using the user's role
        connection_role = mysql.connector.connect(
                host=HOST,
                user=self.role,  #MySQL role
                password='',
                database=DATABASE
        )
        cursor_role = connection_role.cursor()
        
        #Display table names granted to the role in question
        cursor_role.execute("SHOW TABLES")
        table_names = cursor_role.fetchall()

        cursor_role.close()
        connection_role.close()

        if table_names:
            #Populate the selection widget with table names
            for table_name in table_names:
                self.table_selection.addItem(table_name[0])
        else:
            self.table_selection.addItem("No tables available")

        #Connect the table_selection widget itemClicked signal to emit the selected table name
        self.table_selection.itemClicked.connect(self.on_table_selected)

    def on_table_selected(self, item):
        #Get the selected table name
        selected_table = item.text()
        #Emit the selected table name
        self.table_selected.emit(selected_table)

#Create ViewTable class, open tableviewer.ui
class ViewTable(QDialog):
    def __init__(self):
        super(ViewTable, self).__init__()
        loadUi("tableviewer.ui", self)
        self.setFixedSize(750, 500)
        #Create a Standard Item Model to hold data
        self.model = QStandardItemModel()
        #Set the model for the TableView
        self.tableView.setModel(self.model)
        #Set the table to non-editable
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)
        #Align the text in the label to the center
        self.label.setAlignment(Qt.AlignCenter)

    def show_selected_table(self, table_name):
        #Set label text to show the selected table name
        self.label.setText(f"Displaying {table_name}")
        connection = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            database=DATABASE
        )
        cursor = connection.cursor()
        #Execute the SQL query
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        #Get column names from the query result
        column_names = [i[0] for i in cursor.description]

        #Clear the existing data in the model
        self.model.clear()
        #Set the number of columns in the model
        self.model.setColumnCount(len(column_names))
        #Set column headers in the model
        self.model.setHorizontalHeaderLabels(column_names)

        #Iterate through fetched data
        for row_num, row_data in enumerate(data):
            #Create items for each cell in a row
            row_items = [QStandardItem(str(cell)) for cell in row_data]
            #Insert the row into the model
            self.model.insertRow(row_num, row_items)

        #Close cursor and database connection
        cursor.close()
        connection.close()
        
#Main
app = QApplication(sys.argv)
widget = QStackedWidget()
welcome = WelcomeScreen()
widget.addWidget(welcome)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
