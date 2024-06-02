from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

def upload_image(image_file, image_name, type='image_upload'):
    # Read the contents of the JSON key file
    with open(settings.GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE, 'r') as key_file:
        keyfile_dict = json.load(key_file)

    # Save the uploaded image to a temporary file within the project's base directory
    temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', image_name)
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
    with default_storage.open(temp_file_path, 'wb+') as temp_file:
        for chunk in image_file.chunks():
            temp_file.write(chunk)

    # Authenticate with Google Drive using service account credentials
    gauth = GoogleAuth()
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scopes=['https://www.googleapis.com/auth/drive'])
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)

    # Create a file on Google Drive
    folder_id = '1qw2v3RoQ_OJxGfJZcbXZLR9AopxM9Pvj'
    if(type=='profile_pic'):
        folder_id = '15fpEE2rROTRRkUaqbEGP85MuVNF-XdeM'
    
    file_metadata = {
        'title': image_name,
        'parents': [{'id': folder_id}]  # Specify the ID of the folder where you want to upload the file
    }
    file = drive.CreateFile(file_metadata)
    file.SetContentFile(temp_file_path)
    file.Upload()

    # Get the link to the uploaded file
    return file['alternateLink']
