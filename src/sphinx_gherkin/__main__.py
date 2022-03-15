"""
############################
Top-level script environment
############################

Make sure one can invoke !outil! with ``python -m sphinx_gherkin``.
"""
from __future__ import annotations

import sys

from sphinx_gherkin.gherkin2rst import main

if __name__ == "__main__" and not __package__:
    # This should never happen when installed from pip.
    # This workaround is NOT bulletproof, rather brittle as many edge
    # cases are not covered
    # See http://stackoverflow.com/a/28154841/2479038

    print(
        "warning: running package directly, risking ImportError",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
