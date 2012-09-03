Guide: Script to Production
===========================
Index
-----
* [Introduction](#introduction)
* [Install Python, Pip, and Venv](#installpython)
* [Request a Heroku Application and a Git Repository](#requestapps)
* [Set up Version Control with Git](#git)
* [Set up the Project](#startproject)
* [Install Dependencies](#installdependencies)
* [Set up the Database with Postgres (Local)](#postgres)
* [Set up the Background Jobs with Celery and RabbitMQ (Local)](#celery)
* [Write an Application with Django](#django)
* [Deploy to Heroku](#heroku)
* [Set up the Processes (GUnicorn Server, Celeryd Worker, Celerybeat Scheduler)](#processes)
* [Appendix](#appendix)
	* [Troubleshooting](#troubleshooting)
	* [How to continue working on your project on a different computer](#setup)
	* [How to update your .bash_profile to run commands when you get the -bash: command not found error](#updatingbashprofile)
	* [A quick introduction to git](#gittutorial)
	* [A small Postgres reference](#postgrescommands)
	* [Code used in the guide](#code)
		* [models.py](#models.py)
		* [views.py](#views.py)
		* [add_user_form.html](#add_user_form.html)
		* [tasks.py](#tasks.py)

<a name="introduction">Introduction</a>
-------------------------------------
This is a pretty simple yet extensive tutorial on how to go from a Python script that you want to run automatically every so often to a full-functioning production-ready web application. We'll be creating a small application that allows a client to search for a user in Facebook's graph API and store that user's information. We'll also provide some simple API routes to display all users and get any given user's information. Finally, we'll have a backend job that periodically hits Facebook to update all the information in our database.

The tools that we'll be using are:

* [**Django**](https://www.djangoproject.com/) as the web framework
* [**Postgres**](http://www.postgresql.org/) as the persistent storage (database)
* [**Celery**](http://celeryproject.org/) as the job queue
* [**RabbitMQ**](http://www.rabbitmq.com/) as the broker for Celery
* [**Git**](https://github.com/) as the version control system
* [**Heroku**](http://www.heroku.com/) as the production platform


<a name="installpython">Install Python, Pip, and Venv</a>
-------------------------------------------------------
Obviously, to start a Django project, you need to have Python installed. This requires [Homebrew](https://github.com/mxcl/homebrew/wiki/installation), which should already be installed. We're also going to install [Pip](http://pypi.python.org/pypi/pip), which is an easy way to install the Python packages we'll need later. Finally, we're going to install [VirtualEnv](http://pypi.python.org/pypi/virtualenv), which creates an isolated Python environment for our Django project. This is important because we know that our code will work with a particular version of Python (the one we are currently using). It makes sure the code in our project doesn't break when we inevitably do machine-wide Python updates some time in the future. First, open up a terminal.

This installs Homebrew:

	$ ruby <(curl -fsSkL raw.github.com/mxcl/homebrew/go)

This installs Python:

	$ brew install python

This adds Python to your PATH environment variable so you can run python commands from the terminal. Note that this is is not permanent, and you'll have to re-add it each time you restart the terminal, open up a new terminal window, or log out. To permanently add it to $PATH, you'll need to modify your .bash_profile (see [appendix](#updatingbashprofile) for instructions).

	$ export PATH=/usr/local/share/python:$PATH

This installs Pip:

	$ easy_install pip

This installs Venv:

	$ pip install virtualenv


<a name="requestapps">Request a Heroku Application and a Git Repository</a>
-------------------------------------------------------------------------
Both a production-scale Heroku app and a private Git repo cost money, so you're going to have to ask Will to set one of those up for you with the proper tools installed.


<a name="git">Set up Version Control with Git</a>
-----------------------------------------------
Git is an awesome and powerful version control system that saves snapshots of your code's history. It's like having a bunch of save states that you can jump to whenever you want, and it also allows you to collaborate with other people without having to worry about messing up each other's code. A repository also serves as a backup for your code, so if your computer crashes or somehow gets destroyed, you'll still have a remote version of your code that you can retrieve. For a brief introduction to Git, there's a tutorial in the [appendix](#gittutorial).

Note that this assumes you already have a Github account. If you don't, follow [this simple 2-minute guide](#https://help.github.com/articles/set-up-git).

Go to your home directory:

	$ cd ~

Clone the Github repo to your local machine. This copies everything in the remote Github repo called {github_repo} to a directory with the same name in the current directory (which should, at the moment, be your home directory) on your local machine:

	$ git clone git@github.com:{github_repo}.git

If Will just made the repo for you, it should be completely empty except for possibly a README.md file and a .gitignore file. For this tutorial, I'm just going to clone the Adaptly/django-tutorial repo, which will make ~/django-tutorial the root project directory. You won't want to do this, however, because the repo already has a full-functioning Django project! Be sure to either clone over the repo that Will made you or make a new repo on Github and clone that.

Finally, set up your .gitignore file, which resides in the same level as your .git directory (i.e., your project directory, so if you ls -al, you should see both the .git folder and the .gitignore file). The .gitignore file makes sure your useless build artifacts and other non-project-specific files aren't tracked. In .gitignore, add the following lines:

	venv
	*.pyc


<a name="startproject">Set up the Project</a>
-------------------------------------------
Now, we're going to set up the Django project. In this tutorial, we called our root project directory django-tutorial (when we made our git repo). Within the root project directory, we can start a Django project. I'm going to call the project we're going to make testdjango, but you'll probably want to give yours a more descriptive name whenever you make your own project (or give it the same name as your main project directory). Then, we're going to make an application for that project. Each project can have one or more applications, but we'll just make one for our purposes. We'll call it facebookgraph because it hits Facebook's Graph API and pulls user data from that.

Go to your root project directory:

	$ cd ~/django-tutorial

Create a virtual Python environment for your project. This makes a venv directory that has all the Python environment files:

	$ virtualenv venv --distribute

This "activates" the virtual environment so that you're running the isolated version of Python:

	$ source venv/bin/activate

To "deactivate" the virtual environment do the following (or just close the window or log out):

	$ deactivate

**IMPORTANT:** Every time you want to work on your project, when you go into the root project directory, you have to load up the virtual environment (it doesn't do this for you automatically, unlike with Rails).

Install Django, psycopg2 (Django's Postgres adapter), and dj-database-url (makes it easier to configure the database with Heroku)

	$ pip install Django psycopg2 dj-database-url

Start your Django project in the root project directory (don't forget the period):

	$ django-admin.py startproject testdjango .

Now, you can make an application for the project:

	$ mkdir testdjango/facebookgraph
	$ python manage.py startapp facebookgraph testdjango/facebookgraph

Add your application to your project settings. In testdjango/settings.py:

	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    'django.contrib.staticfiles',
	    'testdjango/facebookgraph',
	    # Uncomment the next line to enable the admin:
	    # 'django.contrib.admin',
	    # Uncomment the next line to enable admin documentation:
	    # 'django.contrib.admindocs',
	)

Test to make sure the development server works:

	$ python manage.py runserver


<a name="installdependencies">Install Dependencies (Local)</a>
------------------------------------------------------------
Now, we want to make sure everything we're going to need later is installed on our local machine. Make a file in your root project directory (it should live in ~/django-tutorial) called requirements.txt:
	
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

Install all packages that haven't been installed yet. This uses pip to install everything in your requirements.txt file:

	$ sudo pip install -r requirements.txt

If you want to add any packages to that in the future, just add the package to your requirements.txt and run the same command. Alternatively, you can run the following, which installs the package and writes all of the packages currently managed by pip to your requirements.txt file:

	$ pip install {package}
	$ pip freeze > requirements.txt

Also, there are two more things you need to install that aren't managed by pip.

* Postgres:

	$ brew install postgresql

* RabbitMQ:

	$ brew install rabbitmq

**REMINDER:** If you want to work on a project on another computer, you're going to have to re-run this entire process, as well as a few other commands. See the [appendix](#setup) for details.


<a name="postgres">Set up the Database with Postgres (Local)</a>
--------------------------------------------------------------
We're going to use Postgres for our database. Databases are great because they're the best way to quickly store, organize, and retrieve tons of information. They're like huge spreadsheets that don't suck. Each database is composed of tables, each of which is used to store information about something (e.g. a car company may have a car table, a customers table, an employees table, and a transactions table). Each table has a schema, which is composed of the columns that make up the table (e.g. for the car table, it could have a car name column, a quantity column, and a price column) and the data types of the columns (e.g. for that same table, the car name would be a string, or VARCHAR, the quantity would be an integer, and the price would be a float or decimal), as well as things like primary and foreign keys that you don't really have to worry about yet. Each table is used to store data in the form of tuples (or records). For example, the car table could have the tuple ('2007 Honda Civic', 20, 15000.00). For this tutorial, you don't need to know SQL, but it's highly recommended that you learn it. Go to the [appendix](#postgrescommands) for a list of a few quick Postgres commands.

Create a local development database (your Heroku app should already come with a production database so you don't need to worry about that):

	$ createdb testdjango_development

Make sure your application settings knows about the database. In testdjango/settings.py:

	import dj_database_url
	...
	DATABASES = {'default': dj_database_url.config(default='postgres://:@localhost:5432/testdjango_development')}

This should replace the current DATABASES environment variable in settings.py. For reference, the structure should be:

	default='postgres://{USERNAME}:{PASSWORD}@localhost:{PORT}/{NAME}'

So, in our example, we're using the testdjango_development database with no user and password on port 5432.


<a name="celery">Set up the Background Jobs with Celery and RabbitMQ (Local)</a>
------------------------------------------------------------------------------
Celery is a service that lets you easily manage background jobs. RabbitMQ is the broker (queuing and messaging system) that we're going to use with Celery that makes it really simple to manage the job queues and specific tasks (especially on Heroku). The processes that we'll be running are celeryd, which is the Celery worker that executes our background tasks, and celerybeat, which schedules those tasks.

You should've already installed Celery so again, we need to make sure Django knows to use it. In testdjango/settings.py, add the following to the INSTALLED_APPS variable:

	'djcelery',

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

Temporary solution (for a permanent solution, see the [appendix](#updatingbashprofile)):

	$ export PATH=/usr/local/sbin:$PATH

Add the following line to the bottom of settings.py. This says that Celery is going to use RabbitMQ as its broker with the default settings defined above (username is guest, password is guest, vhost is '/', server is localhost, and port is 5672):

	BROKER_URL = 'amqp://guest:guest@localhost:5672//'

For reference, the BROKER_URL is in the format

	BROKER_URL = 'amqp://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{VHOST}'

Now, you can run stuff locally. In four separate terminal windows, run these commands:

	$ rabbitmq-server
	$ python manage.py runserver
	$ python manage.py celeryd
	$ python manage.py celerybeat

This doesn't do anything yet, but you'll be making use of these processes in the near future.

Sync the development database to use the Celery tables:

	$ python manage.py syncdb


<a name="django">Write an Application with Django</a>
--------------------------------------------------
In this section, I will give you a brief overview of creating a full-functioning Django application. Django is a lightweight web framework (sort of like Rails, but much lighter) that makes it easy to develop web applications. This is not at all meant to be a full guide. Rather, it's a brief introduction to show you how easy it is to quickly get something up and running. I **strongly** encourage you to check out the [Django tutorial](http://www.djangobook.com/en/1.0/), which is extremely comprehensive and very straightforward and easy to understand.

Previously, you made your Django app (called facebookgraph). Now, we're going to actually add functionality to that. Take a look at your project directory (testdjango):

	$ cd ~/django-tutorial/testdjango && ls
	__init__.py	facebookgraph	settings.py	urls.py		wsgi.py

* **facebookgraph:** This is your application's directory. It contains all your application-specific code.
* **settings.py:** This is your project's settings file. Whenever you add applications or packages to your project, you have to update this file.
* **urls.py:** This file lists all the project's routes a user can hit.
* **wsgi.py:** This is the interface between the web server and your Django application. You don't need to mess with this.

Take a look at your application directory:

	$ cd ~/django-tutorial/testdjango/facebookgraph && ls
	__init__.py	models.py	tests.py	views.py

* **models.py:** This defines all of the models your application will use. Models are Django's object representation of database tables. They're what you're going to be using to store your data.
* **tests.py:** This is if you want to write some tests for your app (highly recommended, but not covered here).
* **views.py:** This defines all of the views your applications will use. Views are Django's way of dynamically handling user requests. Each route defined in urls.py will be linked to a specific function in views.py that handles the request to that route.

Here's an outline of what we're going to do:
1. [Make a FacebookUser model that mirrors the responses that we get from the Facebook Graph](#djangopt1)
2. [Make a view that lets the user search for a Facebook user and add that user to the database](#djangopt2)
3. [Make a template to render that view](#djangopt3)
4. [Make API routes that show all users in our database and the information for a specific user](#djangopt4)
5. [Make a background task that keeps our database up-to-date by periodically calling the Facebook Graph API](#djangopt5)

<a name="djangopt1">**Making a FacebookUser Model**</a>

1. Copy the code in django-tutorial/testdjango/facebookgraph/models.py into your own models.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#models.py).
2. Sync the model with the database (NOTE: The first time you run syncdb, it's going to ask you to create a superuser. This isn't necessary, but you can do it if you want to use the [Admin interface](https://docs.djangoproject.com/en/dev/ref/contrib/admin/), which is a nice GUI that you can use to manage your site. I won't cover it here).

		python manage.py syncdb

<a name="djangopt2">**Making an Add User View**</a>

1. Copy the add_user function and the two helper functions (retrieve_facebook_user_data and add_user_to_db) in django-tutorial/testdjango/facebookgraph/views.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#views.py).
2. Add the following to the urlpatterns tuple in testdjango/urls.py:

		url(r'^add_user/$', add_user),

This says that if someone hits the url http://yourbaseurl/add_user, it will handle the response using the add_user function in views.py. The r means raw string (the string will be treated literally), so you don't have to escape special characters. The '^' means match all characters before the string (which, in this case, is nothing - just the root directory '/' which is automatically prepended) and the '$' means stop matching any characters after the string. For example, if you didn't include the $, then the url below would match routes like base_url/add_user/bob and base_url/add_user/1234 as well. [This](http://www.djangobook.com/en/1.0/chapter03/) is a good resource to learn more about urls.py.

<a name="djangopt3">**Making an Add User Template**</a>

1. Make a templates directory in your project directory (testdjango):

		$ cd ~/django-tutorial/testdjango
		$ mkdir templates

2. Copy the code in django-tutorial/testdjango/templates/add_user_form.html. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#add_user_form.html).
3. Update your testdjango/settings.py file. Add this to the top:

		import os

4. Update the TEMPLATE_DIRS variable in testdjango/settings.py:

		TEMPLATE_DIRS = (
	    	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	    	# Always use forward slashes, even on Windows.
	    	# Don't forget to use absolute paths, not relative paths.
	    	os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
		)

5. Start up the development server in a new terminal window:

		$ cd ~/django-tutorial
		$ python manage.py runserver

6. Hit the route to see it in action. In a web browser, go to the address localhost:8000/add_user. Try adding the users 'Coca-Cola' and 'Pepsi.'

<a name="djangopt4">**Making API Routes**</a>

1. Copy the show_all_users function in django-tutorial/testdjango/facebookgraph/views.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#show_all_users).
2. Add the following to the urlpatterns tuple in testdjango/urls.py:

		url(r'^all_users/$', show_all_users),
This says that if someone hits the url http://yourbaseurl/all_users, it will handle the response using the show_all_users function in views.py.

3. Hit the route to see it in action. In a web browser, go to the address localhost:8000/all_users
4. Copy the show_user_info function in django-tutorial/testdjango/facebookgraph/views.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#show_user_info).
5. Add the following to the urlpatterns tuple in testdjango/urls.py:

		url(r'^users/([^/]+)/$', show_user_info),
This says that if someone hits the url http://yourbaseurl/users/{username}, it will handle the response using the show_user_info function in views.py. The regex means accept all input strings of one or more characters that don't include a '/'. The regex is automatically passed as the second parameter to the function show_user_info. Again, [this](http://www.djangobook.com/en/1.0/chapter03/) is a good resource to learn more about regex in urls.py.

6. Hit the route to see it in action. In a web browser, go to the address localhost:8000/users/coca-cola.

<a name="djangopt5">**Making an Update User Background Task**</a>

1. Copy the code in django-tutorial/testdjango/facebookgraph/tasks.py. The code along with a brief explanation that you should definitely look at is in the [appendix](#tasks.py).
2. Comment out the run every 10 minutes line and uncomment the run every 3 seconds line:

		#@periodic_task(run_every=crontab(minute="*/10"))
		@periodic_task(run_every=timedelta(seconds=3))

3. In four separate terminal windows, run these three commands:

		$ rabbitmq-server
		$ python manage.py runserver
		$ python manage.py celeryd
		$ python manage.py celerybeat

4. Now you should be able to see realtime updates to your database information. In a web browser, go to the address localhost:8000/users/coca-cola and keep refreshing the page.
5. Shut down your worker processes and re-comment the task settings (you don't want to hit your rate limits):

		@periodic_task(run_every=crontab(minute="*/10"))
		#@periodic_task(run_every=timedelta(seconds=3))

Congratulations, you've made your web application! Locally, you should be able to add users to your database, view user information, and automatically periodically update that information. Hopefully, you understand all the code here. If not, you *really* should look at the code section of the [appendix](#code). *Seriously.* Now, it's time to put our app into production.


<a name="heroku>Deploy to Heroku</a>
----------------------------------
Heroku is an online web service that runs your production application. Whereas your development application will be run locally, your production application will live on Heroku.

Add the following to your .git/config file:

	[remote "heroku"]
	        url = git@heroku.com:{app_name}.git
	        fetch = +refs/heads/*:refs/remotes/heroku/*

Your Heroku application should've already been created in the section [Request a Heroku Application and a Git Repository](#requestapps), so here, {app_name} is just the name of that application. In my case, the application name is django-tutorial, but yours should be different. If you try to set your "heroku" remote url to git@heroku.com:django-tutorial.git, you won't be able to push to it because you won't have the necessary permissions.

Log into Heroku:

	$ cd ~/django-tutorial
	$ heroku login

There are two important files that should be in your project directory that Heroku uses.

* **Procfile**: Heroku uses this to alias certain commands to processes. You will be using the processes you define in this file to use Heroku workers to run whatever commands you alias.
* **requirements.txt**: Heroku uses this to determine what libraries and dependencies need to be installed. Every time you push to Heroku, it will look at requirements.txt and install all the listed dependencies. For example, so far, we're using Django, psycopg2, and dj-database-url on our local machine, so we need to make Heroku install those as well.

Create an empty file in your projectroot directory called Procfile.

Make sure your requirements.txt looks like this:

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

	$ sudo pip install -r requirements.txt

Check if you have an SSH key (you should already if you've come this far):

	$ ls ~/.ssh/

If you see id_rsa and id_rsa.pub, then you already have an ssh key. If not, generate one:

	$ ssh-keygen -t rsa -C {key_name}

Add it to your Heroku application:

	$ heroku keys:add

To see a list of the SSH keys tied to an account:

	$ heroku keys --long

To remove a key:

	$ heroku keys:remove {key_name}

Because of the way Heroku's SSH system is set up, you might have problems if you have more than one Heroku account. If you're having problems, read [this](http://martyhaught.com/articles/2010/12/14/managing-multiple-heroku-accounts/).

Deploy your application to Heroku:

	$ git add .
	$ git commit -m "Set up the project and application with Postgres. Created an empty Procfile and a requirements.txt with all necessary dependencies."
	$ git push heroku master

Check that everything is working. This gives you a list of currently running processes. Eventually, we'll have 3 processes: one for the web application, one for the celery worker that runs our background job, and one for celerybeat, which schedules the periodic tasks the celery worker performs. The --app parameter specifies the application name. Again, your application won't be called django-tutorial, so just replace that with whatever your app is called. Note that shouldn't have to specify the --app parameter if you've been following along with the tutorial. This is because we've added the Heroku remote to our .git/config file, and we only have one Heroku remote, so it recognizes that application whenever we run any Heroku command.

	$ heroku ps --app django-tutorial

This shows you the logs on Heroku (in case something bad happens):

	$ heroku logs --app django-tutorial

You can also get real-time updates by using tail:

	$ heroku logs --tail --app django-tutorial

And you can follow a specific process:

	$ heroku logs --tail --ps {job_name} --app django-tutorial

Also, you can run any bash command remotely on Heroku that you could in your own terminal. Just do:

	$ heroku run {command}

For example, you can check out your Heroku server's $PATH variable:

	$ heroku run echo '$PATH'

Or, check out Python's or Django's environment variables on Heroku:

	$ heroku run python                 // This is just another Python shell
	$ heroku run python manage.py shell // This shell is specific to your Django app

Inside the shell:

	>>> import os
	>>> os.environ


<a name="processes">Set up the Processes (GUnicorn Server, Celeryd Worker, Celerybeat Scheduler)</a>
--------------------------------------------------------------------------------------------------
**GUnicorn**

Heroku will use GUnicorn as the server for your web pages. It will handle requests whenever someone tries to access your web pages or hit your API routes. It's the first of the three Heroku processes that we're going to set up.

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

**Celeryd and Celerybeat**

To get Celery running on Heroku with RabbitMQ, first, find out what the BROKER_URL is.

	$ heroku config --app django-tutorial
	=== django-tutorial Config Vars
	CLOUDAMQP_URL:              amqp://appNUMBERS_heroku.com:STUFF@NAME.cloudamqp.com/appNUMBERS_heroku.com

Make a file in your project directory called production_settings.py (this should reside in the same level as your settings.py file):

	DEBUG = False
	TEMPLATE_DEBUG = False
	BROKER_URL = 'amqp://appNUMBERS_heroku.com:STUFF@NAME.cloudamqp.com/appNUMBERS_heroku.com'

Then, add the following lines to the VERY bottom of testdjango/settings.py (you want to make sure the import overwrites all variables defined in the file):

	if 'heroku' in os.environ['_']:
	    from production_settings import *

NOTE: You'll also need to add the templates 404.html and 500.html to your templates directory. This is because you've set TEMPLATE_DEBUG to False (which you need to do so clients don't get Django's debug pages and instead get your 404 or 500 page whenever they hit a bad route or when the server is down). If you don't do this, you'll get a TemplateNotFound error when something bad happens. You can copy those templates from the code that I have.

Add the following lines to your Procfile:

	celeryd: python manage.py celeryd -E -B --loglevel=INFO
	celerybeat: python manage.py celerybeat

These alias the Django commands to run the celery worker and the celerybeat scheduling service to the continuous processes "celeryd" and "celerybeat," respectively.

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
	$ heroku ps --app django-tutorial

Remember, you can check how your workers are doing in real-time:

	$ heroku logs --tail --ps celeryd --app django-tutorial
	$ heroku logs --tail --ps celerybeat --app django-tutorial

You can also go to [https://dashboard.heroku.com/apps/django-tutorial/](https://dashboard.heroku.com/apps/django-tutorial/) (replace django-tutorial with whatever your app name is) to get a nice GUI for administrative stuff.

You've just created a full-functioning production-ready application. Now, you should be able to open a web browser and go to your URL (in our case, it's [http://django-tutorial.herokuapp.com](http://django-tutorial.herokuapp.com)). Note that since we haven't made a root page, we'll get a 404 error if we just go to that address.

* Go to [http://django-tutorial.herokuapp.com/add_user](http://django-tutorial.herokuapp.com/add_user)
* Add some users (like Adaptly)
* Check out all of the users currently in the database at [http://django-tutorial.herokuapp.com/all_users](http://django-tutorial.herokuapp.com/all_users)
* Check out Adaptly's stats at [http://django-tutorial.herokuapp.com/users/adaptly](http://django-tutorial.herokuapp.com/users/adaptly)
* Wait 10 minutes and then see if Adaptly's gotten any more likes by refreshing the page.

Congratulations, you're done! Now, go grab yourself a beer and let your application do its stuff.


<a name="appendix">Appendix</a>
-----------------------------

* [Troubleshooting](#troubleshooting)
* [How to continue working on your project on a different computer](#setup)
* [How to update your .bash_profile to run commands when you get the -bash: command not found error](#updatingbashprofile)
* [A quick introduction to git](#gittutorial)
* [A small Postgres reference](#postgrescommands)
* [Code used in the guide](#code)
	* [models.py](#models.py)
	* [views.py](#views.py)
	* [add_user_form.html](#add_user_form.html)
	* [tasks.py](#tasks.py)


<a name="troubleshooting">Troubleshooting</a>
-------------------------------------------
**Local Checklist**

* Are you in the right directory?

		$ pwd
		/Users/username/project-folder
		$ ls
		Procfile    requirements.txt    venv    README.md    manage.py    project-name

* Have you activated your virtual environment?

		$ source venv/bin/activate

* Are your directories structured correctly?

> Look at the Github code for reference.

* Is your requirements.txt file up-to-date?

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

* Are your requirements installed?

		$ pip install -r requirements.txt
		$ brew install postgresql
		$ brew install rabbitmq

* Do you have a copy of the development database?

> Curl it from a remote location:

		$ mkdir tmp
		$ curl -o tmp/mydatabase.db url-to-database // If you're curling from a remote url
		$ curl -o tmp/mydatabase.db `heroku pgbackups:url --app app-name` // If you're curling from Heroku
		$ pg_restore -c -d your_database_name tmp/mydatabase.db
		$ rm -r tmp

> Or make your own:

		$ created your_database_name

* Is your database synced?

		$ python manage.py syncdb

**Heroku Checklist**

* Is your SSH Key added to your Heroku account?

		$ heroku keys:add

* Is your database synced?

		$ heroku run python manage.py syncdb

* Are all of your processes defined in your Procfile?

		$ cat Procfile
		web: gunicorn testdjango.wsgi -b 0.0.0.0:$PORT
		celeryd: python manage.py celeryd -E -B --loglevel=INFO
		celerybeat: python manage.py celerybeat

* Are all your processes running?

		$ heroku ps
		$ heroku ps:scale process_name=1

**Specific Error Messages**

	Error: You appear not to have the 'psql' program installed or on your path.

> If you're on a free database plan, you're not going to be able to run the dbshell via Heroku. If you want to look at the database, drop directly into Postgres:
>
>		$ heroku pg:psql

	!  Your key with fingerprint xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx is not authorized to access your-heroku-application.

> You need to add your SSH key to Heroku:
>
>		$ heroku keys:add

	!    This key is already in use by another account. Each account must have a unique key.

> You already added your SSH key to another Heroku account. See [here](http://martyhaught.com/articles/2010/12/14/managing-multiple-heroku-accounts/) for managing multiple Heroku accounts.

	bash: {command}: command not found

> The command you want to execute isn't in your current $PATH. Read [this](#updatingbashprofile)

<a name="setup">Quick Setup Instructions</a>
------------------------------------------
Suppose you want to continue working on your project from a different computer. Here's what you need to do to get started, assuming you've pushed your current code (that includes your requirements.txt) to Github or another remote repo.

	$ cd ~
	$ ruby <(curl -fsSkL raw.github.com/mxcl/homebrew/go)
	$ brew install python
	$ export PATH=/usr/local/share/python:$PATH
	$ easy_install pip
	$ pip install virtualenv
	$ virtualenv venv --distribute
	$ source venv/bin/activate
	$ git clone git@github.com:Adaptly/django-tutorial.git
	$ cd django-tutorial
	$ sudo pip install -r requirements.txt
	$ brew install postgresql
	$ createdb testdjango_development
	$ brew install rabbitmq
	$ heroku keys:add
	$ python manage.py syncdb


<a name="updatingbashprofile">Updating .bash_profile</a>
-------------------------------------------
If you want to be able to run commands such as rabbitmqctl from anywhere, you have to add its source directory to the $PATH environment variable. However, this variable isn't shared across different terminal sessions, so it gets reset every time you log in and out or open a new terminal window. To fix this, you need to modify your user's .bash_profile, which is located in your home directory (~) and gets loaded up every time a new shell window opens. (For a discussion on .bash_profile vs .bashrc, read [this](http://www.joshstaiger.org/archives/2005/07/bash_profile_vs.html)). When you're modifying this, you have to know the path to the source directory of the commands you want to be able to run from anywhere.

For rabbitmqctl and rabbitmq-server, those commands are located in /usr/local/sbin. To add this to your bash_profile, in ~/.bash_profile, add the following line:

	PATH=$PATH:/usr/local/sbin

Or, you can do the following:

	$ echo 'PATH=$PATH:/usr/local/sbin' >> ~/.bash_profile

Now, you have to reload the shell for the changes to take place. The following command just reloads ~/.bash_profile, which is just as good:

	$ source ~/.bash_profile

Ror Python, do the same thing, except the path will be /usr/local/share/python.

<a name="gittutorial">Git Tutorial</a>
------------------------------------
**Initializing**

If you've already cloned an empty repository for your project from Github or another remote, you can skip this entire Initializing section.

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
	        url = git@github.com:{github_repo}.git
	        fetch = +refs/heads/*:refs/remotes/origin/*

config is the configuration file Git looks at whenever you execute git commands. It aliases a bunch of commands so you only have to type

	$ git fetch origin

instead of

	$ git fetch git@github.com:{github_repo}.git

"Remote" means the remote repository you push your code to or pull/fetch your code from. For our project, we'll have two remotes: Github and Heroku.

**Fetching and Branching**

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

**Adding and Committing**

Make a new file called stuff.txt and add some stuff:

	Hello, world!

Now, you can see that Git recognizes that there's a new file:

	$ git status

In Git, there are three categories of files: untracked, not staged, and staged. 

* **Untracked** files are files that Git doesn't do anything with (e.g. if you make a new file, Git won't track it until you explicitly tell it to). Right now, stuff.txt is untracked.
* **Not staged** files are files that Git is currently tracking that you've changed somehow from what Git last remembers - the most recent commit. (e.g. if you make changes or delete a file that Git is tracking, Git will recognize that you've changed it or deleted it).
* **Staged** files are files that are ready to be committed. You add both untracked and not staged files to staging so you can commit them. A commit is basically a snapshot of your code.

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

**Pushing and Merging**

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


<a name="postgrescommands">Postgres Commands</a>
----------------------------------------------
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

<a name="code">Code Reference</a>
-------------------------------
<a name="models.py">**models.py**</a>

The models.py file is what you use to create all your Django models, which in turn creates any database tables that aren't already in the database whenever you do a syncdb. Feel free to look at the full code on Github as you read this.

First, make sure to import models from django.db module:

	from django.db import models

Then, we'll make a FacebookUser class:

	class FacebookUser(models.Model):

Next, add whatever fields you want the FacebookUser model to have to the class. The syntax is:

	{field_name} = models.{FieldType}({field_parameters})

For example, we want the id field to be the primary key of the model, and we want it to be a long and not null:

	id = models.BigIntegerField(primary_key=True)

Next, we want the name and the username fields to be strings which also shouldn't be null:

	name = models.CharField(max_length=100)
	username = models.CharField(max_length=50)

Let's add a description field, which should be of type text, but can also be null:

	description = models.TextField(null=True)

Here's the rest of the fields I added:

	about = models.TextField(null=True)
	is_published = models.NullBooleanField(null=True)
	website = models.CharField(max_length=100, null=True)
	link = models.CharField(max_length=100, null=True)
	number = models.PositiveIntegerField(null=True)
	talking_about_count = models.IntegerField(null=True)
	likes = models.IntegerField(null=True)

At the bottom, we can modify the FacebookUser's __unicode__ method so that it returns something useful (like the user's name) instead of just <Object: FacebookUser> when you're looking at an instance of the object:

	def __unicode__(self):
		return self.name

IMPORTANT: Django doesn't do database migrations, so if you want to change a table, change its model in the models.py file, delete the table from the database (see [postgres commands](#postgrescommands)), and run another syncdb.

Here's a list of reference materials for more information:

* [A more comprehensive guide to models](http://www.djangobook.com/en/1.0/chapter05/)
* [The model documentation](https://docs.djangoproject.com/en/dev/topics/db/models/)
* [The field types documentation](https://docs.djangoproject.com/en/dev/ref/models/fields/)

Now, it's time to [go back to the guide](#djangopt1)

<a name="views.py">**views.py**</a>

The views.py file receives an HTTP request whenever a user hits a URL defined in urls.py that is mapped to a particular view.

First, let's take care of our imports.

	# Python imports
	import urllib2
	import json
	
	# Django imports
	from django.http import HttpResponse
	from django.shortcuts import render_to_response
	from testdjango.facebookgraph.models import FacebookUser


If you're looking for the code for add_user, go [here](#add_user)

If you're looking for the code for show_all_users, go [here](#show_all_users)

If you're looking for the code for show_user_info, go [here](#show_user_info)

<a name="add_user">**add_user()**</a>

Whenever a client hits the /add_user/ route, we get sent an HTTP request that is handled by the add_user function. The view will interact dynamically with an HTML template, which you will create next. Here's how it will work:

* When the client hits the /add_user/ route, the template will render an input box and an "Add User" button.
* The client can enter any string into the input box. When the client presses the "Add User" button, that will send a GET request with the query passed as a parameter to the same URL, which is handled again by add_user.
	* If there was anything wrong with the search query (e.g. there wasn't a search term), the view will render the same page, but with the errors displayed
	* If there was something wrong with the search itself (e.g. the user couldn't be found), the view will again render the same page, but with the errors displayed
	* If the query was successful, the view will again render the same page, but with a success message.

This is a little complicated to tackle at once, so let's break it down into smaller steps. Feel free to look at the full code on Github as you read this.

1. Create the add_user function. Remember, for any view function that's mapped to a URL, you'll be receiving an HTTP request as a parameter.

		def add_user(request):

2. Inside that function, let's make a list to contain all of the error strings we want to print out in case the client sucks at inputting usernames.

		errors = []

3. Now, we want to handle the GET request. If the client clicked the "Add User" button, the parameter "q_user" will be in the GET request. The name "q_user" is defined in the template (we'll get to that later). For now, just know it's going to be passed in the response if the button is clicked and not if the button isn't.

		if 'q_user' in request.GET:
		    # ...stuff
		else:
		    # ...stuff

4. Let's tackle the easier part of the if/else statement first (the stuff in the else block). If the button isn't clicked, then we just want to render our template normally. So, we call the render_to_response function located in the django.shortcuts library.

		return render_to_response('add_user_form.html')

5. Now, for the hard(er) part (the stuff in the if block). Let's call q the actual search input we got. Then, if q is empty, we want to add an error message to the errors list. We can add more error checking if we want (like checking to make sure q has at least one letter in it), but I think this is good enough. Now that we have our errors, we can call the render_to_response function, this time passing a second parameter, which is a dictionary (mapping) of variable names and their values that the template will take care of.

		q = request.GET['q_user']
		if not q:
		    errors.append('Enter a search term.')
		    return render_to_response('add_user_form.html', {'errors': errors})
		else:
		    # ...stuff

6. Now, we can fill out that else block. If the query's not empty, then we want to try pulling that user's data from Facebook. The retrieve_facebook_user_data helper function takes a query string (like "coca-cola") and returns the parsed JSON response (which should be a dictionary of column names to column values) if successful and an error string otherwise.

		facebook_data = retrieve_facebook_user_data(q)

7. Now, it's time to handle more errors! If we got back an error string, we want to render the same page, but with a different error message. This time, we'll give the mapping in the extra parameter the name "httperror" mapped to the Error string that the function returned.

		if type(facebook_data) is str and 'Error:' in facebook_data:
		    return render_to_response('add_user_form.html', {'httperror': facebook_data})

8. Otherwise, if we got a nicely parsed JSON response, it'll be a dictionary, so we can call the add_user_to_db helper function that I wrote to add the user to the database. Then, we'll render the same page, but this time with a success message. (Note that add_user_to_db may not be able to successfully parse the input. In this case, we'd want to add some more error handling, but I'll let you do that on your own if you really want to).

		elif type(facebook_data) is dict:
		    return render_to_response('add_user_form.html', {'success': True})

9. Finally, if neither the if or the elif got executed, something weird happened, so just render the normal add_user_form template. (If we were more rigorous, we'd want to handle this error, but we're not!)

		else:
		    return render_to_response('add_user_form.html')

10. Add in the two helper functions that I wrote (retrieve_facebook_user_data and add_user_to_form).

That's it! You've written all of the back-end code required to add users to your database. To learn about actually interacting with the database at the view level, read [this](http://www.djangobook.com/en/1.0/chapter05/) (starting at the section titled Inserting and Updating Data). [This](https://docs.djangoproject.com/en/dev/topics/db/queries/) offers more detail of how models interact with the database. We'll also be talking about it later when we write our API views to expose the data in our database.

Now, it's time to [go back to the guide](#djangopt2)

<a name="show_all_users">**show_all_users()**</a>

Feel free to look at the full code on Github as you read this.

Whenever a client hits the /show_all_users/ route, we don't really need to handle the HTTP request. We just want to get all of the users from the database and show them to the client. Since this is pretty simple, we don't even need a template. We can just return an HttpResponse object using the django.http library, which automatically renders the HTML you pass it.

	def show_all_users(request):
	    html = "<html><body><b>ID::Name::Username</b><br>"

Let's start with an HTML string. We'll keep adding results to this for however many results are in the database.

	users = FacebookUser.objects.all()

This just retrieves all of the objects the FacebookUser model has. Now that we have a list of all of the FacebookUser objects, we can start adding them to our HTML string. To access a field for any object, just do object.field_name. You can also set these fields, but they won't be updated in the database until you do object.save().

	for user in users:
	    html += "<li>%d::%s::%s<br>" % (user.id, user.name, user.username)

Now, finish off the string by closing the unclosed tags and return the HttpResponse, which will render the HTML for us.

	html += "</body></html>"
	    return HttpResponse(html)

Now, it's time to [go back to the guide](#djangopt4)

<a name="show_user_info">**show_user_info()**</a>

Feel free to look at the full code on Github as you read this.

Let's try something a little more complicated. This time, whenever a client hits the /users/{username} route, he'll be passing an extra parameter that our view will need to handle. Otherwise, the code will be pretty similar to before:

	def show_user_info(request, input_name):

The next line just gets a list of all of the FacebookUser objects' usernames (in lowercase for more reliable matching):

	all_usernames = map(lambda x: x['username'].lower(), FacebookUser.objects.all().values('username'))

Now, we have two cases. Either, the user the client is searching for will be somewhere in the database or he won't.

	if input_name.lower() in all_usernames:
	    #...stuff
	else:
	    #...stuff

If the user isn't in the database, we can just make some HTML that says the user isn't there:

	html = "<html><h1>User not found!</h1></html>"

However, if the user is actually in the database, we're going to have to build an HTML string with all of the corresponding object's fields and the values of those fields. This just gets the user from the database, doing a case-insensitive matching. You can use the get or filter methods to perform a pseudo database query (e.g. FacebookUser.objects.get(username="Bob") for case-sensitive matching). Note that get only returns a single object (and throws an error if more than one object is returned) whereas filter returns a list of objects, even if only one is returned.

	facebook_user = FacebookUser.objects.get(username__iregex=r"(%s)" % input_name)

Then, we build our HTML string. You can get a list of all of a model's fields with the model._meta.fields attribute, and you can use the getattr(object, field) to get the value of that object's field:

	html = "<html><body>"
	for column in FacebookUser._meta.fields:
	    html += "%s: %s<br>" % (column.name, getattr(facebook_user, column.name))
	html += "</html></body>"

Finally, we return the HttpResponse, which will render the HTML for us.

	return HttpResponse(html)

Note that that was just a very short example of how to interact with models in your views. However, this is a very broad and important topic. You're going to want to reference the following if you want to use models in the future:
 
* [A more comprehensive example of interacting with models](http://www.djangobook.com/en/1.0/chapter05/) (starting at the section titled Inserting and Updating Data).
* [Documentation on interacting with models](https://docs.djangoproject.com/en/dev/topics/db/queries/)

Now, it's time to [go back to the guide](#djangopt4)

<a name="add_user_form.html">**add_user_form.html**</a>

Templates are HTML pages that get rendered whenever a function in view.py calls render_to_response on that template. The template receives any extra variables inside the optional second parameter, a dictionary, passed when render_to_response is called. Feel free to look at the full code on Github as you read this.

Let's look at the template in a little more detail. This is pretty typical HTML structure:

	<!DOCTYPE html>
	<html>
	<head>
	    <title>Add User</title>
	</head>
	<body>
	    <!--...stuff-->
	</body>

Then, things get tricky. Control flow tools can be used in templates with {% control flow tool %} (code to execute) {% end control flow tool %}. Inside {% %}, variables are handled normally. Elsewhere in the code, you can access a variable with {{ variable_name }}.

	{% if success %}
	    <p><b>User successfully added! Add another</b></p>
	{% endif %}

This says that if the success variable is passed in the extra second parameter and if it's true, then the page is going to display an extra message.

	{% if httperror %}
	    <p style="color: red;"><b>{{ httperror }}</b></p>
	{% endif %}

Since the value of httperror will be some string, this just checks if the string is not empty, and if it isn't, it'll display the string.

	{% if errors %}
	    <ul>
	        <p style="color: red;"><b>Something was wrong with your input:</b></p>
	        {% for error in errors %}
	        <p style="color: red;">{{ error }}</p>
	        {% endfor %}
	    </ul>
	{% endif %}

Similarly, since the value of errors will be some list of strings, this just checks if the list is not empty, and if it isn't, it displays every string in the list.

Finally, the most important part: the search form. This is just normal HTML. Here, a form is always created when the page is rendered. It has a text field that's passed as the parameter "q_user" and a submit button that's passed as the parameter "add_user."

	<form action="" method="get">
	    <input type="text" name="q_user">
	    <input type="submit" name="add_user" value="Add">
	</form>

That's it! You've successfully written your first template. To read more about control flow tools and how templates work with Django, you should start [here](http://www.djangobook.com/en/1.0/chapter04/).

Now, it's time to [go back to the guide](#djangopt3)

<a name="tasks.py">**tasks.py**</a>

Here, we're going to write a task that can be executed periodically. In this case, we'll make the task hit the Facebook Graph API and update the information for all of the users we have in the database. Feel free to look at the full code on Github as you read this.

First, take care of your imports:

	from __future__ import absolute_import
	
	# Python imports
	import urllib2
	import json
	from datetime import timedelta
	
	# Django imports
	from testdjango.facebookgraph.models import FacebookUser
	
	# Celery imports
	from celery.task.schedules import crontab
	from celery.decorators import periodic_task

Then, define the function of the task you want to execute and mark it as a periodic task. This has the task run every 10 minutes. Consult [this](http://docs.celeryproject.org/en/latest/getting-started/next-steps.html) to learn about how crontab expressions work.

	@periodic_task(run_every=crontab(minute="*/10"))
	def sync_database():

Finally, make your function do stuff. In your own applications, you can just replace the body with whatever script you want to run periodically. In our case, we're going to use this block of code, all of which you've seen before in previous examples:

	base_url = 'http://graph.facebook.com/%s'
	all_facebook_users = FacebookUser.objects.all()
	all_columns = FacebookUser._meta.fields
	for facebook_user in all_facebook_users:
	    try:
	        response = urllib2.urlopen(base_url % facebook_user.username)
	        json_response = json.loads(response.read())
	        for column in all_columns:
	            if column.name in json_response:
	                setattr(facebook_user, column.name, json_response[column.name])
	        facebook_user.save()
	    except urllib2.HTTPError:
	        continue
	return True

This just gets all of the objects in our database, and then for each object, hits the Facebook Graph page corresponding to that user and updates all of the information. And now you're done! Integrating periodic tasks into a Django application is really that simple.

If you want more flexibility with tasks, you're going to want to read the following:

* [Celery tasks guide](http://docs.celeryproject.org/en/latest/getting-started/next-steps.html)
* [Scheduling periodic tasks](http://ask.github.com/celery/getting-started/periodic-tasks.html)

Now, it's time to [go back to the guide](#djangopt5)
