.. image:: https://travis-ci.org/cfournie/important.svg?branch=master
    :target: https://travis-ci.org/cfournie/important

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

    $ git clone https://github.com/cfournie/important.git
    $ cd important
    $ pip install .

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
