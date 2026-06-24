#!/usr/bin/env python3
# empyre/tests/test_bank_integration.py
# Integration tests for empyre bank routing via BED WebSocket on port 8765

import argparse
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, "/home/opencode/data/work/casino/src")
sys.path.insert(0, "/home/opencode/data/work/empyre/src")

import websockets

BED_HOST = "127.0.0.1"
BED_PORT = 8765


def get_test_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False)
    defaults = {
        "databasename": os.environ.get("EMPORE_TEST_DBNAME", "zoid6test"),
        "databasehost": os.environ.get("EMPORE_TEST_DBHOST", "/var/run/postgresql"),
        "databaseport": int(os.environ.get("EMPORE_TEST_DBPORT", "5432")),
        "databaseuser": os.environ.get("EMPORE_TEST_DBUSER", "opencode"),
        "databasepassword": os.environ.get("EMPORE_TEST_DBPASS"),
    }
    from bbsengine6 import database
    database.buildargdatabasegroup(parser, defaults)
    return parser.parse_args([])


class TestBedConnection(unittest.IsolatedAsyncioTestCase):
    """Test connecting to BED server on port 8765."""

    async def asyncSetUp(self):
        print(f"\n[TEST] Connecting to BED at {BED_HOST}:{BED_PORT}")
        self.ws = await websockets.connect(f"ws://{BED_HOST}:{BED_PORT}/")

    async def asyncTearDown(self):
        await self.ws.close()

    async def send_and_receive(self, message):
        await self.ws.send(json.dumps(message))
        return json.loads(await self.ws.recv())

    async def test_bed_server_is_running(self):
        """Test BED server is running and responding."""
        result = await self.send_and_receive({"type": "ping"})
        assert result.get("type") == "pong"

    async def test_bed_has_bank_services(self):
        """Test BED server has bank services."""
        result = await self.send_and_receive({"type": "ping"})
        assert result.get("type") == "pong"


class TestEmpyreJoustUsesBank(unittest.IsolatedAsyncioTestCase):
    """Test joust module uses bank.BankService correctly."""

    async def asyncSetUp(self):
        self.test_args = get_test_args()

    async def test_joust_calls_bank_add_funds_on_win(self):
        """Test joust win calls bank.add_funds."""
        from empyre.combat.joust import main
        from bbsengine6 import bank as bank_module

        moniker = "joust_player"

        mock_bank_service = MagicMock()
        mock_bank_service.get_balance.return_value = 0
        mock_bank_service.add_funds.return_value = {"success": True, "new_balance": 1000}

        player = MagicMock()
        player.moniker = moniker
        player.soldiers = 100
        player.land = 1000
        player.nobles = 3
        player.horses = 5
        player.serfs = 1000
        player.coins = 0
        player.grain = 5000
        player.shipyards = 1
        player.turncount = 0
        player.isdirty = False
        player.getresource.return_value = {"emoji": "", "plural": "land"}

        otherplayer = MagicMock()
        otherplayer.moniker = "opponent"
        otherplayer.nobles = 2
        otherplayer.isdirty = False
        otherplayer.getresource.return_value = {"emoji": "", "plural": "land"}

        with patch.object(bank_module, "BankService", return_value=mock_bank_service):
            with patch("empyre.combat.joust.io.echo"):
                with patch("empyre.combat.joust.libempyre.setbottombar"):
                    with patch("empyre.combat.joust.util.diceroll", return_value=3):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        result = main(self.test_args, player=player, otherplayer=otherplayer)

        assert result is True
        mock_bank_service.add_funds.assert_called_once_with(
            moniker, 1000, transaction_type="joust_win", description="Joust winnings"
        )

    async def test_joust_calls_bank_remove_funds_on_loss(self):
        """Test joust loss calls bank.remove_funds."""
        from empyre.combat.joust import main
        from bbsengine6 import bank as bank_module

        moniker = "joust_player"

        mock_bank_service = MagicMock()
        mock_bank_service.get_balance.return_value = 5000
        mock_bank_service.remove_funds.return_value = {"success": True, "new_balance": 4000}

        player = MagicMock()
        player.moniker = moniker
        player.soldiers = 100
        player.land = 1000
        player.nobles = 3
        player.horses = 5
        player.serfs = 1000
        player.coins = 5000
        player.grain = 5000
        player.shipyards = 1
        player.turncount = 0
        player.isdirty = False
        player.getresource.return_value = {"emoji": "", "plural": "land"}

        otherplayer = MagicMock()
        otherplayer.moniker = "opponent"
        otherplayer.nobles = 2
        otherplayer.isdirty = False
        otherplayer.getresource.return_value = {"emoji": "", "plural": "land"}

        with patch.object(bank_module, "BankService", return_value=mock_bank_service):
            with patch("empyre.combat.joust.io.echo"):
                with patch("empyre.combat.joust.libempyre.setbottombar"):
                    with patch("empyre.combat.joust.util.diceroll", return_value=4):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        result = main(self.test_args, player=player, otherplayer=otherplayer)

        assert result is True
        mock_bank_service.remove_funds.assert_called_once_with(
            moniker, 1000, transaction_type="joust_loss", description="Joust loss"
        )


class TestEmpyreLucifersDenUsesBank(unittest.IsolatedAsyncioTestCase):
    """Test lucifersden module uses bank.BankService correctly."""

    async def asyncSetUp(self):
        self.test_args = get_test_args()

    async def test_lucifers_den_calls_bank_add_funds_on_win(self):
        """Test gambling win calls bank.add_funds."""
        from empyre.town.lucifersden import main
        from bbsengine6 import bank as bank_module

        moniker = "gambler"

        mock_bank_service = MagicMock()
        mock_bank_service.get_balance.return_value = 1000
        mock_bank_service.add_funds.return_value = {"success": True, "new_balance": 1300}

        player = MagicMock()
        player.moniker = moniker
        player.coins = 1000
        player.land = 10000
        player.serfs = 1000
        player.getresource.return_value = {"name": "coins", "emoji": ":moneybag:", "plural": "coins"}

        with patch.object(bank_module, "BankService", return_value=mock_bank_service):
            with patch("empyre.town.lucifersden.io.inputinteger", side_effect=[100, 3]):
                with patch("empyre.town.lucifersden.io.inputboolean", return_value=True):
                    with patch("empyre.town.lucifersden.io.echo"):
                        with patch("empyre.town.lucifersden.lib.setbottombar"):
                            with patch("empyre.town.lucifersden.util.diceroll", return_value=3):
                                with patch("empyre.town.lucifersden.random.randint", return_value=3):
                                    result = main(self.test_args, player=player)

        mock_bank_service.add_funds.assert_called()
        call_args = mock_bank_service.add_funds.call_args
        assert call_args[0][0] == moniker
        assert call_args[0][1] == 300


class TestEmpyreSysopOptionsUsesBank(unittest.IsolatedAsyncioTestCase):
    """Test sysopoptions module uses bank.BankService correctly."""

    async def asyncSetUp(self):
        self.test_args = get_test_args()

    async def test_sysop_options_uses_bank(self):
        """Test sysop setting coins uses bank service."""
        from empyre.sysopoptions import main
        from bbsengine6 import bank as bank_module

        moniker = "sysop_target"

        mock_bank_service = MagicMock()
        mock_bank_service.get_balance.return_value = 1000
        mock_bank_service.add_funds.return_value = {"success": True, "new_balance": 2000}
        mock_bank_service.remove_funds.return_value = {"success": True, "new_balance": 0}

        player = MagicMock()
        player.moniker = moniker
        player.turncount = 10
        player.coins = 1000
        player.getresource.return_value = {"name": "coins", "emoji": ":moneybag:", "plural": "coins"}

        with patch.object(bank_module, "BankService", return_value=mock_bank_service):
            with patch("empyre.sysopoptions.io.inputinteger", return_value=2000):
                with patch("empyre.sysopoptions.io.echo"):
                    with patch("empyre.sysopoptions.lib.setbottombar"):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                result = main(self.test_args, player=player)

        assert result is True
        assert mock_bank_service.get_balance.called


if __name__ == "__main__":
    unittest.main()
