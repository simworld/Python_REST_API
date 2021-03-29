import psycopg2
import yaml
from sys import stderr, argv

from flask import Flask
from flask import request
import json

app = Flask(__name__)

#connect to a specific database
def dbConnect(dbname, dbhost, user, password):
    try:
        return psycopg2.connect(
            dbname='lab2',
            user=user,
            host=dbhost,
            password=password,
            port='5432',
            sslmode="require"
        )
    except Exception as e:
        stderr.write(f"Can't open database: {e}")
        exit()

#open the config file that contains the db information and credentials
def getConfig():
    try:
        with open('config.yaml') as f:
            return yaml.load(f)
    except Exception as e:
        stderr.write(f"Can't open config file: {e}")
        exit()

#decorator to get all the students in the db using the get_all() function
@app.route("/students", methods=['GET'])
def index():
    stud_data = get_all()
    return json.dumps(stud_data) + "\n"

#decorator to show a specific student using the id
#it uses the select(id) function
@app.route("/stud_id/<int:id>", methods=['GET'])
def get_by_id(id:int):
    select_id = select(id)
    return json.dumps(select_id)

#decorator to delete a specific student using the id
#it uses the delete(id) function
@app.route("/delete/<int:id>", methods=['DELETE'])
def delete_by_id(id : int):
    # stud_id = delete(id)
    delete(id)
    return "Record Deleted!"

#decorator to add a new student using the add_student() function
@app.route("/add_student/", methods=['POST'])
def add_student():
    firstname = request.args.get("firstname")
    lastname = request.args.get("lastname")
    email = request.args.get("email")
    new_student(firstname, lastname, email)
    return "Done"

#decorator to update the email for a specific student indicated by the id
@app.route("/update/", methods= ['PATCH'])
def update_by_id():
    id = request.args.get("id")
    email = request.args.get("email")
    update(email, id)
    return "Done"

#show all the content of the db
def get_all():
    students = []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        students.append({
            'id': row[0],
            'firstname': row[1],
            'lastname': row[2],
            'email': row[3]
        })
    cursor.close()
    return students

#delete a record with a specific id
def delete(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    return "Deleted!"

#update the email content of a specific row identified by the id
def update(new_value, id):
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET email = %s WHERE id = %s", (new_value, id))
    conn.commit()
    cursor.close()
    return "Updated!"

#create a student with a specific id
def select(id):
    new = []
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    for row in cursor.fetchall():
        new.append({
            'id': row[0],
            'firstname': row[1],
            'lastname': row[2],
            'email': row[3]
        })
    return new

#create a new student in the db
def new_student(firstname, lastname, email):
    cursor= conn.cursor()
    cursor.execute("INSERT INTO students(firstname, lastname, email) VALUES (%s, %s, %s )", (firstname, lastname, email))
    conn.commit()
    cursor.close()

#try/execpt to connect the database and print if the connection has been successful or not
try:
    dbname = 'lab2'
    cfg = getConfig()
    db = cfg['databases'][dbname]
    conn = dbConnect(dbname, db['host'], db['user'], db['password'])
    cursor = conn.cursor()
    print("connected")

except:
    print("not connected")

#launch flask on port 80 once the python file is executed
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
