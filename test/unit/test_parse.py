from __future__ import annotations

import pytest

from sphinx_gherkin.gherkin import (
    Background,
    CodeLocation,
    CodeSpan,
    Comment,
    DataTable,
    DocString,
    Document,
    Examples,
    Feature,
    Rule,
    Scenario,
    Step,
    Tag,
)

sample = '''
Feature: Complex background
  We want to ensure PickleStep all have different IDs

  Background: a simple background
    Given the minimalism inside a background

  # Comment above
  # a second line above
  @some_tag
  Scenario: minimalistic
    # Comment within
    # a second line within
    Given some markdown
      """markdown
      Markdown docstring
      """
    And a data table
      | header |
      | one    |
      | two    |
    When the sky is blue
    Then I can listen to the light

  Scenario: also minimalistic
    Given the minimalism

  Rule: My Rule

    Background:
      Given a rule background step

    Scenario: with examples
      Given the <value> minimalism

      Examples:
        | value |
        | 1     |
        | 2     |
'''


def test_parse(expected_document):
    from sphinx_gherkin.gherkin import DefinitionBuildah

    builder = DefinitionBuildah("test_parse", sample)
    document = builder.parse()
    assert expected_document == document


@pytest.fixture
def expected_document():
    return Document(
        name="test_parse",
        lines=(
            "",
            "Feature: Complex background",
            "  We want to ensure PickleStep all have different IDs",
            "",
            "  Background: a simple background",
            "    Given the minimalism inside a background",
            "",
            "  # Comment above",
            "  # a second line above",
            "  @some_tag",
            "  Scenario: minimalistic",
            "    # Comment within",
            "    # a second line within",
            "    Given some markdown",
            '      """markdown',
            "      Markdown docstring",
            '      """',
            "    And a data table",
            "      | header |",
            "      | one    |",
            "      | two    |",
            "    When the sky is blue",
            "    Then I can listen to the light",
            "",
            "  Scenario: also minimalistic",
            "    Given the minimalism",
            "",
            "  Rule: My Rule",
            "",
            "    Background:",
            "      Given a rule background step",
            "",
            "    Scenario: with examples",
            "      Given the <value> minimalism",
            "",
            "      Examples:",
            "        | value |",
            "        | 1     |",
            "        | 2     |",
        ),
        feature=Feature(
            location=CodeSpan(
                start=CodeLocation(line=1, column=0),
                end=CodeLocation(line=39, column=0),
            ),
            keyword="Feature",
            name="Complex background",
            description="  We want to ensure PickleStep all have different IDs",
            tags=(),
            children=(
                Background(
                    location=CodeSpan(
                        start=CodeLocation(line=4, column=2),
                        end=CodeLocation(line=6, column=0),
                    ),
                    keyword="Background",
                    name="a simple background",
                    description="",
                    tags=(),
                    steps=(
                        Step(
                            location=CodeSpan(
                                start=CodeLocation(line=5, column=4),
                                end=CodeLocation(line=6, column=0),
                            ),
                            keyword="Given ",
                            text="the minimalism inside a background",
                            docstring=None,
                            datatable=None,
                        ),
                    ),
                ),
                Scenario(
                    location=CodeSpan(
                        start=CodeLocation(line=9, column=2),
                        end=CodeLocation(line=23, column=0),
                    ),
                    keyword="Scenario",
                    name="minimalistic",
                    description="",
                    tags=(
                        Tag(
                            location=CodeSpan(
                                start=CodeLocation(line=9, column=2),
                                end=CodeLocation(line=6, column=0),
                            ),
                            name="@some_tag",
                        ),
                    ),
                    steps=(
                        Step(
                            location=CodeSpan(
                                start=CodeLocation(line=13, column=4),
                                end=CodeLocation(line=17, column=0),
                            ),
                            keyword="Given ",
                            text="some markdown",
                            docstring=DocString(
                                location=CodeSpan(
                                    start=CodeLocation(line=14, column=6),
                                    end=CodeLocation(line=17, column=0),
                                ),
                                content="Markdown docstring",
                                mediatype="markdown",
                                delimiter='"""',
                            ),
                            datatable=None,
                        ),
                        Step(
                            location=CodeSpan(
                                start=CodeLocation(line=17, column=4),
                                end=CodeLocation(line=21, column=0),
                            ),
                            keyword="And ",
                            text="a data table",
                            docstring=None,
                            datatable=DataTable(
                                values=(("header",), ("one",), ("two",))
                            ),
                        ),
                        Step(
                            location=CodeSpan(
                                start=CodeLocation(line=21, column=4),
                                end=CodeLocation(line=22, column=0),
                            ),
                            keyword="When ",
                            text="the sky is blue",
                            docstring=None,
                            datatable=None,
                        ),
                        Step(
                            location=CodeSpan(
                                start=CodeLocation(line=22, column=4),
                                end=CodeLocation(line=23, column=0),
                            ),
                            keyword="Then ",
                            text="I can listen to the light",
                            docstring=None,
                            datatable=None,
                        ),
                    ),
                    examples=(),
                ),
                Scenario(
                    location=CodeSpan(
                        start=CodeLocation(line=24, column=2),
                        end=CodeLocation(line=26, column=0),
                    ),
                    keyword="Scenario",
                    name="also minimalistic",
                    description="",
                    tags=(),
                    steps=(
                        Step(
                            location=CodeSpan(
                                start=CodeLocation(line=25, column=4),
                                end=CodeLocation(line=26, column=0),
                            ),
                            keyword="Given ",
                            text="the minimalism",
                            docstring=None,
                            datatable=None,
                        ),
                    ),
                    examples=(),
                ),
                Rule(
                    location=CodeSpan(
                        start=CodeLocation(line=27, column=2),
                        end=CodeLocation(line=39, column=0),
                    ),
                    keyword="Rule",
                    name="My Rule",
                    description="",
                    tags=(),
                    children=(
                        Background(
                            location=CodeSpan(
                                start=CodeLocation(line=29, column=4),
                                end=CodeLocation(line=31, column=0),
                            ),
                            keyword="Background",
                            name="",
                            description="",
                            tags=(),
                            steps=(
                                Step(
                                    location=CodeSpan(
                                        start=CodeLocation(line=30, column=6),
                                        end=CodeLocation(line=31, column=0),
                                    ),
                                    keyword="Given ",
                                    text="a rule background step",
                                    docstring=None,
                                    datatable=None,
                                ),
                            ),
                        ),
                        Scenario(
                            location=CodeSpan(
                                start=CodeLocation(line=32, column=4),
                                end=CodeLocation(line=39, column=0),
                            ),
                            keyword="Scenario",
                            name="with examples",
                            description="",
                            tags=(),
                            steps=(
                                Step(
                                    location=CodeSpan(
                                        start=CodeLocation(line=33, column=6),
                                        end=CodeLocation(line=34, column=0),
                                    ),
                                    keyword="Given ",
                                    text="the <value> minimalism",
                                    docstring=None,
                                    datatable=None,
                                ),
                            ),
                            examples=(
                                Examples(
                                    location=CodeSpan(
                                        start=CodeLocation(line=35, column=6),
                                        end=CodeLocation(line=39, column=0),
                                    ),
                                    keyword="Examples",
                                    name="",
                                    description="",
                                    tags=(),
                                    datatable=DataTable(
                                        values=(("value",), ("1",), ("2",))
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            language="en",
        ),
        comments=(
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=7, column=0),
                    end=CodeLocation(line=7, column=17),
                ),
                text="  # Comment above",
            ),
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=8, column=0),
                    end=CodeLocation(line=8, column=23),
                ),
                text="  # a second line above",
            ),
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=11, column=0),
                    end=CodeLocation(line=11, column=20),
                ),
                text="    # Comment within",
            ),
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=12, column=0),
                    end=CodeLocation(line=12, column=26),
                ),
                text="    # a second line within",
            ),
        ),
        ancestry={
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=33, column=6),
                    end=CodeLocation(line=34, column=0),
                ),
                keyword="Given ",
                text="the <value> minimalism",
                docstring=None,
                datatable=None,
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=32, column=4),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Scenario",
                name="with examples",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=33, column=6),
                            end=CodeLocation(line=34, column=0),
                        ),
                        keyword="Given ",
                        text="the <value> minimalism",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(
                    Examples(
                        location=CodeSpan(
                            start=CodeLocation(line=35, column=6),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Examples",
                        name="",
                        description="",
                        tags=(),
                        datatable=DataTable(
                            values=(("value",), ("1",), ("2",))
                        ),
                    ),
                ),
            ),
            Examples(
                location=CodeSpan(
                    start=CodeLocation(line=35, column=6),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Examples",
                name="",
                description="",
                tags=(),
                datatable=DataTable(values=(("value",), ("1",), ("2",))),
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=32, column=4),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Scenario",
                name="with examples",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=33, column=6),
                            end=CodeLocation(line=34, column=0),
                        ),
                        keyword="Given ",
                        text="the <value> minimalism",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(
                    Examples(
                        location=CodeSpan(
                            start=CodeLocation(line=35, column=6),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Examples",
                        name="",
                        description="",
                        tags=(),
                        datatable=DataTable(
                            values=(("value",), ("1",), ("2",))
                        ),
                    ),
                ),
            ),
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=30, column=6),
                    end=CodeLocation(line=31, column=0),
                ),
                keyword="Given ",
                text="a rule background step",
                docstring=None,
                datatable=None,
            ): Background(
                location=CodeSpan(
                    start=CodeLocation(line=29, column=4),
                    end=CodeLocation(line=31, column=0),
                ),
                keyword="Background",
                name="",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=30, column=6),
                            end=CodeLocation(line=31, column=0),
                        ),
                        keyword="Given ",
                        text="a rule background step",
                        docstring=None,
                        datatable=None,
                    ),
                ),
            ),
            Background(
                location=CodeSpan(
                    start=CodeLocation(line=29, column=4),
                    end=CodeLocation(line=31, column=0),
                ),
                keyword="Background",
                name="",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=30, column=6),
                            end=CodeLocation(line=31, column=0),
                        ),
                        keyword="Given ",
                        text="a rule background step",
                        docstring=None,
                        datatable=None,
                    ),
                ),
            ): Rule(
                location=CodeSpan(
                    start=CodeLocation(line=27, column=2),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Rule",
                name="My Rule",
                description="",
                tags=(),
                children=(
                    Background(
                        location=CodeSpan(
                            start=CodeLocation(line=29, column=4),
                            end=CodeLocation(line=31, column=0),
                        ),
                        keyword="Background",
                        name="",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=30, column=6),
                                    end=CodeLocation(line=31, column=0),
                                ),
                                keyword="Given ",
                                text="a rule background step",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=32, column=4),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Scenario",
                        name="with examples",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=33, column=6),
                                    end=CodeLocation(line=34, column=0),
                                ),
                                keyword="Given ",
                                text="the <value> minimalism",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(
                            Examples(
                                location=CodeSpan(
                                    start=CodeLocation(line=35, column=6),
                                    end=CodeLocation(line=39, column=0),
                                ),
                                keyword="Examples",
                                name="",
                                description="",
                                tags=(),
                                datatable=DataTable(
                                    values=(("value",), ("1",), ("2",))
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=32, column=4),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Scenario",
                name="with examples",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=33, column=6),
                            end=CodeLocation(line=34, column=0),
                        ),
                        keyword="Given ",
                        text="the <value> minimalism",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(
                    Examples(
                        location=CodeSpan(
                            start=CodeLocation(line=35, column=6),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Examples",
                        name="",
                        description="",
                        tags=(),
                        datatable=DataTable(
                            values=(("value",), ("1",), ("2",))
                        ),
                    ),
                ),
            ): Rule(
                location=CodeSpan(
                    start=CodeLocation(line=27, column=2),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Rule",
                name="My Rule",
                description="",
                tags=(),
                children=(
                    Background(
                        location=CodeSpan(
                            start=CodeLocation(line=29, column=4),
                            end=CodeLocation(line=31, column=0),
                        ),
                        keyword="Background",
                        name="",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=30, column=6),
                                    end=CodeLocation(line=31, column=0),
                                ),
                                keyword="Given ",
                                text="a rule background step",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=32, column=4),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Scenario",
                        name="with examples",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=33, column=6),
                                    end=CodeLocation(line=34, column=0),
                                ),
                                keyword="Given ",
                                text="the <value> minimalism",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(
                            Examples(
                                location=CodeSpan(
                                    start=CodeLocation(line=35, column=6),
                                    end=CodeLocation(line=39, column=0),
                                ),
                                keyword="Examples",
                                name="",
                                description="",
                                tags=(),
                                datatable=DataTable(
                                    values=(("value",), ("1",), ("2",))
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=25, column=4),
                    end=CodeLocation(line=26, column=0),
                ),
                keyword="Given ",
                text="the minimalism",
                docstring=None,
                datatable=None,
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=24, column=2),
                    end=CodeLocation(line=26, column=0),
                ),
                keyword="Scenario",
                name="also minimalistic",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=25, column=4),
                            end=CodeLocation(line=26, column=0),
                        ),
                        keyword="Given ",
                        text="the minimalism",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ),
            DocString(
                location=CodeSpan(
                    start=CodeLocation(line=14, column=6),
                    end=CodeLocation(line=17, column=0),
                ),
                content="Markdown docstring",
                mediatype="markdown",
                delimiter='"""',
            ): Step(
                location=CodeSpan(
                    start=CodeLocation(line=13, column=4),
                    end=CodeLocation(line=17, column=0),
                ),
                keyword="Given ",
                text="some markdown",
                docstring=DocString(
                    location=CodeSpan(
                        start=CodeLocation(line=14, column=6),
                        end=CodeLocation(line=17, column=0),
                    ),
                    content="Markdown docstring",
                    mediatype="markdown",
                    delimiter='"""',
                ),
                datatable=None,
            ),
            Tag(
                location=CodeSpan(
                    start=CodeLocation(line=9, column=2),
                    end=CodeLocation(line=6, column=0),
                ),
                name="@some_tag",
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=9, column=2),
                    end=CodeLocation(line=23, column=0),
                ),
                keyword="Scenario",
                name="minimalistic",
                description="",
                tags=(
                    Tag(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        name="@some_tag",
                    ),
                ),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=13, column=4),
                            end=CodeLocation(line=17, column=0),
                        ),
                        keyword="Given ",
                        text="some markdown",
                        docstring=DocString(
                            location=CodeSpan(
                                start=CodeLocation(line=14, column=6),
                                end=CodeLocation(line=17, column=0),
                            ),
                            content="Markdown docstring",
                            mediatype="markdown",
                            delimiter='"""',
                        ),
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=17, column=4),
                            end=CodeLocation(line=21, column=0),
                        ),
                        keyword="And ",
                        text="a data table",
                        docstring=None,
                        datatable=DataTable(
                            values=(("header",), ("one",), ("two",))
                        ),
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=21, column=4),
                            end=CodeLocation(line=22, column=0),
                        ),
                        keyword="When ",
                        text="the sky is blue",
                        docstring=None,
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=22, column=4),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Then ",
                        text="I can listen to the light",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ),
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=13, column=4),
                    end=CodeLocation(line=17, column=0),
                ),
                keyword="Given ",
                text="some markdown",
                docstring=DocString(
                    location=CodeSpan(
                        start=CodeLocation(line=14, column=6),
                        end=CodeLocation(line=17, column=0),
                    ),
                    content="Markdown docstring",
                    mediatype="markdown",
                    delimiter='"""',
                ),
                datatable=None,
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=9, column=2),
                    end=CodeLocation(line=23, column=0),
                ),
                keyword="Scenario",
                name="minimalistic",
                description="",
                tags=(
                    Tag(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        name="@some_tag",
                    ),
                ),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=13, column=4),
                            end=CodeLocation(line=17, column=0),
                        ),
                        keyword="Given ",
                        text="some markdown",
                        docstring=DocString(
                            location=CodeSpan(
                                start=CodeLocation(line=14, column=6),
                                end=CodeLocation(line=17, column=0),
                            ),
                            content="Markdown docstring",
                            mediatype="markdown",
                            delimiter='"""',
                        ),
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=17, column=4),
                            end=CodeLocation(line=21, column=0),
                        ),
                        keyword="And ",
                        text="a data table",
                        docstring=None,
                        datatable=DataTable(
                            values=(("header",), ("one",), ("two",))
                        ),
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=21, column=4),
                            end=CodeLocation(line=22, column=0),
                        ),
                        keyword="When ",
                        text="the sky is blue",
                        docstring=None,
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=22, column=4),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Then ",
                        text="I can listen to the light",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ),
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=17, column=4),
                    end=CodeLocation(line=21, column=0),
                ),
                keyword="And ",
                text="a data table",
                docstring=None,
                datatable=DataTable(values=(("header",), ("one",), ("two",))),
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=9, column=2),
                    end=CodeLocation(line=23, column=0),
                ),
                keyword="Scenario",
                name="minimalistic",
                description="",
                tags=(
                    Tag(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        name="@some_tag",
                    ),
                ),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=13, column=4),
                            end=CodeLocation(line=17, column=0),
                        ),
                        keyword="Given ",
                        text="some markdown",
                        docstring=DocString(
                            location=CodeSpan(
                                start=CodeLocation(line=14, column=6),
                                end=CodeLocation(line=17, column=0),
                            ),
                            content="Markdown docstring",
                            mediatype="markdown",
                            delimiter='"""',
                        ),
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=17, column=4),
                            end=CodeLocation(line=21, column=0),
                        ),
                        keyword="And ",
                        text="a data table",
                        docstring=None,
                        datatable=DataTable(
                            values=(("header",), ("one",), ("two",))
                        ),
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=21, column=4),
                            end=CodeLocation(line=22, column=0),
                        ),
                        keyword="When ",
                        text="the sky is blue",
                        docstring=None,
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=22, column=4),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Then ",
                        text="I can listen to the light",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ),
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=21, column=4),
                    end=CodeLocation(line=22, column=0),
                ),
                keyword="When ",
                text="the sky is blue",
                docstring=None,
                datatable=None,
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=9, column=2),
                    end=CodeLocation(line=23, column=0),
                ),
                keyword="Scenario",
                name="minimalistic",
                description="",
                tags=(
                    Tag(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        name="@some_tag",
                    ),
                ),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=13, column=4),
                            end=CodeLocation(line=17, column=0),
                        ),
                        keyword="Given ",
                        text="some markdown",
                        docstring=DocString(
                            location=CodeSpan(
                                start=CodeLocation(line=14, column=6),
                                end=CodeLocation(line=17, column=0),
                            ),
                            content="Markdown docstring",
                            mediatype="markdown",
                            delimiter='"""',
                        ),
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=17, column=4),
                            end=CodeLocation(line=21, column=0),
                        ),
                        keyword="And ",
                        text="a data table",
                        docstring=None,
                        datatable=DataTable(
                            values=(("header",), ("one",), ("two",))
                        ),
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=21, column=4),
                            end=CodeLocation(line=22, column=0),
                        ),
                        keyword="When ",
                        text="the sky is blue",
                        docstring=None,
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=22, column=4),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Then ",
                        text="I can listen to the light",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ),
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=22, column=4),
                    end=CodeLocation(line=23, column=0),
                ),
                keyword="Then ",
                text="I can listen to the light",
                docstring=None,
                datatable=None,
            ): Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=9, column=2),
                    end=CodeLocation(line=23, column=0),
                ),
                keyword="Scenario",
                name="minimalistic",
                description="",
                tags=(
                    Tag(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        name="@some_tag",
                    ),
                ),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=13, column=4),
                            end=CodeLocation(line=17, column=0),
                        ),
                        keyword="Given ",
                        text="some markdown",
                        docstring=DocString(
                            location=CodeSpan(
                                start=CodeLocation(line=14, column=6),
                                end=CodeLocation(line=17, column=0),
                            ),
                            content="Markdown docstring",
                            mediatype="markdown",
                            delimiter='"""',
                        ),
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=17, column=4),
                            end=CodeLocation(line=21, column=0),
                        ),
                        keyword="And ",
                        text="a data table",
                        docstring=None,
                        datatable=DataTable(
                            values=(("header",), ("one",), ("two",))
                        ),
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=21, column=4),
                            end=CodeLocation(line=22, column=0),
                        ),
                        keyword="When ",
                        text="the sky is blue",
                        docstring=None,
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=22, column=4),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Then ",
                        text="I can listen to the light",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ),
            Step(
                location=CodeSpan(
                    start=CodeLocation(line=5, column=4),
                    end=CodeLocation(line=6, column=0),
                ),
                keyword="Given ",
                text="the minimalism inside a background",
                docstring=None,
                datatable=None,
            ): Background(
                location=CodeSpan(
                    start=CodeLocation(line=4, column=2),
                    end=CodeLocation(line=6, column=0),
                ),
                keyword="Background",
                name="a simple background",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=5, column=4),
                            end=CodeLocation(line=6, column=0),
                        ),
                        keyword="Given ",
                        text="the minimalism inside a background",
                        docstring=None,
                        datatable=None,
                    ),
                ),
            ),
            Background(
                location=CodeSpan(
                    start=CodeLocation(line=4, column=2),
                    end=CodeLocation(line=6, column=0),
                ),
                keyword="Background",
                name="a simple background",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=5, column=4),
                            end=CodeLocation(line=6, column=0),
                        ),
                        keyword="Given ",
                        text="the minimalism inside a background",
                        docstring=None,
                        datatable=None,
                    ),
                ),
            ): Feature(
                location=CodeSpan(
                    start=CodeLocation(line=1, column=0),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Feature",
                name="Complex background",
                description="  We want to ensure PickleStep all have different IDs",
                tags=(),
                children=(
                    Background(
                        location=CodeSpan(
                            start=CodeLocation(line=4, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        keyword="Background",
                        name="a simple background",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=5, column=4),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism inside a background",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Scenario",
                        name="minimalistic",
                        description="",
                        tags=(
                            Tag(
                                location=CodeSpan(
                                    start=CodeLocation(line=9, column=2),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                name="@some_tag",
                            ),
                        ),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=13, column=4),
                                    end=CodeLocation(line=17, column=0),
                                ),
                                keyword="Given ",
                                text="some markdown",
                                docstring=DocString(
                                    location=CodeSpan(
                                        start=CodeLocation(line=14, column=6),
                                        end=CodeLocation(line=17, column=0),
                                    ),
                                    content="Markdown docstring",
                                    mediatype="markdown",
                                    delimiter='"""',
                                ),
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=17, column=4),
                                    end=CodeLocation(line=21, column=0),
                                ),
                                keyword="And ",
                                text="a data table",
                                docstring=None,
                                datatable=DataTable(
                                    values=(("header",), ("one",), ("two",))
                                ),
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=21, column=4),
                                    end=CodeLocation(line=22, column=0),
                                ),
                                keyword="When ",
                                text="the sky is blue",
                                docstring=None,
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=22, column=4),
                                    end=CodeLocation(line=23, column=0),
                                ),
                                keyword="Then ",
                                text="I can listen to the light",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=24, column=2),
                            end=CodeLocation(line=26, column=0),
                        ),
                        keyword="Scenario",
                        name="also minimalistic",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=25, column=4),
                                    end=CodeLocation(line=26, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Rule(
                        location=CodeSpan(
                            start=CodeLocation(line=27, column=2),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Rule",
                        name="My Rule",
                        description="",
                        tags=(),
                        children=(
                            Background(
                                location=CodeSpan(
                                    start=CodeLocation(line=29, column=4),
                                    end=CodeLocation(line=31, column=0),
                                ),
                                keyword="Background",
                                name="",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=30, column=6
                                            ),
                                            end=CodeLocation(line=31, column=0),
                                        ),
                                        keyword="Given ",
                                        text="a rule background step",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                            ),
                            Scenario(
                                location=CodeSpan(
                                    start=CodeLocation(line=32, column=4),
                                    end=CodeLocation(line=39, column=0),
                                ),
                                keyword="Scenario",
                                name="with examples",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=33, column=6
                                            ),
                                            end=CodeLocation(line=34, column=0),
                                        ),
                                        keyword="Given ",
                                        text="the <value> minimalism",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                                examples=(
                                    Examples(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=35, column=6
                                            ),
                                            end=CodeLocation(line=39, column=0),
                                        ),
                                        keyword="Examples",
                                        name="",
                                        description="",
                                        tags=(),
                                        datatable=DataTable(
                                            values=(("value",), ("1",), ("2",))
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                language="en",
            ),
            Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=9, column=2),
                    end=CodeLocation(line=23, column=0),
                ),
                keyword="Scenario",
                name="minimalistic",
                description="",
                tags=(
                    Tag(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        name="@some_tag",
                    ),
                ),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=13, column=4),
                            end=CodeLocation(line=17, column=0),
                        ),
                        keyword="Given ",
                        text="some markdown",
                        docstring=DocString(
                            location=CodeSpan(
                                start=CodeLocation(line=14, column=6),
                                end=CodeLocation(line=17, column=0),
                            ),
                            content="Markdown docstring",
                            mediatype="markdown",
                            delimiter='"""',
                        ),
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=17, column=4),
                            end=CodeLocation(line=21, column=0),
                        ),
                        keyword="And ",
                        text="a data table",
                        docstring=None,
                        datatable=DataTable(
                            values=(("header",), ("one",), ("two",))
                        ),
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=21, column=4),
                            end=CodeLocation(line=22, column=0),
                        ),
                        keyword="When ",
                        text="the sky is blue",
                        docstring=None,
                        datatable=None,
                    ),
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=22, column=4),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Then ",
                        text="I can listen to the light",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ): Feature(
                location=CodeSpan(
                    start=CodeLocation(line=1, column=0),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Feature",
                name="Complex background",
                description="  We want to ensure PickleStep all have different IDs",
                tags=(),
                children=(
                    Background(
                        location=CodeSpan(
                            start=CodeLocation(line=4, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        keyword="Background",
                        name="a simple background",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=5, column=4),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism inside a background",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Scenario",
                        name="minimalistic",
                        description="",
                        tags=(
                            Tag(
                                location=CodeSpan(
                                    start=CodeLocation(line=9, column=2),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                name="@some_tag",
                            ),
                        ),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=13, column=4),
                                    end=CodeLocation(line=17, column=0),
                                ),
                                keyword="Given ",
                                text="some markdown",
                                docstring=DocString(
                                    location=CodeSpan(
                                        start=CodeLocation(line=14, column=6),
                                        end=CodeLocation(line=17, column=0),
                                    ),
                                    content="Markdown docstring",
                                    mediatype="markdown",
                                    delimiter='"""',
                                ),
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=17, column=4),
                                    end=CodeLocation(line=21, column=0),
                                ),
                                keyword="And ",
                                text="a data table",
                                docstring=None,
                                datatable=DataTable(
                                    values=(("header",), ("one",), ("two",))
                                ),
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=21, column=4),
                                    end=CodeLocation(line=22, column=0),
                                ),
                                keyword="When ",
                                text="the sky is blue",
                                docstring=None,
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=22, column=4),
                                    end=CodeLocation(line=23, column=0),
                                ),
                                keyword="Then ",
                                text="I can listen to the light",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=24, column=2),
                            end=CodeLocation(line=26, column=0),
                        ),
                        keyword="Scenario",
                        name="also minimalistic",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=25, column=4),
                                    end=CodeLocation(line=26, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Rule(
                        location=CodeSpan(
                            start=CodeLocation(line=27, column=2),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Rule",
                        name="My Rule",
                        description="",
                        tags=(),
                        children=(
                            Background(
                                location=CodeSpan(
                                    start=CodeLocation(line=29, column=4),
                                    end=CodeLocation(line=31, column=0),
                                ),
                                keyword="Background",
                                name="",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=30, column=6
                                            ),
                                            end=CodeLocation(line=31, column=0),
                                        ),
                                        keyword="Given ",
                                        text="a rule background step",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                            ),
                            Scenario(
                                location=CodeSpan(
                                    start=CodeLocation(line=32, column=4),
                                    end=CodeLocation(line=39, column=0),
                                ),
                                keyword="Scenario",
                                name="with examples",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=33, column=6
                                            ),
                                            end=CodeLocation(line=34, column=0),
                                        ),
                                        keyword="Given ",
                                        text="the <value> minimalism",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                                examples=(
                                    Examples(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=35, column=6
                                            ),
                                            end=CodeLocation(line=39, column=0),
                                        ),
                                        keyword="Examples",
                                        name="",
                                        description="",
                                        tags=(),
                                        datatable=DataTable(
                                            values=(("value",), ("1",), ("2",))
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                language="en",
            ),
            Scenario(
                location=CodeSpan(
                    start=CodeLocation(line=24, column=2),
                    end=CodeLocation(line=26, column=0),
                ),
                keyword="Scenario",
                name="also minimalistic",
                description="",
                tags=(),
                steps=(
                    Step(
                        location=CodeSpan(
                            start=CodeLocation(line=25, column=4),
                            end=CodeLocation(line=26, column=0),
                        ),
                        keyword="Given ",
                        text="the minimalism",
                        docstring=None,
                        datatable=None,
                    ),
                ),
                examples=(),
            ): Feature(
                location=CodeSpan(
                    start=CodeLocation(line=1, column=0),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Feature",
                name="Complex background",
                description="  We want to ensure PickleStep all have different IDs",
                tags=(),
                children=(
                    Background(
                        location=CodeSpan(
                            start=CodeLocation(line=4, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        keyword="Background",
                        name="a simple background",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=5, column=4),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism inside a background",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Scenario",
                        name="minimalistic",
                        description="",
                        tags=(
                            Tag(
                                location=CodeSpan(
                                    start=CodeLocation(line=9, column=2),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                name="@some_tag",
                            ),
                        ),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=13, column=4),
                                    end=CodeLocation(line=17, column=0),
                                ),
                                keyword="Given ",
                                text="some markdown",
                                docstring=DocString(
                                    location=CodeSpan(
                                        start=CodeLocation(line=14, column=6),
                                        end=CodeLocation(line=17, column=0),
                                    ),
                                    content="Markdown docstring",
                                    mediatype="markdown",
                                    delimiter='"""',
                                ),
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=17, column=4),
                                    end=CodeLocation(line=21, column=0),
                                ),
                                keyword="And ",
                                text="a data table",
                                docstring=None,
                                datatable=DataTable(
                                    values=(("header",), ("one",), ("two",))
                                ),
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=21, column=4),
                                    end=CodeLocation(line=22, column=0),
                                ),
                                keyword="When ",
                                text="the sky is blue",
                                docstring=None,
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=22, column=4),
                                    end=CodeLocation(line=23, column=0),
                                ),
                                keyword="Then ",
                                text="I can listen to the light",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=24, column=2),
                            end=CodeLocation(line=26, column=0),
                        ),
                        keyword="Scenario",
                        name="also minimalistic",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=25, column=4),
                                    end=CodeLocation(line=26, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Rule(
                        location=CodeSpan(
                            start=CodeLocation(line=27, column=2),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Rule",
                        name="My Rule",
                        description="",
                        tags=(),
                        children=(
                            Background(
                                location=CodeSpan(
                                    start=CodeLocation(line=29, column=4),
                                    end=CodeLocation(line=31, column=0),
                                ),
                                keyword="Background",
                                name="",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=30, column=6
                                            ),
                                            end=CodeLocation(line=31, column=0),
                                        ),
                                        keyword="Given ",
                                        text="a rule background step",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                            ),
                            Scenario(
                                location=CodeSpan(
                                    start=CodeLocation(line=32, column=4),
                                    end=CodeLocation(line=39, column=0),
                                ),
                                keyword="Scenario",
                                name="with examples",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=33, column=6
                                            ),
                                            end=CodeLocation(line=34, column=0),
                                        ),
                                        keyword="Given ",
                                        text="the <value> minimalism",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                                examples=(
                                    Examples(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=35, column=6
                                            ),
                                            end=CodeLocation(line=39, column=0),
                                        ),
                                        keyword="Examples",
                                        name="",
                                        description="",
                                        tags=(),
                                        datatable=DataTable(
                                            values=(("value",), ("1",), ("2",))
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                language="en",
            ),
            Rule(
                location=CodeSpan(
                    start=CodeLocation(line=27, column=2),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Rule",
                name="My Rule",
                description="",
                tags=(),
                children=(
                    Background(
                        location=CodeSpan(
                            start=CodeLocation(line=29, column=4),
                            end=CodeLocation(line=31, column=0),
                        ),
                        keyword="Background",
                        name="",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=30, column=6),
                                    end=CodeLocation(line=31, column=0),
                                ),
                                keyword="Given ",
                                text="a rule background step",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=32, column=4),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Scenario",
                        name="with examples",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=33, column=6),
                                    end=CodeLocation(line=34, column=0),
                                ),
                                keyword="Given ",
                                text="the <value> minimalism",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(
                            Examples(
                                location=CodeSpan(
                                    start=CodeLocation(line=35, column=6),
                                    end=CodeLocation(line=39, column=0),
                                ),
                                keyword="Examples",
                                name="",
                                description="",
                                tags=(),
                                datatable=DataTable(
                                    values=(("value",), ("1",), ("2",))
                                ),
                            ),
                        ),
                    ),
                ),
            ): Feature(
                location=CodeSpan(
                    start=CodeLocation(line=1, column=0),
                    end=CodeLocation(line=39, column=0),
                ),
                keyword="Feature",
                name="Complex background",
                description="  We want to ensure PickleStep all have different IDs",
                tags=(),
                children=(
                    Background(
                        location=CodeSpan(
                            start=CodeLocation(line=4, column=2),
                            end=CodeLocation(line=6, column=0),
                        ),
                        keyword="Background",
                        name="a simple background",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=5, column=4),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism inside a background",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=9, column=2),
                            end=CodeLocation(line=23, column=0),
                        ),
                        keyword="Scenario",
                        name="minimalistic",
                        description="",
                        tags=(
                            Tag(
                                location=CodeSpan(
                                    start=CodeLocation(line=9, column=2),
                                    end=CodeLocation(line=6, column=0),
                                ),
                                name="@some_tag",
                            ),
                        ),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=13, column=4),
                                    end=CodeLocation(line=17, column=0),
                                ),
                                keyword="Given ",
                                text="some markdown",
                                docstring=DocString(
                                    location=CodeSpan(
                                        start=CodeLocation(line=14, column=6),
                                        end=CodeLocation(line=17, column=0),
                                    ),
                                    content="Markdown docstring",
                                    mediatype="markdown",
                                    delimiter='"""',
                                ),
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=17, column=4),
                                    end=CodeLocation(line=21, column=0),
                                ),
                                keyword="And ",
                                text="a data table",
                                docstring=None,
                                datatable=DataTable(
                                    values=(("header",), ("one",), ("two",))
                                ),
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=21, column=4),
                                    end=CodeLocation(line=22, column=0),
                                ),
                                keyword="When ",
                                text="the sky is blue",
                                docstring=None,
                                datatable=None,
                            ),
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=22, column=4),
                                    end=CodeLocation(line=23, column=0),
                                ),
                                keyword="Then ",
                                text="I can listen to the light",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Scenario(
                        location=CodeSpan(
                            start=CodeLocation(line=24, column=2),
                            end=CodeLocation(line=26, column=0),
                        ),
                        keyword="Scenario",
                        name="also minimalistic",
                        description="",
                        tags=(),
                        steps=(
                            Step(
                                location=CodeSpan(
                                    start=CodeLocation(line=25, column=4),
                                    end=CodeLocation(line=26, column=0),
                                ),
                                keyword="Given ",
                                text="the minimalism",
                                docstring=None,
                                datatable=None,
                            ),
                        ),
                        examples=(),
                    ),
                    Rule(
                        location=CodeSpan(
                            start=CodeLocation(line=27, column=2),
                            end=CodeLocation(line=39, column=0),
                        ),
                        keyword="Rule",
                        name="My Rule",
                        description="",
                        tags=(),
                        children=(
                            Background(
                                location=CodeSpan(
                                    start=CodeLocation(line=29, column=4),
                                    end=CodeLocation(line=31, column=0),
                                ),
                                keyword="Background",
                                name="",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=30, column=6
                                            ),
                                            end=CodeLocation(line=31, column=0),
                                        ),
                                        keyword="Given ",
                                        text="a rule background step",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                            ),
                            Scenario(
                                location=CodeSpan(
                                    start=CodeLocation(line=32, column=4),
                                    end=CodeLocation(line=39, column=0),
                                ),
                                keyword="Scenario",
                                name="with examples",
                                description="",
                                tags=(),
                                steps=(
                                    Step(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=33, column=6
                                            ),
                                            end=CodeLocation(line=34, column=0),
                                        ),
                                        keyword="Given ",
                                        text="the <value> minimalism",
                                        docstring=None,
                                        datatable=None,
                                    ),
                                ),
                                examples=(
                                    Examples(
                                        location=CodeSpan(
                                            start=CodeLocation(
                                                line=35, column=6
                                            ),
                                            end=CodeLocation(line=39, column=0),
                                        ),
                                        keyword="Examples",
                                        name="",
                                        description="",
                                        tags=(),
                                        datatable=DataTable(
                                            values=(("value",), ("1",), ("2",))
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                language="en",
            ),
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=7, column=0),
                    end=CodeLocation(line=7, column=17),
                ),
                text="  # Comment above",
            ): None,
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=8, column=0),
                    end=CodeLocation(line=8, column=23),
                ),
                text="  # a second line above",
            ): None,
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=11, column=0),
                    end=CodeLocation(line=11, column=20),
                ),
                text="    # Comment within",
            ): None,
            Comment(
                location=CodeSpan(
                    start=CodeLocation(line=12, column=0),
                    end=CodeLocation(line=12, column=26),
                ),
                text="    # a second line within",
            ): None,
        },
    )
