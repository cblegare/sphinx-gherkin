from __future__ import annotations

from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from docutils.utils import assemble_option_dict
from sphinx.environment import BuildEnvironment
from sphinx.ext.autodoc import Options
from sphinx.ext.autodoc.directive import (
    DocumenterBridge,
    DummyOptionSpec,
    parse_generated_content,
)
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger
from sphinx.util.typing import OptionSpec

from sphinx_gherkin import (
    DocumentedKeyword,
    SphinxGherkinError,
    get_config_gherkin_sources,
    keyword_to_objtype,
)
from sphinx_gherkin.domain import GherkinDomain
from sphinx_gherkin.gherkin import (
    Background,
    DataTable,
    Document,
    Examples,
    Feature,
    Keyword,
    Rule,
    Scenario,
    Step,
)
from sphinx_gherkin.markup import KeywordDirectiveMixin

K = TypeVar("K", bound=Keyword, contravariant=True)

log = getLogger(__name__)


class AutoKeywordDescription(
    Generic[K], SphinxDirective, KeywordDirectiveMixin
):
    """A directive class for all autodoc directives. It works as a dispatcher of Documenters.

    It invokes a Documenter upon running. After the processing, it parses and returns
    the content generated by Documenter.
    """

    option_spec = DummyOptionSpec()
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    @property
    def keyword(self) -> str:
        name = str(self.name)
        if ":" in name[4:]:
            _, directivename = name.split(":", 1)
        else:
            directivename = name

        return directivename[4:].title()

    def run(self) -> List[Node]:
        lineno, source = self.get_source_and_line()
        log.debug(
            "[autodoc] %s:%s: input:\n%s", source, lineno, self.block_text
        )

        reporter = self.state.document.reporter

        # look up target Documenter
        objtype = keyword_to_objtype(self.keyword)
        documenter_class = cast(
            Type[Documenter[K]], self.env.app.registry.documenters[objtype]
        )

        # process the options with the selected documenter's option_spec
        try:
            documenter_options = Options(
                assemble_option_dict(
                    self.options.items(), documenter_class.option_spec
                )
            )
        except (KeyError, ValueError, TypeError) as exc:
            # an option is either unknown or has a wrong type
            log.error(
                "An option to %s is either unknown or has an invalid value: %s"
                % (self.name, exc),
                location=(self.env.docname, lineno),
            )
            return []

        document, keyword = self.get_gherkin_definition()

        # generate the output
        bridge = DocumenterBridge(
            self.env, reporter, documenter_options, lineno or 0, self.state
        )
        documenter = documenter_class(bridge, document, keyword)
        documenter.generate(more_content=self.content)
        if not bridge.result:
            return []

        log.debug("[autodoc] output:\n%s", "\n".join(bridge.result))

        # record all filenames as dependencies -- this will at least
        # partially make automatic invalidation possible
        self.record_dependencies(bridge)

        result = parse_generated_content(self.state, bridge.result, documenter)  # type: ignore # we hope for the best when sending are not exactly properly quackin Documenter duck
        return result

    def get_source_and_line(self) -> Tuple[Optional[int], Optional[str]]:
        reporter = self.state.document.reporter
        try:
            source, lineno = reporter.get_source_and_line(self.lineno)  # type: ignore
        except AttributeError:
            source, lineno = (None, None)
        return lineno, source

    def record_dependencies(self, bridge: DocumenterBridge) -> None:
        for fn in bridge.record_dependencies:
            self.state.document.settings.record_dependencies.add(fn)

    def get_gherkin_definition(self) -> Tuple[Document, K]:
        rst_keyword = self.get_name(self.arguments[0])
        found = self.gherkin_domain.gherkin_documents.find_one(rst_keyword)
        # Not sure how to check that we receive the actual right type K here.
        # Let's hope for the best!
        return found  # type: ignore # see above


class AutoFeatureDescription(AutoKeywordDescription[Feature]):
    allow_nesting = True

    def get_gherkin_definition(self) -> Tuple[Document, Feature]:
        sig = self.arguments[0]
        try:
            documents = self.gherkin_domain.gherkin_documents.documents
            for path in get_config_gherkin_sources(self.env).values():
                candidate = str(path.joinpath(sig))
                if candidate in documents:
                    document = documents[candidate]
                    keyword = document.feature
                    return document, keyword
            else:
                raise KeyError(sig)
        except KeyError:
            return super().get_gherkin_definition()


class AutoRuleDescription(AutoKeywordDescription[Rule]):
    allow_nesting = True


class AutoBackgroundDescription(AutoKeywordDescription[Background]):
    allow_nesting = True


class AutoScenarioDescription(AutoKeywordDescription[Scenario]):
    allow_nesting = True


class AutoExamplesDescription(AutoKeywordDescription[Examples]):
    allow_nesting = True


class AutoStepDescription(AutoKeywordDescription[Step]):
    pass


class AutoScenarioOutlineDescription(AutoKeywordDescription[Scenario]):
    @property
    def keyword(self) -> str:
        return "Scenario Outline"


class Documenter(Generic[K]):
    objtype = "object"
    content_indent = "    "

    option_spec: OptionSpec = {"noindex": directives.flag}

    titles_allowed = True
    allow_nesting = False

    def __init__(
        self,
        bridge: DocumenterBridge,
        gherkin_document: Document,
        keyword: K,
        indent: str = "",
    ):
        self.bridge = bridge
        self.env: BuildEnvironment = bridge.env
        self.options = bridge.genopt
        self.indent = indent
        self.gherkin_document = gherkin_document
        self.keyword = keyword

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """Called to see if a member can be documented by this Documenter."""
        return False

    @property
    def _domain(self) -> GherkinDomain:
        return GherkinDomain.get_instance(self.env)

    @property
    def documented_keyword(self) -> DocumentedKeyword:
        ancestry = self.gherkin_document.get_ancestry(self.keyword)

        return DocumentedKeyword.from_other(
            list(
                (keyword.keyword, keyword.summary)
                for keyword in reversed(ancestry)
            )
        )

    def add_line(self, line: str, source: str, *lineno: int) -> None:
        """Append one line of generated reST to the output."""
        if line.strip():  # not a blank line
            self.bridge.result.append(self.indent + line, source, *lineno)
        else:
            self.bridge.result.append("", source, *lineno)

    def get_sourcename(self) -> str:
        return self.gherkin_document.name

    def add_directive_header(self, sig: str) -> None:
        sourcename = self.get_sourcename()
        self.add_line(
            f".. {self._domain.name}:{self.get_directive_name()}:: {sig}",
            sourcename,
        )

        for option_name, value in self.format_options().items():
            self.add_line(
                f"{self.content_indent}:{option_name}: {value}", sourcename
            )

    def document_members(self) -> None:
        for child in self.get_child_keywords():
            objtype = self._domain.gherkin_documents.objtype_for_keyword_class(
                child.__class__
            )
            documenter_class = self.env.app.registry.documenters[objtype]
            if issubclass(documenter_class, Documenter):
                documenter = documenter_class(  # type: ignore
                    self.bridge, self.gherkin_document, child, self.indent  # type: ignore
                )
                documenter.generate()
            else:
                raise SphinxGherkinError(
                    f"Documenter of objtype '{objtype}' was of unexpected "
                    f"type '{documenter_class}'."
                )

    def get_directive_name(self) -> str:
        return self.objtype

    def format_options(self) -> Dict[str, str]:
        return {}

    def get_child_keywords(self) -> Sequence[Keyword]:
        return []

    def add_content(self, more_content: Optional[StringList]) -> None:
        if more_content:
            for line, src in zip(more_content.data, more_content.items):
                self.add_line(line, src[0], src[1])

    def generate(
        self,
        more_content: Optional[StringList] = None,
    ) -> None:
        self.bridge.record_dependencies.add(self.gherkin_document.name)
        sourcename = self.get_sourcename()

        # generate the directive header and options, if applicable
        self.add_directive_header(self.keyword.summary)
        self.add_line("", sourcename)

        # e.g. the module directive doesn't have content
        self.indent += self.content_indent

        # add all content (from docstrings, attribute docs etc.)
        self.env.ref_context[
            f"{self._domain.name}:scope"
        ] = self.documented_keyword
        self.add_content(more_content)

        self.add_line("", sourcename)

        # document members, if possible
        self.document_members()


class FeatureDocumenter(Documenter[Feature]):
    objtype = "feature"
    allow_nesting = True

    def format_options(self) -> Dict[str, str]:
        return {}

    def get_child_keywords(self) -> Sequence[Keyword]:
        return self.keyword.children

    def add_content(self, more_content: Optional[StringList]) -> None:
        for line in self.keyword.description.splitlines():
            self.add_line(line.lstrip(), self.get_sourcename())

        super().add_content(more_content)


class BackgroundDocumenter(Documenter[Background]):
    objtype = "background"
    allow_nesting = True

    def format_options(self) -> Dict[str, str]:
        return {}

    def get_child_keywords(self) -> Sequence[Keyword]:
        return self.keyword.steps


class ScenarioDocumenter(Documenter[Scenario]):
    objtype = "scenario"
    allow_nesting = True

    def format_options(self) -> Dict[str, str]:
        return {}

    def get_child_keywords(self) -> Sequence[Keyword]:
        return [*self.keyword.steps, *self.keyword.examples]


class RuleDocumenter(Documenter[Rule]):
    objtype = "rule"
    allow_nesting = True

    def format_options(self) -> Dict[str, str]:
        return {}

    def get_child_keywords(self) -> Sequence[Keyword]:
        return self.keyword.children


class StepDocumenter(Documenter[Step]):
    objtype = "step"

    def format_options(self) -> Dict[str, str]:
        return {}

    def get_directive_name(self) -> str:
        return self.keyword.keyword.strip().strip(":").lower()

    def add_content(self, more_content: Optional[StringList]) -> None:
        sourcename = self.get_sourcename()
        if self.keyword.docstring:
            self.add_line(
                f".. code-block:: {self.keyword.docstring.mediatype}",
                sourcename,
            )
            self.add_line("", sourcename)
            for line in self.keyword.docstring.content.splitlines():
                self.add_line(f"{self.content_indent}{line}", sourcename)
            self.add_line("", sourcename)
        if self.keyword.datatable:
            format_datatable(self, self.keyword.datatable)
            self.add_line("", sourcename)

        super().add_content(more_content)


class ExamplesDocumenter(Documenter[Examples]):
    objtype = "examples"
    allow_nesting = True

    def format_options(self) -> Dict[str, str]:
        return {}

    def add_content(self, more_content: Optional[StringList]) -> None:
        sourcename = self.get_sourcename()
        format_datatable(self, self.keyword.datatable)
        self.add_line("", sourcename)

        super().add_content(more_content)


def format_datatable(self: Documenter[K], datatable: DataTable) -> None:
    sourcename = self.get_sourcename()
    self.add_line(".. list-table::", sourcename)
    self.add_line("", sourcename)
    for line in datatable.values:
        first = True
        for cell in line:
            if first:
                self.add_line(f"{self.content_indent}* - {cell}", sourcename)
                first = False
            else:
                self.add_line(f"{self.content_indent}  - {cell}", sourcename)