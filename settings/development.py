DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dbname',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',   # Set to empty string for default.
    }
}

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

# mainly for use with django-ses
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''