XT synchronizer server implementation

= Requirements= 

# python 
# apache web server with mod_wsgi running on localhost serving up /sync by launching server_wsgi.py
# py.test 

== instructions for Ubuntu ==

  apt-get install python-py libapache2-mod-wsgi

  sudo pip install funcparserlib

  sudo make install # installs the wsgi site on apache

= To run unit tests =

== the simple one shot way ==
  cd $REPO
  py.test

== the nice convenient backgronud loop way ==

  sudo apt-get install python-pytest-xdist
  cd $REPO
  py.test -f

This reruns the test whenever you touch a file in $REPO, which saves
you having to launch the test by hand each time.

= Coding style =

Code in this repo follows the guidlines set forth in PEP8

http://www.python.org/dev/peps/pep-0008/

