from datetime import datetime
from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from services.predictionModels import predict
from services.mongoDB import db
import bson

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST', 'GET'])
def upload():
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login.login'))

    # Get current user newborns
    current_user = db.users.find_one({'username': session['username']})
    newborns = current_user['newborns']
    document_size=len(bson.BSON.encode(current_user))

    if request.method == 'GET':
        return render_template("upload.html", newborns=newborns)
    else:
        file = request.files['file']
        if file is None:
            # Return an error message if the file is not in the request
            return 'No file uploaded', 400
        # Calculate the total size of the document and the file
        total_size = document_size + file.content_length
        print(f"Document current size: {total_size} bytes")  # Print the total size
        # Check if the total size exceeds the limit (16MB)
        if total_size > 14 * 1024 * 1024:
            result="Error"
            return result

        # Get the selected newborn's name from the form
        selected_newborn_name = request.form['newborn_name']
        # Set the filename from the form
        filename = request.form['recording_name']

        # Call the predict function to get the result
        result = predict(file)
        print(result)

        # Datetime object containing current date and time
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        file.seek(0)
        db.users.update_one(
            {"username": session['username'], "newborns.name": selected_newborn_name},
            {"$push": {"newborns.$.recordings": {"name": filename, "date": dt_string, "file": file.read(), "label": result}}})
        file.close()

        return result
    
