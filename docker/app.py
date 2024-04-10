from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import random
import argparse
import boto3
import botocore
app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "passwors"
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT"))
BACKGROUND_IMAGE = os.environ.get("BACKGROUND_IMAGE") or "Invalid Image been passed"
GROUP_NAME = os.environ.get('GROUP_NAME') or "GROUP4"


print('GROUP_NAME:', GROUP_NAME)


# Create a connection to the MySQL database
db_conn = connections.Connection(
    host= DBHOST,
    port=DBPORT,
    user= DBUSER,
    password= DBPWD,
    db= DATABASE
)
output = {}
table = 'employee';

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}


# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])

@app.route("/", methods=['GET', 'POST'])
def home():
    print('show me the background image url',BACKGROUND_IMAGE)
    image_url = url_for('static', filename='background_image.png')
    group_name = os.environ.get('GROUP_NAME', 'DefaultGroup')
    return render_template('addemp.html', background_image = image_url, group_name = group_name)
@app.route("/download", methods=['GET','POST'])

def download(image_url):
   try:
         bucket = image_url.split('//')[1].split('.')[0]
         object_name = '/'.join(image_url.split('//')[1].split('/')[1:])
         print(bucket)  # prints 'finalbrojectmoishtor'
         print(object_name)  # prints'wallpaperflare.com_wallpaper.jpg' 
         print("Background Image Location --->" + image_url) # Added for Logging of Background Image Path
         s3 = boto3.resource('s3')
         output_dir = "static"
         if not os.path.exists(output_dir):
                 os.makedirs(output_dir)
         output = os.path.join(output_dir, "background_image.png")
         s3.Bucket(bucket).download_file(object_name, output)

         return output

   except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise





@app.route("/about", methods=['GET','POST'])
def about():
    group_name = os.environ.get('GROUP_NAME', 'DefaultGroup')
    image_url = url_for('static', filename='background_image.png')
    return render_template('about.html', background_image = image_url, group_name = group_name)
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    # Capture form data
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    # Prepare SQL for inserting new employee
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        # Attempt to insert new employee into the database
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    except Exception as e:
        print(e)
        emp_name = "Error adding employee"
    finally:
        cursor.close()

   
    image_url = url_for('static', filename='background_image.png')
    group_name = os.environ.get('GROUP_NAME', 'DefaultGroup')

   
    return render_template('addempoutput.html', background_image=image_url, group_name=group_name, name=emp_name)
    
@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    image_url = url_for('static', filename='background_image.png')
    group_name = os.environ.get('GROUP_NAME', 'DefaultGroup')
    return render_template("getemp.html", background_image = image_url, group_name = group_name)


@app.route("/fetchdata", methods=['POST'])  
def FetchData():
    emp_id = request.form.get('emp_id')  

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        if result:
            output = {
                "emp_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "primary_skills": result[3],
                "location": result[4]
            }
        else:
            output["error"] = "Employee not found"
    except Exception as e:
        print(e)
        output["error"] = "Error fetching employee data"
    finally:
        cursor.close()

    image_url = url_for('static', filename='background_image.png')
    group_name = os.environ.get('GROUP_NAME', 'DefaultGroup')
    return render_template("getempoutput.html", background_image=image_url, group_name=group_name, **output)

if __name__ == '__main__':
    download(BACKGROUND_IMAGE)
    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print("A color was set through environment variable -" + COLOR_FROM_ENV + ". However, color from command line argument takes precendence.")
    elif COLOR_FROM_ENV:
        print("No Command line argument. Color from environment variable =" + COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    app.run(host='0.0.0.0',port=8080,debug=True)