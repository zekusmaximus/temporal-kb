# kb/cli/commands/serve.py

import click
import uvicorn

from ...core.config import get_config
from ..ui import console, print_info


@click.command()
@click.option('--host', default=None, help='Host address')
@click.option('--port', type=int, default=None, help='Port number')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host, port, reload):
    """Start the API server

    Examples:
        kb serve
        kb serve --port 8080
        kb serve --reload
    """

    config = get_config()

    host = host or config.api_host
    port = port or config.api_port

    print_info(f"Starting API server at http://{host}:{port}")
    print_info(f"API docs available at http://{host}:{port}/docs")
    console.print()

    uvicorn.run(
        "kb.api.main:app",
        host=host,
        port=port,
        reload=reload
    )

