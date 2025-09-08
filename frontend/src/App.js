import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds
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

const CompanionCard = ({ name, description, image }) => (
  <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700 hover:border-purple-500 transition-colors">
    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-teal-500 rounded-full mb-4 flex items-center justify-center">
      <span className="text-white font-bold text-xl">{name[0]}</span>
    </div>
    <h3 className="text-xl font-semibold text-white mb-2">{name}</h3>
    <p className="text-gray-300">{description}</p>
  </div>
);

const FeatureCard = ({ title, description }) => (
  <div className="text-center">
    <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
    <p className="text-gray-300">{description}</p>
  </div>
);

const Home = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <img src="/assets/logo.png" alt="Throne Companions" className="w-10 h-10 rounded-lg" />
          <span className="text-xl font-bold">Throne Companions</span>
        </div>
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
          <button className="bg-purple-600 hover:bg-purple-700 px-8 py-4 rounded-lg font-semibold text-lg transition-colors">
            Chat with Companions
          </button>
          <button className="border border-teal-500 text-teal-400 hover:bg-teal-500 hover:text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors">
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
            <CompanionCard 
              name="Sophia"
              description="Wise and thoughtful, Sophia provides deep insights and meaningful conversations about life and philosophy."
            />
            <CompanionCard 
              name="Nova"
              description="Energetic and creative, Nova loves exploring new ideas and helping you brainstorm innovative solutions."
            />
            <CompanionCard 
              name="Zara"
              description="Empathetic and caring, Zara is your supportive friend who's always there to listen and offer comfort."
            />
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
          <button className="bg-purple-600 hover:bg-purple-700 px-12 py-4 rounded-lg font-semibold text-xl transition-colors">
            Get Started Now
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 border-t border-gray-700">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-3 mb-4 md:mb-0">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-teal-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="font-semibold">Throne Companions</span>
          </div>
          <div className="text-gray-400">
            v-now
          </div>
        </div>
      </footer>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;