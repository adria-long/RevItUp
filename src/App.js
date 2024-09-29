import React, { useState } from 'react';
import './App.css'; // Link to the CSS file for styles


function App() {
  const [query, setQuery] = useState('');
  const [recommendation, setRecommendation] = useState(null);

  // Function to fetch recommendations from the Flask backend
  const fetchRecommendation = async () => {
    try {
      const response = await fetch('http://localhost:5000/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "query": query, "last_query": localStorage.getItem("last_query"), "rec_index": localStorage.getItem("recommendation_index") || 0 }),
      });
      

      const data = await response.json();
      localStorage.setItem("last_query", query)
      localStorage.setItem("recommendation_index", data.rec_index)
      if (data.error) {
        alert(data.error);
      } else {
        setRecommendation(data);
      }
    } catch (error) {
      console.error('Error fetching recommendation:', error);
      alert('Failed to fetch recommendation');
    }
  };

  return (
    <div className="container">
      {/* Header section with images and title */}
      <div className="header">
        <img src="/RevItUp.png" alt="logo" className="logo" />
        <h1>Rev It Up</h1>
        <img src="/RevItUp.png" alt="logo" className="logo" />
      </div>

      {/* Search bar */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Enter Song Name, Artist..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="new-song-button" onClick={fetchRecommendation}>
          <i className="fa-solid fa-forward"> New Song</i>
        </button>
      </div>

      {/* Grid to display the recommendation details */}
      {recommendation && (
        <div className="grid-container">
          <div className="grid-item grid-item-top long-track " >Track ID:<br></br> {recommendation.track_id}</div>
          <div className="grid-item grid-item-top long-track">Artist:<br></br> {recommendation.artist}</div>
          <div className="grid-item grid-item-top">Song Name:<br></br> {recommendation.track_name}</div>
          <div className="grid-item grid-item-top">Duration:<br></br> {Math.floor(recommendation.duration_ms / 1000 / 60)} : {Math.floor(recommendation.duration_ms / 1000 % 60)} </div>
          <div className="grid-item grid-item-top">Explicit:<br></br> {recommendation.explicit ? 'Yes' : 'No'}</div>
          <div className="grid-item">Danceability:<br></br> {recommendation.danceability}</div>
          <div className="grid-item">Speechiness:<br></br> {recommendation.speechiness}</div>
          <div className="grid-item">Tempo:<br></br> {recommendation.tempo}</div>
          <div className="grid-item">Genre:<br></br> {recommendation.track_genre}</div>
          <div className="grid-item">Popularity:<br></br> {recommendation.popularity}</div>
        </div>
      )}
    </div>
  );
}

export default App;
