"""
Basic Sphinx markup implementations
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

from docutils import nodes
from docutils.nodes import Element, Node, system_message
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util.logging import getLogger
from sphinx.util.typing import OptionSpec

from sphinx_gherkin import (
    DocumentedKeyword,
    SphinxGherkinError,
    keyword_to_objtype,
)
from sphinx_gherkin.domain import GherkinDomain
from sphinx_gherkin.sphinxapi import SphinxGeneralIndexEntry

log = getLogger(__name__)


class ScopedRefContextMixin:
    allow_nesting = False

    def _ref_context_key(self, key: str) -> str:
        return f"{self.domain}:{key}"  # type: ignore

    def push_ref_context_stack(self, key: str, value: Any) -> Any:
        stack = self.get_ref_context_stack(key)
        stack.append(value)

    def get_ref_context_stack(self, key: str) -> List[Any]:
        stack = self.env.ref_context.setdefault(self._ref_context_key(key), [])  # type: ignore
        if isinstance(stack, list):
            return stack
        else:
            raise SphinxGherkinError(
                f"ref_context for '{self._ref_context_key(key)}' was of unexpected "
                f"type '{type(stack)}'."
            )

    def peek_ref_context_stack(self, key: str) -> Optional[List[Any]]:
        stack = self.env.ref_context.setdefault(f"{self._ref_context_key(key)}", [])  # type: ignore
        if isinstance(stack, list) and stack:
            return stack[-1]  # type: ignore # data from ref_context is untyped
        else:
            return None

    def pop_ref_context_stack(self, key: str) -> Any:
        stack = self.get_ref_context_stack(key)
        if self.allow_nesting:
            try:
                stack.pop()
            except IndexError:
                pass


class KeywordDirectiveMixin(ScopedRefContextMixin):
    @property
    def keyword(self) -> str:
        name = self.name  # type: ignore # stateful mixin is hacky, we know
        if ":" in name:
            _, _keyword = name.split(":", 1)
        else:
            _keyword = name

        return str(_keyword).title()

    @property
    def objtype(self) -> str:
        return keyword_to_objtype(self.keyword)

    @objtype.setter
    def objtype(self, value: Any) -> None:
        pass

    @property
    def domain(self) -> str:
        return self.gherkin_domain.name

    @domain.setter
    def domain(self, value: Any) -> None:
        pass

    @property
    def gherkin_domain(self) -> GherkinDomain:
        return GherkinDomain.get_instance(self.env)  # type: ignore # a stateful mixin is not cleanly typed.

    def get_name(self, sig: str) -> DocumentedKeyword:
        parent = self.peek_ref_context_stack("scopes")
        name = (self.keyword, sig)
        if not parent:
            scope = (name,)
        else:
            scope = tuple([parent, name])  # type: ignore # stuff from the ref_context are untyped
        name_object = DocumentedKeyword.from_other(scope)
        return name_object


class GherkinDirective(  # type: ignore # We hacked "domain" and "objtype"
    ObjectDescription[DocumentedKeyword], KeywordDirectiveMixin
):
    option_spec: OptionSpec = {
        "noindex": directives.flag,
    }


class KeywordDescription(GherkinDirective):
    required_arguments = 0
    optional_arguments = 1
    option_spec: OptionSpec = {
        "noindex": directives.flag,
        "alias": directives.unchanged,
    }

    allow_nesting = False

    @property
    def object_id(self) -> str:
        if hasattr(self, "_object_id"):
            return str(getattr(self, "_object_id"))
        else:
            raise SphinxGherkinError(
                f"Premature access to {self.__class__}.object_id"
            )

    @object_id.setter
    def object_id(self, value: str) -> None:
        if not hasattr(self, "_object_id"):
            setattr(self, "_object_id", value)

    def run(self) -> List[Node]:
        if not self.arguments:
            self.arguments.append("")
        return super().run()

    def handle_signature(
        self, sig: str, signode: addnodes.desc_signature
    ) -> DocumentedKeyword:
        name = self.get_name(sig)

        signature_nodes = self.make_signature_nodes(name)
        signode.extend(signature_nodes)

        node_id = name.make_node_id(self.env, self.state.document)

        self.object_id = node_id

        signode["keyword"] = name
        signode["signature"] = sig
        signode["node_id"] = node_id

        return name

    def add_target_and_index(
        self,
        name: DocumentedKeyword,
        sig: str,
        signode: addnodes.desc_signature,
    ) -> None:
        signature_node_id = signode["node_id"]
        signode["ids"].append(signature_node_id)

        self.state.document.note_explicit_target(signode)

        self.gherkin_domain.note_keyword(
            self.object_id, name, signature_node_id, location=signode
        )

    def before_content(self) -> None:
        """
        Setup the environment to give signature context to the content.

        This is called after handling the signatures and before parsing
        the content.  We push the current signature on top of a stack in
        the env.  This enable us to use relative roles from within
        definition, and thus enable a lot shorter cross-ref role markup.

        Anything "pushed" here must be "poped" in :meth:`~after_content`.
        """
        # In the Gherkin context, :attr:`~names` should always have only
        # one item, which is the Gherkin keyword signature, or summary.
        # This summary can also be the empty string.
        name: DocumentedKeyword = self.names[0]
        if self.allow_nesting:
            self.push_ref_context_stack("scopes", name)
        self.env.ref_context[f"{self.domain}:scope"] = name

    def after_content(self) -> None:
        self.pop_ref_context_stack("scopes")

    def make_signature_nodes(
        self, name: DocumentedKeyword
    ) -> List[nodes.Element]:
        keyword_nodes = self.make_keyword_nodes(name)
        summary_nodes = self.make_summary_nodes(name)

        signature_nodes = [
            *keyword_nodes,
            addnodes.desc_sig_space(),
            *summary_nodes,
        ]
        return signature_nodes

    def make_summary_nodes(
        self, name: DocumentedKeyword
    ) -> List[nodes.Element]:
        return [addnodes.desc_name(name.summary, "", nodes.Text(name.summary))]

    def make_keyword_nodes(
        self, name: DocumentedKeyword
    ) -> Sequence[nodes.Element]:
        keyword_nodes = [
            addnodes.desc_annotation(
                name.keyword,
                "",
                nodes.Text(name.keyword.title()),
                addnodes.desc_sig_punctuation("", ":"),
            )
        ]
        return keyword_nodes


class FeatureDescription(KeywordDescription):
    allow_nesting = True


class RuleDescription(KeywordDescription):
    allow_nesting = True


class BackgroundDescription(KeywordDescription):
    allow_nesting = True


class ScenarioDescription(KeywordDescription):
    allow_nesting = True


class ExamplesDescription(KeywordDescription):
    allow_nesting = True


class StepDescription(KeywordDescription):
    def make_keyword_nodes(
        self, name: DocumentedKeyword
    ) -> Sequence[nodes.Element]:
        keyword_nodes = [
            addnodes.desc_annotation(
                name.keyword, "", nodes.Text(name.keyword.title())
            )
        ]
        return keyword_nodes


class ScenarioOutlineDescription(KeywordDescription):
    @property
    def keyword(self) -> str:
        return "Scenario Outline"


class GherkinCrossReferenceRole(XRefRole):
    """
    Define a gherkin object reference role.

    Cross referencing gherkin objects works alike crossreference to
    objects of the Python domain.

    The customization of a standard cross-reference can be done either
    by supplying constructor parameters or subclassing and overwriting
    the :meth:`sphinx.roles.XRefRole.process_link` and/or
    the :meth:`sphinx.roles.XRefRole.result_nodes` methods.
    """

    def process_link(
        self,
        env: BuildEnvironment,
        refnode: Element,
        has_explicit_title: bool,
        title: str,
        target: str,
    ) -> Tuple[str, str]:
        """
        Process link for a given cross-reference role.

        See also:
            The parent class method docstring is something like

                Called after parsing title and target text, and creating
                the reference node (given in *refnode*).  This method can
                alter the reference node and must return a new (or the same)
                ``(title, target)`` tuple.
        Args:
            env:
                Sphinx build environment.
            refnode:
                The created referenced node, which can be altered here.
            has_explicit_title:
                An explicit title in a role is when a display string is
                provided as part of the role's interpreted text. For example

                .. code-block: rst

                    :ref:`Here is an explicit title<some-reference-target>`

                would diplay an hyperlink to ``some-reference-target`` with
                ``Here is an explicit title`` as the link text.

                This value is also available as a instance member with the
                same name (``self.has_explicit_title``).
            title:
                The link title.
            target:
                The link target identifier.

        Returns:
            Title and target strings.
        """
        log.debug(f"Processing links for {self._role_string()}.")
        title, target = super().process_link(
            env, refnode, has_explicit_title, title, target
        )

        parent_definition = env.ref_context.get(
            "gherkin:scope", DocumentedKeyword.from_other([])
        )
        if "." == target[0:1]:
            newtarget = ".".join(
                part
                for part in [".".join(parent_definition.summaries), target[1:]]
                if part
            )
            if "." == target[-1]:
                newtarget += "."
            target = newtarget

        return title, target

    def result_nodes(
        self,
        document: nodes.document,
        env: BuildEnvironment,
        node: Element,
        is_ref: bool,
    ) -> Tuple[List[Node], List[system_message]]:
        """
        Add general index nodes just before returning the finished xref nodes.

        See also:
            The parent class method docstring is something like

                Called before returning the finished nodes.

                *node* is the reference node if one was created (*is_ref*
                is then true), else the content node.  This method can add
                other nodes and must return a ``(nodes, messages)`` tuple
                (the usual return value of a role function).
        Args:
            document:
                Source document where this ref was defined.
            env:
                Current Sphinx build environment.
            node:
                This role's node.
            is_ref:
                True when this is the reference node, else it's the content
                node.

        Returns:
            A tuple having a list of final nodes for this role and a list
            of system messages if appropriate.
        """
        log.debug(f"Resulting nodes for {self._role_string()}.")
        entry = SphinxGeneralIndexEntry(
            entrytype="single",
            entryname=self.target,
            targetid="",  # targetid=self.rawtext,
            mainname=node.attributes.get("refdoc", ""),
            key=None,
        )
        inode = addnodes.index(entries=[entry])
        node.append(inode)
        return [node], []

    def _role_string(self) -> str:
        if self.has_explicit_title:
            return f":{self.name}:`{self.title} <{self.target}>`"
        else:
            return f":{self.name}:`{self.target}`"
