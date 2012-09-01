Guide: Script to Production
===========================


Introduction
------------
This is a pretty simple yet extensive tutorial on how to go from a simple Python script to a full-functioning production-ready web application. We'll be creating a simple application that allows an end-user to search for a user in Facebook's graph API and store that user's information. We'll also provide some simple API routes to display all users and get any user's information. Finally, we'll have a backend job that periodically hits Facebook to update all the information in our database.

The tools that we'll be using are:

* Django as the web framework
* Postgres as the persistent storage (database)
* Celery as the job queue
* RabbitMQ as the broker for Celery
* Git as the version control system
* Heroku as the production platform


Install Python, Pip, and Venv
-----------------------------
Obviously, to start a Django project, you need to have Python installed. This requires [Homebrew](https://github.com/mxcl/homebrew/wiki/installation), which should already be installed. We're also going to install [Pip](http://pypi.python.org/pypi/pip), which is an easy way to install the Python packages we'll need later. Finally, we're going to install [VirtualEnv](http://pypi.python.org/pypi/virtualenv), which creates an isolated Python environment for our Django project. This is important because we know that our code will work with a particular version of Python (the one we are currently using). It makes sure the code in our project doesn't break when we inevitably do machine-wide Python updates some time in the future.

First, open up a terminal.

This installs Homebrew:

	$ ruby <(curl -fsSkL raw.github.com/mxcl/homebrew/go)

This installs Python:

	$ brew install python

This adds Python to your PATH environment variable so you can run python commands from the terminal. Note that this is is not permanent, and you'll have to re-add it each time you restart the terminal, open up a new terminal window, or log out. To permanently add it to $PATH, you'll need to modify your .bashrc (see appendix for instructions).

	$ export PATH=/usr/local/share/python:$PATH

This installs Pip:

	$ easy_install pip

This installs Venv:

	$ pip install virtualenv


Request a Heroku Application and a Git Repository
-------------------------------------------------
Both a production-scale Heroku app and a private Git repo cost money, so you're going to have to ask Will to set one of those up for you with the proper tools installed.


Set up Version Control with Git
-------------------------------
Git is an awesome and powerful version control system that saves snapshots of your code's history. It's like having a bunch of save states that you can jump to whenever you want, and it also allows you to collaborate with other people without having to worry about messing up each other's code. A repository also serves as a backup for your code, so if your computer crashes or somehow gets destroyed, you'll still have a remote version of your code that you can retrieve. For a brief introduction to Git, there's a tutorial in the appendix.

Go to your home directory:

	$ cd ~

Clone the Github repo to your local machine. This copies everything in the remote Github repo to a directory called django-tutorial in the current directory (which should be your home directory) on your local machine:

	$ git clone git@github.com:Adaptly/django-tutorial.git

Finally, set up your .gitignore file, which resides in the same level as your .git directory (i.e., your project directory, so if you ls -al, you should see both the .git folder and the .gitignore file). The .gitignore file makes sure your useless build artifacts and other non-project-specific files aren't tracked. In .gitignore, add the following lines:

	venv
	*.pyc


Set up the Project
------------------
Now, we're going to set up the Django project. You can call it whatever you want, but ideally you'll give it the same name that Will gives the Heroku app to avoid any confusion down the line. In this tutorial, we called our project django-tutorial (when we made our git repo). Within the project, we can make one or more Django apps. In most cases, you'll just want one. I'm going to call the application we're going to make testdjango, but you'll probably want to give yours a more descriptive name whenever you make your own project.

Go to your project directory:

	$ cd ~/django-tutorial

Create a virtual Python environment for your project. This makes a venv directory that has all the Python environment files:

	$ virtualenv venv --distribute

Modify your $PATH environment variable to use the new Python environment instead of your machine's:

	$ source venv/bin/activate

Install Django, psycopg2 (Django's Postgres adapter), and dj-database-url (makes it easier to configure the database with Heroku)

	$ pip install Django psycopg2 dj-database-url

Create your Django application in the project directory:

	$ django-admin.py startproject testdjango .

Add your application to your application settings. In testdjango/settings.py:

	```python
	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    'django.contrib.staticfiles',
	    'testdjango',
	    # Uncomment the next line to enable the admin:
	    # 'django.contrib.admin',
	    # Uncomment the next line to enable admin documentation:
	    # 'django.contrib.admindocs',
	)
	```

Test to make sure the development server works:

	$ python manage.py runserver


Set up the Database with Postgres
---------------------------------
We're going to use Postgres for our database. Databases are great because they're the best way to quickly store, organize, and retrieve tons of information. They're like huge spreadsheets that don't suck. Each database is composed of tables, each of which is used to store information about something (e.g. a car company may have a car table, a customers table, an employees table, and a transactions table). Each table has a schema, which is composed of the columns that make up the table (e.g. for the car table, it could have a car name column, a quantity column, and a price column) and the data types of the columns (e.g. for that same table, the car name would be a string, or VARCHAR, the quantity would be an integer, and the price would be a float or decimal), as well as things like primary and foreign keys that you don't really have to worry about yet. Each table is used to store data in the form of tuples (or records). For example, the car table could have the tuple (2007 Honda Civic, 20, 15000.00). For this tutorial, you don't need to know SQL, but it's highly recommended that you learn it. Go to the appendix for a list of a few quick Postgres commands.

Postgres should already be installed, but if it isn't:

	$ brew install postgresql

Create a local development database (your Heroku app should already come with a production database so you don't need to worry about that):

	$ created testdjango_development

Make sure your application settings knows about the database. In testdjango/settings.py:

	```python
	import dj_database_url
	...
	DATABASES = {'default': dj_database_url.config(default='postgres://:@localhost:5432/testdjango_development')}
	```

This should replace the current DATABASES environment variable in settings.py. The structure should be:

	default='postgres://{USER}:{PASSWORD}@localhost:{PORT}/{NAME}'

So, in our example, we're using the testdjango_development database with no user and password on port 5432.


Deploy to Heroku
----------------
Heroku is an online web service that runs your production application (kind of like a server). Whereas your development application will be run locally, your production application will live on Heroku.

Add the following to your .git/config file:

	[remote "heroku"]
	        url = git@heroku.com:{app_name}.git
	        fetch = +refs/heads/*:refs/remotes/heroku/*

Log into Heroku:

	$ heroku login

There are two important files that should be in your project directory that Heroku uses.

* Procfile: Heroku uses this to alias certain commands to processes. You will be using the processes you define in this file to use Heroku workers to run whatever commands you alias.
* requirements.txt: Heroku uses this to determine what libraries and dependencies need to be installed. Every time you push to Heroku, it will look at requirements.txt and install all the listed dependencies. For example, so far, we're using Django, psycopg2, and dj-database-url on our local machine, so we need to make Heroku install those as well.

Create an empty file in your project directory called Procfile.

Create a file in your project directory called requirements.txt:

	Django==1.4.1
	amqplib==1.0.2
	anyjson==0.3.3
	billiard==2.7.3.12
	celery==3.0.8
	distribute==0.6.27
	dj-database-url==0.2.1
	django-celery==3.0.6
	gunicorn==0.14.6
	psycopg2==2.4.5
	python-dateutil==1.5
	pytz==2012d
	wsgiref==0.1.2

Install all packages that haven't been installed yet:

	$ pip install -r requirements.txt

If you want to add any packages to that in the future, just add the package to your requirements.txt and run the same command. Alternatively, you can run the following, which installs the package and writes all of the packages currently managed by pip to your requirements.txt file:

	$ pip install {package}
	$ pip freeze > requirements.txt

Deploy your application to Heroku:

	$ git add .
	$ git commit -m "Set up the project and application with Postgres. Created an empty Procfile and a requirements.txt with all necessary dependencies."
	$ git push heroku master

Check that everything is working. This gives you a list of currently running processes. Eventually, we'll have 3 processes: one for the web application, one for the celery worker that runs our background job, and one for celerybeat, which schedules the periodic tasks the celery worker performs.

	$ heroku ps --app django-tutorial

This shows you the logs on Heroku (in case something bad happens):

	$ heroku logs --app django-tutorial

You can also get real-time updates by using tail:

	$ heroku logs --tail --app django-tutorial

And you can follow a specific process:

	$ heroku logs --tail --ps {job_name} --app django-tutorial


Set up the Production Server with GUnicorn
------------------------------------------
Heroku will use this as the server for your web pages. It will handle requests whenever someone tries to access your web pages or hit your API routes. It's the first of the three Heroku processes that we're going to set up.

You should've already installed GUnicorn in the previous step, so now we need to make sure Django knows to use it. In testdjango/settings.py, add the following to the INSTALLED_APPS variable:

	'gunicorn',

Add the following line to your empty Procfile:

	web: gunicorn testdjango.wsgi -b 0.0.0.0:$PORT

This aliases the command gunicorn testdjango.wsgi -b 0.0.0.0:$PORT to the continuous process "web," which you will tell a separate Heroku worker to execute.

Check that your process can run locally:

	$ foreman start

Then, push to Heroku, which will automatically start the web process:

	$ git add .
	$ git commit -m "Added GUnicorn to the project."
	$ git push heroku master
	$ heroku 


Set up your Background Jobs with Celery and RabbitMQ
----------------------------------------------------
Celery is queuing and messaging service that lets you easily manage background jobs. RabbitMQ is the broker (queuing and messaging system system) that we're going to use with Celery that makes it really easy to manage the job queues and specific tasks (especially on Heroku). The processes that we'll be running are celeryd, which is the Celery worker that executes our background tasks, and celerybeat, which schedules those tasks. These are second and third of the three Heroku processes that we're going to use.

You should've already installed Celery as well, so again, we need to make sure Django knows to use it. In testdjango/settings.py, add the following to the INSTALLED_APPS variable:

	'djcelery',

Now, let's install RabbitMQ locally (it should already be installed on your Heroku app, so you don't have to worry about adding it to requirements.txt or anything).

	$ brew install rabbitmq

WARNING: RabbitMQ is not managed by pip, so whenever you want to work on the project locally from a different computer, you have to run:

	$ brew install rabbitmq

in addition to:

	$ pip install -r requirements.txt

Whenever you install RabbitMQ, it comes with a default administrative user whose settings are:

* User: guest
* Password: guest
* VHost (queue): /

This should be fine for our purposes, but if you want to make more users or queues, in a separate tab:

	$ rabbitmqctl add_user {username} {password}
	$ rabbitmqctl add_vhost {vhost_name}
	$ rabbitmqctl set_permissions -p {vhost_name} {username} ".*" ".*" ".*"

You can also list users, vhosts, and permissions. See the [RabbitMQ Documentation](http://www.rabbitmq.com/man/rabbitmqctl.1.man.html) for more info.

You may need to add /usr/local/sbin to your $PATH variable if you get one of these errors:

	-bash: rabbitmqctl: command not found
	-bash: rabbitmq-server: command not found

Solution:

	$ export PATH=/usr/local/sbin:$PATH

Add the following line to the bottom of the same file. This says that Celery is going to use RabbitMQ as its broker with the default settings defined above (username is guest, password is guest, vhost is '/', server is localhost, and port is 5672):

	BROKER_URL = 'amqp://guest:guest@localhost:5672//'

Now, you can run stuff locally. In three separate tabs, run these three commands:

	$ rabbitmq-server
	$ python manage.py celeryd
	$ python manage.py celerybeat

To get this running on Heroku, first, find out what the BROKER_URL is.

	$ heroku config --app django-tutorial
	=== django-tutorial Config Vars
	CLOUDAMQP_URL:              amqp://appNUMBERS_heroku.com:STUFF@NAME.cloudamqp.com/appNUMBERS_heroku.com

Make a file in your testdjango directory called production_settings.py:

	```python
	DEBUG = False
	TEMPLATE_DEBUG = False
	BROKER_URL = '{Get this from CLOUDAMQP_URL}'
	```

Then, add the following lines to the VERY bottom of testdjango/settings.py (you want to make sure the import overwrites all variables defined in the file):

	```python
	if 'heroku' in os.environ['_']:
	    from production_settings import *
	```

You'll also need to add the templates 404.html and 500.html to your templates directory. You can copy those over from the code that I have.

Add the following lines to your Procfile:

	celeryd: python manage.py celeryd -E -B --loglevel=INFO
	celerybeat: python manage.py celerybeat

These alias the Django commands to run the celery worker and the celerybeat scheduling service to the continuous processes "celery" and "celerybeat," respectively.

Sync the development database to use the Celery tables:

	$ python manage.py syncdb

Commit and push to heroku:

	$ echo celerybeat-schedule >> .gitignore
	$ git add .
	$ git commit -m "Added Celery with RabbitMQ"
	$ git push heroku master

Sync the production database to use the Celery tables:

	$ heroku run python manage.py syncdb --app django-tutorial

Try scaling up the workers. Initially, you'll have 0 workers running for your newly defined celeryd and celerybeat processes (but you should still have your gunicorn web worker, defined previously, running).

	$ heroku ps:scale celeryd=1 --app django-tutorial
	$ heroku ps:scale celerybeat=1 --app django-tutorial
	$ heroku ps


Appendix
--------

Notes
-----
pip install -r requirements.txt
brew install rabbitmq

Updating .bashrc
----------------

Git Tutorial
============
Initializing
------------
Go to your home directory:

	$ cd ~

Make a directory for the project:

	$ mkdir django-tutorial
	$ cd django-tutorial

This makes a Git repository in your current directory:

	$ git init

It makes a hidden .git folder in your current directory where all the Git goodies are stored. To remove a git repository, just delete the .git folder:

	$ rm -r .git

In the file .git/config, add the following lines:

	[remote "origin"]
	        url = git@github.com:Adaptly/test-django.git
	        fetch = +refs/heads/*:refs/remotes/origin/*

config is the configuration file Git looks at whenever you execute git commands. It aliases a bunch of commands so you only have to type

	$ git fetch origin

instead of

	$ git fetch git@github.com:Adaptly/test-django.git

"Remote" means the remote repository you push your code to or pull/fetch your code from. For our project, we'll have two remotes: Github and Heroku.


Fetching and Branching
----------------------
Now that you've properly configured your .git/config file, you can fetch the contents of your Github repo. Fetch basically grabs the contents of your remote repository and rebasing puts whatever changes you made on top of those contents. Notice that below, we specify the branch we rebase off of as well (in this case, master). That means, we take all of the code currently in the master branch of the repository (as opposed to any other branch). If you run into any merge conflicts, talk to Will.

	$ git fetch origin
	$ git rebase origin/master

Some more about branching: you make a new branch whenever you want to make some changes to your current code but you don't want to accidentally mess up anything in the main branch (maybe the main branch is currently being used in production or something).
To see the branch you are currently on (right now, this should say master):

	$ git status

To switch to a branch (this switches to the master branch, which is the main branch):

	$ git checkout master

To create a new branch off of the branch you're currently on (note that this branches off your current branch, which is not necessarily master):

	$ git checkout -b new_branch

To see all the branches you have on your local machine:

	$ git branch

To delete a branch, first switch back to master, and then delete:

	$ git checkout master
	$ git branch -D new_branch

Let's make a new branch again, change some stuff, and merge it into master:

	$ git checkout -b another_branch

Adding and Committing
---------------------

Make a new file called stuff.txt and add some stuff:

	Hello, world!

Now, you can see that Git recognizes that there's a new file:

	$ git status

In Git, there are three categories of files: untracked, not staged, and staged. 

* Untracked files are files that Git doesn't do anything with (e.g. if you make a new file, Git won't track it until you explicitly tell it to). Right now, stuff.txt is untracked.
* Not staged file are files that Git is currently tracking that you've changed somehow from what Git last remembers - the most recent commit. (e.g. if you make changes or delete a file that Git is tracking, Git will recognize that you've changed it or deleted it).
* Staged files are files that are ready to be committed. You add both untracked and not staged files to staging so you can commit them. A commit is basically a snapshot of your code.

Most of the time, you'll just add all of the changes to staging:

	$ git add .

But sometimes, you'll want to commit some changes but not others. In this case, you selectively add the files you want to stage:

	$ git add stuff.txt

If you want to undo this (unstage all files or unstage stuff.txt):

	$ git reset HEAD
	$ git reset HEAD stuff.txt

If you want to undo the changes you've made to a particular file:

	$ git checkout -- filename

If you want to delete an untracked file just remove it normally:

	$ rm filename

If you want to delete a tracked file, make sure you delete it via git:

	$ git rm filename

When you've added all the changes that you want, you can commit:

	$ git commit

This will prompt you to enter a commit message. Make it descriptive so that when you're looking back through your changes, you have a good idea of what changes you made and when. This shortcut lets you specify the commit message in the command:

	$ git commit -m "My commit message."

And this shortcut automatically stages all not staged (but not untracked!) files and commits them:

	$ git commit -a
	$ git commit -am "My commit message."

To see a list of all the changes (commits) that have been made to your code:

	$ git log

To revert your code to a previous state, do a reset. Your current changes will still be present but not committed, so you can just revert the changes as shown above:

	$ git reset {hash that you get from the commit log}

Pushing and Merging
-------------------
Now, you can push your changes to your remote repository. -u says to create the branch upstream (since it doesn't exist in your remote repository - in this case, Github - yet). If the branch was already there and you're pushing again, you wouldn't need the -u. origin specifies the remote repository (remember, we set origin to Github in our .git/config file). another_branch is the branch you're pushing from on your local machine:

	$ git push -u origin another_branch

Now, you should be able to see a new branch called another_branch on Github with your changes. You can merge those changes on Github or on your local machine. If you merge them on Github, be sure to keep your local master branch up to date by switching back to master and doing a fetch and rebase:

	$ git checkout master
	$ git fetch origin
	$ git rebase origin/master

If you merge the changes on your local machine, first switch to your local master branch and make sure it's up to date. Then, push from your master branch to your remote (Github) to make sure the remote's master branch is up to date.

	$ git checkout master
	$ git merge another_branch
	$ git push origin master

That was a quick and dirty introduction to Git, but there's a lot more that it has to offer. There are many awesome [Git tutorials](http://sixrevisions.com/resources/git-tutorials-beginners/) online if you want to learn more.


Postgres Commands
-----------------
Here are a few commands to help you navigate your database (some are Postgres-specific):

Create the database:

	$ createdb database_name

Delete the database:

	$ dropdb database_name

Open up the database:

	$ psql database_name

Display all of the tables in your database:

	\d

Look at the table schema for a particular table:

	\d tablename

Select all records from a particular table:

	SELECT * FROM {table name};

Select the number of records from a particular table:

	SELECT COUNT(*) FROM {table name};

Select the first 5 records from a particular table:

	SELECT * FROM {table name} limit 5;

Select a single column for all records from a particular table:

	SELECT {column name} FROM {table name};

Select Bob's records from a particular table with a column called name:

	SELECT * FROM {table name} WHERE name = 'Bob';

Select all records where the count is greater than 100 from a particular table with a column called count;

	SELECT * FROM {table name} WHERE count > 100;

Select the 10 records with the greatest count from a particular table with a column called count:

	SELECT * FROM {table name} ORDER BY count DESC LIMIT 10;

Select the 10 records with the lowest count from a particular table with a column called count:

	SELECT * FROM {table name} ORDER BY count ASC LIMIT 10;

Delete all the records from a particular table:

	DELETE FROM {table name};

Drop (delete) a particular table:

	DROP TABLE {table name};

Toggle the display between normal and extended mode. Extended mode gives you a prettier look at records in your database:

	\x

Exit the database:

	\q
