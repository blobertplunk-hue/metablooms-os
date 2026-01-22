# ECL_VERSION: 1
# ECL_SCOPE: METABLOOMS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms post-run utilities.

This package is intentionally lightweight. All post-run side effects must be
restricted to writing review artifacts (reports/MMTs/evidence), never mutating
system state.
"""

from __future__ import annotations
