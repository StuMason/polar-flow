import asyncio
import os
from polar_flow.auth import OAuth2Handler

async def test():
    oauth = OAuth2Handler(
        client_id="32c36267-d144-47f5-92cd-bd32adea42b3",
        client_secret="ba98f5ca-235b-4d9d-aa7b-6cc5ca76de3e",
        redirect_uri="http://localhost:8888/callback"
    )
    
    # For testing, let me manually input a code after getting it
    print("Authorization URL:")
    print(oauth.get_authorization_url())
    print("\nPaste the authorization code here:")
    code = input().strip()
    
    try:
        token = await oauth.exchange_code(code)
        print(f"\nSuccess! Access token: {token.access_token}")
        print(f"User ID: {token.user_id}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
