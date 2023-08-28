# Filebox
> File Storage API

Filebox is an API created using FastAPI to upload files to local storage.
# Endpoints

<details>
<summary>Files</summary>
  
Method	| Path	| Description	| User authenticated	
------------- | ------------------------- | ------------- |:-------------:|
GET	| /files/{path}	| Get file information	| * 
GET	| /files/{path}/download	| Download a file	| × 
POST	| /files/	| Upload a file	| *  
POST	| /files/batch	| Upload a list of files	| *  
DELETE | /files/{path} | Delete a file | *
</details>

<details>
<summary>Folders</summary>
  
Method	| Path	| Description	| User authenticated
------------- | ------------------------- | ------------- |:-------------:|
GET	| /folders/{path}	| Get specified folder	| × 
GET	| /folders/	| Get all folders and subitems	| × 
POST	| /folders/	| Create new folder	| ×  
DELETE	| /folders/	| Delete a folder	| ×  
</details>


<details>
<summary>Users</summary>
  
Method	| Path	| Description	| User authenticated
------------- | ------------------------- | ------------- |:-------------:|
GET	| /users/{user_id}	| Get specified account data	| super_user
GET	| /users/me	| Get current account data	| × 
GET	| /users/	| Get all users	| super_user
PUT	| /users/{user_id}	| Update a  user	| *  
DELETE	| /users/{user_id}	| Delete a user	| × 
POST	| /users/	| Register a new account	|  
</details>

<details>
<summary>Auth</summary>
  
Method	| Path	| Description	| User authenticated
------------- | ------------------------- | ------------- |:-------------:|
POST	| /token	| Get an access token	| 
</details>

# Setting up
Run using containers:
```bash
git clone https://github.com/triciopo/filebox
cd filebox
docker compose up -d
```
Run locally:
```bash
pip install -r requirements.txt
uvicorn filebox.main:app --port 8000 --reload
```
## License

[MIT License](LICENSE)

