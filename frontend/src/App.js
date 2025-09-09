import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Landing Page Component
const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center px-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="mb-8">
          <img 
            src="/public/assets/logo.png" 
            alt="Throne Companions" 
            className="w-24 h-24 mx-auto mb-6 rounded-full border-2 border-purple-400"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
          <h1 className="text-6xl font-bold text-white mb-4 tracking-tight">
            Throne Companions
          </h1>
          <p className="text-xl text-purple-200 mb-8 max-w-2xl mx-auto">
            Meet your AI companions - each with unique personalities, wisdom, and charm. 
            Choose your guide for meaningful conversations.
          </p>
        </div>
        
        <Link 
          to="/companions"
          className="inline-flex items-center px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors duration-200 shadow-lg hover:shadow-xl"
        >
          Meet Your Companions
          <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>
      </div>
    </div>
  );
};

// Companions List Component
const Companions = () => {
  const [companions, setCompanions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCompanions = async () => {
      try {
        const response = await axios.get(`${API}/companions`);
        setCompanions(response.data);
      } catch (error) {
        console.error('Failed to fetch companions:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCompanions();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading companions...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">Choose Your Companion</h1>
          <p className="text-purple-200 text-lg">Select a companion to start your conversation</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {companions.map((companion) => (
            <div key={companion._id} className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-purple-500 transition-colors">
              <div className="text-center mb-4">
                <img 
                  src={companion.avatar_path} 
                  alt={companion.name}
                  className="w-20 h-20 mx-auto rounded-full border-2 border-purple-400 mb-4"
                  onError={(e) => {
                    e.target.src = '/public/assets/logo.png';
                  }}
                />
                <h3 className="text-xl font-semibold text-white mb-2">{companion.name}</h3>
                <p className="text-purple-200 mb-4">{companion.short_bio}</p>
              </div>
              <Link 
                to={`/chat/${companion._id}`}
                className="block w-full bg-purple-600 hover:bg-purple-700 text-white text-center py-3 rounded-lg transition-colors"
              >
                Start Conversation
              </Link>
            </div>
          ))}
        </div>
        
        <div className="text-center mt-12">
          <Link to="/" className="text-purple-400 hover:text-purple-300 transition-colors">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

// Chat Component
const Chat = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [companion, setCompanion] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');

  useEffect(() => {
    // Get or create session ID
    let storedSessionId = localStorage.getItem('guest_session_id');
    if (!storedSessionId) {
      storedSessionId = 'guest_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('guest_session_id', storedSessionId);
    }
    setSessionId(storedSessionId);

    // Fetch companion details
    const fetchCompanion = async () => {
      try {
        const response = await axios.get(`${API}/companions/${id}`);
        setCompanion(response.data);
      } catch (error) {
        console.error('Failed to fetch companion:', error);
        navigate('/companions');
      }
    };
    
    fetchCompanion();
  }, [id, navigate]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    // Add user message to UI immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await axios.post(`${API}/chat`, {
        companion_id: id,
        message: userMessage,
        session_id: sessionId
      });

      // Update with full thread from server
      setMessages(response.data.thread);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!companion) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <img 
              src={companion.avatar_path} 
              alt={companion.name}
              className="w-10 h-10 rounded-full border-2 border-purple-400"
              onError={(e) => {
                e.target.src = '/public/assets/logo.png';
              }}
            />
            <div>
              <h2 className="text-white font-semibold">{companion.name}</h2>
              <p className="text-purple-200 text-sm">{companion.short_bio}</p>
            </div>
          </div>
          <Link 
            to="/companions" 
            className="text-purple-400 hover:text-purple-300 transition-colors"
          >
            ← Back
          </Link>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 max-w-4xl mx-auto w-full p-4 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center text-purple-200 mt-8">
            Start a conversation with {companion.name}!
          </div>
        )}
        
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
          >
            <div 
              className={`inline-block max-w-xs md:max-w-md p-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-slate-700 text-white'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="text-left mb-4">
            <div className="inline-block bg-slate-700 text-white p-3 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="bg-slate-800 border-t border-slate-700 p-4">
        <div className="max-w-4xl mx-auto flex space-x-4">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 bg-slate-700 text-white p-3 rounded-lg border border-slate-600 focus:border-purple-500 focus:outline-none resize-none"
            rows="1"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !inputMessage.trim()}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 text-white rounded-lg transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/companions" element={<Companions />} />
          <Route path="/chat/:id" element={<Chat />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;