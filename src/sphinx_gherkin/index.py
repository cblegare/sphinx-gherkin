from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from sphinx.domains import Index, IndexEntry

from sphinx_gherkin import (
    DocumentedKeyword,
    NotFound,
    get_gherkin_file_symbolic_path,
)
from sphinx_gherkin.domain import GherkinDomain
from sphinx_gherkin.sphinxapi import SphinxDomainObjectDescription


class GherkinDefinitionsIndex(Index):
    name = "keywordindex"
    localname = "Gherkin Keyword Index"
    shortname = localname

    def generate(
        self, docnames: Optional[Iterable[str]] = None
    ) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
        """
        Generate gherkin domain index entries.

        Note:
             Entries should be filtered by the docnames provided. To do.

        Args:
            docnames: Restrict source Restructured text documents to these.

        Returns:
            See :meth:`sphinx.domains.Index.generate` for details.
        """
        grouped: Dict[str, List[SphinxDomainObjectDescription]] = defaultdict(
            list
        )

        objects = self.domain.get_objects()

        name_entry: SphinxDomainObjectDescription
        for name_entry in objects:  # type: ignore
            grouped[name_entry.dispname].append(name_entry)

        content_working_copy = defaultdict(list)

        for display_name, entries in grouped.items():
            for letter, index_entry in self.method_name(display_name, entries):
                content_working_copy[letter].append(index_entry)

        # convert the dict to the sorted list of tuples expected
        content = sorted(content_working_copy.items())

        return content, True

    def method_name(
        self, display_name: str, entries: List[SphinxDomainObjectDescription]
    ) -> Iterator[Tuple[str, IndexEntry]]:
        # generate the expected output, shown below, from the above using the
        # first letter of the npc as a key to group thing
        #
        # name, subtype, docname, anchor, extra, qualifier, description
        #
        # This shows:
        #
        #     D
        #   - **Display Name** *(extra info)* **qualifier:** typ
        #       **Sub Entry** *(extra info)* **qualifier:** typ
        SUBTYPE_NORMAL = 0
        SUBTYPE_WITHSUBS = 1  # noqa: F841
        SUBTYPE_SUB = 2  # noqa: F841
        first_letter = display_name[0].lower()

        first_entry = entries[0]

        if first_letter == " ":
            entry_display_name = f"unnamed {first_entry.dispname}"
        else:
            entry_display_name = first_entry.dispname
        if len(entries) == 1:
            yield first_letter, self._make_index_entry(
                first_entry, entry_display_name, SUBTYPE_NORMAL
            )
        else:
            yield first_letter, self._make_index_entry(
                first_entry, entry_display_name, SUBTYPE_WITHSUBS
            )
            for other_entry in entries[1:]:
                yield first_letter, self._make_index_entry(
                    other_entry, entry_display_name, SUBTYPE_SUB
                )

    def _make_index_entry(
        self,
        reference: SphinxDomainObjectDescription,
        displayname: str,
        subtype: int,
    ) -> IndexEntry:
        domain = GherkinDomain.get_instance(self.domain.env)

        documented_keyword: DocumentedKeyword = domain.get_keyword(
            reference.name
        )

        try:
            document, keyword = domain.gherkin_documents.find_one(
                documented_keyword
            )
            path = get_gherkin_file_symbolic_path(
                document.name, self.domain.env
            )
            extra_info = f"{path} line {keyword.location.start.line + 1}"
        except NotFound:
            if documented_keyword.parent:
                parent_display = documented_keyword.parent.display_name
                extra_info = f"{reference.docname} in {parent_display}"
            else:
                extra_info = reference.docname

        return IndexEntry(
            displayname,
            subtype,
            reference.docname,
            reference.anchor,
            extra_info,
            "",  # qualifier
            reference.type,
        )
