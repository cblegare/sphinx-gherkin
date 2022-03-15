test-full-feature
=================

Minimal smoke test.


.. default-domain:: gherkin


.. feature:: Some feature

    Lenghty description here with

    And various ways of cross-referencing elements:

    *   The keyword's summary can be used to build a target by separating
        them with dots ``.``.

        .. code-block:: rst

            :step:`Some feature.Minimalistic.I can hear the light`

        .. admonition:: Result

            :step:`Some feature.Minimalistic.I can hear the light`

    *   Dots and the begining or end of the summary are stripped in the
        internal representation. Other dots may break things.

        .. code-block:: rst

            :step:`Some feature.Ending with a dot`

        .. admonition:: Result

            :step:`Some feature.Ending with a dot`

    *   The target need not be fully namespaced.  The only requirement is
        that only one cross reference result is yielded.

        .. code-block:: rst

            :rule:`My Rule`

        .. admonition:: Result

            :rule:`My Rule`

    *   Prepending parent summaries is only needed when there is ambiguity.

        .. code-block:: rst

            :step:`Some feature.Minimalistic.this is duplicated`

        .. admonition:: Result

            :step:`Some feature.Minimalistic.this is duplicated`

    *   It is not needed to prepend the whole summary paths to resolve ambiguity.

        .. code-block:: rst

            :step:`Minimalistic.this is duplicated`

        .. admonition:: Result

            :step:`Minimalistic.this is duplicated`

    *   When documenting from **within** a keyword definition, you can use
        a ``.`` prefix to your target to indicate a relative target.

        .. code-block:: rst

            :scenario:`.duplicated`

        .. admonition:: Result

            :scenario:`.duplicated`

    *   The empty string is a valid summary

        .. code-block:: rst

            :background:`My Rule.`

        .. admonition:: Result

            :background:`My Rule.`

    *   The object ID you want to cross-refence.  Its value is built with
        an unstable algorithm. While it can be used as a cross-reference
        target, it probably shouldn't.

        .. code-block:: rst

            :step:`feature-Some-feature.scenario-Minimalistic.step-then-I-can-hear-the-light`

        .. admonition:: Result

            :step:`feature-Some-feature.scenario-Minimalistic.step-then-I-can-hear-the-light`

    .. background:: a simple background

        .. given:: the minimalism inside a background

    .. scenario:: Minimalistic

        .. given:: some markdown

            .. code-block:: markdown

                Markdown docstring

        .. and:: this is duplicated

        .. and:: a data table

            +--------+
            | header |
            +--------+
            | one    |
            +--------+
            | two    |
            +--------+

        .. when:: the sky is blue

        .. then:: I can hear the light

    .. scenario:: also minimalistic

        .. given:: the minimalism

        .. and:: this is duplicated

    .. scenario:: Ending with a dot.

    .. scenario:: duplicated

        .. given:: Something

    .. rule:: My Rule

        .. background::

            .. given:: a rule background step

        .. outline:: with examples

            .. given:: the <value> minimalism

            .. examples::

                +-------+
                | value |
                +-------+
                | 1     |
                +-------+
                | 2     |
                +-------+

        .. scenario:: duplicated
