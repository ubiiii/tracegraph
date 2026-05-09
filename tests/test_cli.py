import subprocess
import sys
from pathlib import Path


def run_cli(args, cwd):
    return subprocess.run([sys.executable, "-m", "tracegraph.cli", *args], cwd=cwd, capture_output=True, text=True)


def test_prepare_demo_and_build_graph(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    out_demo = repo / "data" / "demo"
    r1 = run_cli(["prepare-demo", "--output-dir", str(out_demo), "--force"], repo)
    assert r1.returncode == 0, r1.stderr
    r2 = run_cli(["build-graph", "--input-dir", str(out_demo)], repo)
    assert r2.returncode == 0, r2.stderr


def test_retrieve_and_answer(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    demo = repo / "data" / "demo"
    assert run_cli(["prepare-demo", "--output-dir", str(demo), "--force"], repo).returncode == 0
    assert run_cli(["build-graph", "--input-dir", str(demo)], repo).returncode == 0
    r = run_cli(
        [
            "retrieve",
            "--question",
            "What decision did we make about data retention, and which compliance clause justified it?",
        ],
        repo,
    )
    assert r.returncode == 0, r.stderr
