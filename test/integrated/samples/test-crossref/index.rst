test-full-feature
=================

Minimal smoke test.


.. default-domain:: gherkin


.. feature:: Some feature

    .. background:: a simple background

        .. given:: the minimalism inside a background

    .. scenario:: Minimalistic

        .. given:: some markdown

            .. code-block:: markdown

                Markdown docstring

        .. and:: this is duplicated

        .. and:: a data tabe

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

    .. scenario:: duplicated
