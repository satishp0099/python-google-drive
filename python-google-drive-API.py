import io
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from googleapiclient import errors

class drive():
    def __init__(self):
        '''
        Authorize Google Drive API
        '''
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = None
        if os.path.exists(r'Credentials\token.json'):
            creds = Credentials.from_authorized_user_file(r'Credentials\token.json', SCOPES)
        if not creds or not creds.valid: 
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    r'Credentials\credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open(r'Credentials\token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def create_folder(self, folder_name : str, parent_folder_id= str | None):
        '''
        Create folder.
        args:
            folder_name : str
            parent_folder_id : str
        '''

        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' : [parent_folder_id]
            }

            file = self.service.files().create(body=file_metadata, fields='id'
                                        ).execute()
            print(F'Folder ID: "{file.get("id")}".')
            return file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None
        
    def download_file(self, real_file_id):
        '''
        Download file using file id.

        args:
            real_file_id : str
        '''

        try:
            file_id = real_file_id
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}.')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None
        print(file_id)
        return file.getvalue()
    
    def search_file(self, folder_id):
        '''
        Search file inside the given folder id.
        args:
            folder_id : str
        '''
        files=[]
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = self.service.files().list(#q=f"mimeType='{mimeType}', '{folder_id}' in parents",
                                            q=f"'{folder_id}' in parents and trashed=false",
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                    'files(id, name)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print(F'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return files

    def upload_basic(self, file_name, parent_folder, mimetype=None):
        '''
        Upload the file.
        args:
            file_name : str
            parent_folder : str
        '''

        try:
            file_metadata = {'name': file_name,
                            'parents': [parent_folder]}
            media = MediaFileUpload(file_name,
                                    mimetype=mimetype
                                    )
            file = self.service.files().create(body=file_metadata, media_body=media,
                                        fields='id').execute()
            print(F'File ID: {file.get("id")}')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        return file.get('id')

    def update_file(self, file_id, new_filename, new_name=None, new_description='', new_mime_type=None):
        '''
        Update the existing file.
        args:
            file_id : str
            new_filename : str
            new_name : str
            new_description : str
            new_mime_type : str
        '''

        if new_name==None: new_name=new_filename

        try:
            file = self.service.files().get(fileId=file_id).execute()

            file['name'] = new_name
            #file['description'] = new_description
            #file['mimeType'] = new_mime_type
            file['trashed'] = True
            file_metadata = {
                'name' : new_name,
                'description' : new_description,
            }

            media_body = MediaFileUpload(
                new_filename, mimetype=new_mime_type, resumable=True)

            updated_file = self.service.files().update(
                fileId=file_id,
                body=file_metadata,
                media_body=media_body).execute()
            return updated_file
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            return None