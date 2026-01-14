import uuid
import fakeredis 

r = fakeredis.FakeStrictRedis()

class Vault:
    def __init__(self, ttl_seconds=600):
        self.ttl = ttl_seconds

    def store(self, token: str, real_value: str):
        r.setex(token, self.ttl, real_value)

    def retrieve(self, token: str):
        val = r.get(token)
        return val.decode('utf-8') if val else None

def generate_token(entity_type):
    return f"<{entity_type}_{uuid.uuid4().hex[:6]}>"