# python-google-drive
Simple python wrapper for Google drive API.

Add the credentials.json file into the Credential folder of the working directory.

# Getting started

from python-google-drive-API import drive

# Authorize account permission when prompted

client = drive()

# download the file using file id

file = client.download_file('[FILE_ID]')
