.. _markup:

#########################
Detailed markup reference
#########################

This document provide details about the roles and directives used to define
and reference Gherkin keywords.

.. tip:: You may find redundant that all roles and directives are prefixed
    with the Gherkin domain identifier (``gherkin``).  It can be omitted
    by defining ``gherkin`` as the default :doc:`Sphinx domain <usage/restructuredtext/domains>`,
    either globally using :confval:`primary_domain` configuration or locally in a
    RestructuredText document by using the :rst:dir:`default-domain`
    directive.

.. _Sphinx domain:

.. _roles:

Roles
=====

The following documentation references our :ref:`examplefeature` to provide
working examples.

.. rst:role:: gherkin:feature

    Cross reference a Gherkin *Feature*.

    .. code-block:: rst

        :gherkin:feature:`XRef with Sphinx-Gherkin`

    .. admonition:: Result

        :gherkin:feature:`XRef with Sphinx-Gherkin`


.. rst:role:: gherkin:rule

    Cross reference a Gherkin *Rule*.

    .. code-block:: rst

        :gherkin:rule:`My example Rule`

    .. admonition:: Result

        :gherkin:rule:`My example Rule`


.. rst:role:: gherkin:scenario

    Cross reference a Gherkin *Scenario*.

    .. hint:: |project| consider *Scenario outline* and *Scenario template*
        as normal a scenario.

    .. code-block:: rst

        :gherkin:scenario:`Minimalistic example`

    .. admonition:: Result

        :gherkin:scenario:`Minimalistic example`

.. rst:role:: gherkin:example

    Alias for :rst:role:`gherkin:scenario`.

.. rst:role:: gherkin:template

    Alias for :rst:role:`gherkin:scenario`.

.. rst:role:: gherkin:outline

    Alias for :rst:role:`gherkin:scenario`.


.. rst:role:: gherkin:background

    Cross reference a Gherkin *Background*.

    .. code-block:: rst

        :gherkin:background:`a simple example background`

    .. admonition:: Result

        :gherkin:background:`a simple example background`

.. rst:role:: gherkin:step

    Cross reference a Gherkin *Step*.

    .. tip:: Since steps are often reused in several scenarios, you might
        need to specify some context.  For specific examples, see our
        :ref:`examplefeature`.

    .. code-block:: rst

        :gherkin:step:`Minimalistic example.the sky is blue`

    .. admonition:: Result

        :gherkin:step:`Minimalistic example.the sky is blue`

.. rst:role:: gherkin:given

    Alias for :rst:role:`gherkin:step`.

.. rst:role:: gherkin:when

    Alias for :rst:role:`gherkin:step`.

.. rst:role:: gherkin:then

    Alias for :rst:role:`gherkin:step`.

.. rst:role:: gherkin:and

    Alias for :rst:role:`gherkin:step`.

.. rst:role:: gherkin:but

    Alias for :rst:role:`gherkin:step`.


.. _directives:

Directives
==========

While this can be unusual, |project| provides directives to write feature
definitions in ReStructuredText instead of in Gherkin.  Since there are no
automation framework the would support this way of writing features, it can
only be used for documentation purposes.

Directives can (or must) be nested in each other, the same way keywords
are nested and indented when using the Gherkin grammar.


.. rst:directive:: gherkin:feature

    Documents a Gherkin *Feature*.

    .. code-block:: rst

        .. gherkin:feature:: Some documented Feature

            Here You can add scenarios and more.

    .. admonition:: Result

        .. gherkin:feature:: Some documented Feature

            Here You can add scenarios and more.


.. rst:directive:: gherkin:rule

    Documents a Gherkin *Rule*.

    .. code-block:: rst

        .. gherkin:rule:: Some documented Rule

            Here You can add scenarios and more.

    .. admonition:: Result

        .. gherkin:rule:: Some documented Rule

            Here You can add scenarios and more.


.. rst:directive:: gherkin:scenario

    Documents a Gherkin *Scenario*.

    .. code-block:: rst

        .. gherkin:scenario:: Some documented Scenario

            Here You can add steps.

    .. admonition:: Result

        .. gherkin:scenario:: Some documented Scenario

            Here You can add steps.

.. rst:directive:: gherkin:example

    Alias of :rst:dir:`gherkin:scenario`.

.. rst:directive:: gherkin:template

    Alias of :rst:dir:`gherkin:scenario`.

.. rst:directive:: gherkin:outline

    Alias of :rst:dir:`gherkin:scenario`.

.. rst:directive:: gherkin:background

    Documents a Gherkin *Background*.

    .. code-block:: rst

        .. gherkin:background:: Some documented Background

            Here You can add steps.

    .. admonition:: Result

        .. gherkin:background:: Some documented Background

            Here You can add steps.

.. rst:directive:: gherkin:step

    Documents a Gherkin *Step*.

    .. code-block:: rst

        .. gherkin:step:: Some documented Step

            Here You can add some content.

    .. admonition:: Result

        .. gherkin:step:: Some documented Step

            Here You can add some content.

    Using one of the below directive would render the appropriate keyword
    (``Given``, ``When``, ...).

.. rst:directive:: gherkin:given

    Alias of :rst:dir:`gherkin:step`.

.. rst:directive:: gherkin:when

    Alias of :rst:dir:`gherkin:step`.

.. rst:directive:: gherkin:then

    Alias of :rst:dir:`gherkin:step`.

.. rst:directive:: gherkin:and

    Alias of :rst:dir:`gherkin:step`.

.. rst:directive:: gherkin:but

    Alias of :rst:dir:`gherkin:step`.
