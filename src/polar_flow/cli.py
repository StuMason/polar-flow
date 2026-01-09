"""CLI tool for Polar Flow API."""

import asyncio
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import typer
from rich.console import Console
from rich.panel import Panel

from polar_flow.auth import OAuth2Handler

app = typer.Typer(
    name="polar-flow",
    help="Modern async Python client for Polar AccessLink API",
    add_completion=False,
)
console = Console()


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    auth_code: str | None = None

    def do_GET(self) -> None:
        """Handle GET request with OAuth callback."""
        # Parse the query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params:
            CallbackHandler.auth_code = params["code"][0]

            # Send success response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            success_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login Successful</title>
                <style>
                    body {
                        font-family: monospace;
                        background: #1a1a1a;
                        color: #fff;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container { text-align: center; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Login Successful</h1>
                    <p>You can now close this window.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            error_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login Failed</title>
                <style>
                    body {
                        font-family: monospace;
                        background: #1a1a1a;
                        color: #fff;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container { text-align: center; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Login Failed</h1>
                    <p>Please try again from your terminal.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default logging."""
        pass


@app.command()
def auth(
    client_id: str = typer.Option(
        None,
        "--client-id",
        envvar="CLIENT_ID",
        help="Polar OAuth2 client ID (or set CLIENT_ID env var)",
    ),
    client_secret: str = typer.Option(
        None,
        "--client-secret",
        envvar="CLIENT_SECRET",
        help="Polar OAuth2 client secret (or set CLIENT_SECRET env var)",
    ),
    callback_url: str = typer.Option(
        "http://localhost:8888/callback",
        "--callback-url",
        help="OAuth callback URL (must match registered URL)",
    ),
    save: bool = typer.Option(
        True,
        "--save/--no-save",
        help="Save access token to ~/.polar-flow/token",
    ),
) -> None:
    """Authenticate with Polar Flow and get an access token.

    This command will:
    1. Start a local HTTP server for the OAuth callback
    2. Open your browser to the Polar authorization page
    3. Exchange the authorization code for an access token
    4. Optionally save the token for future use

    Examples:
        polar-flow auth --client-id YOUR_ID --client-secret YOUR_SECRET
        polar-flow auth  # Uses CLIENT_ID and CLIENT_SECRET from environment
    """
    # Validate credentials
    if not client_id:
        console.print("[red]Error: CLIENT_ID is required[/red]")
        console.print("Set it via --client-id flag or CLIENT_ID environment variable")
        raise typer.Exit(1)

    if not client_secret:
        console.print("[red]Error: CLIENT_SECRET is required[/red]")
        console.print("Set it via --client-secret flag or CLIENT_SECRET environment variable")
        raise typer.Exit(1)

    # Extract port from callback URL
    parsed = urlparse(callback_url)
    port = parsed.port or 8888

    console.print(
        Panel.fit(
            "[bold cyan]Polar Flow Authentication[/bold cyan]\n\n"
            f"Client ID: [green]{client_id[:8]}...[/green]\n"
            f"Callback URL: [green]{callback_url}[/green]",
            border_style="cyan",
        )
    )

    # Initialize OAuth handler
    oauth = OAuth2Handler(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=callback_url,
    )

    # Get authorization URL
    auth_url = oauth.get_authorization_url()

    console.print("\n[bold]Step 1:[/bold] Starting local callback server...")
    console.print(f"[dim]Listening on port {port}[/dim]")

    # Start local HTTP server for callback
    server = HTTPServer(("localhost", port), CallbackHandler)

    console.print("\n[bold]Step 2:[/bold] Opening browser for authorization...")
    console.print(f"[dim]{auth_url}[/dim]\n")

    # Open browser
    if not webbrowser.open(auth_url):
        console.print("[yellow]Could not open browser automatically.[/yellow]")
        console.print(f"Please open this URL manually:\n{auth_url}\n")

    console.print("[bold cyan]Waiting for authorization...[/bold cyan]")
    console.print("[dim]Complete the login in your browser[/dim]\n")

    # Wait for callback (handle single request)
    server.handle_request()

    if not CallbackHandler.auth_code:
        console.print("[red]Error: No authorization code received[/red]")
        raise typer.Exit(1)

    console.print("[green]✓[/green] Authorization code received!\n")

    console.print("[bold]Step 3:[/bold] Exchanging code for access token...")

    # Exchange code for token
    try:
        token = asyncio.run(oauth.exchange_code(CallbackHandler.auth_code))
    except Exception as e:
        console.print(f"[red]Error exchanging code: {e}[/red]")
        raise typer.Exit(1) from e

    console.print("[green]✓[/green] Access token obtained!\n")

    # Display token info
    console.print(
        Panel.fit(
            f"[bold green]Access Token:[/bold green]\n{token.access_token}\n\n"
            f"[bold]Token Type:[/bold] {token.token_type}\n"
            f"[bold]User ID:[/bold] {token.user_id}",
            title="[bold]Authentication Successful[/bold]",
            border_style="green",
        )
    )

    # Save token if requested
    if save:
        token_dir = Path.home() / ".polar-flow"
        token_dir.mkdir(exist_ok=True)
        token_file = token_dir / "token"

        token_file.write_text(token.access_token)
        console.print(f"\n[green]✓[/green] Token saved to [cyan]{token_file}[/cyan]")
        console.print("[dim]You can also set it as ACCESS_TOKEN environment variable[/dim]")
    else:
        console.print("\n[yellow]Token not saved (use --save to save)[/yellow]")

    console.print(
        "\n[bold green]You're all set![/bold green] Use this token to access the Polar API."
    )


@app.command()
def version() -> None:
    """Show version information."""
    from polar_flow import __version__

    console.print(f"polar-flow version [bold cyan]{__version__}[/bold cyan]")


if __name__ == "__main__":
    app()
