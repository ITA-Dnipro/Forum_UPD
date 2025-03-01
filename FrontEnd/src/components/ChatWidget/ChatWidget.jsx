import React, { useState } from 'react';
import useWebSocket from 'react-use-websocket';
import './ChatWidget.css';

const ChatWidget = () => {
  const socketUrl = 'ws://localhost:8001/ws/chat/asd/';
  const [messages, setMessages] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');

  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl, {
    onOpen: () => console.log('WebSocket connected'),
    onClose: () => console.log('WebSocket disconnected'),
    onError: (error) => console.error('WebSocket error:', error),

    shouldReconnect: (closeEvent) => {
      console.log('Attempting to reconnect...', closeEvent.reason);
      return true; // Always attempt to reconnect
    },

    reconnectAttempts: 10, // Try reconnecting up to 10 times
    reconnectInterval: 3000, // Wait 3 seconds between attempts

    onMessage: (message) => {
      // Check the type of message
      let msg = message.data;

      // If it's an object, stringify it
      if (typeof msg !== 'string') {
        try {
          msg = JSON.stringify(msg);
        } catch (e) {
          msg = 'Error parsing message';
        }
      }

      // Add the message to the state
      setMessages((prevMessages) => [...prevMessages, msg]);
    },
  });

  const handleSendMessage = () => {
    if (input.trim()) {
      sendMessage(JSON.stringify({ message: input }));
      setMessages((prevMessages) => [...prevMessages, `You: ${input}`]);
      setInput('');
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

          {/* Messages display */}
          <div className="message-container">
            {messages.length === 0 ? (
              <p>No messages yet.</p>
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

          {/* Message input form */}
          <div className="input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="input-field"
              placeholder="Type a message..."
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button onClick={handleSendMessage} className="send-button">
              ➤
            </button>
          </div>

          {/* Connection status */}
          <div className="status-bar">
            Status: {['Connecting', 'Open', 'Closing', 'Closed'][readyState]}
          </div>
          <div>
            Last message: {lastMessage ? lastMessage.data : 'No message'}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
