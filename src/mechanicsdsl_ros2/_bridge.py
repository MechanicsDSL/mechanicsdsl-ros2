"""
_bridge.py
----------
The bridge between the frozen ``mechanicsdsl-core`` compiler and this
package's code generators.

Every real generation path in ``mechanicsdsl-embedded`` starts here: a DSL
spec (``.msl`` file or raw string) is compiled by the core
:class:`~mechanics_dsl.PhysicsCompiler`, and the resulting equations of
motion, coordinates, parameters and initial conditions are packaged into a
plain, generator-ready :class:`CompiledSystem`.

The core package is imported as ``mechanics_dsl`` (underscore) — *not*
``mechanicsdsl`` — and exposes no top-level ``generate()`` helper; code is
produced by ``mechanics_dsl.codegen`` generator classes that consume exactly
the fields assembled here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    import sympy as sp
except ImportError:  # pragma: no cover - sympy ships with core
    sp = None  # type: ignore


class CoreNotInstalled(RuntimeError):
    """Raised when ``mechanicsdsl-core`` is not importable."""


class DSLCompileError(RuntimeError):
    """Raised when the core compiler rejects a DSL spec."""


@dataclass
class CompiledSystem:
    """A DSL system compiled down to generator-ready primitives.

    Attributes
    ----------
    name:
        System name from ``\\system{...}``.
    coordinates:
        Generalized coordinate names, e.g. ``["theta1", "theta2"]``.
    parameters:
        Flat ``name -> float`` map of physical parameters.
    initial_conditions:
        Initial state, including both ``q`` and ``q_dot`` entries.
    equations:
        Acceleration equations as ``"{coord}_ddot" -> sympy.Expr``. This is
        exactly the shape every :class:`mechanics_dsl.codegen` generator
        expects.
    units:
        Optional ``param -> unit`` map, preserved for documentation/comments.
    source:
        The originating DSL text, embedded into generated files for
        provenance.
    """

    name: str
    coordinates: List[str]
    parameters: Dict[str, float]
    initial_conditions: Dict[str, float]
    equations: Dict[str, "sp.Expr"]
    units: Dict[str, str] = field(default_factory=dict)
    source: str = ""

    @property
    def state_dim(self) -> int:
        """Phase-space dimension (2 per coordinate)."""
        return 2 * len(self.coordinates)


def _read_source(spec: str) -> str:
    """Return DSL text from a path or a raw DSL string."""
    # Heuristic: a spec containing a backslash-command is already DSL text.
    if "\\system" in spec or "\\lagrangian" in spec or "\\hamiltonian" in spec:
        return spec
    if os.path.isfile(spec):
        with open(spec, "r", encoding="utf-8") as fh:
            return fh.read()
    # Fall back to treating it as literal DSL so a helpful compile error
    # surfaces rather than a confusing "file not found".
    return spec


def compile_spec(spec: str) -> CompiledSystem:
    """Compile a DSL spec into a :class:`CompiledSystem`.

    Parameters
    ----------
    spec:
        Either a path to a ``.msl`` file, a raw DSL string, or the name of a
        core preset (e.g. ``"pendulum"``, ``"double_pendulum"``).

    Raises
    ------
    CoreNotInstalled
        If ``mechanicsdsl-core`` cannot be imported.
    DSLCompileError
        If the core compiler fails to compile the spec.
    """
    try:
        from mechanics_dsl import PhysicsCompiler
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise CoreNotInstalled(
            "mechanicsdsl-core is required for code generation.\n"
            "Install it with: pip install mechanicsdsl-core"
        ) from exc

    # Allow a bare preset name as a convenience.
    source = spec
    if "\\" not in spec and not os.path.isfile(spec):
        try:
            from mechanics_dsl import get_preset

            source = get_preset(spec)
        except Exception:
            source = spec
    source = _read_source(source)

    compiler = PhysicsCompiler()
    result = compiler.compile_dsl(source)
    if not result.get("success"):
        raise DSLCompileError(result.get("error", "unknown compilation error"))

    parameters = {
        name: float(info["value"])
        for name, info in (compiler.parameters_def or {}).items()
    }
    units = {
        name: str(info.get("unit", ""))
        for name, info in (compiler.parameters_def or {}).items()
    }

    return CompiledSystem(
        name=compiler.system_name,
        coordinates=list(compiler.get_coordinates()),
        parameters=parameters,
        initial_conditions=dict(compiler.initial_conditions or {}),
        equations=dict(compiler.equations or {}),
        units=units,
        source=source.strip(),
    )
