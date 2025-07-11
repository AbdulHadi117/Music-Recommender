# import necessary libraries
from flask import Flask, redirect, request, session, url_for, render_template, jsonify
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import logging

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_COOKIE_NAME"] = "Spotify Music Recommender"

# Retrieve Spotify API credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Initialize Spotify OAuth client
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=(
        "user-read-email user-read-private user-library-modify "
        "user-library-read user-read-recently-played user-top-read "
        "playlist-read-private playlist-modify-private playlist-modify-public"
    ),
)

# Configure Logging
logging.basicConfig(level=logging.INFO)

def get_spotify_auth_token():
    """
    Retrieves the Spotify authentication token from the session.
    If the token is expired, attempts to refresh it.
    Returns:
        dict: The Spotify authentication token info
    """
    # Retrieve the token info from the session
    token_info = session.get("token_info")
    if not token_info:
        return None

    # Check if the token has expired
    if sp_oauth.is_token_expired(token_info):
        try:
            # Attempt to refresh the token
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
            # Store the refreshed token in the session
            session["token_info"] = token_info
        except Exception as e:
            # Log the error if the token cannot be refreshed
            logging.error(f"Error refreshing token: {e}")
            return None

    return token_info

def get_spotify_client():
    """
    Retrieves the Spotify client using the stored token info.

    If the token info is not available, or if the token is expired,
    attempts to refresh the token and store it in the session.

    Returns:
        spotipy.Spotify: The Spotify client
    """
    token_info = get_spotify_auth_token()
    if not token_info:
        return None

    # Create the Spotify client with the access token
    return spotipy.Spotify(auth=token_info["access_token"])

def validate_uris(uris):
    """
    Validates a list of Spotify track URIs.

    Uses the Spotify client to attempt to retrieve the track data for each URI.
    If the track data can be retrieved, the URI is considered valid and added
    to the list of valid URIs.

    Args:
        uris (list): A list of Spotify track URIs to validate

    Returns:
        list: A list of valid Spotify track URIs
    """
    sp = get_spotify_client()
    if not sp:
        return []
    valid_uris = []
    for uri in uris:
        try:
            # Attempt to retrieve the track data
            sp.track(uri)
            # If the track data can be retrieved, the URI is valid
            valid_uris.append(uri)
        except spotipy.exceptions.SpotifyException:
            # Log a warning if the URI is invalid
            logging.warning(f"Invalid URI: {uri}")
    return valid_uris

def fetch_profile_data(sp):
    """
    Fetches the current user's profile data, including the number of playlists,
    top tracks, top artists, and top genres.

    Args:
        sp (spotipy.Spotify): The Spotify client

    Returns:
        tuple: A tuple containing profile data, number of playlists, top genres,
               top artists, and top tracks
    """
    # Get the user's profile data
    profile_data = sp.current_user()

    # Get the total number of playlists
    num_playlists = sp.current_user_playlists()["total"]

    # Get the user's top tracks, limited to 5
    top_tracks = sp.current_user_top_tracks(limit=5)

    # Get the user's top artists, limited to 5
    top_artists = sp.current_user_top_artists(limit=5)

    top_genres = []
    # Collect genres from top artists
    for artist in top_artists["items"]:
        top_genres.extend(artist["genres"])

    # Deduplicate and limit the top genres to 3
    top_genres = list(set(top_genres[:3]))
    # Capitalize each genre
    top_genres = [genre.title() for genre in top_genres]

    return profile_data, num_playlists, top_genres, top_artists, top_tracks

def fetch_recommendations(sp):
    """
    Fetches the current user's top tracks and uses them as seed tracks to get
    music recommendations.

    Args:
        sp (spotipy.Spotify): The Spotify client

    Returns:
        dict: A dictionary containing the recommendations
    """
    # Get the user's top tracks, limited to 5
    top_tracks = sp.current_user_top_tracks(limit=5)
    # Get the track IDs from the top tracks
    seed_tracks = [track["id"] for track in top_tracks["items"]]
    # If there are no tracks, return an empty list
    if not seed_tracks:
        return {"tracks": []}
    # Limit the seed tracks to 5
    seed_tracks = seed_tracks[:5]
    # Get the recommendations
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=10)
    return recommendations


@app.route("/")
def home():
    """
    Renders the home page.

    Returns:
        A rendered template for the home page.
    """
    # Render the home page template
    return render_template("home.html")

@app.route("/logout")
def logout():
    """
    Logs out the user by clearing the session.

    Returns:
        A redirect to the home page.
    """
    # Clear the session
    session.clear()
    # Redirect to the home page
    return redirect(url_for("home"))

@app.route("/login")
def login():
    """
    Redirects the user to the Spotify authorization URL.

    Redirects the user to the Spotify authorization URL to log in and
    authorize the application to access their data.

    Returns:
        A redirect to the Spotify authorization URL.
    """
    # Get the authorization URL
    auth_url = sp_oauth.get_authorize_url()
    # Redirect the user to the authorization URL
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """
    Handles the authorization callback from Spotify.

    The authorization code is retrieved from the query string, and the access
    token is fetched using the Spotify client. The access token is stored in the
    session for later use.

    Returns:
        A redirect to the profile page.
    """
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400

    try:
        # Get the access token using the authorization code
        token_info = sp_oauth.get_access_token(code)
        # Store the access token in the session
        session["token_info"] = token_info
    except Exception as e:
        # Log any errors that occur
        logging.error(f"Error getting access token: {e}")
        return jsonify({"error": str(e)}), 400

    # Redirect to the profile page
    return redirect(url_for("profile"))

@app.route("/profile")
def profile():
    """
    Renders the user profile page.

    The user profile page is rendered with data fetched from the Spotify API,
    including the user's profile data, the number of playlists, top genres,
    top artists, and top tracks.

    If the access token is invalid or missing, the user is redirected to the
    login page.

    Returns:
        A rendered template for the profile page.
    """
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))

    try:
        # Fetch the user profile data, number of playlists, top genres,
        # top artists, and top tracks from the Spotify API
        profile_data, num_playlists, top_genres, top_artists, top_tracks = fetch_profile_data(sp)
    except spotipy.exceptions.SpotifyException as e:
        logging.error(f"Spotify API error: {e}")
        return jsonify({"error": "Spotify API error: " + str(e)}), 400

    return render_template(
        "profile.html",
        profile=profile_data,
        num_playlists=num_playlists,
        top_genres=top_genres,
        top_artists=top_artists,
        top_tracks=top_tracks,
    )


@app.route("/recommendations")
def recommendations():
    """
    Renders the recommendations page.

    The recommendations page is rendered with music recommendations fetched
    from the Spotify API.

    If the access token is invalid or missing, the user is redirected to the
    login page.

    Returns:
        A rendered template for the recommendations page.
    """
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))

    try:
        # Fetch the recommendations from the Spotify API
        recommendations = fetch_recommendations(sp)
    except Exception as e:
        logging.error(f"Error fetching recommendations: {e}")
        # If an error occurs, render the page with an empty list of tracks
        recommendations = {"tracks": []}

    return render_template("recommendations.html", recommendations=recommendations)

@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    """
    Handles the creation of a new playlist using the Spotify API.

    Retrieves playlist name and track URIs from the form data. Validates the
    input and creates a new playlist for the current user, adding the selected
    tracks to it.

    Returns:
        A redirect to the playlist success page if successful, or a JSON error
        response in case of failure.
    """
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for("login"))

    # Retrieve form data
    playlist_name = request.form.get("playlist_name")
    track_uris = request.form.getlist("track_uris")

    # Validate input
    if not playlist_name:
        return jsonify({"error": "Please provide a playlist name."}), 400
    if not track_uris:
        return jsonify({"error": "Please select at least one track to add to the playlist."}), 400

    # Validate and filter track URIs
    track_uris = validate_uris(track_uris)

    try:
        # Get the current user's ID
        user_id = sp.current_user()["id"]
        # Create a new playlist for the user
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
        # Add tracks to the newly created playlist
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
        # Redirect to the success page
        return redirect(url_for("playlist_success", playlist_name=playlist_name))
    except spotipy.exceptions.SpotifyException as e:
        # Log Spotify API errors
        logging.error(f"Spotify API error: {e}")
        return jsonify({"error": "Failed to create playlist due to an API error."}), 500
    except Exception as e:
        # Log general errors
        logging.error(f"Error creating playlist: {e}")
        return jsonify({"error": "Failed to create playlist."}), 500

@app.route("/playlist_success")
def playlist_success():
    """
    Renders the playlist success page.

    The playlist success page is rendered after a playlist is successfully
    created. The page displays a success message with the name of the
    playlist.

    Args:
        playlist_name (str): The name of the playlist.

    Returns:
        A rendered template for the playlist success page.
    """
    playlist_name = request.args.get("playlist_name", "Your playlist")
    return render_template("playlist_success.html", playlist_name=playlist_name)

if __name__ == "__main__":
    app.run(debug=True, port=8888)