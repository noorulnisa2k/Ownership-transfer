
## To run this Script

#### Create Service account key:
- Go to Google service account: https://cloud.google.com/iam/docs/keys-create-delete
- Select a project
- Enable google drive api for the project
- Click the email address of the service account that you want to create a key for.
- Click the Keys tab
- Click the Add key drop-down menu, then select Create new key.
- Select JSON as the Key type and click Create. (credentials will be donwloaded)

#### Required Dependencies
```bash
  Pip install google-api-python-client
```
```bash
  pip install google-auth google-auth-oauthlib google-auth-httplib2
```
