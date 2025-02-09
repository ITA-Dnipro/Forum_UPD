import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Import axios for API requests
import './ChatWidget.css'; // Make sure to import the CSS

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! How can I help you?' },
  ]);
  const [input, setInput] = useState('');
  const [socket, setSocket] = useState(null);

  // Open WebSocket connection when the component mounts
  useEffect(() => {
    // Replace the WebSocket URL with your backend WebSocket endpoint
    const ws = new WebSocket('wss://your-websocket-url.com/ws/chat/');

    ws.onopen = () => {
      console.log('WebSocket connection opened');
    };

    ws.onmessage = (event) => {
      const botResponse = JSON.parse(event.data).message; // Adjust based on your WebSocket response
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'bot', text: botResponse },
      ]);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    setSocket(ws);

    return () => {
      if (ws) ws.close(); // Clean up WebSocket connection when the component unmounts
    };
  }, []);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add the user's message to the chat
    setMessages([...messages, { sender: 'user', text: input }]);

    // Clear the input field
    setInput('');

    try {
      // If you're also sending to the backend (e.g., for logging or additional processing)
      await axios.post(
        `${process.env.REACT_APP_BASE_API_URL}/api/chats/create/`,
        {
          message: input,
        },
      );

      // Send the message through WebSocket
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ message: input }));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'bot', text: 'Sorry, there was an error. Please try again.' },
      ]);
    }
  };

  return (
    <div className="chat-widget-container">
      {/* Chat Toggle Button */}
      <button onClick={toggleChat} className="chat-toggle-button">
        💬 Chat
      </button>

      {/* Chat Box */}
      {isOpen && (
        <div className="chat-box">
          <div className="chat-header">Chat</div>
          <div className="messages-container">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`message ${
                  msg.sender === 'user' ? 'user-message' : 'bot-message'
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <div className="input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="input-field"
              placeholder="Type a message..."
            />
            <button onClick={sendMessage} className="send-button">
              ➤
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
