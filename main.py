########################### worked ###############################
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json, time


######################################   Authentication   ######################################

def authenticate_user():
    # Set the path to your credentials JSON file
    credentials_path = 'client_secret.json'

    # Set the API scope
    scope = ['https://www.googleapis.com/auth/drive.readonly']

    if os.path.exists('token.json'):
        # read token
        with open('token.json', 'r') as token_file:
            file = json.loads(token_file.read())
        credentials = Credentials.from_authorized_user_info(file)

        # if token is expired it will refresh and overwrite
        if credentials.expired:
            print('token expired')
            credentials.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())
    else:
        # Load credentials
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes=scope)
        credentials = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
 
    # Build the Google Drive API service
    drive_service = build('drive', 'v3', credentials=credentials)
    
    return drive_service
    
######################################  Extracting Folder ids owned by me ###################################

def get_permissions(folders):
    try:
        selected_ids = []
        for folder in folders:
            file_id = folder['id']
            file_name = folder['name']
            
            # Retrieve the list of permissions for the file
            permissions = drive_service.permissions().list(fileId=file_id).execute().get('permissions', [])

            for permission in permissions:
                if permission['role'] == 'owner':
                    # print(f"Permission ID: {permission['id']}")
                    # print(f"Role: {permission['role']}")
                    # print(f"Type: {permission['type']}")
                    currentOwner = drive_service.permissions().get(fileId=file_id,permissionId=permission['id'],fields='emailAddress').execute()['emailAddress']
                    if currentOwner == 'noor.nisa@lyftrondata.com':
                        # print(f"{file_name} {currentOwner}")
                        selected_ids.append(file_id)
        print(len(selected_ids))
        return selected_ids

    except Exception as e:
        print(f"Error: {e}")

######################################  Getting all folders exist in parent folder ###################################
        
def get_folder(drive_service, parent_folder_id):

    # List all folders in the specified parent folder
    results = drive_service.files().list(
        q=f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false").execute()

    folders = results.get('files', [])

    # Display folder names
    if not folders:
        print('No folders found.')
        return []
    else:
        print('Folders in the parent folder:', len(folders))
        # for folder in folders:
        #     print(f"{folder['name']} (ID: {folder['id']})")
        return folders

######################################  Getting files exist in all subfolders ###################################
    
def get_folder_files(folder_ids):
    file_ids = []
    for id in folder_ids:
        results = drive_service.files().list(q=f"'{id}' in parents and trashed=false").execute()
        files = results.get('files', [])

        # Display file names
        if not files:
            print('No files found.')
        else:
            # print('Files in the folder:')
            for file in files:
                file_ids.append(file['id'])
    print(len(file_ids))
    return file_ids

######################################  Transfered ownership  ###################################

def transfer_permissions(file_ids, email, role='owner'):
    try:
        for file_id in file_ids:
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            drive_service.permissions().create(fileId=file_id, body=permission, transferOwnership=True).execute()

        print(f"Users {email} added to permissions successfully!")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':

    # Set the ID of the parent folder
    parent_folder_id = '1ud5AeMAJMssOJgIA8gJ6OY3UrtevwA0e'
    users_to_transfer = ['mohsin.karim@lyftrondata.com']

    drive_service = authenticate_user()

    # getting all folder
    folders = get_folder(drive_service, parent_folder_id)

    # getting folders owned by me
    folder_ids = get_permissions(folders)

    # transfered folders ownership
    transfer_permissions(folder_ids, users_to_transfer)

    # getting all files exist in those folder (owned by me)
    file_ids = get_folder_files(folder_ids)

    # transfered ownership of all files
    transfer_permissions(file_ids, users_to_transfer)
