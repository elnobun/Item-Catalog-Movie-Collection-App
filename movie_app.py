from moviecollection import app
import uuid

# Item Catalog project main app.
# Run this file as 'python catalog_app.py' to initialize the server.
# Before running this app, ensure that the database is setup by running 'database_setup.py'.

app.start_session()
app.secret_key = uuid.uuid4().hex  # 'secret_key'
app.debug = True

# If debug is enabled, the server will reload itself each time it notices a code change.
# it is advisable to turn debug off in production.
# The debugging console allows code to be executed directly on the server.

app.run(host='0.0.0.0', port=5000)  # Tells the web-server on the vagrant machine to listen on all public IP-addresses.
