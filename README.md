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
	* [How to continue working on your project on a different computer](#setup)
	* [How to update your .bashrc to run commands when you get the -bash: command not found error](#updatingbashrc)
	* [A quick introduction to git](#gittutorial)
	* [A small Postgres reference](#postgrescommands)
	* [Code used in the guide](#code)
		* [models.py](#models.py)
		* [views.py](#views.py)
		* [add_user_form.html](#add_user_form.html)
		* [tasks.py](#tasks.py)

<a name="introduction">Introduction</a>
-------------------------------------
This is a pretty simple yet extensive tutorial on how to go from a simple Python script to a full-functioning production-ready web application. We'll be creating a small application that allows an end-user to search for a user in Facebook's graph API and store that user's information. We'll also provide some simple API routes to display all users and get any user's information. Finally, we'll have a backend job that periodically hits Facebook to update all the information in our database.

The tools that we'll be using are:

* **Django** as the web framework
* **Postgres** as the persistent storage (database)
* **Celery** as the job queue
* **RabbitMQ** as the broker for Celery
* **Git** as the version control system
* **Heroku** as the production platform


<a name="installpython">Install Python, Pip, and Venv</a>
-------------------------------------------------------
Obviously, to start a Django project, you need to have Python installed. This requires [Homebrew](https://github.com/mxcl/homebrew/wiki/installation), which should already be installed. We're also going to install [Pip](http://pypi.python.org/pypi/pip), which is an easy way to install the Python packages we'll need later. Finally, we're going to install [VirtualEnv](http://pypi.python.org/pypi/virtualenv), which creates an isolated Python environment for our Django project. This is important because we know that our code will work with a particular version of Python (the one we are currently using). It makes sure the code in our project doesn't break when we inevitably do machine-wide Python updates some time in the future. First, open up a terminal.

This installs Homebrew:

	$ ruby <(curl -fsSkL raw.github.com/mxcl/homebrew/go)

This installs Python:

	$ brew install python

This adds Python to your PATH environment variable so you can run python commands from the terminal. Note that this is is not permanent, and you'll have to re-add it each time you restart the terminal, open up a new terminal window, or log out. To permanently add it to $PATH, you'll need to modify your .bashrc (see [appendix](#updatingbashrc) for instructions).

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

Go to your home directory:

	$ cd ~

Clone the Github repo to your local machine. This copies everything in the remote Github repo to a directory called django-tutorial in the current directory (which should be your home directory) on your local machine:

	$ git clone git@github.com:Adaptly/django-tutorial.git

Finally, set up your .gitignore file, which resides in the same level as your .git directory (i.e., your project directory, so if you ls -al, you should see both the .git folder and the .gitignore file). The .gitignore file makes sure your useless build artifacts and other non-project-specific files aren't tracked. In .gitignore, add the following lines:

	venv
	*.pyc


<a name="startproject">Set up the Project</a>
-------------------------------------------
Now, we're going to set up the Django project. You can call it whatever you want, but ideally you'll give it the same name that Will gives the Heroku app to avoid any confusion down the line. In this tutorial, we called our main project directory django-tutorial (when we made our git repo). Within the main project directory, we can start a Django project. I'm going to call the project we're going to make testdjango, but you'll probably want to give yours a more descriptive name whenever you make your own project. Then, we're going to make an application for that project. Each project can have one or more applications, but we'll just make one for our purposes. We'll call it facebookgraph because it hits Facebook's Graph API and pulls user data from that.

Go to your main project directory:

	$ cd ~/django-tutorial

Create a virtual Python environment for your project. This makes a venv directory that has all the Python environment files:

	$ virtualenv venv --distribute

Modify your $PATH environment variable to use the new Python environment instead of your machine's. This "activates" the virtual environment:

	$ source venv/bin/activate

To "deactivate" the virtual environment do the following (or just close the window or log out):

	$ deactivate

IMPORTANT: Every time you want to work on your project, when you go into the project directory, you have to load up the virtual environment (it doesn't do this for you automatically, unlike with Rails).

Install Django, psycopg2 (Django's Postgres adapter), and dj-database-url (makes it easier to configure the database with Heroku)

	$ pip install Django psycopg2 dj-database-url

Start your Django project in the project directory:

	$ django-admin.py startproject testdjango .

Now, you can make one or more applications for the project:

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
Now, we want to make sure everything we're going to need later is installed on our local machine. Make a file in your base project directory (it should live in ~/django-tutorial) called requirements.txt:
	
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
We're going to use Postgres for our database. Databases are great because they're the best way to quickly store, organize, and retrieve tons of information. They're like huge spreadsheets that don't suck. Each database is composed of tables, each of which is used to store information about something (e.g. a car company may have a car table, a customers table, an employees table, and a transactions table). Each table has a schema, which is composed of the columns that make up the table (e.g. for the car table, it could have a car name column, a quantity column, and a price column) and the data types of the columns (e.g. for that same table, the car name would be a string, or VARCHAR, the quantity would be an integer, and the price would be a float or decimal), as well as things like primary and foreign keys that you don't really have to worry about yet. Each table is used to store data in the form of tuples (or records). For example, the car table could have the tuple (2007 Honda Civic, 20, 15000.00). For this tutorial, you don't need to know SQL, but it's highly recommended that you learn it. Go to the [appendix](#postgrescommands) for a list of a few quick Postgres commands.

Create a local development database (your Heroku app should already come with a production database so you don't need to worry about that):

	$ createdb testdjango_development

Make sure your application settings knows about the database. In testdjango/settings.py:

	import dj_database_url
	...
	DATABASES = {'default': dj_database_url.config(default='postgres://:@localhost:5432/testdjango_development')}

This should replace the current DATABASES environment variable in settings.py. The structure should be:

	default='postgres://{USER}:{PASSWORD}@localhost:{PORT}/{NAME}'

So, in our example, we're using the testdjango_development database with no user and password on port 5432.


<a name="celery">Set up the Background Jobs with Celery and RabbitMQ (Local)</a>
------------------------------------------------------------------------------
Celery is queuing and messaging service that lets you easily manage background jobs. RabbitMQ is the broker (queuing and messaging system system) that we're going to use with Celery that makes it really easy to manage the job queues and specific tasks (especially on Heroku). The processes that we'll be running are celeryd, which is the Celery worker that executes our background tasks, and celerybeat, which schedules those tasks.

You should've already installed Celery as well, so again, we need to make sure Django knows to use it. In testdjango/settings.py, add the following to the INSTALLED_APPS variable:

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

Solution:

	$ export PATH=/usr/local/sbin:$PATH

Add the following line to the bottom of the settings.py. This says that Celery is going to use RabbitMQ as its broker with the default settings defined above (username is guest, password is guest, vhost is '/', server is localhost, and port is 5672):

	BROKER_URL = 'amqp://guest:guest@localhost:5672//'

Now, you can run stuff locally. In four separate terminal windows, run these three commands:

	$ rabbitmq-server
	$ python manage.py runserver
	$ python manage.py celeryd
	$ python manage.py celerybeat

This doesn't do anything yet, but you'll be using these commands in the near future.


<a name="django">Write an Application with Django</a>
--------------------------------------------------
In this section, I will give you a brief overview of creating a full-functioning Django application. Django is a lightweight web framework (sort of like Rails, but much lighter) that makes it easy to develop web applications. It's not at all meant to be a full guide. Rather, it's a brief introduction so that you can quickly get something running. I strongly encourage you to check out the [Django tutorial](http://www.djangobook.com/en/1.0/), which is extremely comprehensive and very straightforward and easy to understand.

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
* [Make a FacebookUser model that mirrors the responses that we get from the Facebook Graph](#djangopt1)
* [Make a view that lets the user search for a Facebook user and add that user to the database](#djangopt2)
* [Make a template to render that view](#djangopt3)
* [Make a views that show all users in our database and the information for a specific user (like API routes)](#djangopt4)
* [Make a task that keeps our database up-to-date by periodically calling the Facebook Graph API](#djangopt5)

<a name="djangopt1">**Making a FacebookUser Model**</a>

1. Copy the code in django-tutorial/testdjango/facebookgraph/models.py into your own models.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#models.py).
2. Sync the model with the database (NOTE: The first time you run syncdb, it's going to ask you to create a superuser. This isn't necessary, but you can do it if you want to use the [Admin interface](https://docs.djangoproject.com/en/dev/ref/contrib/admin/), which is a nice GUI that you can use to manage your site. I won't cover it here).

		python manage.py syncdb

<a name="djangopt2">**Making an Add User View**</a>

1. Copy the add_user function and the two helper functions (retrieve_facebook_user_data and add_user_to_db) in django-tutorial/testdjango/facebookgraph/views.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#views.py).
2. Add the following to the urlpatterns tuple in testdjango/urls.py. This says that if someone hits the url your_base_url/add_user, it will handle the response using the add_user function in views.py. The r means raw string (the string will be treated literally), so you don't have to escape special characters. The '^' means match all characters before the string (which, in this case, is nothing - just the root directory '/' which is automatically prepended) and the '$' means stop matching any characters after the string. For example, if you didn't include the $, then the url below would match routes like base_url/add_user/bob and base_url/add_user/1234 as well. [This](http://www.djangobook.com/en/1.0/chapter03/) is a good resource to learn more about urls.py:

		url(r'^add_user/$', add_user),

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

1. Copy the show_all_users function in django-tutorial/testdjango/facebookgraph/views.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#views.py).
2. Add the following to the urlpatterns tuple in testdjango/urls.py. This says that if someone hits the url your_base_url/all_users, it will handle the response using the show_all_users function in views.py:

		url(r'^all_users/$', show_all_users),

3. Hit the route to see it in action. In a web browser, go to the address localhost:8000/all_users
4. Copy the show_user_info function in django-tutorial/testdjango/facebookgraph/views.py. The code itself along with a brief explanation that you should definitely look at is in the [appendix](#views.py).
5. Add the following to the urlpatterns tuple in testdjango/urls.py. This says that if someone hits the url your_base_url/users/{username}, it will handle the response using the show_user_info function in views.py. The regex means accept all input strings of one or more characters that don't include a '/'. The regex is automatically passed as the second parameter to the function show_user_info:

		url(r'^users/([^/]+)/$', show_user_info),

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
5. Shut down your worker processes and re-comment the task settings (you don't want to hit your rate limits)

		@periodic_task(run_every=crontab(minute="*/10"))
		#@periodic_task(run_every=timedelta(seconds=3))

Congratulations, you've made your web application! Locally, you should be able to add users to your database, view user information, and automatically periodically update that information. Hopefully, you understand all the code here. If not, you *really* should look at the code section of the [appendix](#code). *Seriously.* Now, it's time to put our app into production.


<a name="heroku>Deploy to Heroku</a>
----------------------------------
Heroku is an online web service that runs your production application (kind of like a server). Whereas your development application will be run locally, your production application will live on Heroku.

Add the following to your .git/config file:

	[remote "heroku"]
	        url = git@heroku.com:{app_name}.git
	        fetch = +refs/heads/*:refs/remotes/heroku/*

Log into Heroku:

	$ cd ~/django-tutorial
	$ heroku login

There are two important files that should be in your project directory that Heroku uses.

* **Procfile**: Heroku uses this to alias certain commands to processes. You will be using the processes you define in this file to use Heroku workers to run whatever commands you alias.
* **requirements.txt**: Heroku uses this to determine what libraries and dependencies need to be installed. Every time you push to Heroku, it will look at requirements.txt and install all the listed dependencies. For example, so far, we're using Django, psycopg2, and dj-database-url on our local machine, so we need to make Heroku install those as well.

Create an empty file in your project base directory called Procfile.

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

Make a file in your testdjango directory called production_settings.py:

	DEBUG = False
	TEMPLATE_DEBUG = False
	BROKER_URL = '{Get this from CLOUDAMQP_URL}'

Then, add the following lines to the VERY bottom of testdjango/settings.py (you want to make sure the import overwrites all variables defined in the file):

	if 'heroku' in os.environ['_']:
	    from production_settings import *

NOTE: You'll also need to add the templates 404.html and 500.html to your templates directory. This is because you've set TEMPLATE_DEBUG to False (which you need to do so clients don't get Django's debug pages and instead get your 404 or 500 page whenever they hit a bad route or when the server is down). If you don't do this, you'll get a TemplateNotFound error when something bad happens. You can copy those templates from the code that I have.

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

Remember, you can check how your workers are doing in real-time:

	$ heroku logs --tail --ps celeryd --app django-tutorial
	$ heroku logs --tail --ps celerybeat --app django-tutorial

You can also go to [https://dashboard.heroku.com/apps/django-tutorial/](https://dashboard.heroku.com/apps/django-tutorial/) (or replace django-tutorial with whatever your app name is) to get a nice GUI for administrative stuff.

Congratulations, you're done! You've just created a full-functioning production-ready application in about an hour. Now, you should be able to open a web browser and go to your URL (in our case, it's [http://django-tutorial.herokuapp.com](http://django-tutorial.herokuapp.com)). Note that since we haven't made a root page, we'll get a 404 error if we just go to that address.

* Go to [http://django-tutorial.herokuapp.com/add_user](http://django-tutorial.herokuapp.com/add_user)
* Add some users (like Adaptly)
* Check out all of the users currently in the database at [http://django-tutorial.herokuapp.com/all_users](http://django-tutorial.herokuapp.com/all_users)
* Check out Adaptly's stats at [http://django-tutorial.herokuapp.com/users/adaptly](http://django-tutorial.herokuapp.com/users/adaptly)
* Wait 10 minutes and then see if Adaptly's gotten any more likes by refreshing the page.


<a name="appendix">Appendix</a>
-----------------------------

* [How to continue working on your project on a different computer](#setup)
* [How to update your .bashrc to run commands when you get the -bash: command not found error](#updatingbashrc)
* [A quick introduction to git](#gittutorial)
* [A small Postgres reference](#postgrescommands)
* [Code used in the guide](#code)
	* [models.py](#models.py)
	* [views.py](#views.py)
	* [add_user_form.html](#add_user_form.html)
	* [tasks.py](#tasks.py)

<a name="setup">Quick Setup Instructions</a>
------------------------------------------
Suppose you want to continue working on your project from a different computer. Here's what you need to do to get started, assuming you've pushed your current code (that includes your requirements.txt) to git.

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


<a name="updatingbashrc">Updating .bashrc</a>
-------------------------------------------
If you want to be able to run commands such as rabbitmqctl from anywhere, you have to add its source directory to the $PATH environment variable. However, this variable isn't shared across different terminal sessions, so it gets reset every time you log in and out or open a new terminal window. To fix this, you need to modify your user's .bashrc, which is located in your home directory (~) and gets loaded up every time a new shell window opens. When you're modifying this, you have to know the path to the source directory of the commands you want to be able to run from anywhere. For rabbitmqctl and rabbitmq-server, those commands are located in /usr/local/sbin. To add this to your bashrc, in ~/.bashrc, add the following line:

	PATH=$PATH:/usr/local/sbin

Or, you can do the following:

	echo 'PATH=$PATH:/usr/local/sbin' >> ~/.bashrc

Now, you have to reload the shell for the changes to take place. The following command just reloads ~/.bashrc, which is just as good:

	exec bash

<a name="gittutorial">Git Tutorial</a>
------------------------------------
**Initializing**

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

The models.py file is what you use to create all your Django models, which in turn creates any database tables that aren't already in the database whenever you do a syncdb.

First, make sure to import models from django.db module:

	from django.db import models

Then, we'll make a FacebookUser class:

	class FacebookUser(models.Model):

Finally, add whatever fields you want the FacebookUser model to have to the class. (Remember, indentation is important in Python). The syntax is:

	{column_name} = models.{FieldType}({field_parameters})

For example, we want the id column to be the primary key of the field, and we want it to be a long and not null:

	id = models.BigIntegerField(primary_key=True)

Next, we want the name and the username columns to be strings which also shouldn't be null:

	name = models.CharField(max_length=100)
	username = models.CharField(max_length=50)

Let's add a description column, which should be of type text, but can be null:

	description = models.TextField(null=True)

Here's the rest of the columns I added:

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

That's it! Feel free to look at the full code in the Github repository.

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

*If you're looking for the code for add_user, go [here](#add_user)
*If you're looking for the code for show_all_users, go [here](#show_all_users)
*If you're looking for the code for show_user_info, go [here](#show_user_info)

<a name="add_user">add_user()</a>

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

<a name="show_all_users">show_all_users()</a>

<a name="show_user_info">show_user_info()</a>

Now, it's time to [go back to the guide](#djangopt4)

	# Python imports
	import urllib2
	import json
	
	# Django imports
	from django.http import HttpResponse
	from django.shortcuts import render_to_response
	from testdjango.facebookgraph.models import FacebookUser
	
	def add_user(request):
	    errors = []
	    if 'q_user' in request.GET:
	        q = request.GET['q_user']
	        if not q:
	            errors.append('Enter a search term.')
	        if len(errors) != 0:
	            return render_to_response('add_user_form.html', {'errors': errors})
	        else:
	            facebook_data = retrieve_facebook_user_data(q)
	            if type(facebook_data) is str and 'Error:' in facebook_data:
	                return render_to_response('add_user_form.html', {'httperror': facebook_data})
	            elif type(facebook_data) is dict:
	                add_user_to_db(facebook_data)
	                return render_to_response('add_user_form.html', {'success': True})
	            else:
	                return render_to_response('add_user_form.html')
	    else:
	        return render_to_response('add_user_form.html')
	
	def show_all_users(request):
	    html = "<html><body><b>ID::Name::Username</b><br>"
	    users = FacebookUser.objects.all()
	    for user in users:
	        html += "<li>%d::%s::%s<br>" % (user.id, user.name, user.username)
	    html += "</body></html>"
	    return HttpResponse(html)
	
	def show_user_info(request, input_name):
	    all_usernames = map(lambda x: x['username'].lower(), FacebookUser.objects.all().values('username'))
	    if input_name.lower() in all_usernames:
	        facebook_user = FacebookUser.objects.get(username__iregex=r"(%s)" % input_name)
	        html = "<html><body>"
	        for column in FacebookUser._meta.fields:
	            html += "%s: %s<br>" % (column.name, getattr(facebook_user, column.name))
	        html += "</body></html>"
	    else:
	        html = "<html><h1>User not found!</h1></html>"
	    return HttpResponse(html)
	
	# Helper functions
	
	def retrieve_facebook_user_data(input_name):
	    base_url = 'http://graph.facebook.com/%s'
	    try:
	        response = urllib2.urlopen(base_url % input_name)
	        return json.loads(response.read())
	    except urllib2.HTTPError, e:
	        return "Error: Either could not connect to Facebook or user was not found."
	    except ValueError, e:
	        return "Error: JSON could not be decoded. Maybe you were redirected to another page."
	
	def add_user_to_db(facebook_data):
	    all_columns = FacebookUser._meta.fields
	    facebook_user = FacebookUser()
	    for column in all_columns:
	        if column.name in facebook_data:
	            setattr(facebook_user, column.name, facebook_data[column.name])
	    facebook_user.save()

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
	
	@periodic_task(run_every=crontab(minute="*/10"))
	#@periodic_task(run_every=timedelta(seconds=3))
	def sync_database():
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

Now, it's time to [go back to the guide](#djangopt5)
