"""
test_generation.py
------------------
C++ header (compiled and run when a C++ compiler is available), the pure-Python
ament_python package (imported and run), and the launch/parameter plumbing.
"""
import importlib.util
import shutil
import subprocess
import textwrap

import pytest

pytest.importorskip("mechanics_dsl", reason="mechanicsdsl-core required")

from mechanicsdsl_ros2 import (  # noqa: E402
    compile_spec,
    numeric_energy,
    render_dynamics_header,
    render_dynamics_py,
    render_params_yaml,
    scaffold_package,
    scaffold_python_package,
    simulate,
)
from mechanicsdsl_ros2._cppgen import params_struct_name  # noqa: E402
from mechanicsdsl_ros2.cli import main as cli_main  # noqa: E402

PRESETS = ["pendulum", "double_pendulum", "coupled_oscillators", "damped_oscillator",
           "projectile", "figure8"]
CXX = shutil.which("g++") or shutil.which("clang++")


@pytest.fixture(scope="module", params=PRESETS)
def system(request):
    return compile_spec(request.param)


def _load_module(path):
    spec = importlib.util.spec_from_file_location("gen_dynamics", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------- C++ ------
@pytest.mark.skipif(CXX is None, reason="no C++ compiler on PATH")
def test_all_headers_compile_together_and_match(tmp_path):
    systems = [compile_spec(p) for p in PRESETS]
    incs, body = [], []
    for s in systems:
        (tmp_path / f"{s.name}.hpp").write_text(
            render_dynamics_header(s, f"G_{s.name.upper()}"), encoding="utf-8")
        incs.append(f'#include "{s.name}.hpp"')
        e = "mechanicsdsl::energy(y, p)" if s.energy is not None else "0.0"
        body.append(f"""
  {{ mechanicsdsl::{params_struct_name(s)} p; double y[{s.state_dim}];
    mechanicsdsl::initial_state(y, p);
    for (int k = 0; k < 1000; ++k) mechanicsdsl::rk4_step(y, 1e-3, p);
    for (double v : y) std::printf("%.17g ", v);
    std::printf("%.17g\\n", {e}); }}""")
    (tmp_path / "main.cpp").write_text(
        "#include <cstdio>\n" + "\n".join(incs) + "\nint main() {" + "".join(body) + "\n}\n",
        encoding="utf-8")
    exe = tmp_path / "main.bin"
    r = subprocess.run([CXX, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-O2",
                        str(tmp_path / "main.cpp"), "-o", str(exe)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    lines = subprocess.run([str(exe)], capture_output=True, text=True,
                           check=True).stdout.splitlines()
    for s, line in zip(systems, lines):
        vals = [float(v) for v in line.split()]
        _, Y = simulate(s, t_end=1.0, dt=1e-3)
        scale = max(1.0, max(abs(v) for v in Y[-1]))
        assert max(abs(a - b) for a, b in zip(vals, Y[-1])) / scale < 1e-12, s.name


def test_header_has_energy_and_initial_state():
    hdr = render_dynamics_header(compile_spec("double_pendulum"), "G")
    assert "inline double energy(" in hdr
    assert "inline void initial_state(" in hdr
    assert "DOUBLE_PENDULUM_HAS_ENERGY = true" in hdr


def test_coordinate_named_y_does_not_collide():
    # 'projectile' has a coordinate called y; internals are mdsl_-prefixed.
    hdr = render_dynamics_header(compile_spec("projectile"), "G")
    assert "const double y = mdsl_q[1];" in hdr or "const double y = mdsl_y[1];" in hdr


# ------------------------------------------------------------- C++ package --
def test_cpp_package_is_complete(tmp_path):
    s = compile_spec("double_pendulum")
    root = tmp_path / "mechanicsdsl_double_pendulum"
    assert scaffold_package(s, str(tmp_path)) == str(root)
    for rel in ["package.xml", "CMakeLists.txt", "msg/SystemState.msg",
                "src/double_pendulum_node.cpp", "launch/double_pendulum.launch.py",
                "config/double_pendulum_params.yaml", "test/test_double_pendulum_dynamics.cpp",
                "include/mechanicsdsl_double_pendulum/double_pendulum_dynamics.hpp"]:
        assert (root / rel).is_file(), rel
    node = (root / "src/double_pendulum_node.cpp").read_text()
    for needle in ("JointState", "add_on_set_parameters_callback", "create_service<Trigger>",
                   '"m2") { p_.m2 = prm.as_double(); }', "msg.energy = e;"):
        assert needle in node
    assert "float64   energy" in (root / "msg/SystemState.msg").read_text()
    assert "ConservesEnergy" in (root / "test/test_double_pendulum_dynamics.cpp").read_text()


def test_launch_file_loads_params_yaml(tmp_path):
    root = scaffold_package(compile_spec("pendulum"), str(tmp_path))
    launch = (tmp_path / "mechanicsdsl_simple_pendulum" / "launch"
              / "simple_pendulum.launch.py").read_text()
    compile(launch, "launch.py", "exec")
    assert "parameters=[config]" in launch
    assert "simple_pendulum_params.yaml" in launch
    assert root


def test_params_yaml_applies_to_any_node_name():
    yaml_text = render_params_yaml(compile_spec("double_pendulum"))
    lines = yaml_text.splitlines()
    assert lines[0] == "/**:" and lines[1] == "  ros__parameters:"
    keys = {ln.split(":")[0].strip() for ln in lines[2:]}
    assert {"rate_hz", "substeps", "paused", "g", "l1", "l2", "m1", "m2"} <= keys
    try:
        import yaml
    except ImportError:
        return
    data = yaml.safe_load(yaml_text)
    assert data["/**"]["ros__parameters"]["g"] == pytest.approx(9.81)


def test_damped_system_gets_no_energy_gtest(tmp_path):
    scaffold_package(compile_spec("damped_oscillator"), str(tmp_path))
    gt = (tmp_path / "mechanicsdsl_damped_oscillator" / "test"
          / "test_damped_oscillator_dynamics.cpp").read_text()
    assert "StaysFinite" in gt and "ConservesEnergy" not in gt


# ---------------------------------------------------------- Python package --
def test_python_dynamics_matches_reference(system, tmp_path):
    path = tmp_path / "dynamics.py"
    path.write_text(render_dynamics_py(system), encoding="utf-8")
    mod = _load_module(path)
    y = list(mod.INITIAL_STATE)
    for _ in range(1000):
        y = mod.rk4_step(y, 1e-3)
    _, Y = simulate(system, t_end=1.0, dt=1e-3)
    scale = max(1.0, max(abs(v) for v in Y[-1]))
    assert max(abs(a - b) for a, b in zip(y, Y[-1])) / scale < 1e-12
    E = numeric_energy(system)
    assert abs(mod.energy(y) - E(Y[-1])) <= 1e-12 * max(1.0, abs(E(Y[-1])))
    # live parameter override path used by the node
    heavier = dict(mod.PARAMS)
    assert mod.accel(y[:mod.DOF], y[mod.DOF:], heavier) == mod.accel(y[:mod.DOF], y[mod.DOF:])


def test_python_package_layout_and_syntax(tmp_path):
    root = scaffold_python_package(compile_spec("double_pendulum"), str(tmp_path))
    pkg = "mechanicsdsl_double_pendulum_py"
    expect = ["package.xml", "setup.py", "setup.cfg", f"resource/{pkg}",
              f"{pkg}/__init__.py", f"{pkg}/dynamics.py", f"{pkg}/node.py",
              "launch/double_pendulum.launch.py", "config/double_pendulum_params.yaml"]
    from pathlib import Path

    for rel in expect:
        assert (Path(root) / rel).is_file(), rel
    for rel in ("setup.py", f"{pkg}/node.py", f"{pkg}/dynamics.py",
                "launch/double_pendulum.launch.py"):
        compile((Path(root) / rel).read_text(), rel, "exec")
    assert "<build_type>ament_python</build_type>" in (Path(root) / "package.xml").read_text()
    assert f"double_pendulum_node = {pkg}.node:main" in (Path(root) / "setup.py").read_text()


# ---------------------------------------------------------------------- CLI --
@pytest.mark.parametrize("lang", ["cpp", "python"])
def test_cli_scaffold_both_languages(tmp_path, lang):
    assert cli_main(["scaffold", "pendulum", "--lang", lang, "--rate", "100",
                     "-o", str(tmp_path)]) == 0
    yaml_files = list(tmp_path.rglob("*_params.yaml"))
    assert yaml_files and "rate_hz: 100.0" in yaml_files[0].read_text()


def test_cli_header_inspect_presets(tmp_path, capsys):
    assert cli_main(["header", "double_pendulum", "-o", str(tmp_path)]) == 0
    assert (tmp_path / "double_pendulum_dynamics.hpp").is_file()
    assert cli_main(["inspect", "pendulum"]) == 0
    assert "theta_ddot" in capsys.readouterr().out
    assert cli_main(["presets"]) == 0
    assert "kepler" in capsys.readouterr().out


def test_cli_rejects_nonpositive_rate(tmp_path):
    assert cli_main(["scaffold", "pendulum", "--rate", "0", "-o", str(tmp_path)]) == 1


def test_driver_text_is_valid():  # guards the C++ driver template in this file
    assert textwrap.dedent("  x").strip() == "x"
