# ABOUTME: Tests for CLI command structure and argument parsing
# ABOUTME: Verifies help output and command availability

"""Tests for CLI commands."""

from click.testing import CliRunner

from src.cli import main


def test_cli_version():
    """Test --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "sovereign" in result.output
    assert "0.1.0" in result.output


def test_cli_help():
    """Test --help flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Sovereign Compliance Demo" in result.output
    assert "setup" in result.output
    assert "validate" in result.output
    assert "demo" in result.output
    assert "evidence" in result.output


def test_setup_help():
    """Test setup command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["setup", "--help"])
    assert result.exit_code == 0
    assert "--cluster-name" in result.output
    assert "--region" in result.output
    assert "--method" in result.output


def test_validate_help():
    """Test validate command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--help"])
    assert result.exit_code == 0
    assert "--verbose" in result.output
    assert "--json" in result.output


def test_demo_list_help():
    """Test demo list command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["demo", "list", "--help"])
    assert result.exit_code == 0


def test_demo_run_help():
    """Test demo run command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["demo", "run", "--help"])
    assert result.exit_code == 0
    assert "SCENARIO" in result.output


def test_evidence_export_help():
    """Test evidence export command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["evidence", "export", "--help"])
    assert result.exit_code == 0
    assert "--days" in result.output
    assert "--output" in result.output


def test_evidence_verify_help():
    """Test evidence verify command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["evidence", "verify", "--help"])
    assert result.exit_code == 0
    assert "PACKAGE_PATH" in result.output
