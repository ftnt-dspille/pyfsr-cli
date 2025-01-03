.. _configuration:

Configuration
=============

PyFSR CLI can be configured using command-line arguments, environment variables, or a configuration file.

Command-Line Options
--------------------
You can provide options like `--server`, `--token`, etc., directly in the command line.

.. code-block:: bash

   pyfsr --server <server> --token <token> alerts list

Environment Variables
---------------------
Set environment variables for repeated use:

.. code-block:: bash

   export PYFSR_SERVER=fortisoar.example.com
   export PYFSR_TOKEN=<token>

Configuration File
------------------
Use a `.pyfsr.yaml` file to persist your configuration:

.. code-block:: yaml

   server: fortisoar.example.com
   token: <token>
   verify_ssl: true
