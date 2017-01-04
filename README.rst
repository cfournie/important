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

Coming to pypi soon, but in the meantime, install from source using:

.. code:: bash

    $ pip install https://github.com/cfournie/important.git

Requirements
------------

This works best when run from a virtualenv where your project's requirements
are installed (to translate requirements to module names).

This tool requires that it be installed with the same Python version as the
source code that's analyzing and that the source code is syntactically correct.

Usage
-----

Check for unused requirements using:

.. code:: bash

    $ important -v --requirements requirements.txt .
    Error: Unused requirements or violated constraints found
    caniusepython3 (unused requirement)


Check for imports that are used too frequently (to prevent further usage of a
requirement while you phase it out) using:

.. code:: bash

    $ important -v --constraints constraints.txt .
    Error: Unused requirements or violated constraints found
    click<=1 (constraint violated by click==2)


Check for unused requirements but exclude test files using:

.. code:: bash

    $ important -v --requirements requirements.txt **/test_*.py .
    Error: Unused requirements or violated constraints found
    caniusepython3 (unused requirement)


Ignore errors related to some of your requirements using:

.. code:: bash

   $ important -v --requirements requirements.txt --ignore caniusepython3 .
   $ important -v --requirements requirements.txt --ignorefile ignored.txt .
