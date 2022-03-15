#########
|project|
#########

.. container:: tagline

    A Sphinx_ extension for documenting **Gherkin** features.

|project| is simple to use and integrate smoothly with your Gherkin_ codebase.

    Programs must be written for people to read, and only incidentally
    for machines to execute.

    -- `SICP <https://mitpress.mit.edu/sites/default/files/sicp/index.html>`__

Code can become reusable when it is clearly visible, searchable and
referenceable.  |project| will help

*   **further improve collaboration** with stakeholders by exposing the
    behaviors and ubiquitous language beyond the development team.

*   **promote knowledge** and foster a community spirit around your code;

*   **keep track** of *why* things work the way they do.


Quick start
===========

Install |project|:

.. code-block:: shell

    pip install -U sphinx-gherkin

Enable |project| in your ``conf.py`` (:mod:`conf`), and configure where
to find the feature files:

.. code-block:: python
    :caption: conf.py

    extensions = [
        # other extensions ...
        "sphinx_gherkin"
    ]

    gherkin_sources = "../relativeto/docsfolder/gherkin"

.. tip:: For details about **configuration**, see :ref:`configuration`.

Place your behavior specifications within your documentation:

.. code-block:: rst
    :caption: some_documentation.rst

    .. gherkin:autofeature:: some-file.feature

.. tip:: For details about sourcing documentation from feature files, see
    :ref:`autofeature`.

Then cross-reference your definitions with some of our roles:

.. code-block::
    :caption: some_other_documentation.rst

    You should really check out :gherkin:scenario:`A nice scenario`.

.. tip:: for more information about supported **roles**, see :ref:`roles`.

.. _Sphinx: https://www.sphinx-doc.org/en/master/index.html

.. toctree::
    :maxdepth: 1
    :hidden:

    usage
    references/index
    demo/index
    contributing
    changelog
    about


.. _links:

Links
=====

|project| is

- `Hosted on Gitlab <https://gitlab.com/cblegare/sphinx-gherkin>`__
- `Mirrored on Github <https://github.com/cblegare/sphinx-gherkin>`__
- `Distributed on PyPI <https://pypi.org/project/sphinx-gherkin/>`__
- `Documented online <https://cblegare.gitlab.io/sphinx-gherkin/>`__


Indices and references
======================

*   :ref:`genindex`
*   :ref:`gherkin-keywordindex`
*   :ref:`search`
*   :ref:`glossary`

.. important:: **Gherkin**, **Cucumber** and their respective Logo are
    trademarks of SmartBear_. |project| is not associated with SmartBear.

.. _SmartBear: https://smartbear.com
.. _Gherkin: https://cucumber.io/docs/guides/overview/#what-is-gherkin
