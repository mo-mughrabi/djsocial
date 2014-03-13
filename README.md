Introduction
-----

djsocial was developed as initiative to create a robotic web based solution for social media, starting with twitter
and expanding later to other channels. Unfortunately, investment was cut off and project decided to be discontinued,
so we moved the project to the open source arena.

We will continue to support it if any issue arises and we will work on a roadmap to build further features and
integration with other social channels in the next period.

At the moment, djsocial is built with twitter integration. With the following functionality

    1) Auto follow certain hashtags
    2) Auto favorite certain hashtags
    3) Auto follow back
    4) Auto unfollow backard


Setup and Installation
-----

The solution will only work on *postgresql* databases, since we are heavily using hstore dictionary fields in our
model design.

to begin clone the project and install the requirements

    git clone git@github.com:mo-mughrabi/djsocial.git
    pip install -r requirements.txt
    cp settings/development.py settings/local_env.py
    python manage.py resetdb

The last commands loads fixture data for groups and the admin user.

To change the admin password use the following command:

```
>>> python manage.py changepassword admin
```
    
Note that you need to edit the file  settings/local_env.py with :

    * Database credentials
    * Twitter app cosumer key and secret


To execute scheduled tasks, celery needs to be running (rabbitmq required):

```
>>> python manage.py celery worker -Q djsocial -B -E --loglevel=INFO
```

    
Contributors
-----

    * Mo Mughrabi - Lead developer
    * Ahmed Elhamidi - Developer
    * Mariusz Kosakowski - Developer


