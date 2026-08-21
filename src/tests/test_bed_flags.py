"""Tests for the --bed-* argparse flags and the args.bed_reachable lifecycle.

These tests cover:

- Default values for every new flag (host=localhost, port=8765, etc).
- CLI overrides for each flag.
- The database args still parse (we just hid them from --help).
- empyre.lib.init sets args.bed_reachable correctly in three states:
  bed_disable=True, bed unreachable, bed reachable.
"""

import argparse
from unittest.mock import patch

import pytest

from empyre.lib import buildargs, init


def _parse_args(argv):
    parser = buildargs()
    return parser.parse_args(argv)


class TestBedFlagDefaults:
    def test_default_bed_host_is_localhost(self):
        ns = _parse_args([])
        assert ns.bed_host == "localhost"

    def test_default_bed_port_is_8765(self):
        ns = _parse_args([])
        assert ns.bed_port == 8765

    def test_default_bed_path_is_slash(self):
        ns = _parse_args([])
        assert ns.bed_path == "/"

    def test_default_bed_probe_timeout_is_quarter_second(self):
        ns = _parse_args([])
        assert ns.bed_probe_timeout == 0.25

    def test_default_bed_call_timeout_is_five_seconds(self):
        ns = _parse_args([])
        assert ns.bed_call_timeout == 5.0

    def test_default_bed_disable_is_false(self):
        ns = _parse_args([])
        assert ns.bed_disable is False


class TestBedFlagOverrides:
    def test_cli_override_bed_host(self):
        ns = _parse_args(["--bed-host", "bed.internal"])
        assert ns.bed_host == "bed.internal"

    def test_cli_override_bed_port(self):
        ns = _parse_args(["--bed-port", "9999"])
        assert ns.bed_port == 9999

    def test_cli_override_bed_path(self):
        ns = _parse_args(["--bed-path", "/api"])
        assert ns.bed_path == "/api"

    def test_cli_override_bed_probe_timeout(self):
        ns = _parse_args(["--bed-probe-timeout", "1.5"])
        assert ns.bed_probe_timeout == 1.5

    def test_cli_override_bed_call_timeout(self):
        ns = _parse_args(["--bed-call-timeout", "30"])
        assert ns.bed_call_timeout == 30.0

    def test_cli_set_bed_disable(self):
        ns = _parse_args(["--bed-disable"])
        assert ns.bed_disable is True


class TestDatabaseArgsStillAccepted:
    """Regression guard: --database* is hidden from --help but still parses."""

    def test_databasename_override(self):
        ns = _parse_args(["--databasename", "mygame"])
        assert ns.databasename == "mygame"

    def test_databasehost_override(self):
        ns = _parse_args(["--databasehost", "10.0.0.1"])
        assert ns.databasehost == "10.0.0.1"

    def test_databaseport_override(self):
        ns = _parse_args(["--databaseport", "6543"])
        assert ns.databaseport == 6543

    def test_database_args_have_defaults(self):
        ns = _parse_args([])
        for attr in (
            "databasename",
            "databasehost",
            "databaseport",
            "databaseuser",
            "databasepassword",
        ):
            assert hasattr(ns, attr), f"missing database arg: {attr}"


class TestInitBedReachable:
    def test_init_sets_bed_reachable_false_when_disabled(self):
        args = argparse.Namespace(bed_disable=True)
        with patch("empyre.bed_client.probe_bed") as mock_probe:
            result = init(args)
        assert result is True
        assert args.bed_reachable is False
        mock_probe.assert_not_called()

    def test_init_sets_bed_reachable_false_when_unreachable(self):
        args = argparse.Namespace(bed_disable=False)
        with patch("empyre.bed_client.probe_bed", return_value=False) as mock_probe:
            result = init(args)
        assert result is True
        assert args.bed_reachable is False
        mock_probe.assert_called_once_with(args)

    def test_init_sets_bed_reachable_true_when_reachable(self):
        args = argparse.Namespace(bed_disable=False)
        with patch("empyre.bed_client.probe_bed", return_value=True):
            result = init(args)
        assert result is True
        assert args.bed_reachable is True

    def test_init_works_with_minimal_namespace(self):
        """init() must not crash on a test fixture namespace that
        lacks bed_host / bed_port (conftest builds a minimal one)."""
        args = argparse.Namespace(bed_disable=True)
        with patch("empyre.bed_client.probe_bed"):
            result = init(args)
        assert result is True
        assert args.bed_reachable is False
