# proj6-mongo
Simple list of dated memos kept in MongoDB database
(Forked and edited by Ramsey McGrath) 
## What is not here
Your credentials.ini file should include
- DB : The name of your MongoDB database, which may include multiple collections
- DB_USER : A use name for your application.  
- DB_USER_PW : The password your application gives to access your database
- ADMIN_USER : The administrative user for your MongoDB
installation.  If you install MongoDB on your own computer, you need
this for creating a database.  You don't need it if you use a
cloud-hosted MongoDB service. 
- ADMIN_PW : Password for the administrative user.  You need this if
you use create_db.py to initialize your database.  You don't need it
if you use a cloud-hosted MongoDB service
- DB_HOST : The host computer on which your MongoDB database runs.  This
might be 'localhost' or it might be something like ds884198.mlab.com
- DB_PORT : The network port on which your MongoDB database listens.
  If you run MongoDB on your own computer, the default is 27017.  If
  you run MongoDB on MLab or a similar cloud service, it will be a port
  assigned by your cloud service. 
## Functionality 
User can add dated memos, all stored in a handy mongo DB!
They can also delete them and read them
## Setting up
You will need a mongo instance available, 
and you'll need to put the credentials into a test credentials.ini file.


