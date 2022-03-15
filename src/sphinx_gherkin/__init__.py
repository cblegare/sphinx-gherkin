"""
This is **not** an API.
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.environment import BuildEnvironment
from sphinx.errors import SphinxError
from sphinx.highlighting import PygmentsBridge
from sphinx.util.logging import getLogger
from sphinx.util.nodes import make_id

from sphinx_gherkin.i18n import t__
from sphinx_gherkin.sphinxapi import ExtensionMetadata

if TYPE_CHECKING or sys.version_info < (3, 8, 0):
    from importlib_metadata import PackageNotFoundError, version
else:
    from importlib.metadata import PackageNotFoundError, version


package_dir = Path(__file__).parent.resolve()

# _package_name = __name__
_package_name = "sphinx_gherkin"

try:
    __version__ = str(version(_package_name))  # type: ignore # the typing is missing for this function
except PackageNotFoundError:
    # package is not installed
    __version__ = "(please install the package)"


log = getLogger(__name__)


DOMAIN_NAME = "gherkin"

KEYWORD_OBJTYPE = {
    "feature": "feature",
    "rule": "rule",
    "background": "background",
    "scenario": "scenario",
    "example": "scenario",
    "scenario outline": "scenario",
    "scenario template": "scenario",
    "outline": "scenario",
    "template": "scenario",
    "examples": "examples",
    "scenarios": "examples",
    "step": "step",
    "given": "step",
    "and": "step",
    "but": "step",
    "*": "step",
    "when": "step",
    "then": "step",
}


class ObjectId(str):
    pass


def keyword_to_objtype(keyword: str) -> str:
    return KEYWORD_OBJTYPE[keyword.strip().strip(":").lower()]


class SphinxGherkinError(SphinxError):
    category = "Sphinx-Gherkin error"


class NotFound(SphinxGherkinError):
    pass


class MultipleFound(SphinxGherkinError):
    pass


def setup(app: Sphinx) -> ExtensionMetadata:
    app.require_sphinx("3")

    app.add_config_value("gherkin_sources", app.srcdir, "env", [str, dict])
    app.add_config_value("gherkin_comment_markup", "", "env", [str])

    from sphinx_gherkin.markup.autodoc import Documenter

    for documenter_class in Documenter.__subclasses__():
        app.registry.add_documenter(
            documenter_class.objtype, documenter_class  # type: ignore # it is not a real documenter
        )

    from sphinx_gherkin.domain import GherkinDomain

    app.add_domain(GherkinDomain.new())

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def get_config_gherkin_comment_markup(env: BuildEnvironment) -> str:
    configured = env.config.gherkin_comment_markup

    return str(configured)


def get_config_gherkin_sources(
    env: BuildEnvironment,
) -> Dict[str, Path]:
    configured = env.config.gherkin_sources

    if not configured or not isinstance(configured, (str, Dict, Path)):
        raise SphinxGherkinError(
            t__(
                "No gherkin sources where configured in conf.py. "
                "Please provide a value to 'gherkin_sources'."
            )
        )

    if isinstance(configured, (str, Path)):
        configured = {Path(configured).name: configured}

    for name in configured:
        path = Path(configured[name])
        if not path.is_absolute():
            path = Path(env.project.srcdir, path)
        configured[name] = path

    return configured


def get_gherkin_file_symbolic_path(
    gherkin_file: Union[str, Path], env: BuildEnvironment
) -> Path:
    sources = get_config_gherkin_sources(env)
    gherkin_file = Path(gherkin_file)
    path = gherkin_file
    for folder in sources.values():
        try:
            sympath = gherkin_file.relative_to(folder)
        except ValueError:
            pass
        else:
            if not path or len(str(sympath)) < len(str(path)):
                path = sympath

    return path


def get_env(app_or_env: Union[Sphinx, BuildEnvironment]) -> BuildEnvironment:
    if isinstance(app_or_env, BuildEnvironment):
        return app_or_env
    if isinstance(app_or_env.env, BuildEnvironment):
        return app_or_env.env
    raise SphinxGherkinError("Build environment not ready.")


def get_app(app_or_env: Union[Sphinx, BuildEnvironment]) -> Sphinx:
    if isinstance(app_or_env, BuildEnvironment):
        return app_or_env.app
    return app_or_env


def get_builder(app_or_env: Union[Sphinx, BuildEnvironment]) -> Builder:
    app = get_app(app_or_env)
    if isinstance(app.builder, Builder):
        return app.builder

    raise SphinxGherkinError("Builder not ready.")


def get_highlighter(
    app_or_env: Union[Sphinx, BuildEnvironment]
) -> PygmentsBridge:
    builder = get_builder(app_or_env)

    if hasattr(builder, "highlighter"):
        return builder.highlighter  # type: ignore

    raise SphinxGherkinError("Unsupported builder.")


K = TypeVar("K", bound="DocumentedKeyword")


@dataclasses.dataclass(order=True, frozen=True)
class DocumentedKeyword:
    """
    The documented keyword is the whole signature including documented parents.

    Example:
        Given the following markup for documenting a feature

        .. code-block:: rst

            .. default-domain:: gherkin

            .. feature:: Some feature

                .. background:

                    .. given:: something in a background

                .. scenario:: minimalistic

                    .. given:: a first step

        Then, the following names will be defined for their respective directives:

        *   **Directive:**
                .. code-block:: rst

                    .. feature:: Some feature

            **value:**
                .. code-block:: python

                    (
                        ("Feature", "Some feature"),
                    )

        *   **Directive:**
                .. code-block:: rst

                    .. scenario:: minimalistic

            **value:**
                .. code-block:: python

                    (
                        ("Feature", "Some feature"),
                        ("Scenario", "minimalistic"),
                    )

        *   **Directive:**
                .. code-block:: rst

                    .. given:: a first step

            **value:**
                .. code-block:: python

                    (
                        ("Feature", "Some feature"),
                        ("Scenario", "minimalistic"),
                        ("Given", "a first step"),
                    )

        *   **Directive:**
                .. code-block:: rst

                    .. background:

            **value:**
                .. code-block:: python

                    (
                        ("Feature", "Some feature"),
                        ("Background", ""),
                    )
    """

    value: Tuple[Tuple[str, str], ...]

    @classmethod
    def null(cls: Type[K]) -> K:
        return cls(tuple())

    @classmethod
    def from_other(
        cls: Type[K], other: Sequence[Union[K, Tuple[str, str]]]
    ) -> K:
        """
        Maybe crappy but still the main constructor from something else.

        Examples:
            >>> keyword = DocumentedKeyword.from_other([("Scenario", "foo")])
            >>> keyword.summary
            'foo'
            >>> other = DocumentedKeyword.from_other([keyword])
            >>> keyword.summary ==other.summary
            True

        Args:
            other:

        Returns:
            A newly created documented keyword, built from the combination
            of what is in the parameter.
        """
        name: List[Tuple[str, str]] = []
        for ancestor in other:
            if isinstance(ancestor, DocumentedKeyword):
                name.extend(ancestor.value)
            else:
                name.append(ancestor)  # type: ignore # we already checked
        return cls(tuple(name))

    def __bool__(self) -> bool:
        return bool(self.value)

    @property
    def parent(self) -> DocumentedKeyword:
        parent_value = self.value[:-1]
        if parent_value:
            return DocumentedKeyword(parent_value)
        else:
            return DocumentedKeyword.null()

    @property
    def keyword(self) -> str:
        keyword, _ = self.value[-1]
        return keyword

    @property
    def keywords(self) -> Sequence[str]:
        return tuple(k for k, _ in self.value)

    @property
    def objtype(self) -> str:
        return keyword_to_objtype(self.keyword)

    @property
    def objtypes(self) -> Sequence[str]:
        return tuple(keyword_to_objtype(k) for k, _ in self.value)

    @property
    def summary(self) -> str:
        _, summary = self.value[-1]
        return summary

    @property
    def summaries(self) -> Sequence[str]:
        return tuple(s for _, s in self.value)

    @property
    def display_name(self) -> str:
        return f"{self.summary} ({self.keyword})"

    def make_node_id(
        self, env: BuildEnvironment, document: nodes.document, prefix: str = ""
    ) -> str:
        parts = []
        for keyword, summary in self.value:
            objtype = keyword_to_objtype(keyword)
            if objtype == "step":
                summary_slug = f"{self.keyword.lower()}-{summary.strip()}"
            else:
                summary_slug = summary.strip()
            parts.append(f"{objtype}-{summary_slug}")
        qualname = ".".join(parts)

        return make_id(env, document, prefix, qualname)
