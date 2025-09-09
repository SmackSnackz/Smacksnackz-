import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, useNavigate, useParams, Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Generate a session ID for guest users
const getGuestSessionId = () => {
  let sessionId = localStorage.getItem('guest_session_id');
  if (!sessionId) {
    sessionId = 'guest_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    localStorage.setItem('guest_session_id', sessionId);
  }
  return sessionId;
};

const StatusBadge = () => {
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await axios.get(`${API}/`);
        if (response.status === 200) {
          setStatus('online');
        }
      } catch (error) {
        setStatus('offline');
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
      status === 'online' ? 'bg-emerald-100 text-emerald-800' : 
      status === 'offline' ? 'bg-red-100 text-red-800' : 
      'bg-gray-100 text-gray-800'
    }`}>
      <div className={`w-2 h-2 rounded-full mr-1 ${
        status === 'online' ? 'bg-emerald-500' : 
        status === 'offline' ? 'bg-red-500' : 
        'bg-gray-500'
      }`}></div>
      {status === 'online' ? 'Online' : status === 'offline' ? 'Offline' : 'Checking...'}
    </div>
  );
};

const CompanionCard = ({ companion, onClick }) => (
  <div 
    onClick={() => onClick(companion.id)}
    className="bg-gray-800/50 rounded-xl p-6 border border-gray-700 hover:border-purple-500 transition-all cursor-pointer transform hover:-translate-y-2"
  >
    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-teal-500 rounded-full mb-4 flex items-center justify-center">
      <span className="text-white font-bold text-xl">{companion.name[0]}</span>
    </div>
    <h3 className="text-xl font-semibold text-white mb-2">{companion.name}</h3>
    <p className="text-gray-300 text-sm mb-3">{companion.short_bio}</p>
    <div className="flex flex-wrap gap-1">
      {companion.traits.slice(0, 3).map((trait, index) => (
        <span key={index} className="px-2 py-1 bg-purple-600/20 text-purple-300 text-xs rounded-full">
          {trait}
        </span>
      ))}
    </div>
  </div>
);

const FeatureCard = ({ title, description }) => (
  <div className="text-center">
    <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
    <p className="text-gray-300">{description}</p>
  </div>
);

const Home = () => {
  const navigate = useNavigate();

  const handleChatWithCompanions = () => {
    navigate('/companions');
  };

  const handleCreateCompanion = () => {
    navigate('/companions/new');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3">
          <img src="/assets/logo.png" alt="Throne Companions" className="w-10 h-10 rounded-lg" />
          <span className="text-xl font-bold">Throne Companions</span>
        </Link>
        <StatusBadge />
      </header>

      {/* Hero Section */}
      <section className="px-6 py-20 text-center max-w-4xl mx-auto">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-teal-400 bg-clip-text text-transparent">
          Your AI Companions—Real Presence, Real Memory.
        </h1>
        <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
          Create or chat with Sophia, Nova, Zara, and more—personalities that remember, care, and evolve.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button 
            onClick={handleChatWithCompanions}
            className="bg-purple-600 hover:bg-purple-700 px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
          >
            Chat with Companions
          </button>
          <button 
            onClick={handleCreateCompanion}
            className="border border-teal-500 text-teal-400 hover:bg-teal-500 hover:text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
          >
            Create a Companion
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-16 bg-gray-800/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose Throne Companions?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard 
              title="Multiple AI Models"
              description="Access various AI personalities, each with unique traits and capabilities."
            />
            <FeatureCard 
              title="Deep Personalization"
              description="Companions adapt to your preferences and communication style over time."
            />
            <FeatureCard 
              title="Adaptive Memory"
              description="Your companions remember past conversations and build meaningful relationships."
            />
            <FeatureCard 
              title="Secure & Private"
              description="Your conversations and data are protected with enterprise-grade security."
            />
          </div>
        </div>
      </section>

      {/* Companions Section */}
      <section className="px-6 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Meet Your Companions</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div onClick={() => navigate('/companions')} className="cursor-pointer">
              <CompanionCard 
                companion={{
                  id: "sophia",
                  name: "Sophia",
                  short_bio: "Wise and thoughtful, provides deep insights about life and philosophy.",
                  traits: ["Wise", "Philosophical", "Empathetic"]
                }}
                onClick={() => navigate('/companions')}
              />
            </div>
            <div onClick={() => navigate('/companions')} className="cursor-pointer">
              <CompanionCard 
                companion={{
                  id: "nova",
                  name: "Nova",
                  short_bio: "Energetic and creative, loves exploring new ideas and innovative solutions.",
                  traits: ["Creative", "Energetic", "Innovative"]
                }}
                onClick={() => navigate('/companions')}
              />
            </div>
            <div onClick={() => navigate('/companions')} className="cursor-pointer">
              <CompanionCard 
                companion={{
                  id: "zara",
                  name: "Zara",
                  short_bio: "Empathetic and caring, always there to listen and offer comfort.",
                  traits: ["Empathetic", "Caring", "Supportive"]
                }}
                onClick={() => navigate('/companions')}
              />
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-16 bg-gradient-to-r from-purple-600/20 to-teal-600/20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Meet Your Perfect Companion?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Start your journey with AI companions that truly understand and remember you.
          </p>
          <button 
            onClick={handleChatWithCompanions}
            className="bg-purple-600 hover:bg-purple-700 px-12 py-4 rounded-lg font-semibold text-xl transition-colors"
          >
            Get Started Now
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 border-t border-gray-700">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center">
          <Link to="/" className="flex items-center space-x-3 mb-4 md:mb-0">
            <img src="/assets/logo.png" alt="Throne Companions" className="w-8 h-8 rounded-lg" />
            <span className="font-semibold">Throne Companions</span>
          </Link>
          <div className="text-gray-400">
            v-now
          </div>
        </div>
      </footer>
    </div>
  );
};

const CompanionsPage = () => {
  const [companions, setCompanions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCompanions = async () => {
      try {
        const response = await axios.get(`${API}/companions`);
        setCompanions(response.data);
      } catch (error) {
        console.error('Error fetching companions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanions();
  }, []);

  const handleCompanionClick = (companionId) => {
    navigate(`/chat/${companionId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-gray-700">
        <Link to="/" className="flex items-center space-x-3">
          <img src="/assets/logo.png" alt="Throne Companions" className="w-10 h-10 rounded-lg" />
          <span className="text-xl font-bold">Throne Companions</span>
        </Link>
        <StatusBadge />
      </header>

      <div className="px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold">Choose Your Companion</h1>
            <Link 
              to="/companions/new"
              className="bg-teal-600 hover:bg-teal-700 px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Create New Companion
            </Link>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {companions.map((companion) => (
              <CompanionCard 
                key={companion.id}
                companion={companion}
                onClick={handleCompanionClick}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const ChatPage = () => {
  const { id } = useParams();
  const [companion, setCompanion] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [typing, setTyping] = useState(false);
  const sessionId = getGuestSessionId();

  useEffect(() => {
    const fetchCompanionAndMessages = async () => {
      try {
        // Fetch companion details
        const companionResponse = await axios.get(`${API}/companions/${id}`);
        setCompanion(companionResponse.data);

        // Fetch chat history
        const messagesResponse = await axios.get(`${API}/chat/${id}?session_id=${sessionId}`);
        setMessages(messagesResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanionAndMessages();
  }, [id, sessionId]);

  const sendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    setSending(true);
    setTyping(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        companion_id: id,
        message: newMessage,
        session_id: sessionId
      });

      // Add user message immediately
      const userMessage = {
        id: Date.now().toString(),
        message: newMessage,
        is_user: true,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, userMessage, response.data]);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
      setTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (!companion) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Companion Not Found</h2>
          <Link to="/companions" className="text-purple-400 hover:text-purple-300">
            Back to Companions
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-gray-700 bg-slate-800">
        <div className="flex items-center space-x-4">
          <Link to="/companions" className="text-gray-400 hover:text-white">
            ← Back
          </Link>
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-teal-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">{companion.name[0]}</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">{companion.name}</h1>
              <p className="text-sm text-gray-400">{companion.short_bio}</p>
            </div>
          </div>
        </div>
        <StatusBadge />
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <div key={message.id || index} className={`flex ${message.is_user ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.is_user 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-700 text-gray-100'
              }`}>
                <p>{message.message}</p>
                <p className="text-xs opacity-70 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {typing && (
            <div className="flex justify-start">
              <div className="bg-gray-700 text-gray-100 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-4 bg-slate-800">
        <div className="max-w-4xl mx-auto flex space-x-4">
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Message ${companion.name}...`}
            className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
            rows="2"
            disabled={sending}
          />
          <button
            onClick={sendMessage}
            disabled={sending || !newMessage.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-2 rounded-lg font-medium transition-colors"
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

const CreateCompanionPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    short_bio: '',
    long_backstory: '',
    traits: []
  });
  const [newTrait, setNewTrait] = useState('');
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (creating) return;

    setCreating(true);
    try {
      await axios.post(`${API}/companions`, formData);
      navigate('/companions');
    } catch (error) {
      console.error('Error creating companion:', error);
      alert('Failed to create companion. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const addTrait = () => {
    if (newTrait.trim() && !formData.traits.includes(newTrait.trim())) {
      setFormData(prev => ({
        ...prev,
        traits: [...prev.traits, newTrait.trim()]
      }));
      setNewTrait('');
    }
  };

  const removeTrait = (trait) => {
    setFormData(prev => ({
      ...prev,
      traits: prev.traits.filter(t => t !== trait)
    }));
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-gray-700">
        <Link to="/companions" className="flex items-center space-x-3">
          <span className="text-gray-400">← Back to Companions</span>
        </Link>
        <StatusBadge />
      </header>

      <div className="px-6 py-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Create New Companion</h1>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({...prev, name: e.target.value}))}
                className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Short Bio</label>
              <input
                type="text"
                value={formData.short_bio}
                onChange={(e) => setFormData(prev => ({...prev, short_bio: e.target.value}))}
                placeholder="A brief one-line description..."
                className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Long Backstory</label>
              <textarea
                value={formData.long_backstory}
                onChange={(e) => setFormData(prev => ({...prev, long_backstory: e.target.value}))}
                placeholder="Detailed background and personality description..."
                rows="4"
                className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Personality Traits</label>
              <div className="flex space-x-2 mb-2">
                <input
                  type="text"
                  value={newTrait}
                  onChange={(e) => setNewTrait(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTrait())}
                  placeholder="Add a trait..."
                  className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  type="button"
                  onClick={addTrait}
                  className="bg-teal-600 hover:bg-teal-700 px-4 py-2 rounded-lg transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.traits.map((trait, index) => (
                  <span 
                    key={index}
                    className="bg-purple-600/20 text-purple-300 px-3 py-1 rounded-full text-sm flex items-center space-x-2"
                  >
                    <span>{trait}</span>
                    <button
                      type="button"
                      onClick={() => removeTrait(trait)}
                      className="text-purple-300 hover:text-white"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={creating}
                className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 px-6 py-3 rounded-lg font-medium transition-colors"
              >
                {creating ? 'Creating...' : 'Create Companion'}
              </button>
              <Link
                to="/companions"
                className="px-6 py-3 border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 rounded-lg font-medium transition-colors text-center"
              >
                Cancel
              </Link>
            </div>
          </form>
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
          <Route path="/" element={<Home />} />
          <Route path="/companions" element={<CompanionsPage />} />
          <Route path="/chat/:id" element={<ChatPage />} />
          <Route path="/companions/new" element={<CreateCompanionPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;