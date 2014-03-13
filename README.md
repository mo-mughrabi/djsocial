Introduction
-----

djsocial is an opensource software. Planned to launch for twitter and as demand increase both functionality and
social integration

    1) Auto follow certain hashtags
    2) Auto favorite certain hashtags
    3) Auto follow back
    4) Auto unfollow backard


Setup and Installation
-----

First step is to creare a postresql database and create a virtual environment with :

```
>>> virtualenv djsocial_env
```

Second step is to clone the project and install the requirements

    1) git clone git@github.com:mo-mughrabi/djsocial.git
    2) pip install -r requirements.txt
    3) cp settings/development.py settings/local_env.py
    3) python manage.py resetdb

The last commands loads fixture data for groups and the admin user.

To change the admin password use the following command in the django shell:

```
>>> admin = User.objects.get(id=1)
>>> admin.setpassword("new_password")
>>> admin.save()
```
    
Note that you need to edit the file  settings/local_env.py with :

    * Database credentials
    * Twitter app cosumer key and secret
    * Amazon access Key and Secret

=======

To execute scheduled tasks, celery needs to be running (rabbitmq required):

```
>>> python manage.py celery worker -Q djsocial -B -E --loglevel=INFO
```

    
Contributors
-----

    * Mo Mughrabi - Lead developer
    * Ahmed Elhamidi - Developer
    * Mariusz Kosakowski - Developer


