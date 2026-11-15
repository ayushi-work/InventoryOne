"""WebSocket consumers for live plot availability."""
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class InventoryConsumer(AsyncWebsocketConsumer):
    """Broadcasts plot status changes to every subscribed dashboard.

    Clients join the shared ``inventory`` group. The API layer calls
    :func:`broadcast_inventory` whenever a plot status changes.
    """

    group_name = 'inventory'

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({'type': 'connected'}))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Allow clients to request a refresh."""
        try:
            payload = json.loads(text_data or '{}')
        except (TypeError, ValueError):
            return
        if payload.get('type') == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))

    async def inventory_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'inventory',
            'project_id': event.get('project_id'),
            'plot_id': event.get('plot_id'),
            'status': event.get('status'),
            'counts': event.get('counts', {}),
        }))


async def broadcast_inventory(project_id=None, plot_id=None, status=None, counts=None):
    """Send an inventory update to all connected dashboards."""
    try:
        from channels.layers import get_channel_layer

        layer = get_channel_layer()
        if layer is None:
            return False
        await layer.group_send(
            InventoryConsumer.group_name,
            {
                'type': 'inventory_update',
                'project_id': project_id,
                'plot_id': plot_id,
                'status': status,
                'counts': counts or {},
            },
        )
        return True
    except Exception:  # pragma: no cover - transport is best effort
        return False


def broadcast_inventory_sync(project_id=None, plot_id=None, status=None, counts=None):
    """Synchronous helper usable from Django views."""
    import asyncio

    try:
        asyncio.run(broadcast_inventory(project_id, plot_id, status, counts))
        return True
    except RuntimeError:
        # Already inside an event loop (e.g. under ASGI) - schedule it.
        try:
            from asgiref.sync import async_to_sync

            async_to_sync(broadcast_inventory)(project_id, plot_id, status, counts)
            return True
        except Exception:
            return False
    except Exception:
        return False
