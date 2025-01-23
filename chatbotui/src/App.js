import React, { useState } from 'react';
import './App.css';

// Placeholder for the chatbot component
import ChatBot from './components/ChatBot'; // Assume you have a ChatBot component

function App() {
  const [address, setAddress] = useState('');
  const [image, setImage] = useState(null);
  const [instagramImage , setInstagramImage] = useState(null);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [imagepath, setImagepath] = useState('')
  const baseUrl = 'https://08cc-2600-3c03-00-f03c-91ff-fe6d-9676.ngrok-free.app'
  const handleAddressInput = (e) => {
    setAddress(e.target.value);
  };

  const fetchImageFromZillow = async () => {
    try {
      const response = await fetch(`${baseUrl}/scrape-image?address=${encodeURIComponent(address)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      console.log(data)
      if (response.ok) {
        setImage(`${data.image_url}`);
        setImagepath(`.${data.downloadable_url}`)
        setInstagramImage(`http://45.79.156.12:8000${data.downloadable_url}`)  
      } else {
        alert(data.message);  
      }
    } catch (error) {
      console.error('Error fetching image:', error);
      alert('Failed to fetch image. Please try again.');
    }
  };

  const handlePostToInstagram = async () => {
    const imagePath = imagepath; 
    const caption = address; 

    try {
      const response = await fetch(`${baseUrl}/upload-image`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image_path: imagePath, caption: caption }),
      });

      if (!response.ok) {
        throw new Error("Failed to upload image");
      }

      const data = await response.json();
      alert("Successfully posted to Instagram.");
      console.log(data.message); // Handle success message
    } catch (error) {
      alert("Error: " + error.message);
      console.error("Error:", error);
    }
  };

  return (
    <div className="App">
      <header className="App-header flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <input 
          type="text" 
          value={address} 
          onChange={handleAddressInput} 
          placeholder="Enter home address" 
          className="p-2 border border-gray-300 rounded mb-4 w-[400px]"
        />
        <button 
          onClick={fetchImageFromZillow} 
          className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          Generate Image
        </button>
        {image && <img src={image} alt="Generated" className="mt-4 max-w-xs rounded shadow-lg w-[300px]" />}
        <ChatBot 
          image={instagramImage} 
          onConfirm={handlePostToInstagram} 
          onCancel={() => setIsConfirmed(false)} 
        />
      </header>
    </div>
  );
}

export default App;