"""Exercise the real UI build entry points without package downloads."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "entry", ["docker/build_admin_ui.sh", "ui/litellm-dashboard/build_ui.sh"]
)
@pytest.mark.parametrize("version", ["18.17.0", "20.18.1", "selected"])
def test_ui_build_preserves_selected_node(tmp_path, entry, version):
    selected = (ROOT / ".node-version").read_text().strip()
    for name in [
        ".node-version",
        "docker/check_node_runtime.sh",
        "docker/build_admin_ui.sh",
        "ui/litellm-dashboard/build_ui.sh",
    ]:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        target.chmod(0o755)
    colors = tmp_path / "enterprise/enterprise_ui/enterprise_colors.json"
    colors.parent.mkdir(parents=True)
    colors.write_text('{"primary_color": "test"}')
    ui = tmp_path / "ui/litellm-dashboard"
    (ui / "ui_colors.json").write_text(colors.read_text())
    output = tmp_path / "litellm/proxy/_experimental/out"
    output.mkdir(parents=True)
    binaries = tmp_path / "bin"
    binaries.mkdir()
    (binaries / "node").write_text('#!/bin/sh\nprintf "%s\\n" "$TEST_NODE_VERSION"\n')
    (binaries / "npm").write_text(
        '#!/bin/sh\nif [ "$1" = "--version" ]; then echo 10.9.2; exit 0; fi\n[ "$*" = "ci" ] && exit 0\n[ "$*" = "run build" ] || exit 98\nmkdir -p out\nprintf built > out/index.html\n'
    )
    for name in ["nvm", "curl", "apt-get", "apk", "brew"]:
        (binaries / name).write_text("#!/bin/sh\nexit 99\n")
    for binary in binaries.iterdir():
        binary.chmod(0o755)
    env = dict(
        os.environ,
        PATH=f"{binaries}:{os.environ['PATH']}",
        HOME=str(tmp_path),
        TEST_NODE_VERSION=selected if version == "selected" else version,
    )
    cwd = tmp_path if entry.startswith("docker/") else ui
    result = subprocess.run(
        ["bash", str(tmp_path / entry)],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    if version == "selected":
        assert result.returncode == 0, result.stdout + result.stderr
        assert (output / "index.html").read_text() == "built"
    else:
        assert result.returncode != 0
        assert f"requires Node.js {selected}" in result.stderr
        assert not (output / "index.html").exists()


def test_ui_guard_rejects_unavailable_node(tmp_path):
    binaries = tmp_path / "bin"
    binaries.mkdir()
    for name in ["dirname", "tr"]:
        (binaries / name).symlink_to(shutil.which(name))
    result = subprocess.run(
        [shutil.which("bash"), str(ROOT / "docker/check_node_runtime.sh")],
        env=dict(os.environ, PATH=str(binaries)),
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "install Node.js" in result.stderr


def test_prisma_source_defaults_do_not_reuse_old_global_or_cached_node(monkeypatch):
    pytest.importorskip("prisma")
    from prisma._config import Config
    from prisma.cli import _node

    for name in [
        "PRISMA_USE_GLOBAL_NODE",
        "PRISMA_USE_NODEJS_BIN",
        "PRISMA_NODEENV_EXTRA_ARGS",
        "PRISMA_NODEENV_CACHE_DIR",
    ]:
        monkeypatch.delenv(name, raising=False)
    config = Config.load(ROOT / "pyproject.toml")
    selected = (ROOT / ".node-version").read_text().strip()
    assert not config.use_global_node
    assert not config.use_nodejs_bin
    assert config.nodeenv_extra_args == [f"--node={selected}"]
    assert selected in str(config.nodeenv_cache_dir)
    monkeypatch.setattr(_node, "config", config)

    def reject_global_lookup(_target):
        raise AssertionError(
            "standalone defaults must not inspect an old global runtime"
        )

    monkeypatch.setattr(_node, "_get_global_binary", reject_global_lookup)
    provisioned = object()
    monkeypatch.setattr(
        _node.NodeBinaryStrategy,
        "from_nodeenv",
        classmethod(lambda cls, target: provisioned),
    )
    assert _node.resolve("node") is provisioned
    assert _node.resolve("npm") is provisioned

    monkeypatch.setenv("PRISMA_USE_GLOBAL_NODE", "true")
    assert Config.load(ROOT / "pyproject.toml").use_global_node
