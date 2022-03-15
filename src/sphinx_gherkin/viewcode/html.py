from __future__ import annotations

import os
from pathlib import Path
from types import TracebackType
from typing import Any, List, Optional, Sequence, Tuple, Type, Union

from sphinx.util.logging import getLogger

from sphinx_gherkin import (
    get_builder,
    get_gherkin_file_symbolic_path,
    get_highlighter,
)
from sphinx_gherkin.domain import GherkinDomain
from sphinx_gherkin.gherkin import Document, Keyword
from sphinx_gherkin.i18n import t_
from sphinx_gherkin.sphinxapi import HtmlPage
from sphinx_gherkin.viewcode import get_config_gherkin_viewcode_objtypes

log = getLogger(__name__)


class HtmlWriter:
    def __init__(self, domain: GherkinDomain, output_dirname: Path):
        self._domain = domain
        self._output_dirname = Path(output_dirname)

        self._highlighter = get_highlighter(domain.env)

    def make_pagename(self, gherkin_file: Union[str, Path]) -> Path:
        page_name = self._output_dirname.joinpath(
            self.get_symbolic_path(gherkin_file)
        )
        return page_name

    def gen_sourcecode_html(self, gherkin_file: Union[str, Path]) -> HtmlPage:
        code = self._domain.gherkin_documents.get_code(gherkin_file)
        pagename = self.make_pagename(gherkin_file)
        highlighted_code = self.highlight_code(code)

        annotated_highlighted_code = self._add_backlinks_to_documentation(
            highlighted_code, gherkin_file
        )

        log.debug(f"Emitting HTML for {gherkin_file}")
        context = {
            "title": self.get_symbolic_path(gherkin_file),
            "body": (
                t_("<h1>Source code for %s</h1>")
                % self.get_symbolic_path(gherkin_file)
                + "\n"
                + "\n".join(annotated_highlighted_code)
            ),
        }
        return HtmlPage(str(pagename), context, "page.html")

    def gen_root_module_index(self) -> HtmlPage:
        pagename = self._output_dirname.joinpath("index")

        html_list: List[str] = []
        html = Html(html_list)

        with html.tag("ul"):
            for (
                document_name,
                document,
            ) in sorted(self._domain.gherkin_documents.documents.items()):
                with html.tag("li"):
                    with html.tag(
                        "a",
                        href=self._urito(
                            pagename,
                            self._output_dirname.joinpath(
                                self.get_symbolic_path(document_name)
                            ),
                        ),
                    ):
                        html.append(document.feature.summary)

        context = {
            "title": t_("Overview: Gherkin code"),
            "body": (
                t_("<h1>All features for which code is available</h1>")
                + "\n"
                + "\n".join(html_list)
            ),
        }
        return HtmlPage(str(pagename), context, "page.html")

    def highlight_code(self, code: Sequence[str]) -> List[str]:
        lexer = "gherkin"

        highlighted = self._highlighter.highlight_block(
            os.linesep.join(code), lexer, linenos=False
        )
        highlighted_lines = highlighted.splitlines()
        before, after = highlighted_lines[0].split("<pre>")
        highlighted_lines[0:1] = [before + "<pre>", after]

        return highlighted_lines

    def get_symbolic_path(self, gherkin_file: Union[str, Path]) -> Path:
        """
        Return the path to a file name starting with the root module's name.
        """
        return get_gherkin_file_symbolic_path(gherkin_file, self._domain.env)

    def _add_backlinks_to_documentation(
        self,
        highlighted_code: List[str],
        gherkin_file: Union[str, Path],
    ) -> List[str]:
        pagename = self.make_pagename(gherkin_file)
        for line_number, line_of_code in enumerate(highlighted_code):
            if line_of_code.startswith("<span"):
                first_line_of_code = line_number
                break
        else:
            first_line_of_code = 0

        backrefed_objtypes = get_config_gherkin_viewcode_objtypes(
            self._domain.env
        )

        for documented_object in self._domain.get_objects(
            filepath=gherkin_file
        ):
            if documented_object.type not in backrefed_objtypes:
                continue
            backlink = (
                f"{self._urito(pagename, documented_object.docname)}"
                "#"
                f"{documented_object.anchor}"
            )
            rst_keyword = self._domain.get_keyword(documented_object.name)
            found: Tuple[
                Document, Keyword
            ] = self._domain.gherkin_documents.find_one(rst_keyword)
            _, keyword = found

            definition_starting_line = (
                keyword.location.start.line + first_line_of_code
            )
            definition_ending_line = (
                keyword.location.end.line + first_line_of_code
            )
            highlighted_code[definition_starting_line] = "".join(
                [
                    f'<div class="viewcode-block" id="{documented_object.name}">',
                    f'<a class="viewcode-back" href="{backlink}">',
                    f"{t_('[docs]')}</a>{highlighted_code[definition_starting_line]}",
                ]
            )
            highlighted_code[definition_ending_line] += "</div>"
        return highlighted_code

    def _urito(
        self,
        from_page: Union[str, Path],
        to_page: Union[str, Path],
        typ: Optional[str] = None,
    ) -> str:
        return get_builder(self._domain.env).get_relative_uri(
            str(from_page), str(to_page), typ  # type: ignore # typ is wrongly typed upstream
        )


class Html:
    class _inner(object):
        def __init__(self, tagger: Html, tag: str, **attributes: str):
            self.tagger = tagger
            self.tag = tag
            self.attributes = attributes

        def __enter__(self) -> None:
            if self.attributes:
                attribute_str = " ".join(
                    f'{key}="{value}"' for key, value in self.attributes.items()
                )
                self.tagger.append(f"<{self.tag} {attribute_str}>")
            else:
                self.tagger.append(f"<{self.tag}>")
            self.tagger.indent_count += 1

        def __exit__(
            self,
            exctype: Optional[Type[BaseException]],
            excvalue: Optional[BaseException],
            traceback: Optional[TracebackType],
        ) -> None:
            self.tagger.indent_count -= 1
            self.tagger.append(f"</{self.tag}>")

    def __init__(
        self,
        container: List[str],
        initial_indent_count: int = 0,
        indent_increment: str = "  ",
    ):
        self.container = container
        self.indent_count = initial_indent_count
        self.indent_increment = indent_increment

    def tag(self, tag: str, **attributes: str) -> Any:
        return self._inner(self, tag, **attributes)

    def append(self, some_html: str) -> None:
        self.container.append(
            f"{self.indent_increment * self.indent_count}{some_html}"
        )
