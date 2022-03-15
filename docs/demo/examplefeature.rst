.. _examplefeature:

##########################
Example feature definition
##########################


.. gherkin:feature:: XRef with Sphinx-Gherkin

    Lenghty description here with an `hyperlink <https://example.com>`__.

    And various ways of cross-referencing elements:

    *   The keyword's summary can be used to build a target by separating
        them with dots ``.``.

        .. code-block:: rst

            :gherkin:step:`XRef with Sphinx-Gherkin.Minimalistic example.I can hear the light`

        .. admonition:: Result

            :gherkin:step:`XRef with Sphinx-Gherkin.Minimalistic example.I can hear the light`

    *   Dots and the begining or end of the summary are stripped in the
        internal representation. Other dots may break things.

        .. code-block:: rst

            :gherkin:scenario:`XRef with Sphinx-Gherkin.Ending with a dot`

        .. admonition:: Result

            :gherkin:scenario:`XRef with Sphinx-Gherkin.Ending with a dot`

    *   The target need not be fully namespaced.  The only requirement is
        that only one cross reference result is yielded.

        .. code-block:: rst

            :gherkin:rule:`My example Rule`

        .. admonition:: Result

            :gherkin:rule:`My example Rule`

    *   Prepending parent summaries is only needed when there is ambiguity.

        .. code-block:: rst

            :gherkin:step:`XRef with Sphinx-Gherkin.Minimalistic example.this is duplicated`

        .. admonition:: Result

            :gherkin:step:`XRef with Sphinx-Gherkin.Minimalistic example.this is duplicated`

    *   It is not needed to prepend the whole summary paths to resolve ambiguity.

        .. code-block:: rst

            :gherkin:step:`Minimalistic example.this is duplicated`

        .. admonition:: Result

            :gherkin:step:`Minimalistic example.this is duplicated`

    *   When documenting from **within** a keyword definition, you can use
        a ``.`` prefix to your target to indicate a relative target.

        .. code-block:: rst

            :gherkin:scenario:`.duplicated`

        .. admonition:: Result

            :gherkin:scenario:`.duplicated`

    *   The empty string is a valid summary

        .. code-block:: rst

            :gherkin:background:`My example Rule.`

        .. admonition:: Result

            :gherkin:background:`My example Rule.`

    *   The object ID you want to cross-refence.  Its value is built with
        an unstable algorithm. While it can be used as a cross-reference
        target, it probably shouldn't.

        .. code-block:: rst

            :gherkin:step:`feature-XRef-with-Sphinx-Gherkin.scenario-Minimalistic-example.step-then-I-can-hear-the-light`

        .. admonition:: Result

            :gherkin:step:`feature-XRef-with-Sphinx-Gherkin.scenario-Minimalistic-example.step-then-I-can-hear-the-light`

    .. gherkin:background:: a simple example background

        .. gherkin:given:: the minimalism inside a background

    .. gherkin:scenario:: Minimalistic example

        .. gherkin:given:: some markdown

            .. code-block:: markdown

                Markdown docstring

        .. gherkin:and:: this is duplicated

        .. gherkin:and:: a data table

            +--------+
            | header |
            +--------+
            | one    |
            +--------+
            | two    |
            +--------+

        .. gherkin:when:: the sky is blue

        .. gherkin:then:: I can hear the light

    .. gherkin:scenario:: also minimalistic

        .. gherkin:given:: the minimalism

        .. gherkin:and:: this is duplicated

    .. gherkin:scenario:: Ending with a dot.

    .. gherkin:scenario:: duplicated

        .. gherkin:given:: Something

    .. gherkin:rule:: My example Rule

        .. gherkin:background::

            .. gherkin:given:: a rule background step

        .. gherkin:outline:: with examples

            .. gherkin:given:: the <value> minimalism

            .. gherkin:examples::

                +-------+
                | value |
                +-------+
                | 1     |
                +-------+
                | 2     |
                +-------+

        .. gherkin:scenario:: duplicated
