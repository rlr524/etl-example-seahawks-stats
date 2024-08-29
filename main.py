import psycopg2
import openpyxl
import configparser

# Create a configparser instance to read values from config.ini
config = configparser.ConfigParser()

# Read the values from config.ini
config.read('config.ini')

# Assign the values from config.ini to variables
database = config.get('database', 'database')
user = config.get('database', 'user')
password = config.get('database', 'password')
host = config.get('database', 'host')
port = config.get('database', 'port')

# Create a connection to the Docker PostgreSQL database using psycopg2,
# which is the most commonly used PG database driver for Python
connection = psycopg2.connect(
    database = database,
    user = user,
    password = password,
    host = host,
    port = port
)

# The cursor is a class on the Psycopg library, and most other Python SQL
# libraries that allows python code to execute SQL commands in a DB session.
cursor = connection.cursor()

# Save the path to the Excel file to a variable
file = '/Users/rob/Downloads/sportsref_download.xlsx'

# Use Openpyxl to load the workbook from the Excel file
# and save the active sheet to a variable
workbook = openpyxl.load_workbook(file)
sheet = workbook.active

# Grab the column names from the header for the active sheet
column_names = [column.value for column in sheet[1]]

# Create an empty list to store the sheet data
data = []

# Iterate over each row of the sheet starting with row 2 (to skip the header in this
# case) and append each row to the data list. The values only True setting causes only
# the row values to be returned, and any formulas ignored.
for row in sheet.iter_rows(min_row=2, values_only=True):
    data.append(row)

# Set the name for the PG schema and table we want to create
schema_name: str = 'stats'
table_name: str = 'rushing'

# PSQL command to create the schema
schema_creation = f'CREATE SCHEMA IF NOT EXISTS {schema_name}'

# PSQL command to create the table
table_creation = f"""
CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
{", ".join([f'"{name}" TEXT' for name in column_names])}
)
"""

# Use the cursor instance to execute the schema and table creation commands
cursor.execute(schema_creation)
cursor.execute(table_creation)

# PSQL command to insert the sheet data into the DB using parameterized queries
insert_data = f"""
INSERT INTO {schema_name}.{table_name} ({", ".join([f'"{name}"' for name in column_names])})
VALUES({", ".join(['%s' for _ in column_names])})
"""

# Use the cursor instance to execute the insert_data queries (note there are many
# queries because it's a new query for each row of data in the data list
cursor.executemany(insert_data, data)

# Commit the changes to the DB
connection.commit()

# Close the cursor instance and DB connection
cursor.close()
connection.close()

print("Import successfully completed!")