import React from 'react';
import './App.css'; // Link to the CSS file for styles

function App() {
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
        <input type="text" placeholder="Enter Artist, Song Name, or Genre..." />
        <button className="new-song-button">
          <i className="fa-solid fa-forward"> New Song</i>
        </button>
      </div>

      {/* Grid for track details */}
      <div className="grid-container">
        <div className="grid-item">Track ID</div>
        <div className="grid-item">Artist</div>
        <div className="grid-item">Song Name</div>
        <div className="grid-item">Duration</div>
        <div className="grid-item">Explicit</div>
        <div className="grid-item">Danceability</div>
        <div className="grid-item">Speechiness</div>
        <div className="grid-item">Tempo</div>
        <div className="grid-item">Genre</div>
        <div className="grid-item">Popularity</div>
      </div>
    </div>
  );
}

export default App;
