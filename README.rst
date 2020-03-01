Babu
====

Babu is a static site generator for Python, designed to let you build your static sites the way you build dynamic sites in Django and Flask, rather than (mis-)using YAML for everything.

It is named after Akshinthala Seshu Babu, `current holder of the world record for motionlessness <http://www.recordholders.org/en/records/motion.html>`_.

Babu sites are made up of URL routes and views, just like your run-of-the-mill server-rendered Web app built using Django or Flask. The biggest difference: URL routers know how to build every possible page they can route to (which is how your static site gets built).

Your data is stored in files on disk, just like any other static site generator, but you define your data's structure and query it from views using SQLAlchemy.