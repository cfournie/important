.. image:: https://travis-ci.org/cfournie/important.svg?branch=master
    :target: https://travis-ci.org/cfournie/important
.. image:: https://coveralls.io/repos/github/cfournie/important/badge.svg?branch=master
    :target: https://coveralls.io/github/cfournie/important?branch=master

Important
=========

A simple source code import checker that checks your project for whether you:

- Import and use everything in your `requirements.txt` file; and/or
- Import packages with specified frequencies using a constraint file (use to
  wean a project off of a dependency).

Installation
------------

Install the latest stable version from PyPI using:

.. code:: bash

    pip install important

Otherwise, to grab the latest version on master, use:
    
.. code:: bash
          
    pip install git+https://github.com/cfournie/important.git

Requirements
------------

This works best when run from a virtualenv where your project's requirements
are installed (to translate requirements to module names).

This tool requires that it be installed with the same Python version as the
source code that it's analyzing and that the source code is syntactically correct.

Usage
-----

Check for unused requirements using:

.. code:: bash

    $ important -v --requirements requirements.txt .
    Parsed 52 imports in 8 files
    Error: Unused requirements or violated constraints found
    caniusepython3 (unused requirement)


Check for imports that are used too frequently (to prevent further usage of a
requirement while you phase it out) using:

.. code:: bash

    $ important -v --constraints constraints.txt .
    Parsed 52 imports in 8 files
    Error: Unused requirements or violated constraints found
    click<=1 (constraint violated by click==2)


Check for unused requirements but exclude test files using:

.. code:: bash

    $ important -v --requirements requirements.txt --exclude **/test_*.py .
    Parsed 52 imports in 8 files
    Error: Unused requirements or violated constraints found
    caniusepython3 (unused requirement)


Ignore errors related to some of your requirements using:

.. code:: bash

   $ important -v --requirements requirements.txt --ignore caniusepython3 .
   Parsed 52 imports in 8 files
   $ important -v --requirements requirements.txt --ignorefile ignored.txt .
   Parsed 52 imports in 8 files


Alternatively, you can configure ``important`` using a ``setup.cfg`` file in the current working directory, e.g.:

.. code:: ini

   [important]
   requirements=
       requirements.txt
   constraints=
       constraints.txt
   ignore=
       Sphinx
       flake8
   exclude=
       .git
   sourcecode=.

Then run using:

.. code:: bash

   $ important -v
   Parsed 52 imports in 8 files
