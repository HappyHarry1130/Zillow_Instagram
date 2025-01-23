import React from 'react';

const ChatBot = ({ image, onConfirm, onCancel }) => {
    return (
      <div className="chatbot p-6 bg-white rounded-lg shadow-md mt-[60px]">
        {image ? (
          <div className="flex flex-col items-center">
            <p className="text-lg mb-2">Your generated image is ready!</p>
            <img 
              src={image} 
              alt="Generated for Instagram" 
              className="object-cover rounded-lg mb-4 w-[300px]" 
            />
            <p className="text-md mb-4">Do you want to post this image to Instagram?</p>
            <div className="flex space-x-4">
              <button 
                onClick={onConfirm} 
                className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition"
              >
                Yes, post it!
              </button>
              <button 
                onClick={onCancel} 
                className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition"
              >
                No, cancel
              </button>
            </div>
          </div>
        ) : (
          <p className="text-lg">No image generated yet.</p>
        )}
      </div>
    );
  };


export default ChatBot;