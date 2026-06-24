# empyre/src/tests/test_api_handler.py
# Tests for empyre WebSocket API handler

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from empyre.api.handler import (
    SessionManager,
    BaseService,
    AuthService,
    MemberServiceHandler,
    IslandServiceHandler,
    ShipServiceHandler,
    TownServiceHandler,
    MarketServiceHandler,
    ChatServiceHandler,
    BankServiceHandler,
    MessageRouter,
)


class TestSessionManager:
    def test_init(self):
        sm = SessionManager()
        assert sm._sessions == {}
        assert sm._islands == {}

    def test_register_session(self):
        sm = SessionManager()
        sm.register_session(1, "testuser", is_sysop=False)
        assert sm.get_moniker(1) == "testuser"
        assert sm.get_is_sysop(1) is False

    def test_register_session_sysop(self):
        sm = SessionManager()
        sm.register_session(1, "testuser", is_sysop=True)
        assert sm.get_is_sysop(1) is True

    def test_unregister_session(self):
        sm = SessionManager()
        sm.register_session(1, "testuser")
        sm.unregister_session(1)
        assert sm.get_moniker(1) is None

    def test_set_island_moniker(self):
        sm = SessionManager()
        sm.register_session(1, "testuser")
        sm.set_island_moniker(1, "test_island")
        assert sm.get_island_moniker(1) == "test_island"

    def test_get_session(self):
        sm = SessionManager()
        sm.register_session(1, "testuser")
        session = sm.get_session(1)
        assert session["moniker"] == "testuser"


class TestAuthService:
    def test_init(self, test_args):
        sm = SessionManager()
        auth = AuthService(test_args, sm)
        assert auth.args is test_args
        assert auth.sessions is sm

    def test_handle_ping(self, test_args):
        sm = SessionManager()
        auth = AuthService(test_args, sm)
        server = Mock()
        websocket = Mock()
        message = {"type": "ping"}

        result = AuthService.handle_message(auth, server, websocket, "", message)
        assert result["type"] == "pong"
        assert "timestamp" in result


class TestMessageRouter:
    def test_init(self, test_args):
        router = MessageRouter(test_args)
        assert router.args is test_args
        assert router.sessions is not None
        assert router.channel_state is not None

    def test_services_created(self, test_args):
        router = MessageRouter(test_args)
        assert router.auth_service is not None
        assert router.member_service is not None
        assert router.island_service is not None
        assert router.ship_service is not None
        assert router.town_service is not None
        assert router.market_service is not None
        assert router.chat_service is not None
        assert router.bank_service is not None

    def test_register_all(self, test_args):
        router = MessageRouter(test_args)
        server = Mock()
        server.register_service = Mock()

        router.register_all(server)

        assert server.register_service.call_count >= 8

    def test_unregister_session(self, test_args):
        router = MessageRouter(test_args)
        router.sessions.register_session(1, "testuser")

        router.unregister_session(1)
        assert router.sessions.get_moniker(1) is None


class TestMemberServiceHandler:
    def test_init(self, test_args):
        sm = SessionManager()
        handler = MemberServiceHandler(test_args, sm)
        assert handler.args is test_args
        assert handler.sessions is sm


class TestIslandServiceHandler:
    def test_init(self, test_args):
        sm = SessionManager()
        handler = IslandServiceHandler(test_args, sm)
        assert handler.args is test_args
        assert handler.sessions is sm


class TestShipServiceHandler:
    def test_init(self, test_args):
        sm = SessionManager()
        handler = ShipServiceHandler(test_args, sm)
        assert handler.args is test_args
        assert handler.sessions is sm


class TestTownServiceHandler:
    def test_init(self, test_args):
        sm = SessionManager()
        handler = TownServiceHandler(test_args, sm)
        assert handler.args is test_args
        assert handler.sessions is sm


class TestMarketServiceHandler:
    def test_init(self, test_args):
        sm = SessionManager()
        handler = MarketServiceHandler(test_args, sm)
        assert handler.args is test_args
        assert handler.sessions is sm


class TestChatServiceHandler:
    def test_init(self, test_args):
        sm = SessionManager()
        handler = ChatServiceHandler(test_args, sm)
        assert handler.args is test_args
        assert handler.sessions is sm

    @pytest.mark.asyncio
    async def test_handle_chat_global_not_authenticated(self, test_args):
        sm = SessionManager()
        handler = ChatServiceHandler(test_args, sm)
        server = Mock()
        websocket = Mock()
        message = {"type": "chat_global", "message": "Hello"}

        result = await handler.handle_message(server, websocket, "", message)
        assert result["code"] == "not_authenticated"

    @pytest.mark.asyncio
    async def test_handle_chat_global_authenticated(self, test_args):
        sm = SessionManager()
        sm.register_session(1, "testuser")
        handler = ChatServiceHandler(test_args, sm)
        server = Mock()
        websocket = Mock()
        message = {"type": "chat_global", "message": "Hello"}

        result = await handler.handle_message(server, websocket, "", message)
        assert result["type"] == "chat_message"
        assert result["scope"] == "global"
        assert result["from_moniker"] == "testuser"
        assert result["message"] == "Hello"


class TestBankServiceHandler:
    def test_init(self, test_args):
        sm = SessionManager()
        handler = BankServiceHandler(test_args, sm)
        assert handler.args is test_args
        assert handler.sessions is sm
        assert handler.bank_service is not None
