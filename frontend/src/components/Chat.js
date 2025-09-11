import { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import Navigation from "./Navigation";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Chat = () => {
  const { id } = useParams();
  const [companion, setCompanion] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchCompanion();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchCompanion = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/companions/${id}`);
      setCompanion(response.data);
      
      // Add a welcome message
      setMessages([
        {
          id: 'welcome',
          type: 'companion',
          message: `Hello! I'm ${response.data.name}. ${response.data.short_bio} What would you like to talk about?`,
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (err) {
      console.error("Error fetching companion:", err);
      setError("Companion not found or failed to load.");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || sending) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      message: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage("");
    setSending(true);

    try {
      const response = await axios.post(`${API}/chat/${id}`, {
        message: currentMessage
      });

      const companionMessage = {
        id: response.data.id,
        type: 'companion',
        message: response.data.companion_response,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, companionMessage]);
    } catch (err) {
      console.error("Error sending message:", err);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        message: "Sorry, I'm having trouble responding right now. Please try again.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setSending(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center min-h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading companion...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-md mx-auto mb-4">
              {error}
            </div>
            <Link 
              to="/companions"
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition duration-300"
            >
              Back to Companions
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <Navigation />
      
      {/* Chat Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center">
            <Link 
              to="/companions"
              className="mr-4 text-blue-600 hover:text-blue-800 transition duration-300"
            >
              ← Back
            </Link>
            <img
              src={companion?.avatar_path}
              alt={companion?.name}
              className="w-10 h-10 rounded-full border-2 border-gray-200 mr-3"
              onError={(e) => {
                e.target.src = `data:image/svg+xml,<svg width="40" height="40" xmlns="http://www.w3.org/2000/svg"><rect width="40" height="40" fill="%23f0f0f0"/><circle cx="20" cy="16" r="8" fill="%23ddd"/><circle cx="20" cy="28" r="10" fill="%23ddd"/></svg>`;
              }}
            />
            <div>
              <h2 className="text-xl font-bold text-gray-800">
                {companion?.name}
              </h2>
              <p className="text-sm text-gray-600">
                {companion?.short_bio}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="container mx-auto px-4 py-4">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.type === 'error'
                      ? 'bg-red-100 text-red-800 border border-red-300'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.message}</p>
                  <p className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-sm">Typing...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={sendMessage} className="flex space-x-4">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={`Type a message to ${companion?.name}...`}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={sending}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || sending}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition duration-300"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;