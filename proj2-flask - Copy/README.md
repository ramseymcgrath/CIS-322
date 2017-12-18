# proj2-flask
A starter project for using the Flask framework

Remember to remove these instructions and replace them with the 
an appropriate README. 


## Basic task

* Fork on github (or bitbucket)
* Clone in your workspace and on ix
* Enhance the class schedule display
  * The starting date of each week should display
  * The current week (just the column with the week number, or the
    whole row if you prefer) should be highlighted in some way. 


## In docker
Use a more modern workspace! I've included a dockerfile which builds a python container to run this code. Leave your local python envrioment alone (:

`docker build -t project2 .`
`docker run project2`

By default, you can now access your app using the ip of your container and port 5000

## In your workspace

'bash ./configure' should create appropriate configuration files on
most Unix files.   If you are using Windows, some additional editing
of configuration files may be necessary.  You might have to edit the
Makefile to find the right version of 
pyvenv.

If you can run flask applications in your development environment, the
application would might be run by
`   python3 syllabus.py`
and then reached with url
`   http://localhost:5000`

`make run` will launch the debugging server built into flask.  It
provides the best support for tracking down bugs in your server, but
it's not suitable for use by many users or over a long period.  `make
service` starts a Green Unicorn (gunicorn) server; you may note the extra
lime sparkles all around you.  Green Unicorn can be used for servers
that run over a longer period (e.g., if you want to leave a web
service running on your Pi).   

## On ix.cs.uoregon.edu

You may optionally use ix for testing.  This could be of most use to
Windows users;  for MacOS users, there is very little advantage of
testing on ix over testing on MacOS.

## On your Pi

It is important to test your service on your Pi.  You should be able
to write a simple shell script that installs the latest version of
your system (by cloning your repository from github), configures it,
and launches a server for testing.   If you are not familiar enough
with Unix and with bash shell scripting to do that, work with
classmates to develop the scripts you need.  I'll contribute to that
effort, but I prefer to be part of a collaborative effort rather than
just developing the scripts myself and giving them to you.  (I'll
defintely have my own for installing and testing your projects.) 

## In docker

I've 


