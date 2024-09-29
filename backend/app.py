from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Load dataset and process data
data = pd.read_csv('dataset.csv')

# Features to be used for recommendation
features = data[['duration_ms', 'danceability', 'speechiness', 'tempo', 'popularity', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness']]
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Create the model
model = NearestNeighbors(n_neighbors=10)
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
            if feature in song_a and feature in song_b:
                distance += weights[feature] * abs(song_a[feature] - song_b[feature])
        elif feature == 'track_genre':
            if song_a.get('track_genre') != song_b.get('track_genre'):
                distance += weights[feature] * 1
    return distance

def recommended_songs(song_index, model, data, features, weights, n_neighbors=15):
    distances, indices = model.kneighbors([scaled_features[song_index]], n_neighbors=n_neighbors)
    recommendations = []
    target_song_name = data.iloc[song_index]['track_name']

    seen_songs = set()
    i = 0

    while i < len(indices[0]) and len(recommendations) < 10:
        neighbor_index = indices[0][i]
        if neighbor_index != song_index:
            neighbor_song_name = data.iloc[neighbor_index]['track_name']
            if neighbor_song_name != target_song_name and neighbor_song_name not in seen_songs:
                neighbor_song = features.iloc[neighbor_index]
                distance = weighted_distance(features.iloc[song_index], neighbor_song, weights)
                recommendations.append((neighbor_index, distance))
                seen_songs.add(neighbor_song_name)
        i += 1

        if i >= len(indices[0]) and len(recommendations) < 10:
            n_neighbors += 5
            distances, indices = model.kneighbors([scaled_features[song_index]], n_neighbors=n_neighbors)
            i = 0

    recommendations.sort(key=lambda x: x[1])
    print(f'Song recommendations for: {data.iloc[song_index]["track_name"]}')
    for idx, dist in recommendations[:10]:
        print(f'Recommended: {data.iloc[idx]["track_name"]} | Artist: {data.iloc[idx]["artists"]}')
    return [idx for idx, _ in recommendations]

@app.route('/recommend', methods=['POST'])
def recommend_song():
    query = request.json.get('query', '')
    print(request.json)
    last_query = ""
    last_query = request.json.get('last_query', '')
    rec_index1 = request.json.get('rec_index', 0) or "0"
    rec_index = int(rec_index1)
    

    try:
        song_name, artist_name = query.split(", ")
        print(song_name, artist_name)
    except ValueError:
        return jsonify({"error": "Please provide input in the format: 'Song Name, Artist'"}), 400

    if last_query != query:
        session['last_query'] = query
        rec_index = 0

    print(data[:10])
    song_row = data[(data['track_name'] == song_name) & (data['artists'] == artist_name)]
    
    if song_row.empty:
        return jsonify({"error": "Song not found"}), 404

    song_index = int(song_row.index[0])
    recommendations = recommended_songs(song_index, model, data, features, weights)
    
    if rec_index >= len(recommendations):
        rec_index = 0

    next_song_index = recommendations[rec_index]
    rec_index += 1

    recommended_song = data.iloc[next_song_index]

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
        "rec_index": rec_index
    })

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
