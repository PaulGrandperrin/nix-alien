from pathlib import Path
from unittest.mock import call, patch

from nix_alien import fhs_shell


@patch("nix_alien.fhs_shell.find_libs")
def test_create_fhs_shell(mock_find_libs):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    assert (
        fhs_shell.create_fhs_shell("xyz")
        == """\
{ pkgs ? import <nixpkgs> { } }:

let
  inherit (pkgs) buildFHSUserEnv;
in
buildFHSUserEnv {
  name = "xyz-fhs";
  targetPkgs = p: with p; [
    bar.out
    foo.out
    quux.out
  ];
  runScript = "%s/xyz";
}
"""
        % Path(__file__).parent.parent.absolute()
    )


@patch("nix_alien.fhs_shell.subprocess")
@patch("nix_alien.fhs_shell.find_libs")
def test_main_wo_args(mock_find_libs, mock_subprocess, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }
    fhs_shell.main(["xyz"])
    shell_nix = next((tmp_path / ".cache/nix-alien").glob("*/fhs-env/default.nix"))

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 2


@patch("nix_alien.fhs_shell.subprocess")
@patch("nix_alien.fhs_shell.find_libs")
def test_main_with_args(mock_find_libs, mock_subprocess, tmp_path):
    mock_find_libs.return_value = {
        "libfoo.so": "foo.out",
        "libfoo.6.so": "foo.out",
        "libbar.so": "bar.out",
        "libquux.so": "quux.out",
    }

    fhs_shell.main(["xyz", "--destination", str(tmp_path), "--recreate"])
    shell_nix = tmp_path / "default.nix"

    assert shell_nix.is_file()
    assert mock_subprocess.run.call_count == 2
