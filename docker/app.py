from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import random
import argparse
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")  # Consider securing your database password
DATABASE = os.environ.get("DATABASE", "employees")
COLOR_FROM_ENV = os.environ.get('APP_COLOR', "lime")
DBPORT = int(os.environ.get("DBPORT", 3306))
BACKGROUND_IMAGE = os.environ.get("BACKGROUND_IMAGE", "Invalid Image been passed")
GROUP_NAME = os.environ.get('GROUP_NAME', "GROUP4")

# AWS S3 Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", None)  # This is optional and used for temporary credentials

db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD, 
    db=DATABASE
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

SUPPORTED_COLORS = ",".join(color_codes.keys())
COLOR = random.choice(list(color_codes.keys()))

@app.route("/", methods=['GET', 'POST'])
def home():
    download_background_image(BACKGROUND_IMAGE)
    image_url = url_for('static', filename='PJpicture.jpg')
    group_name = GROUP_NAME
    return render_template('addemp.html', background_image=image_url, group_name=group_name)

@app.route("/about", methods=['GET','POST'])
def about():
    download_background_image(BACKGROUND_IMAGE)
    image_url = url_for('static', filename='PJpicture.jpg')
    group_name = GROUP_NAME
    return render_template('about.html', background_image=image_url, group_name=group_name)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    download_background_image(BACKGROUND_IMAGE)
    image_url = url_for('static', filename='PJpicture.jpg')
    group_name = GROUP_NAME
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, background_image=image_url, group_name=group_name)
    
@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    download_background_image(BACKGROUND_IMAGE)
    image_url = url_for('static', filename='PJpicture.jpg')
    group_name = GROUP_NAME
    return render_template("getemp.html", background_image=image_url, group_name=group_name)

@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    download_background_image(BACKGROUND_IMAGE)
    image_url = url_for('static', filename='PJpicture.jpg')
    group_name = GROUP_NAME
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], color=color_codes[COLOR], background_image=image_url, group_name=group_name)


def download_background_image(image_url):
    try:
        if not image_url.startswith("http"):
            print("BACKGROUND_IMAGE is not a valid URL.")
            return

        bucket_name = image_url.split('/')[2].split('.')[0]
        object_key = '/'.join(image_url.split('/')[3:])
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN  # This is optional and for temporary credentials
        )

        local_filename = "static/PJpicture.jpg"
        s3_client.download_file(bucket_name, object_key, local_filename)
        print("Background image downloaded successfully from S3.")
    
    except ClientError as e:
        print(f"Failed to download from S3: {e}")
    except Exception as e:
        print(f"Error downloading background image: {e}")

# Include other route handlers here...

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False, help="Set the color of the application background.")
    args = parser.parse_args()

    if args.color and args.color in color_codes:
        COLOR = args.color
    elif COLOR_FROM_ENV and COLOR_FROM_ENV in color_codes:
        COLOR = COLOR_FROM_ENV
    else:
        print(f"Using a random color: {COLOR}")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
