import { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import Companions from "./components/Companions";
import Chat from "./components/Chat";
import Navigation from "./components/Navigation";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Welcome to AI Companions
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Meet your AI companions, each with unique personalities and insights to guide your conversations.
          </p>
          <div className="mt-8">
            <a
              href="/companions"
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition duration-300 text-lg font-semibold"
            >
              Meet Your Companions
            </a>
          </div>
        </header>
        
        <div className="text-center mt-16">
          <a
            className="inline-block opacity-50 hover:opacity-75 transition duration-300"
            href="https://emergent.sh"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img 
              src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4" 
              alt="Emergent Logo"
              className="w-16 h-16 mx-auto rounded-full"
            />
            <p className="mt-2 text-sm text-gray-500">Powered by Emergent</p>
          </a>
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
          <Route path="/companions" element={<Companions />} />
          <Route path="/chat/:id" element={<Chat />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;