# empyre/api/handler.py
# WebSocket message handler - routes messages to empyre services

from datetime import datetime
from typing import Any, Dict, Optional

from bbsengine6 import io, member
from bbsengine6.message import deliver_pending_on_connect, get_unread_count
from bbsengine6.net import (
    ChannelState,
    channel_subscribe,
    channel_unsubscribe,
    channel_unsubscribe_all,
    channel_get_session_channels,
)


class SessionManager:
    """Manages WebSocket sessions and authentication state."""

    def __init__(self):
        self._sessions: Dict[int, Dict[str, Any]] = {}
        self._islands: Dict[str, set] = {}

    def register_session(self, session_id: int, moniker: str, is_sysop: bool = False) -> None:
        self._sessions[session_id] = {"moniker": moniker, "island_moniker": None, "is_sysop": is_sysop}

    def unregister_session(self, session_id: int) -> None:
        if session_id in self._sessions:
            island_moniker = self._sessions[session_id].get("island_moniker")
            if island_moniker and island_moniker in self._islands:
                self._islands[island_moniker].discard(session_id)
            del self._sessions[session_id]

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def get_moniker(self, session_id: int) -> Optional[str]:
        session = self._sessions.get(session_id)
        return session.get("moniker") if session else None

    def get_island_moniker(self, session_id: int) -> Optional[str]:
        session = self._sessions.get(session_id)
        return session.get("island_moniker") if session else None

    def set_island_moniker(self, session_id: int, island_moniker: Optional[str]) -> None:
        io.echo(f"set_island_moniker: session_id={session_id}, island_moniker={island_moniker}", level="info")
        if session_id in self._sessions:
            self._sessions[session_id]["island_moniker"] = island_moniker

    def get_is_sysop(self, session_id: int) -> bool:
        session = self._sessions.get(session_id)
        return session.get("is_sysop", False) if session else False


class BaseService:
    """Base class for message handlers."""

    def __init__(self, args: Any, session_manager: SessionManager):
        self.args = args
        self.sessions = session_manager

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class AuthService(BaseService):
    """Handle authentication messages."""

    def __init__(self, args: Any, session_manager: SessionManager, channel_state: Optional[ChannelState] = None):
        super().__init__(args, session_manager)
        self.channel_state = channel_state

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "auth":
            return await self._handle_auth(websocket, message)
        elif msg_type == "ping":
            return {"type": "pong", "timestamp": datetime.utcnow().isoformat()}

        return None

    async def _handle_auth(self, websocket: Any, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = message.get("moniker", "")
        password = message.get("password", "")

        if not moniker:
            return {"type": "error", "code": "invalid_credentials", "message": "Moniker and password required"}

        from empyre import player as empyre_player

        player = empyre_player.loadplayer(self.args, moniker)
        if not player:
            return {
                "type": "auth_result",
                "success": False,
                "moniker": moniker,
                "message": "Player not found",
            }

        if not empyre_player.checkpassword(player, password):
            return {
                "type": "auth_result",
                "success": False,
                "moniker": moniker,
                "message": "Invalid password",
            }

        session_id = id(websocket)
        is_sysop = member.issysop(self.args, moniker=moniker) is True
        self.sessions.register_session(session_id, moniker, is_sysop=is_sysop)

        from bbsengine6 import bank

        bank_service = bank.BankService(self.args)
        balance = bank_service.get_balance(moniker)

        if self.channel_state:
            channel_subscribe(self.channel_state, session_id, f"member:{moniker}")

        pending_messages = []
        try:
            pending_messages = deliver_pending_on_connect(moniker, database=self.args.databasename)
        except Exception as e:
            io.echo(f"Failed to deliver pending messages: {e}", level="warning")

        unread_count = 0
        try:
            unread_count = get_unread_count(moniker, database=self.args.databasename)
        except Exception as e:
            io.echo(f"Failed to get unread count: {e}", level="warning")

        return {
            "type": "auth_result",
            "success": True,
            "moniker": moniker,
            "balance": balance,
            "message": "Authenticated",
            "pending_messages": pending_messages,
            "unread_count": unread_count,
            "turns": getattr(player, "turncount", 0),
            "land": getattr(player, "land", 0),
        }


class MemberServiceHandler(BaseService):
    """Handle member profile, tier, and referral messages."""

    def __init__(self, args: Any, session_manager: SessionManager):
        super().__init__(args, session_manager)
        from bbsengine6.services.member import MemberService

        self.member_service = MemberService(args)

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "member_profile":
            return await self._handle_profile(message)
        elif msg_type == "member_tier":
            return await self._handle_tier(message)
        elif msg_type == "member_referral_code":
            return await self._handle_referral_code(message)
        elif msg_type == "member_referrals":
            return await self._handle_referrals(message)

        return None

    async def _handle_profile(self, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = message.get("moniker", "")
        if not moniker:
            return {"type": "error", "code": "invalid_request", "message": "Moniker required"}

        profile = self.member_service.get_profile(moniker)
        if profile:
            return {"type": "member_profile_result", "success": True, "profile": profile}
        return {"type": "member_profile_result", "success": False, "message": "Member not found"}

    async def _handle_tier(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action", "get")
        moniker = message.get("moniker", "")

        if action == "get":
            if not moniker:
                return {"type": "error", "code": "invalid_request", "message": "Moniker required"}
            tier = self.member_service.get_tier(moniker)
            return {"type": "member_tier_result", "success": True, "moniker": moniker, "tier": tier}

        return {"type": "error", "code": "invalid_action", "message": "Invalid action"}

    async def _handle_referral_code(self, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = message.get("moniker", "")
        if not moniker:
            return {"type": "error", "code": "invalid_request", "message": "Moniker required"}

        refcode = self.member_service.get_referral_code(moniker)
        return {"type": "member_referral_code_result", "success": True, "moniker": moniker, "refcode": refcode}

    async def _handle_referrals(self, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = message.get("moniker", "")
        if not moniker:
            return {"type": "error", "code": "invalid_request", "message": "Moniker required"}

        referrals = self.member_service.get_referrals(moniker)
        return {"type": "member_referrals_result", "success": True, "moniker": moniker, "referrals": referrals}


class IslandServiceHandler(BaseService):
    """Handle island/colony management messages."""

    def __init__(self, args: Any, session_manager: SessionManager, channel_state: Optional[ChannelState] = None):
        super().__init__(args, session_manager)
        self.channel_state = channel_state

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "list_islands":
            return await self._handle_list_islands(message)
        elif msg_type == "join_island":
            return await self._handle_join_island(id(websocket), message)
        elif msg_type == "leave_island":
            return await self._handle_leave_island(id(websocket), message)
        elif msg_type == "island_info":
            return await self._handle_island_info(message)
        elif msg_type == "list_colonies":
            return await self._handle_list_colonies(message)

        return None

    async def _handle_list_islands(self, message: Dict[str, Any]) -> Dict[str, Any]:
        from empyre.island import lib as island_lib

        islands = island_lib.listislands(self.args)
        return {"type": "island_list", "islands": islands}

    async def _handle_join_island(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        island_moniker = message.get("moniker")
        if not island_moniker:
            return {"type": "error", "code": "invalid_request", "message": "island moniker required"}

        from empyre.island import lib as island_lib

        result = island_lib.joinisland(self.args, moniker, island_moniker)
        if result:
            self.sessions.set_island_moniker(session_id, island_moniker)
            if self.channel_state:
                channel_subscribe(self.channel_state, session_id, f"empyre:island:{island_moniker}")
            return {"type": "joined_island", "moniker": island_moniker}

        return {"type": "error", "code": "join_failed", "message": "Could not join island"}

    async def _handle_leave_island(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        island_moniker = self.sessions.get_island_moniker(session_id)
        if not island_moniker:
            return {"type": "error", "code": "not_at_island"}

        self.sessions.set_island_moniker(session_id, None)
        if self.channel_state:
            channel_unsubscribe(self.channel_state, session_id, f"empyre:island:{island_moniker}")

        return {"type": "left_island", "moniker": island_moniker}

    async def _handle_island_info(self, message: Dict[str, Any]) -> Dict[str, Any]:
        island_moniker = message.get("moniker")
        if not island_moniker:
            return {"type": "error", "code": "invalid_request", "message": "island moniker required"}

        from empyre.island import lib as island_lib

        island = island_lib.getisland(self.args, island_moniker)
        if island:
            return {"type": "island_info", "island": island}

        return {"type": "error", "code": "not_found", "message": "Island not found"}

    async def _handle_list_colonies(self, message: Dict[str, Any]) -> Dict[str, Any]:
        island_moniker = message.get("island_moniker", "")
        from empyre.colony import lib as colony_lib

        colonies = colony_lib.listcolonies(self.args, island_moniker)
        return {"type": "colony_list", "colonies": colonies}


class ShipServiceHandler(BaseService):
    """Handle ship management messages."""

    def __init__(self, args: Any, session_manager: SessionManager, channel_state: Optional[ChannelState] = None):
        super().__init__(args, session_manager)
        self.channel_state = channel_state

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "list_ships":
            return await self._handle_list_ships(message)
        elif msg_type == "ship_info":
            return await self._handle_ship_info(message)
        elif msg_type == "buy_ship":
            return await self._handle_buy_ship(id(websocket), message)
        elif msg_type == "sail_ship":
            return await self._handle_sail_ship(id(websocket), message)

        return None

    async def _handle_list_ships(self, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = message.get("moniker", "")
        from empyre.ship import lib as ship_lib

        ships = ship_lib.listships(self.args, moniker)
        return {"type": "ship_list", "ships": ships}

    async def _handle_ship_info(self, message: Dict[str, Any]) -> Dict[str, Any]:
        ship_id = message.get("ship_id")
        if not ship_id:
            return {"type": "error", "code": "invalid_request", "message": "ship_id required"}

        from empyre.ship import lib as ship_lib

        ship = ship_lib.getship(self.args, ship_id)
        if ship:
            return {"type": "ship_info", "ship": ship}

        return {"type": "error", "code": "not_found", "message": "Ship not found"}

    async def _handle_buy_ship(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        ship_kind = message.get("kind", "passenger")
        from empyre.ship import lib as ship_lib

        result = ship_lib.buyship(self.args, moniker, ship_kind)
        return result

    async def _handle_sail_ship(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        ship_id = message.get("ship_id")
        destination = message.get("destination")

        if not ship_id or not destination:
            return {"type": "error", "code": "invalid_request", "message": "ship_id and destination required"}

        from empyre.ship import lib as ship_lib

        result = ship_lib.sailship(self.args, moniker, ship_id, destination)
        return result


class TownServiceHandler(BaseService):
    """Handle town management messages."""

    def __init__(self, args: Any, session_manager: SessionManager):
        super().__init__(args, session_manager)

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "list_towns":
            return await self._handle_list_towns(message)
        elif msg_type == "town_info":
            return await self._handle_town_info(message)
        elif msg_type == "town_tax":
            return await self._handle_town_tax(id(websocket), message)
        elif msg_type == "recruit_soldiers":
            return await self._handle_recruit_soldiers(id(websocket), message)

        return None

    async def _handle_list_towns(self, message: Dict[str, Any]) -> Dict[str, Any]:
        island_moniker = message.get("island_moniker", "")
        from empyre.town import lib as town_lib

        towns = town_lib.listtowns(self.args, island_moniker)
        return {"type": "town_list", "towns": towns}

    async def _handle_town_info(self, message: Dict[str, Any]) -> Dict[str, Any]:
        town_name = message.get("name")
        if not town_name:
            return {"type": "error", "code": "invalid_request", "message": "town name required"}

        from empyre.town import lib as town_lib

        town = town_lib.gettown(self.args, town_name)
        if town:
            return {"type": "town_info", "town": town}

        return {"type": "error", "code": "not_found", "message": "Town not found"}

    async def _handle_town_tax(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        town_name = message.get("town")
        rate = message.get("rate")

        if not town_name or rate is None:
            return {"type": "error", "code": "invalid_request", "message": "town and rate required"}

        from empyre.town import changetaxrate

        result = changetaxrate.changetaxrate(self.args, moniker, town_name, rate)
        return result

    async def _handle_recruit_soldiers(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        town_name = message.get("town")
        amount = message.get("amount", 0)

        if not town_name or amount <= 0:
            return {"type": "error", "code": "invalid_request", "message": "town and amount required"}

        from empyre.town import trainsoldiers

        result = trainsoldiers.trainsoldiers(self.args, moniker, town_name, amount)
        return result


class MarketServiceHandler(BaseService):
    """Handle market trading messages."""

    def __init__(self, args: Any, session_manager: SessionManager):
        super().__init__(args, session_manager)

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "market_prices":
            return await self._handle_market_prices(message)
        elif msg_type == "buy_resource":
            return await self._handle_buy_resource(id(websocket), message)
        elif msg_type == "sell_resource":
            return await self._handle_sell_resource(id(websocket), message)

        return None

    async def _handle_market_prices(self, message: Dict[str, Any]) -> Dict[str, Any]:
        from empyre import market

        prices = market.getprices(self.args)
        return {"type": "market_prices", "prices": prices}

    async def _handle_buy_resource(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        resource = message.get("resource")
        quantity = message.get("quantity", 0)

        if not resource or quantity <= 0:
            return {"type": "error", "code": "invalid_request", "message": "resource and quantity required"}

        from empyre import market

        result = market.buy(self.args, moniker, resource, quantity)
        return result

    async def _handle_sell_resource(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        resource = message.get("resource")
        quantity = message.get("quantity", 0)

        if not resource or quantity <= 0:
            return {"type": "error", "code": "invalid_request", "message": "resource and quantity required"}

        from empyre import market

        result = market.sell(self.args, moniker, resource, quantity)
        return result


class ChatServiceHandler(BaseService):
    """Handle chat messages."""

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type in ("chat_island", "chat_global", "emote"):
            return await self._handle_chat(id(websocket), msg_type, message)

        return None

    async def _handle_chat(
        self, session_id: int, msg_type: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        chat_msg = message.get("message", "")

        if msg_type == "chat_island":
            island_moniker = self.sessions.get_island_moniker(session_id)
            if not island_moniker:
                return {"type": "error", "code": "not_at_island"}

            return {
                "type": "chat_message",
                "from_moniker": moniker,
                "message": chat_msg,
                "scope": "island",
                "moniker": island_moniker,
                "timestamp": datetime.utcnow().isoformat(),
            }

        elif msg_type == "chat_global":
            return {
                "type": "chat_message",
                "from_moniker": moniker,
                "message": chat_msg,
                "scope": "global",
                "timestamp": datetime.utcnow().isoformat(),
            }

        elif msg_type == "emote":
            island_moniker = self.sessions.get_island_moniker(session_id)
            return {
                "type": "chat_message",
                "from_moniker": moniker,
                "message": chat_msg,
                "scope": "island" if island_moniker else "global",
                "moniker": island_moniker,
                "timestamp": datetime.utcnow().isoformat(),
            }

        return None


class ChannelServiceHandler(BaseService):
    """Handle channel subscription messages."""

    def __init__(self, args: Any, session_manager: SessionManager, channel_state: ChannelState, server: Any):
        super().__init__(args, session_manager)
        self.channel_state = channel_state
        self._server = server

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "subscribe_channel":
            return await self._handle_subscribe(id(websocket), message)
        elif msg_type == "unsubscribe_channel":
            return await self._handle_unsubscribe(id(websocket), message)
        elif msg_type == "get_subscriptions":
            return await self._handle_get_subscriptions(id(websocket))

        return None

    async def _handle_subscribe(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        channel = message.get("channel", "").strip()
        if not channel:
            return {"type": "error", "code": "invalid_request", "message": "channel required"}

        channel_subscribe(self.channel_state, session_id, channel)

        return {
            "type": "subscribed",
            "channel": channel,
            "message": f"Subscribed to {channel}",
        }

    async def _handle_unsubscribe(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        channel = message.get("channel", "").strip()
        if not channel:
            return {"type": "error", "code": "invalid_request", "message": "channel required"}

        channel_unsubscribe(self.channel_state, session_id, channel)

        return {
            "type": "unsubscribed",
            "channel": channel,
            "message": f"Unsubscribed from {channel}",
        }

    async def _handle_get_subscriptions(self, session_id: int) -> Dict[str, Any]:
        moniker = self.sessions.get_moniker(session_id)
        if not moniker:
            return {"type": "error", "code": "not_authenticated"}

        channels = channel_get_session_channels(self.channel_state, session_id)

        return {
            "type": "subscriptions",
            "channels": list(channels),
        }


class BankServiceHandler(BaseService):
    """Handle bank management messages."""

    def __init__(self, args: Any, session_manager: SessionManager):
        super().__init__(args, session_manager)
        from bbsengine6 import bank

        self.bank_service = bank.BankService(args)

    async def handle_message(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")

        if msg_type == "bank_balance":
            return await self._handle_balance(id(websocket), message)
        elif msg_type == "bank_add":
            return await self._handle_add(id(websocket), message)
        elif msg_type == "bank_remove":
            return await self._handle_remove(id(websocket), message)
        elif msg_type == "bank_history":
            return await self._handle_history(id(websocket), message)

        return None

    async def _handle_balance(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        session = self.sessions.get_session(session_id)
        if not session:
            return {"type": "error", "code": "not_authenticated"}

        moniker = message.get("moniker", session.get("moniker"))
        if not moniker:
            return {"type": "error", "code": "invalid_request", "message": "moniker required"}

        balance = self.bank_service.get_balance(moniker)

        return {
            "type": "bank_balance",
            "moniker": moniker,
            "balance": balance,
        }

    async def _handle_add(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        session = self.sessions.get_session(session_id)
        if not session:
            return {"type": "error", "code": "not_authenticated"}

        moniker = message.get("moniker")
        if not moniker:
            return {"type": "error", "code": "invalid_request", "message": "moniker required"}

        amount = message.get("amount", 0)
        description = message.get("description", "deposit")

        result = self.bank_service.add_funds(
            moniker,
            amount,
            transaction_type="deposit",
            description=description,
        )

        if result.get("success"):
            return {
                "type": "bank_added",
                "moniker": moniker,
                "amount": amount,
                "new_balance": result.get("new_balance"),
            }
        else:
            return {"type": "error", "code": "add_failed", "message": result.get("message", "")}

    async def _handle_remove(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        session = self.sessions.get_session(session_id)
        if not session:
            return {"type": "error", "code": "not_authenticated"}

        moniker = message.get("moniker")
        if not moniker:
            return {"type": "error", "code": "invalid_request", "message": "moniker required"}

        amount = message.get("amount", 0)
        description = message.get("description", "withdrawal")

        result = self.bank_service.remove_funds(
            moniker,
            amount,
            transaction_type="withdrawal",
            description=description,
        )

        if result.get("success"):
            return {
                "type": "bank_removed",
                "moniker": moniker,
                "amount": amount,
                "new_balance": result.get("new_balance"),
            }
        else:
            return {"type": "error", "code": "remove_failed", "message": result.get("message", "")}

    async def _handle_history(self, session_id: int, message: Dict[str, Any]) -> Dict[str, Any]:
        session = self.sessions.get_session(session_id)
        if not session:
            return {"type": "error", "code": "not_authenticated"}

        moniker = message.get("moniker")
        if not moniker:
            return {"type": "error", "code": "invalid_request", "message": "moniker required"}

        limit = message.get("limit", 50)
        history = self.bank_service.get_history(moniker, limit)

        return {
            "type": "bank_history",
            "moniker": moniker,
            "transactions": history,
        }


class MessageRouter:
    """
    Main message handler that coordinates all empyre services.
    Handles broadcasting and session lifecycle.
    """

    def __init__(self, args: Any) -> None:
        self.args = args
        self.sessions = SessionManager()
        self.channel_state = ChannelState()

        self.auth_service = AuthService(args, self.sessions, self.channel_state)
        self.member_service = MemberServiceHandler(args, self.sessions)
        self.island_service = IslandServiceHandler(args, self.sessions, self.channel_state)
        self.ship_service = ShipServiceHandler(args, self.sessions, self.channel_state)
        self.town_service = TownServiceHandler(args, self.sessions)
        self.market_service = MarketServiceHandler(args, self.sessions)
        self.chat_service = ChatServiceHandler(args, self.sessions)
        self.bank_service = BankServiceHandler(args, self.sessions)
        self.channel_service: Optional[ChannelServiceHandler] = None

    def register_all(self, server: Any) -> None:
        """Register all services with the WebSocketServer."""
        server.register_service(self.auth_service, ["auth", "ping"])
        server.register_service(self.member_service, [
            "member_profile", "member_tier", "member_referral_code", "member_referrals"
        ])
        server.register_service(self.island_service, [
            "list_islands", "join_island", "leave_island", "island_info", "list_colonies"
        ])
        server.register_service(self.ship_service, [
            "list_ships", "ship_info", "buy_ship", "sail_ship"
        ])
        server.register_service(self.town_service, [
            "list_towns", "town_info", "town_tax", "recruit_soldiers"
        ])
        server.register_service(self.market_service, [
            "market_prices", "buy_resource", "sell_resource"
        ])
        server.register_service(self.chat_service, ["chat_island", "chat_global", "emote"])
        server.register_service(self.bank_service, [
            "bank_balance", "bank_add", "bank_remove", "bank_history"
        ])

        self.channel_service = ChannelServiceHandler(
            self.args, self.sessions, self.channel_state, server
        )
        server.register_service(self.channel_service, [
            "subscribe_channel", "unsubscribe_channel", "get_subscriptions"
        ])

    async def handle_broadcast(
        self, server: Any, websocket: Any, path: str, message: Dict[str, Any]
    ) -> None:
        """Handle message that should be broadcast."""
        msg_type = message.get("type")

        if msg_type == "chat_message":
            scope = message.get("scope", "global")
            island_moniker = message.get("moniker")

            if scope == "island" and island_moniker:
                await server.publish(f"empyre:island:{island_moniker}", message)
            else:
                await server.publish("empyre:global", message)

    def unregister_session(self, session_id: int) -> None:
        """Clean up session on disconnect."""
        channel_unsubscribe_all(self.channel_state, session_id)
        self.sessions.unregister_session(session_id)
