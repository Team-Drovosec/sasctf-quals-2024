
import socket

import src.connections as connections
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


hostname = socket.gethostname()

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> str:
    now = connections.get_connections()
    max = connections.MAX_CONNS

    return f'''
# HELP ppc_drovosec_connections_now Number of drovosex connections now
# TYPE ppc_drovosec_connections_now gauge
ppc_drovosec_connections_now{{host="{hostname}"}} {now}
# HELP ppc_drovosec_connections_max Max set in settings for connections
# TYPE ppc_drovosec_connections_max gauge
ppc_drovosec_connections_max{{host="{hostname}"}} {max}
    '''.strip()




