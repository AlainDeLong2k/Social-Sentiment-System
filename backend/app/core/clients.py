from qstash import QStash, Receiver
from app.core.config import settings

# Initialize the QStash client for publishing messages
# qstash_client = QStash(token=settings.QSTASH_TOKEN, base_url=settings.QSTASH_URL)
qstash_client = QStash(token=settings.QSTASH_TOKEN)

# Initialize the QStash receiver for verifying incoming messages
qstash_receiver = Receiver(
    current_signing_key=settings.QSTASH_CURRENT_SIGNING_KEY,
    next_signing_key=settings.QSTASH_NEXT_SIGNING_KEY,
)
