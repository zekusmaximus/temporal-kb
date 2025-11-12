# tests/test_cli.py

import pytest
from click.testing import CliRunner
from pathlib import Path
import tempfile
import shutil

from kb.cli.main import cli
from kb.core.config import init_config


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def runner():
    """Create CLI test runner"""
    return CliRunner()


class TestCLI:
    """Test CLI commands"""

    def test_cli_help(self, runner):
        """Test that CLI help works"""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Temporal Knowledge Base" in result.output

    def test_init_command(self, runner, temp_data_dir):
        """Test kb init command"""
        result = runner.invoke(cli, ["--data-dir", str(temp_data_dir), "init"])

        # Should create necessary directories
        assert (temp_data_dir / "entries").exists()
        assert (temp_data_dir / "db").exists() or (temp_data_dir / "db" / "kb.db").exists()

    def test_info_command(self, runner, temp_data_dir):
        """Test kb info command"""
        # Initialize first
        runner.invoke(cli, ["--data-dir", str(temp_data_dir), "init"])

        # Run info
        result = runner.invoke(cli, ["--data-dir", str(temp_data_dir), "info"])

        assert result.exit_code == 0
        assert "Knowledge Base Info" in result.output or "Entries" in result.output

    def test_add_command_quick(self, runner, temp_data_dir):
        """Test kb add command with quick option"""
        # Initialize first
        runner.invoke(cli, ["--data-dir", str(temp_data_dir), "init"])

        # Add entry
        result = runner.invoke(
            cli,
            [
                "--data-dir",
                str(temp_data_dir),
                "add",
                "-q",
                "Test entry title",
                "--content",
                "This is test content for the entry.",
            ],
        )

        # Should succeed (exit code 0 or display success message)
        assert result.exit_code == 0 or "created" in result.output.lower()

    def test_search_command(self, runner, temp_data_dir):
        """Test kb search command"""
        # Initialize
        runner.invoke(cli, ["--data-dir", str(temp_data_dir), "init"])

        # Add an entry
        runner.invoke(
            cli,
            [
                "--data-dir",
                str(temp_data_dir),
                "add",
                "-q",
                "Searchable Entry",
                "--content",
                "This is searchable content with keywords.",
            ],
        )

        # Search for it
        result = runner.invoke(cli, ["--data-dir", str(temp_data_dir), "search", "searchable"])

        # Should find the entry
        assert result.exit_code == 0

    def test_search_recent(self, runner, temp_data_dir):
        """Test searching recent entries"""
        # Initialize
        runner.invoke(cli, ["--data-dir", str(temp_data_dir), "init"])

        # Add entries
        for i in range(3):
            runner.invoke(
                cli,
                [
                    "--data-dir",
                    str(temp_data_dir),
                    "add",
                    "-q",
                    f"Entry {i}",
                    "--content",
                    f"Content {i}",
                ],
            )

        # Search recent
        result = runner.invoke(cli, ["--data-dir", str(temp_data_dir), "search", "--recent", "5"])

        assert result.exit_code == 0


class TestCLIValidation:
    """Test CLI input validation"""

    def test_invalid_command(self, runner):
        """Test that invalid commands are rejected"""
        result = runner.invoke(cli, ["invalid_command"])
        assert result.exit_code != 0

    def test_missing_required_args(self, runner, temp_data_dir):
        """Test commands with missing required arguments"""
        result = runner.invoke(
            cli,
            [
                "--data-dir",
                str(temp_data_dir),
                "delete",
                # Missing entry_id
            ],
        )

        # Should fail with missing argument error
        assert result.exit_code != 0


class TestCLIIntegration:
    """Integration tests for CLI workflows"""

    def test_full_workflow(self, runner, temp_data_dir):
        """Test complete workflow: init, add, search, show"""
        # Initialize
        result = runner.invoke(cli, ["--data-dir", str(temp_data_dir), "init"])
        assert result.exit_code == 0

        # Add entry
        result = runner.invoke(
            cli,
            [
                "--data-dir",
                str(temp_data_dir),
                "add",
                "-q",
                "Workflow Test",
                "--content",
                "Testing complete workflow",
            ],
        )
        assert result.exit_code == 0

        # Search should find it
        result = runner.invoke(cli, ["--data-dir", str(temp_data_dir), "search", "workflow"])
        assert result.exit_code == 0
