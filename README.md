# Tesla

This repository contains a small demonstration web application that shows
how to authenticate with Tesla's OAuth service and access the Owner API.

## OAuth Login

1. Set the required environment variables before running the server:
   - `TESLA_CLIENT_ID` – the OAuth client ID (typically `ownerapi`).
   - `TESLA_CLIENT_SECRET` – your Tesla OAuth client secret.
   - `TESLA_REDIRECT_URI` – URL that Tesla should redirect to after login.

2. Start the web application:
   ```bash
   pip install -r requirements.txt
   python tesla_web.py
   ```

3. Open `http://localhost:5000/login` in your browser. After successful
   login you will be redirected back to `/callback` which exchanges the
   provided `code` for an access and refresh token. The tokens are stored
   in the Flask session.

4. Visit `/location` to display the current position of your first
   registered vehicle on a small map.

5. Use `/logout` to clear the current session.

The example fetches the vehicle location via the Owner API and displays
it with Leaflet. You can extend the code to call additional endpoints as
needed.
