"""
Provides configuration options for the Flask application. This file is supposed to be loaded using
the `app.config.from_object` method.
"""
# Sets the secret key used by the Flask application
# This should always be set to a secret value
SECRET_KEY = "somethinguniqueandsecret"

# Sets the server name to be used by Flask to generate full paths
# This should match your domain name or hostname
SERVER_NAME = "localhost:5000"

# Sets debug mode
# This should always be False in production environments
DEBUG = False
