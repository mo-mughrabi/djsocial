DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'djsocial',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'dbagent',
        'PASSWORD': 'yyy',
        'HOST': '127.0.0.1', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',   # Set to empty string for default.
    }
}

TWITTER_CONSUMER_KEY = 'anMqBzlUFSqlwZEUr6IsA'
TWITTER_CONSUMER_SECRET = 'bthQkBtWnE60Wvrc53JmjaZrfepLWela5utP7zrI'

# mainly for use with django-ses
AWS_ACCESS_KEY_ID = 'AKIAIXAY4GRLRQ4ZRIWA'
AWS_SECRET_ACCESS_KEY = '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'