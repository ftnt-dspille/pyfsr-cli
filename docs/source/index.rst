Welcome to PyFSR CLI Documentation
==================================

PyFSR CLI is a command-line interface for interacting with the FortiSOAR REST API.

.. click:: pyfsr_cli.cli:cli
   :prog: pyfsr
   :nested: full

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install pyfsr-cli

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   # Using token authentication
   pyfsr --server fortisoar.example.com --token <token> alerts list

   # Using username/password
   pyfsr --server fortisoar.example.com --username admin alerts list

Configuration
-------------

The CLI can be configured using:

* Command line options
* Environment variables
* Configuration file

For detailed configuration options, see :ref:`configuration`.

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   autoapi/index
   configuration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`