import boto3
import uuid
from flask import Flask, redirect, url_for, request, render_template
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
load_dotenv()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'bmp', 'tiff', 'tif', 'gif', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


db_config = {
    "pool_name": os.getenv("DB_POOL_NAME"),
    "pool_size": int(os.getenv("DB_POOL_SIZE")),
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE"),
}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)


def connect_to_database():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        return connection, cursor
    except:
        return None, None


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    files = []
    bucket_name = "testboard.meow-meow-nanny.website"
    s3 = boto3.resource("s3")
    uuid_number = uuid.uuid4().hex
    if request.method == "POST":
        input_message = request.form.get("message")
        con, cursor = connect_to_database()
        cursor.execute(
            "INSERT INTO message(uuid,message) VALUES (%s,%s)", (uuid_number, input_message))
        con.commit()
        cursor.close()
        con.close()

        uploaded_file = request.files["file-to-upload"]
        if not allowed_file(uploaded_file.filename):
            return "File not allowed!"

        new_filename = uuid_number + '.' + \
            uploaded_file.filename.rsplit('.', 1)[1].lower()

        s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)
        return redirect(url_for("index"))
    con, cursor = connect_to_database()
    cursor.execute("SELECT message FROM message")
    messages = cursor.fetchall()
    cursor.close()
    con.close()

    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.all():
        files.append(obj.key)
    length = len(files)
    return render_template("index.html", files=files, messages=messages, length=length)


app.run(host='0.0.0.0', port=5000, debug=True)
