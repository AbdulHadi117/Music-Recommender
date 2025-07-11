# Spotify Music Recommender

A web application that integrates with the Spotify API to provide music recommendations and playlist creation functionality.

## Features

- **Authentication:** Authenticates users using OAuth 2.0 and authorizes access to their Spotify data.
- **User Profile:** Retrieves user profile data, including top tracks, artists, and genres.
- **Music Recommendations:** Provides music recommendations based on user's top tracks.
- **Playlist Creation:** Allows users to create new playlists with specified names and tracks.
- **Token Management:** Handles token refresh and session management to maintain user authentication.
- **Error Handling:** Includes error handling for API calls and user input validation.

## Setup

1. **Create a Spotify Developer Account:**
   - Register an application to obtain a Client ID and Client Secret.

2. **Set Environment Variables:**
   - Create a `.env` file in the project root directory with the following content:
  
     ```.env
     CLIENT_ID=<your_spotify_client_id>
     CLIENT_SECRET=<your_spotify_client_secret>
     REDIRECT_URI=<your_redirect_uri>
     FLASK_SECRET_KEY=<your_flask_secret_key>
     ```

3. **Install Required Packages:**
   - Run the following command to install the necessary Python packages:

     ```bash
     pip install -r requirements.txt
     ```

4. **Run the Application:**
   - Start the Flask web server with:

     ```bash
     python app.py
     ```

## Usage

1. **Visit the Home Page:**
   - Open your web browser and navigate to [http://localhost:8888/](http://localhost:8888/).

2. **Login:**
   - Click the "Login" button to authenticate with Spotify. You will be redirected to Spotify's login page to grant access to your data.

3. **Grant Access:**
   - Authorize the application to access your Spotify data.

4. **View Profile Data:**
   - Once authenticated, you will be redirected to your profile page where you can view your top tracks, artists, and genres.

5. **Explore Recommendations:**
   - Access the recommendations page to explore music suggestions based on your top tracks.

6. **Create Playlists:**
   - Use the form on the playlist creation page to specify a playlist name and select tracks to add. Your new playlist will be created and populated with the selected tracks.

## Technical Details

- **Framework:** Built using Flask, a micro web framework for Python.
- **Spotify Integration:** Utilizes the `spotipy` library to interact with the Spotify API.
- **OAuth 2.0:** Implements OAuth 2.0 authentication and authorization using the `SpotifyOAuth` class.
- **Session Management:** Stores access tokens in user sessions using Flask's session management. Handles token refresh to maintain active sessions.
- **Error Handling:** Includes error handling for Spotify API calls and user input validation. Logs errors and provides informative messages for failed operations.
- **Logging:** Uses Python's `logging` module to log errors and warnings for debugging and maintenance.

## Endpoints

- **`/`**: Home page.
- **`/login`**: Initiates the OAuth 2.0 authorization flow with Spotify.
- **`/callback`**: Handles the callback from Spotify after authentication.
- **`/profile`**: Displays user profile data including top tracks, artists, and genres.
- **`/recommendations`**: Shows music recommendations based on user's top tracks.
- **`/create_playlist`**: Handles POST requests to create new playlists with specified tracks.
- **`/playlist_success`**: Displays a success message after creating a playlist.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please submit pull requests or open issues to report bugs or suggest new features.

## Acknowledgments

This project was inspired by the Spotify API and the `spotipy` library. Special thanks to the Flask and Spotipy communities for their support and resources.
