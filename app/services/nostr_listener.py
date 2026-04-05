import asyncio
import logging
from typing import Optional
from nostr_sdk import Client, Keys, Filter, Kind, KindStandard, Event, NostrSigner, RelayUrl, HandleNotification

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NostrListener")

class NotificationHandler(HandleNotification):
    def __init__(self):
        super().__init__()

    async def handle(self, relay_url: RelayUrl, subscription_id: str, event: Event):
        """
        Maneja eventos entrantes. En 0.44.2, handle recibe: relay_url, subscription_id, event.
        """
        try:
            kind_val = event.kind().as_u16()
            if kind_val == 1:
                logger.info(f"--- NUEVA NOTA (Kind 1) ---")
                logger.info(f"Autor: {event.author().to_bech32()}")
                logger.info(f"Contenido: {event.content()}")
                logger.info(f"---------------------------")
        except Exception as e:
            logger.error(f"Error procesando evento: {e}")

    async def handle_msg(self, relay_url: RelayUrl, message):
        """
        Maneja mensajes de relay CRUD/Auth si fuera necesario.
        """
        pass

class NostrListener:
    def __init__(self, private_key_hex: Optional[str] = None):
        if private_key_hex:
            self.keys = Keys.parse(private_key_hex)
            logger.info("Keys cargadas.")
        else:
            self.keys = Keys.generate()
            logger.info(f"Nuevas Keys generadas: {self.keys.secret_key().to_bech32()}")
        
        signer = NostrSigner.keys(self.keys)
        self.client = Client(signer)
        
    async def connect_and_listen(self):
        await self.client.add_relay(RelayUrl.parse("wss://relay.damus.io"))
        await self.client.add_relay(RelayUrl.parse("wss://nos.lol"))
        
        logger.info("Conectando...")
        await self.client.connect()
        
        f = Filter().kind(Kind.from_std(KindStandard.TEXT_NOTE)).limit(0)
        await self.client.subscribe(f, None)
        logger.info("=> Escuchando Kind 1...")
        
        # En 0.44.2 pasamos la instancia del handler
        handler = NotificationHandler()
        try:
            await self.client.handle_notifications(handler)
        except asyncio.CancelledError:
            logger.info("Listener detenido.")
        except Exception as e:
            logger.error(f"Error en handle_notifications: {e}")

if __name__ == "__main__":
    async def main_test():
        listener = NostrListener()
        await listener.connect_and_listen()

    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        print("\nPrueba finalizada.")
