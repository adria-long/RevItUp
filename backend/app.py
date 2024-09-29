from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
# from flask_session import Session

app = Flask(__name__)
CORS(app)

# Configure the session to use server-side storage (or you could use client-side cookies)


# Load dataset and process data
data = pd.read_csv('dataset.csv')

# Features to be used for recommendation
features = data[['duration_ms', 'danceability', 'speechiness', 'tempo', 'popularity', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness']]
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Create the model
model = NearestNeighbors(n_neighbors=10)  # Get 10 recommendations to allow for multiple presses
model.fit(scaled_features)

weights = {
    'duration_ms': 0.3,
    'danceability': 0.5,
    'speechiness': 0.25,
    'tempo': 0.5,
    'popularity': 0.05,
    'energy': 0.15,
    'loudness': 0.15,
    'acousticness': 0.15,
    'instrumentalness': 0.3,
    'track_genre': 1
}

def weighted_distance(song_a, song_b, weights):
    distance = 0
    for feature in weights.keys():
        if feature in ['duration_ms', 'danceability', 'speechiness', 'tempo', 'popularity', 'energy', 'loudness', 'acousticness', 'instrumentalness']:
            # Ensure both songs have the feature
            if feature in song_a and feature in song_b:
                distance += weights[feature] * abs(song_a[feature] - song_b[feature])
        elif feature == 'track_genre':
            # Compare genres and increase distance if they don't match
            if song_a.get('track_genre') != song_b.get('track_genre'):
                distance += weights[feature] * 1  # Fixed 1 point penalty for genre mismatch
    return distance

# Helper function to calculate recommendations
#defining the function that recomends the songs
def recommended_songs(song_index, model, data, features, weights, n_neighbors=15):
    # Increase the number of neighbors to search for if needed (set initial to 15 for safety)
    distances, indices = model.kneighbors([scaled_features[song_index]], n_neighbors=n_neighbors)
    recommendations = []
    target_song_name = data.iloc[song_index]['track_name']

    seen_songs = set()  # Set to track already recommended songs
    i = 0  # Counter for neighbors

    # Continue until you have 10 unique recommendations
    while i < len(indices[0]) and len(recommendations) < 10:
        neighbor_index = indices[0][i]

        # Check if the neighbor song is not the same as the target song
        if neighbor_index != song_index:
            neighbor_song_name = data.iloc[neighbor_index]['track_name']
            if neighbor_song_name != target_song_name and neighbor_song_name not in seen_songs:  # Ensure uniqueness
                neighbor_song = features.iloc[neighbor_index]
                distance = weighted_distance(features.iloc[song_index], neighbor_song, weights)
                recommendations.append((neighbor_index, distance))
                seen_songs.add(neighbor_song_name)  # Add to seen songs

        i += 1  # Increment the counter

        # If we run out of neighbors to look at, increase n_neighbors and try again
        if i >= len(indices[0]) and len(recommendations) < 10:
            n_neighbors += 5  # Increase the number of neighbors
            distances, indices = model.kneighbors([scaled_features[song_index]], n_neighbors=n_neighbors)
            i = 0  # Reset counter to go through the new neighbors

        # Sort the recommendations by distance
    recommendations.sort(key=lambda x: x[1])
    print('Song recommendations for:', data.iloc[song_index]['track_name'], 'Genre:', data.iloc[song_index]['track_genre'])
    for idx, dist in recommendations[:10]:
        print('Rev recommends:', data.iloc[idx]['track_name'], '|Artist:', data.iloc[idx]['artists'],'|Genre:', data.iloc[idx]['track_genre'], '|Track_ID:', idx)
    return [idx for idx, num in recommendations]

@app.route('/recommend', methods=['POST'])
def recommend_song():
    print(request.json)
    print(request.data)
    query = request.json.get('query')
    last_query = request.json.get('last_query')
    rec_index = int(request.json.get('rec_index'))
    print(f"Received query: {query}")
    
    try:
        song_name, artist_name = query.split(", ")
    except ValueError:
        return jsonify({"error": "Please provide input in the format: 'Song Name, Artist'"}), 400

    
    # Check if we're dealing with the same song (session management)
    if last_query != query:
        # New search, reset the session
        print("hello - step1")
        print(session)
        session['last_query'] = query
        rec_index = 0  # Start with the first recommendation
    
    # Search for the song in the dataset
    
    song_row = data[(data['track_name'] == song_name) & (data['artists'] == artist_name)]
    
    if song_row.empty:
        return jsonify({"error": "Song not found"}), 404

    print(song_row)
    song_index = song_row.index[0]
    print(song_index)

    # Get all recommendations for this song
    recommendations = recommended_songs(song_index, model, data, features, weights)
    print(recommendations)
    
    # Get the next recommendation based on the current recommendation index
    # rec_index = session['recommendation_index']
    
    print("recindex", rec_index)

    # If the user has already seen all recommendations, loop back to the first one
    if rec_index >= len(recommendations):
        rec_index = 0
        rec_index = 0
    
    next_song_index = recommendations[rec_index]
    print("nextsongindex", next_song_index)
    rec_index += 1  # Move to the next recommendation for the next click

    # Get the details of the recommended song
    recommended_song = data.iloc[next_song_index]
    print(recommended_song)

    return jsonify({
        "track_id": str(recommended_song['track_id']),
        "track_name": str(recommended_song['track_name']),
        "artist": str(recommended_song['artists']),
        "duration_ms": str(recommended_song['duration_ms']),
        "explicit": str(recommended_song['explicit']),
        "danceability": str(recommended_song['danceability']),
        "speechiness": str(recommended_song['speechiness']),
        "tempo": str(recommended_song['tempo']),
        "track_genre": str(recommended_song['track_genre']),
        "popularity": str(recommended_song['popularity']),
        "energy": str(recommended_song['energy']),
        "loudness": str(recommended_song['loudness']),
        "acousticness": str(recommended_song['acousticness']),
        "instrumentalness": str(recommended_song['instrumentalness']),
        "liveness": str(recommended_song['liveness']),
        "rec_index": str(rec_index)
    })

if __name__ == '__main__':
    app.secret_key = 'super secret key'

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
