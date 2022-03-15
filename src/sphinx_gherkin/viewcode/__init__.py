"""
Similar to :mod:`sphinx.ext.viewcode`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, Set, Tuple

from docutils import nodes
from docutils.nodes import Element, Node
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.environment import BuildEnvironment
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import status_iterator
from sphinx.util.logging import getLogger
from sphinx.util.nodes import make_refnode

from sphinx_gherkin import DOMAIN_NAME, NotFound, __version__, get_builder
from sphinx_gherkin.domain import GherkinDomain
from sphinx_gherkin.gherkin import Document, Keyword
from sphinx_gherkin.i18n import t_, t__
from sphinx_gherkin.sphinxapi import ExtensionMetadata, HtmlPage

OUTPUT_DIRNAME = "_gherkin_files"

log = getLogger(__name__)


def setup(app: Sphinx) -> ExtensionMetadata:
    app.require_sphinx("3")

    app.add_config_value(
        "gherkin_viewcode_objtypes",
        ["feature", "rule", "scenario"],
        "env",
        [list],
    )

    app.connect("env-purge-doc", env_purge_doc)
    app.connect("doctree-read", doctree_read)
    app.connect("html-collect-pages", collect_pages)
    app.add_post_transform(ViewcodeAnchorToggler)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def get_config_gherkin_viewcode_objtypes(env: BuildEnvironment) -> Set[str]:
    configured = env.config.gherkin_viewcode_objtypes

    return set(configured)


def env_purge_doc(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    pass
    # fixme
    # domain = GherkinDomain.get_instance(app)
    # domain.store.purge_usage(docname)


def doctree_read(app: Sphinx, doctree: Node) -> None:
    """
    Find HCL documentation and gather associated source code.

    Args:
        app:
            From the app we get the environment, our storage (cache).
        doctree:
            The document tree we will traverse in order to find HCL signatures.
    """
    domain = GherkinDomain.get_instance(app)

    done: Set[str] = set()

    for signature_node in _gen_gherkin_signature_nodes(doctree):
        _maybe_mark_signode_with_viewcode_anchor(signature_node, done, domain)


def _maybe_mark_signode_with_viewcode_anchor(
    signature_node: addnodes.desc_signature,
    done: Set[str],
    domain: GherkinDomain,
) -> None:
    backrefed_objtypes = get_config_gherkin_viewcode_objtypes(domain.env)
    rst_keyword = signature_node.get("keyword")
    if rst_keyword.objtype not in backrefed_objtypes:
        return

    object_id = signature_node.get("node_id")

    if object_id in done:
        return
    done.add(object_id)

    try:
        found: Tuple[Document, Keyword] = domain.gherkin_documents.find_one(
            rst_keyword
        )
        gherkin_document, gherkin_keyword = found
    except NotFound:
        log.info(
            f"Documented keyword '{rst_keyword}' could not be found "
            "in Gherkin documents."
        )
        return

    from sphinx_gherkin.viewcode.html import HtmlWriter

    writer = HtmlWriter(domain, Path(OUTPUT_DIRNAME))

    signature_node += viewcode_anchor(
        reftarget=str(writer.make_pagename(gherkin_document.name)),
        refid=object_id,
        refdoc=domain.env.docname,
    )


class ViewcodeAnchorToggler(SphinxPostTransform):
    """
    Convert or remove :class:`~viewcode_anchor`.
    """

    default_priority = 100

    def run(self, **kwargs: Any) -> None:
        if is_supported_builder(self.app):
            self.convert_viewcode_anchors()
        else:
            self.remove_viewcode_anchors()

    def convert_viewcode_anchors(self) -> None:
        for node in self.document.findall(viewcode_anchor):
            anchor = nodes.inline("", t_("[source]"), classes=["viewcode-link"])
            refnode = make_refnode(
                get_builder(self.app),
                node["refdoc"],
                node["reftarget"],
                node["refid"],
                anchor,
            )
            node.replace_self(refnode)

    def remove_viewcode_anchors(self) -> None:
        for node in list(self.document.findall(viewcode_anchor)):
            node.parent.remove(node)


def is_supported_builder(app: Sphinx) -> bool:
    if not isinstance(app.builder, Builder):
        return False

    if app.builder.format != "html":
        return False
    elif app.builder.name == "singlehtml":
        return False
    elif (
        app.builder.name.startswith("epub")
        and not app.builder.config.viewcode_enable_epub
    ):
        return False
    else:
        return True


def collect_pages(app: Sphinx) -> Iterator[HtmlPage]:
    from sphinx_gherkin.viewcode.html import HtmlWriter

    domain = GherkinDomain.get_instance(app)
    writer = HtmlWriter(domain, Path(OUTPUT_DIRNAME))

    gherkin_files = sorted(domain.gherkin_documents.get_documented_files())

    for gherkin_file in status_iterator(
        gherkin_files,
        t__("highlighting code..."),
        "blue",
        len(gherkin_files),
        app.verbosity,
        str,
    ):
        code_page = writer.gen_sourcecode_html(gherkin_file)
        yield code_page

    index_page = writer.gen_root_module_index()
    yield index_page


class viewcode_anchor(Element):
    """
    A sentinel node for viewcode anchors.

    Nodes of this type will be

    *   converted to anchors in supported builders or
    *   removed otherwise.

    This happens as a post transform phase.
    See also :class:`~ViewcodeAnchorToggler`.
    """


def _gen_gherkin_signature_nodes(
    node: Node,
) -> Iterator[addnodes.desc_signature]:
    def condition(candidate: Node) -> bool:
        return (
            isinstance(candidate, addnodes.desc)
            and candidate.get("domain") == DOMAIN_NAME
        )

    description_node: nodes.Node
    for description_node in node.findall(condition=condition):

        signature_node: addnodes.desc_signature
        for signature_node in description_node.findall(  # type: ignore # error: <nothing> has no attribute "findall" ?!?
            addnodes.desc_signature
        ):
            yield signature_node
