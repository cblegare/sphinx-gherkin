"""
RestructuredText generator from Gherkin
"""
from __future__ import annotations

import argparse
import fnmatch
import locale
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple, Union

import sphinx
from sphinx.util.logging import getLogger
from sphinx.util.template import ReSTRenderer

import sphinx_gherkin
from sphinx_gherkin import __version__
from sphinx_gherkin.gherkin import DefinitionBuildah, Document
from sphinx_gherkin.i18n import t__

log = getLogger(__name__)

GHERKIN_SUFFIXES = (".feature",)


template_dir = Path(__file__).parent.resolve()


class Command:
    def __init__(self, root: Path, args: argparse.Namespace):
        self.root = root
        self.args = args

    @property
    def header(self) -> str:
        if self.args.header is None:
            return self.root.name
        return str(self.args.header)

    @property
    def output_file_suffix(self) -> str:
        suffix = str(self.args.suffix)
        if suffix.startswith("."):
            return suffix[1:]
        return suffix

    @property
    def template_dirs(self) -> List[str]:
        if self.args.templatedir:
            return [str(self.args.templatedir), str(template_dir)]
        else:
            return [str(template_dir)]

    def run(self) -> None:
        gherkin_documents = self.gather_gherkin_document(self.root)
        for docname, content in self.gather_rendered_docs(gherkin_documents):
            self.write_document(docname, content)

        if self.args.tocfile:
            child_folders = self.child_folders(self.root, gherkin_documents)
            content = self.render_toc(
                [self.make_docname(child) for child in child_folders]
            )
            self.write_document(self.args.tocfile, content)

    def gather_gherkin_document(self, root: Path) -> Dict[Path, List[Document]]:
        files = defaultdict(list)
        for path in root.rglob("*"):
            if not self.is_excluded(path) and path.is_file():
                files[path.parent].append(self.parse_gherkin(path.resolve()))

        # add intermediate folders that do not contain feature files
        found_folders = list(files.keys())
        for folder in found_folders:
            parent = folder
            while parent != self.root:
                files.setdefault(parent, [])
                parent = parent.parent

        return files

    def is_excluded(self, path: Path) -> bool:
        if path.suffix in GHERKIN_SUFFIXES:
            for exclude in self.args.exclude_pattern:
                if fnmatch.fnmatch(path, exclude):
                    return True
            return False
        return True

    def child_folders(
        self, folder: Path, gherkin_documents: Dict[Path, List[Document]]
    ) -> List[Path]:
        folders = [
            child
            for child in gherkin_documents.keys()
            if child.parent == folder
        ]
        return folders

    def gather_rendered_docs(
        self, gherkin_documents: Dict[Path, List[Document]]
    ) -> Iterator[Tuple[str, str]]:
        for folder in sorted(gherkin_documents.keys()):
            features = sorted(
                gherkin_documents[folder], key=lambda doc: doc.feature.summary
            )
            if self.args.separatefeatures:
                for feature_document in features:
                    feature_docname = self.make_docname(feature_document.name)
                    rendered_feature = self.render_feature_file_doc(
                        feature_document
                    )
                    yield feature_docname, rendered_feature
            folder_docname = self.make_docname(folder)
            child_folders = self.child_folders(folder, gherkin_documents)
            rendered_folder = self.render_feature_folder_doc(
                folder, features, child_folders
            )
            yield folder_docname, rendered_folder

    def parse_gherkin(self, path: Path) -> Document:
        parser = DefinitionBuildah.from_path(path)
        document = parser.parse()
        return document

    def make_docname(self, path: Union[str, Path]) -> str:
        relative = Path(path).relative_to(self.root)
        if str(relative).endswith(GHERKIN_SUFFIXES):
            relative = relative.with_suffix("")

        docname = ".".join([self.root.name, *relative.parts])
        return docname

    def render_toc(self, docnames: List[str]) -> str:
        context = {
            "header": self.header,
            "maxdepth": self.args.maxdepth,
            "docnames": docnames,
        }

        text = self.render("toc.rst_t", context)

        return text

    def render_feature_file_doc(self, document: Document) -> str:
        context: Dict[str, Any] = {
            "show_headings": True,
            "summary": document.feature.summary,
            "signature": document.name,
            "autofeature_options": {},
        }

        text = self.render("feature.rst_t", context)

        return text

    def render_feature_folder_doc(
        self, folder: Path, features: List[Document], child_folders: List[Path]
    ) -> str:
        context = {
            "show_headings": True,
            "foldername": str(folder.relative_to(self.root.parent)),
            "separatefeatures": self.args.separatefeatures,
            "subfolders": [self.make_docname(child) for child in child_folders],
            "features": {
                Path(feature.name).relative_to(self.root): feature
                for feature in features
            },
            "autofeature_options": {},
            "maxdepth": self.args.maxdepth,
        }

        text = self.render("folder.rst_t", context)

        return text

    def render(self, template: str, context: Dict[str, Any]) -> str:
        renderer = ReSTRenderer(self.template_dirs)
        text = renderer.render(template, context)
        return text

    def write_document(self, docname: str, content: str) -> Path:
        no_suffix = Path(self.args.destdir, docname)
        destination = no_suffix.with_name(
            f"{no_suffix.name}.{self.output_file_suffix}"
        )
        if not self.args.dryrun:
            if self.args.force or not destination.exists():
                destination.write_text(content)
                log.info(f"Writing {destination}.")
            else:
                log.info(
                    f"{destination} already exist. Use '--force' to overwrite."
                )
        else:
            log.info(f"dryrun: did not write {destination}.")

        return destination


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] -o <OUTPUT_PATH> <FEATURE_PATH> "
        "[EXCLUDE_PATTERN, ...]",
        epilog=t__(
            "For more information, visit <https://cblegare.gitlab.io/sphinx-gherkin/>."
        ),
        description=t__(
            """
Look recursively in <FEATURE_PATH> for Gherkin features and create one or
more reST file with autofeature directives per folder in the <OUTPUT_PATH>.
The <EXCLUDE_PATTERN>s can be file and/or directory patterns that will be
excluded from generation.
Note: By default this script will not overwrite already created files."""
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        dest="show_version",
        version="%%(prog)s %s" % __version__,
    )

    parser.add_argument(
        "features_path", help=t__("path to feature folder to document")
    )
    parser.add_argument(
        "exclude_pattern",
        nargs="*",
        help=t__(
            "fnmatch-style file and/or directory patterns "
            "to exclude from generation"
        ),
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        action="store",
        dest="destdir",
        required=True,
        help=t__("directory to place all output"),
    )
    parser.add_argument(
        "-q",
        action="store_true",
        dest="quiet",
        help=t__("no output on stdout, just warnings on stderr"),
    )
    parser.add_argument(
        "-d",
        "--maxdepth",
        action="store",
        dest="maxdepth",
        type=int,
        default=4,
        help=t__(
            "maximum depth of submodules to show in the TOC " "(default: 4)"
        ),
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force",
        help=t__("overwrite existing files"),
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        dest="dryrun",
        help=t__("run the script without creating files"),
    )
    parser.add_argument(
        "-e",
        "--separate",
        action="store_true",
        dest="separatefeatures",
        help=t__(
            "put documentation for each feature on its own page "
            "(default: one page per folder of features)"
        ),
    )
    parser.add_argument(
        "--tocfile",
        action="store",
        dest="tocfile",
        default="features",
        help=t__("filename of table of contents (default: features)"),
    )
    parser.add_argument(
        "-T",
        "--no-toc",
        action="store_false",
        dest="tocfile",
        help=t__("don't create a table of contents file"),
    )
    parser.add_argument(
        "-s",
        "--suffix",
        action="store",
        dest="suffix",
        default="rst",
        help=t__("file suffix (default: rst)"),
    )
    parser.add_argument(
        "-H",
        "--header",
        action="store",
        dest="header",
        help=t__("project name (default: root module name)"),
    )
    group = parser.add_argument_group(t__("Project templating"))
    group.add_argument(
        "-t",
        "--templatedir",
        metavar="TEMPLATEDIR",
        dest="templatedir",
        help=t__("template directory for template files"),
    )

    return parser


def main(argv: List[str] = sys.argv[1:]) -> int:
    """Parse and check the command line arguments."""
    sphinx.locale.setlocale(locale.LC_ALL, "")
    sphinx.locale.init_console(
        os.path.join(sphinx_gherkin.package_dir, "locale"), "sphinx"
    )

    parser = get_parser()
    args = parser.parse_args(argv)

    rootpath = Path(args.features_path).resolve()

    # normalize opts
    if not rootpath.is_dir():
        print(t__("%s is not a directory.") % rootpath, file=sys.stderr)
        sys.exit(1)
    if not args.dryrun:
        Path(args.destdir).mkdir(parents=True, exist_ok=True)

    cmd = Command(rootpath, args)

    cmd.run()

    return 0


if __name__ == "__main__":
    main()
