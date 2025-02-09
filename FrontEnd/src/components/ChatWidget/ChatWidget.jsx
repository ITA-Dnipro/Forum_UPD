import React, { useState } from 'react';
import useWebSocket from 'react-use-websocket';
import './ChatWidget.css'; // Make sure you have the CSS file for styling

const ChatWidget = () => {
  const socketUrl = 'ws://localhost:8000/ws/chat/';
  const [messages, setMessages] = useState([]);
  const [isOpen, setIsOpen] = useState(false); // Track if chat is open or closed
  const [input, setInput] = useState(''); // Store the user input message

  const { sendMessage } = useWebSocket(socketUrl, {
    onOpen: () => console.log('WebSocket opened'),
    shouldReconnect: () => false, // Disable reconnection
    onMessage: (message) => {
      setMessages((prevMessages) => [...prevMessages, message.data]); // Add new message to the list
    },
  });

  const handleSendMessage = () => {
    if (input.trim()) {
      sendMessage(JSON.stringify({ message: input }));
      setMessages((prevMessages) => [...prevMessages, input]); // Add the message to the local list of messages
      setInput(''); // Clear the input after sending
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div>
      {/* Floating chat icon */}
      <button className="chat-icon" onClick={toggleChat}>
        💬
      </button>

      {isOpen && (
        <div className="chat-box">
          <div className="chat-header">
            <h1>WebSocket Chat</h1>
            <button className="close-chat" onClick={toggleChat}>
              ×
            </button>
          </div>

          {/* Message input form */}
          <div className="input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)} // Update the input state on change
              className="input-field"
              placeholder="Type a message..."
            />
            <button onClick={handleSendMessage} className="send-button">
              ➤
            </button>
          </div>

          {/* Messages display */}
          <div className="message-container">
            {messages.length === 0 ? (
              <p>No messages received yet.</p>
            ) : (
              <ul className="messages-list">
                {messages.map((message, index) => (
                  <li key={index} className="message-item">
                    {message}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
