
# PROJECT 3 - Item - Catalog (Movie Collection App)

> A Project in partial requirement of the the course: FULL STACK FOUNDATIONS and AUTHENTICATION / AUTHORIZATION: OAuth

* [Summary](#summary)
* [Requirements](#requirements)
* [Important Files](#important_files)
* [How to run the app](#how_to_run_the_app)
* [References](#references)

## Summary
A Fullstack project built using Flask with an SQLite database, running on a virtual machine.

This application provides a list of Movies within a variety of 
Collections as well as provide a (Google and Facebook) user registration and authentication system.
The app also prove a JSON and ATOM endpoints.
Registered users have the ability to post, edit and delete their own Movie category. 

In addition, user have the ability to upload movie photos from their local files,
or through a phtot url. Each user can view other user's data but cannot perform a CRUD
function.

Program Builder:

- **Flask** framework driven by **SQLite** database
- **OAuth2** Google+ anf Facebook SignIn for authorization and authentication

Programmer: Ellis Enobun (Udacious)


## Requirements
- [**SQLAlchemy**](http://www.sqlalchemy.org/)
- [**Flask**](http://www.flask.pocoo.org/)
- [**SQLite**](https://www.sqlite.org/)
- [**Vagrantup**](https://www.vagrantup.com/)
- [**Oracle Virtual Machine**](https://www.virtualbox.org/)
- **Browser:** Safari and Chrome (Preferrably Safari) 


## Important Files
***'movie_app'*** - The program that runs the server side operations.

***'moviecollection/__init__.py'*** - The package init file.

***'moviecollection/api_JSON_ATOM.py'*** - Flask routing that returns data in JSON and ATOM format.

***'moviecollection/login.py'*** - Flask routing that handles Google+  and  Facebook login and logout

***'moviecollection/views.py'*** - This is the Flask routing that returns HTML pages.

***'moviecollection/database_setup.py'*** - This contains the database table information 
that creates the restaurant.db (Restaurant Database). A session is gotten when this file is run.

***'static/css'*** - This folder contains styles methods that styles the html templates.

***'templates/'*** - Contains the html code for rendering. The base.html file, 
contains header and footer that is shared with other *.html files by calling the base file in each.

***'g_client_secret.json'*** - This is the app authentication for communicating with the Google+ API. 
It contains the client ID uniquely used to communicate between the Google+ API server and 
the client when a Google+ button is clicked.

***'fb_client_secret.json'*** - This is the app authentication for communicating with the Facebook API. 
It contains the client ID uniquely used to communicate between the Facebook API server and 
the client when a facebook button is clicked.


## How to run the app
1. **Set up the Virtual Machine:**
	-To set up the Vagrant VM, follow the instructions from [Udacity.com](https://www.udacity.com/wiki/ud088/vagrant)

2. **Open the app in Vagrant VM:**

	```
	$ git clone https://github.com/elnobun/Item-Catalog (Movie Collection App).git
	$ cd Item-Catalog (Movie Collection App)
	$ cd vagrant
	```
	Having navigated to the 'vagrant' directory, run the VM:
	
	```
	$ vagrant up   #to launch and provision the vagrant environment
	$ vagrant ssh  #to login to your vagrant environment
	```
3. **Movie Collection database:**
	-The database_setup.py file, creates moviecollections.db file which contains
	the tables. It was created by running:

	```
	vagrant@vagrant-ubuntu-trusty-32:~$ cd /vagrant/moviecollection
	trusty-32:/vagrant/moviecollection$ python database_setup.py
	```
4. **Run the server**	
	- movie_app.py can be run from the 'vagrant' directory.

	```ssh
	...-trusty-32:/vagrant$ python restaurantmenu_app.py
	 * Running on http://0.0.0.0:5000/
	 * Restarting with reloader
	```
5. **In (safari or google chrome) Navigate to 'http://localhost:5000':**

6. **Viewing the Website**
	- The public page lists all the movie collections, without the edit buttons. Corresponding movies 
	can be viewed but cannot be edited until the user is logged in. Users can only perform CRUD function
	in their session, but can only view other users session without the authorization to perform a CRUD function
	- A login button is present at the top-right corner on the 
	navigation bar, which when clicked on any part of the pages, directs user to a login page containing
	Google+  and Facebook login ooptions. Each User photo is displayed on corresponding CRUD performance.
	When the user is logged in, the editing buttons are displayed.
	Now the user can create/edit a collection , its correspoding movie, and also upload a movie image via local
	file or url.

	## References
	***udacity.com***

	- [Authentication & Authorization course](https://www.udacity.com/course/viewer#!/c-ud330-nd/l-3967218625/e-3963648623/m-4044308696)

	***Stackoverflow.com***

	***SQLAlchemy.org***

	***Flask.pocoo.org***

	- [How to organize a bigger app](http://flask.pocoo.org/docs/0.10/patterns/packages/)
	- [Log in decorator needs 'wraps'](http://flask.pocoo.org/docs/0.10/patterns/viewdecorators/)




