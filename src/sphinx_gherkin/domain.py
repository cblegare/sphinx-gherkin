from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from docutils.nodes import Element
from sphinx import addnodes
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.util.logging import getLogger
from sphinx.util.nodes import make_refnode

from sphinx_gherkin import (
    DOMAIN_NAME,
    DocumentedKeyword,
    NotFound,
    ObjectId,
    SphinxGherkinError,
    get_config_gherkin_sources,
    get_env,
    keyword_to_objtype,
)
from sphinx_gherkin.gherkin import (
    Background,
    DefinitionBuildah,
    Document,
    Examples,
    Feature,
    Keyword,
    Rule,
    Scenario,
    Step,
)
from sphinx_gherkin.i18n import t_
from sphinx_gherkin.sphinxapi import SphinxDomainObjectDescription

if TYPE_CHECKING or sys.version_info < (3, 8, 0):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

D = TypeVar("D", bound="GherkinDomain")
K = TypeVar("K", bound="Keyword")
ObjectIdLike = Union[str, ObjectId]

log = getLogger(__name__)


class UnresolvableKeyword(SphinxGherkinError):
    pass


class DomainData(TypedDict, total=False):
    version: int
    gherkin: RegistryData
    objects: Dict[ObjectId, List[SphinxDomainObjectDescription]]
    object_id_to_keyword: Dict[ObjectId, DocumentedKeyword]
    keyword_to_object_id: Dict[DocumentedKeyword, ObjectId]
    objtype_selectors: Dict[str, Dict[str, Set[ObjectId]]]


class DomainStore:
    def __init__(self, data: Optional[DomainData] = None):
        self._data: DomainData = data or self.initial_data()

    @classmethod
    def initial_data(cls) -> DomainData:
        return DomainData(
            gherkin=RegistryData.new(),
            objects=defaultdict(list),
            object_id_to_keyword=dict(),
            keyword_to_object_id=dict(),
            objtype_selectors=dict(
                feature=defaultdict(set),
                rule=defaultdict(set),
                background=defaultdict(set),
                scenario=defaultdict(set),
                outline=defaultdict(set),
                examples=defaultdict(set),
                step=defaultdict(set),
            ),
        )

    @property
    def gherkin(self) -> RegistryData:
        return self._data["gherkin"]

    def get_objects(
        self,
    ) -> Dict[ObjectId, List[SphinxDomainObjectDescription]]:
        return self._data["objects"]

    def add_object(
        self,
        object_id: ObjectIdLike,
        obj_description: SphinxDomainObjectDescription,
    ) -> None:
        self._data["objects"][ObjectId(object_id)].append(obj_description)

    def get_object(
        self, specifier: Union[ObjectIdLike, DocumentedKeyword]
    ) -> SphinxDomainObjectDescription:
        try:
            if isinstance(specifier, DocumentedKeyword):
                object_id = self.get_object_id(specifier)
            else:
                object_id = ObjectId(specifier)

            objects = self._data["objects"][ObjectId(object_id)]
            return next(iter(objects))
        except (KeyError, StopIteration):
            raise NotFound(f"Documented object not found '{specifier}'.")

    def get_object_id(self, keyword: DocumentedKeyword) -> ObjectId:
        return self._data["keyword_to_object_id"][keyword]

    def get_keyword(self, object_id: ObjectIdLike) -> DocumentedKeyword:
        return self._data["object_id_to_keyword"][ObjectId(object_id)]

    def add_keyword(
        self, object_id: ObjectIdLike, keyword: DocumentedKeyword
    ) -> None:
        object_id = ObjectId(object_id)
        self._data["object_id_to_keyword"][object_id] = keyword
        self._data["keyword_to_object_id"][keyword] = object_id

        selectors = self.selectors_for_type(keyword.objtype)

        for selector in (
            object_id,
            keyword.keyword,
            keyword.summary.strip("."),
            keyword.objtype,
        ):
            selectors[selector].add(object_id)

    def selectors_for_type(self, objtype: str) -> Dict[str, Set[ObjectId]]:
        return self._data["objtype_selectors"][objtype]


R = TypeVar("R", bound="RegistryData")


class RegistryData(NamedTuple):
    documents: Dict[str, Document]
    rst_references: Dict[str, Set[str]]

    @classmethod
    def new(cls: Type[R]) -> R:
        return cls(documents={}, rst_references=defaultdict(set))


class GherkinDocumentRegistry:
    _objtype_keywordclass = {
        "feature": Feature,
        "rule": Rule,
        "background": Background,
        "scenario": Scenario,
        "examples": Examples,
        "step": Step,
    }

    def __init__(self, datastore: Optional[RegistryData] = None):
        self.data: RegistryData = datastore or RegistryData.new()

    @property
    def documents(self) -> Dict[str, Document]:
        return self.data.documents

    @property
    def rst_references(self) -> Dict[str, Set[str]]:
        return self.data.rst_references

    def get_documented_files(self) -> Collection[Path]:
        return [Path(name) for name in self.documents.keys()]

    def load_folder(self, feature_tree_root: Path) -> None:
        for feature_file in feature_tree_root.rglob("*.feature"):
            self.add_file(feature_file)

    def add_document(self, document: Document) -> Document:
        self.documents[document.name] = document
        return document

    def add_file(self, feature_file: Path) -> Document:
        builder = DefinitionBuildah.from_path(feature_file)
        document = builder.parse()
        return self.add_document(document)

    def add_gherkin(self, name: str, code: str) -> Document:
        builder = DefinitionBuildah(name, code)
        document = builder.parse()
        return self.add_document(document)

    def register_rst_keyword(
        self, object_id: str, rst_keyword: DocumentedKeyword
    ) -> None:
        found = self.find_first(rst_keyword)
        if found:
            document, keyword = found
            self.rst_references[document.name].add(object_id)

    def get_code(self, gherkin_file: Union[str, Path]) -> Sequence[str]:
        return self.documents[str(gherkin_file)].lines

    def find(
        self, keyword: DocumentedKeyword
    ) -> Iterator[Tuple[Document, Keyword]]:
        for document in self.documents.values():
            for found in document.find(
                self._keyword_class(keyword), self._make_matcher(keyword)
            ):
                yield document, found

    def find_one(self, keyword: DocumentedKeyword) -> Tuple[Document, Keyword]:
        found: Optional[Tuple[Document, Keyword]] = self.find_first(keyword)
        if not found:
            raise NotFound(keyword)
        return found

    def find_first(
        self, keyword: DocumentedKeyword
    ) -> Optional[Tuple[Document, Keyword]]:
        try:
            return next(self.find(keyword))
        except StopIteration:
            return None

    def keyword_class_for_objtype(self, objtype: str) -> Type[Keyword]:
        return self._objtype_keywordclass[objtype]

    def objtype_for_keyword_class(self, keyword_class: Type[Keyword]) -> str:
        for objtype, cls in self._objtype_keywordclass.items():
            if cls == keyword_class:
                return objtype
        else:
            raise KeyError(keyword_class)

    def _keyword_class(self, keyword: DocumentedKeyword) -> Type[Keyword]:
        return self.keyword_class_for_objtype(keyword.objtype)

    def _make_matcher(
        self, keyword: DocumentedKeyword
    ) -> Callable[[Keyword, Document], bool]:
        def matcher(gherkin_keyword: Keyword, document: Document) -> bool:
            ancestor = keyword
            gherkin_ancestor = gherkin_keyword

            while ancestor:
                if not isinstance(
                    gherkin_ancestor, self._keyword_class(ancestor)
                ):
                    return False

                if gherkin_ancestor.summary != ancestor.summary:
                    return False

                ancestor = ancestor.parent
                gherkin_ancestor = document.ancestry.get(gherkin_ancestor, None)  # type: ignore # it is ok for gherkin_ancestor to be None
            return True

        return matcher


class GherkinDomain(Domain):

    name: str = DOMAIN_NAME
    """
    The domain name, short and unique.
    """

    label: str = "Gherkin"

    @classmethod
    def get_instance(
        cls: Type[D], app_or_env: Union[Sphinx, BuildEnvironment]
    ) -> D:
        env = get_env(app_or_env)
        domain = env.get_domain(cls.name)
        return domain  # type: ignore

    @property
    def store(self) -> DomainStore:
        return DomainStore(self.data)  # type: ignore

    @property
    def gherkin_documents(self) -> GherkinDocumentRegistry:
        if not hasattr(self, "_registry"):
            registry = GherkinDocumentRegistry(self.store.gherkin)
            for name, path in get_config_gherkin_sources(self.env).items():
                registry.load_folder(path)

            setattr(
                self, "_registry", GherkinDocumentRegistry(self.data["gherkin"])
            )

        return getattr(self, "_registry")  # type: ignore

    def note_keyword(
        self,
        object_id: str,
        keyword: DocumentedKeyword,
        signature_node_id: str,
        location: Any = None,
    ) -> None:
        obj_description = SphinxDomainObjectDescription(
            object_id,
            keyword.display_name,
            keyword.objtype,
            self.env.docname,
            signature_node_id,
            1,
        )

        self.store.add_object(object_id, obj_description)
        self.store.add_keyword(object_id, keyword)
        self.gherkin_documents.register_rst_keyword(object_id, keyword)

    def get_keyword(self, object_id: ObjectIdLike) -> DocumentedKeyword:
        return self.store.get_keyword(object_id)

    def get_objects(
        self,
        *,
        object_id: Optional[ObjectIdLike] = None,
        filepath: Optional[Union[str, Path]] = None,
    ) -> Iterable[SphinxDomainObjectDescription]:
        """
        Return an iterable of "object descriptions".

        See Also:
             Parent method :meth:`sphinx.domains.Domain.get_objects`.

        Returns:
            Object descriptions are tuples with six items.
            See :class:`sphinx_gherkin.sphinxapi.SphinxDomainObjectDescription`.
        """
        if object_id and filepath:
            raise ValueError()

        if filepath:
            yield from self.get_objects_in_file(filepath)
        elif object_id:
            yield from self.store.get_objects()[ObjectId(object_id)]
        else:
            for object_list in self.store.get_objects().values():
                yield from object_list

    def get_objects_in_file(
        self, filepath: Union[str, Path]
    ) -> Iterable[SphinxDomainObjectDescription]:
        for object_id in self.gherkin_documents.rst_references[str(filepath)]:
            yield from self.get_objects(object_id=object_id)

    def merge_domaindata(
        self, docnames: List[str], otherdata: Dict[str, Any]
    ) -> None:
        # fixme
        pass

    def resolve_any_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> List[Tuple[str, Element]]:
        # fixme
        return []

    def resolve_xref(
        self,
        env: "BuildEnvironment",
        fromdocname: str,
        builder: Builder,
        objtype: str,
        target: str,
        node: addnodes.pending_xref,
        contnode: Element,
    ) -> Optional[Element]:
        """
        Resolve the pending_xref *node* with the given *typ* and *target*.

        See also:
            The parent class method docstring is something like

                Resolve the pending_xref *node* with the given *typ* and
                *target*.

                This method should return a new node, to replace the xref
                node, containing the *contnode* which is the markup content
                of the cross-reference.

                If no resolution can be found, None can be returned; the
                xref node will then given to the :event:`missing-reference`
                event, and if that yields no resolution, replaced by *contnode*.

                The method can also raise :exc:`sphinx.environment.NoUri`
                to suppress the :event:`missing-reference` event being emitted.

        Args:
            env:
                Current Sphinx build environment.
            fromdocname:
                Document name where the cross-reference was used.
            builder:
                Current Sphinx builder.
            objtype:
                Object type name.
            target:
                Looked up object identifier.
            node:
                Document node for the xref.
            contnode:
                The markup content of the cross-reference.

        If no resolution can be found, ``None`` can be returned;
        the xref node will then given to the ``missing-reference`` event,
        and if that yields no resolution, replaced by contnode.

        Returns:
            A reference node or None if no reference could be resolved.
        """
        objtype = keyword_to_objtype(objtype)
        try:
            keywords = self._resolve_keywords(objtype, target)

            keyword = self._pick_one_keyword(keywords, objtype, target)

            if keyword:
                object_id = self.store.get_object_id(keyword)
                object_description = self.store.get_object(object_id)

                return make_refnode(
                    builder,
                    fromdocname,
                    object_description.docname,
                    object_description.anchor,
                    contnode,
                    object_description.dispname,
                )
        except UnresolvableKeyword:
            pass
        return None

    def _resolve_feature_parents(
        self, target: str
    ) -> Collection[DocumentedKeyword]:
        return tuple()

    def _resolve_rule_parents(
        self, target: str
    ) -> Collection[DocumentedKeyword]:
        *parent_selectors, _ = target.split(".")
        candidate_parents: Set[DocumentedKeyword] = set()

        if len(parent_selectors) == 1:
            candidate_parents.update(
                self._resolve_keywords("feature", next(iter(parent_selectors)))
            )

        if len(parent_selectors) > 1:
            log.warning(f"No canditates found for 'rule' '{target}'.")
            log.warning(
                "Rules are only found in Features and never two level deep. "
                "May you have a dot ('.') in a summary?"
            )
            raise UnresolvableKeyword(target)

        return candidate_parents

    def _resolve_background_parents(
        self, target: str
    ) -> Collection[DocumentedKeyword]:
        return self._resolve_background_or_scenario_parents(
            "background", target
        )

    def _resolve_scenario_parents(
        self, target: str
    ) -> Collection[DocumentedKeyword]:
        return self._resolve_background_or_scenario_parents("scenario", target)

    def _resolve_background_or_scenario_parents(
        self, objtype: str, target: str
    ) -> Collection[DocumentedKeyword]:
        *parent_selectors, _ = target.split(".")
        candidate_parents: Set[DocumentedKeyword] = set()

        parent_target = ".".join(parent_selectors)

        if len(parent_selectors) == 2:
            candidate_parents.update(
                self._resolve_keywords("rule", parent_target, strict=False)
            )
        elif len(parent_selectors) == 1:
            candidate_parents.update(
                self._resolve_keywords("rule", parent_target, strict=False)
            )
            candidate_parents.update(
                self._resolve_keywords("feature", parent_target, strict=False)
            )

            if not candidate_parents:
                log.warning(f"No canditates found for '{objtype}' '{target}'.")
                raise UnresolvableKeyword(target)
        elif len(parent_selectors) > 1:
            log.warning(f"No canditates found for '{objtype}' '{target}'.")
            log.warning(
                f"{objtype.title()} are only found in Features and Rules, "
                "never three level deep. "
                f"May you have a dot ('.') in a summary?"
            )
            raise UnresolvableKeyword(target)

        return candidate_parents

    def _resolve_step_parents(
        self, target: str
    ) -> Collection[DocumentedKeyword]:
        *parent_selectors, terminal_selector = target.split(".")
        candidate_parents: Set[DocumentedKeyword] = set()

        parent_target = ".".join(parent_selectors)

        if len(parent_selectors) in (1, 2, 3):
            candidate_parents.update(
                self._resolve_keywords("scenario", parent_target, strict=False)
            )
            candidate_parents.update(
                self._resolve_keywords(
                    "background", parent_target, strict=False
                )
            )
            if not candidate_parents:
                log.warning(f"No canditates found for 'step' '{target}'.")
                raise UnresolvableKeyword(target)
        elif len(parent_selectors) > 3:
            log.warning(f"No canditates found for 'step' '{target}'.")
            log.warning(
                "Step are only found in Scenario and Background, "
                "never three level deep. "
                "Maybe you have a dot ('.') in a summary?"
            )
            raise UnresolvableKeyword(target)

        return candidate_parents

    def _resolve_whole_target(
        self, objtype: str, target: str
    ) -> Collection[DocumentedKeyword]:
        selectors = self.store.selectors_for_type(objtype)

        try:
            object_ids = selectors[target]
            if len(object_ids) == 1:
                object_id = next(iter(object_ids))
                return {self.get_keyword(object_id)}
        except KeyError:
            pass
        return set()

    def _resolve_keywords(
        self, objtype: str, target: str, strict: bool = True
    ) -> Collection[DocumentedKeyword]:
        resolved = self._resolve_whole_target(objtype, target)
        if resolved:
            return resolved

        *_, terminal_selector = target.split(".")
        selectors = self.store.selectors_for_type(objtype)

        try:
            filter = self._make_parent_filter(objtype, target)

            return set(
                self.get_keyword(object_id)
                for object_id in selectors[terminal_selector]
                if filter(object_id)
            )
        except UnresolvableKeyword as e:
            if strict:
                raise e
            else:
                return {}

    def _make_parent_filter(
        self, objtype: str, target: str, strict: bool = True
    ) -> Callable[[str], bool]:
        *parent_selectors, _ = target.split(".")

        if parent_selectors:
            candidate_parents = self._resolve_candidate_parents(objtype, target)

            def filter(object_id: str) -> bool:
                return self.get_keyword(object_id).parent in candidate_parents

        else:

            def filter(object_id: str) -> bool:
                return True

        return filter

    def _resolve_candidate_parents(
        self, objtype: str, target: str
    ) -> Set[DocumentedKeyword]:
        parent_resolver = getattr(self, f"_resolve_{objtype}_parents")
        candidate_parents: Set[DocumentedKeyword] = set(
            parent
            for parent in parent_resolver(target)
            if parent and parent.value
        )
        return candidate_parents

    def _pick_one_keyword(
        self,
        matching_keywords: Collection[DocumentedKeyword],
        objtype: str,
        target: str,
    ) -> Optional[DocumentedKeyword]:
        if len(matching_keywords) == 1:
            keyword = next(iter(matching_keywords))
            return keyword
        if not matching_keywords:
            log.warning(f"No canditates found for '{objtype}' '{target}'.")
            return None
        log.warning(
            f"Many canditates found for xref to '{objtype}' '{target}'."
        )
        log.warning("Candidates are")
        for matching in matching_keywords:
            log.warning(matching)
        return None

    @classmethod
    def new(cls: Type[D]) -> Type[D]:  # noqa
        from sphinx_gherkin.index import GherkinDefinitionsIndex
        from sphinx_gherkin.markup import (
            BackgroundDescription,
            ExamplesDescription,
            FeatureDescription,
            GherkinCrossReferenceRole,
            RuleDescription,
            ScenarioDescription,
            ScenarioOutlineDescription,
            StepDescription,
        )
        from sphinx_gherkin.markup.autodoc import (
            AutoBackgroundDescription,
            AutoExamplesDescription,
            AutoFeatureDescription,
            AutoRuleDescription,
            AutoScenarioDescription,
            AutoScenarioOutlineDescription,
            AutoStepDescription,
        )

        markup_keywords = {
            "feature": (
                "feature",
                FeatureDescription,
                AutoFeatureDescription,
                GherkinCrossReferenceRole,
            ),
            "rule": (
                "rule",
                RuleDescription,
                AutoRuleDescription,
                GherkinCrossReferenceRole,
            ),
            "background": (
                "background",
                BackgroundDescription,
                AutoBackgroundDescription,
                GherkinCrossReferenceRole,
            ),
            "scenario": (
                "scenario",
                ScenarioDescription,
                AutoScenarioDescription,
                GherkinCrossReferenceRole,
            ),
            "example": (
                "scenario",
                ScenarioDescription,
                AutoScenarioDescription,
                GherkinCrossReferenceRole,
            ),
            "outline": (
                "scenario",
                ScenarioOutlineDescription,
                AutoScenarioOutlineDescription,
                GherkinCrossReferenceRole,
            ),
            "template": (
                "scenario",
                ScenarioOutlineDescription,
                AutoScenarioOutlineDescription,
                GherkinCrossReferenceRole,
            ),
            "examples": (
                "examples",
                ExamplesDescription,
                AutoExamplesDescription,
                GherkinCrossReferenceRole,
            ),
            "scenarios": (
                "examples",
                ExamplesDescription,
                AutoExamplesDescription,
                GherkinCrossReferenceRole,
            ),
            "given": (
                "step",
                StepDescription,
                AutoStepDescription,
                GherkinCrossReferenceRole,
            ),
            "and": (
                "step",
                StepDescription,
                AutoStepDescription,
                GherkinCrossReferenceRole,
            ),
            "but": (
                "step",
                StepDescription,
                AutoStepDescription,
                GherkinCrossReferenceRole,
            ),
            # We don't allow the :gherkin:*:`...` role.
            "*": ("step", None, None, None),
            "when": (
                "step",
                StepDescription,
                AutoStepDescription,
                GherkinCrossReferenceRole,
            ),
            "then": (
                "step",
                StepDescription,
                AutoStepDescription,
                GherkinCrossReferenceRole,
            ),
            "step": (
                "step",
                StepDescription,
                AutoStepDescription,
                GherkinCrossReferenceRole,
            ),
        }

        objtype_roles = defaultdict(list)

        domain_namespace = {
            "roles": {},
            "directives": {},
            "object_types": {},
            "indices": [
                GherkinDefinitionsIndex,
            ],
            "initial_data": DomainStore.initial_data(),
        }

        for keyword_name, mapping in markup_keywords.items():
            objtype, directive, auto_directive, xrefrole = mapping
            if xrefrole:
                objtype_roles[objtype].append(keyword_name)
                domain_namespace["roles"][keyword_name] = xrefrole()  # type: ignore # Unsupported target for indexed assignment (I don't get it)

            if directive:
                domain_namespace["directives"][keyword_name] = directive  # type: ignore # Unsupported target for indexed assignment (I don't get it)

            if auto_directive:
                domain_namespace["directives"][  # type: ignore # Unsupported target for indexed assignment (I don't get it)
                    f"auto{keyword_name}"
                ] = auto_directive

        for objtype, role_names in objtype_roles.items():
            domain_namespace["object_types"][objtype] = ObjType(  # type: ignore # Unsupported target for indexed assignment (I don't get it)
                t_(objtype), *role_names
            )

        return type("Gherkin", (cls,), domain_namespace)
