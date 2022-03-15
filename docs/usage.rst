.. _usage:

###########
User manual
###########

|project| can help communicate your design whether or not you are using the
automation capabilities of Gherkin_.

|project| let you use some :ref:`sphinx:rst-directives` to include
the documentation found within your Gherkin source files, and
:term:`roles` to make hyperlinked cross-references to them.


.. _Gherkin: https://cucumber.io/docs/guides/overview/#what-is-gherkin


.. _autofeature:

Documenting existing Gherkin code
=================================

The most basic use-case of |project| is to embed existing behavior
specifications from Gherkin files into your documentation.

.. rst:directive::  gherkin:autofeature

    Include documentation from a Gherkin feature.

    As an argument, you can use either a relative (to a folder configured
    with :confval:`gherkin_sources`) filepath of a feature file, or directly
    the feature's summary text.

    Given the following feature file

    .. code-block:: gherkin
        :caption: some-feature.feature

        Feature: Document a whole feature file

          Most of the time, users already have feature definitions.
          They can directly include a whole feature in their documentation.

          Scenario: Using a file path

            Given a properly written feature file
            When the autofeature directive is used with its path as an argument
            Then the feature is added to the documentation

          Scenario: Using the feature's summary text

            Given a properly written feature file
            When the autofeature directive is used with its summary as an argument
            Then the feature is added to the documentation

    Then both the following usages of :rst:dir:`gherkin:autofeature` will
    include the feature in the documentation.

    .. code-block:: rst

        .. autofeature:: some-feature.feature

    .. code-block:: rst

        .. autofeature:: Document a whole feature file

.. hint:: This works quite similarily to the :mod:`sphinx.ext.autodoc`
    Sphinx module for automatically documenting Python modules.


.. _rstgen:

Generating documentation
========================

While the :ref:`autofeature` method is great for fine control of the
disposition of features within the documentation, |project| also provides
a way to embed features automatically by generating RestructedText files
with the correct directives in them.

.. tip:: In case you have your feature files spread across several directories
    far from each other, you might consider running the generator more than
    one time.

For a basic usage, run it like so:

.. code-block:: shell

    $ python -m sphinx_gherkin -o docs my-feature-dir

For details, see its :ref:`manual page <gherkin2rst>`.


.. _crossref:

Cross-referencing Gherkin
=========================

|project| makes it easy to cross-references anything in Gherkin specifications.
by providing several :term:`roles` to create inline cross-references
(hyperlinks) to your definitions' documentation.

.. tip:: |project| will keep track of all these cross-references and add
    them to the :ref:`General Index <genindex>` as well under their respective
    target entry as numbered hyperlinks (``[1]``, ``[2]`` and so forth).

Roles that cross-reference Gherkin definitions can be quite flexible.
|project| will be as permissive as possible to resolve cross-references.

**In general**, our roles work by interpreting a keyword's **summary**.
By *summary*, we mean the text on a single line that follows a Gherkin keyword.
To cross-reference an object, use the appropriate role followed by its summary.

Here is an example:

.. code-block:: rst

    :gherkin:rule:`My Rule`

.. admonition:: Result

    :gherkin:rule:`My Rule`

While it is common practice to have the exact same keyword definition reused
in many places (e.g. *Given that the user is authenticated*), |project|
cannot create a reference to an ambiguous keyword usesince it needs to find
one and only one object to cross-reference to.  In order to narrow the reference
search, you can use a *path* of summaries, by adding the summary of parent
objects.  The ancestry of summaries is delimited with dots (``.``).

.. code-block:: rst

    :gherkin:step:`Minimalistic.this is duplicated`

.. admonition:: Result

    :gherkin:step:`Minimalistic.this is duplicated`

It is not needed to add the whole ancestry to remove ambiguity.  |project|
will emit a *warning* when a cross-reference is ambiguous.

Our :ref:`examplefeature` provides numerous cross-referencing examples.


.. _viewcode:

Embedding the Gherkin source code
=================================

When using the :ref:`autofeature` or the :ref:`gherkin2rst` tool, the
Gherkin source code is usually available at build time.  You can embed and
link that source code when using supported builders (e.g. *HTML*).

The resulting source is highlighted, available from a ``[source]`` link
near the Gherkin definition documentation, which is back-referenced from
the highlighted source itself by a ``[docs]`` link.

It works a lot like the builtin Sphinx :mod:`sphinx.ext.viewcode` module.

To use this, you need to add it to your enabled extensions in your ``conf.py``
(:mod:`conf`)

.. code-block:: python
    :caption: conf.py

    extensions = [
        # other extensions ...
        "sphinx_gherkin.viewcode"
    ]

To see it in action, have a look at our :doc:`demo/generated/features` document.


.. _keywordindex:

The Keyword Index
=================

When using |project|, all the documented Gherkin keywords are indexed and
aggregated in a special domain-specific index.

To create a link to this index, use the following :term:`roles`.

.. code-block:: rst

    :ref:`gherkin-keywordindex`

Which results in :ref:`gherkin-keywordindex`.

Index entries are grouped when their summaries are identical.  Keyword
without a summary are labeled ``unnamed``.
