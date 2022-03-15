.. _configuration:

#############
Configuration
#############

|project| uses few but important configuration values from your
:mod:`conf` (``conf.py``).

.. confval:: gherkin_sources

    *optional*

    Indicates where to find Gherkin source files (``.feature`` files).

    Can be either

    **A string**
        that provide the path to your one Gherkin root folder.

    **A dictionary**
        that maps root folder names to path to Gherkin root folder.

        The names (keys) are not used yet.
