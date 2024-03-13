import os

def user_image_upload_path(user_id, filename):
    # Construct the upload path with the user's ID
    upload_path = os.path.join('images', f'user_{user_id}', filename)
    
    # Ensure that the directory structure exists
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    
    return upload_path
