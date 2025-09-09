import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useParams } from "react-router-dom";
import axios from "axios";

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
    <div>
      <header className="App-header">
        <a
          className="App-link"
          href="https://emergent.sh"
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4" />
        </a>
        <p className="mt-5">Building something incredible ~!</p>
        <Link to="/companions" className="mt-4 text-blue-400 underline">
          View Companions
        </Link>
      </header>
    </div>
  );
};

const Companions = () => {
  const [companions, setCompanions] = useState([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">Companions</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companions.map((companion) => (
            <div key={companion.slug} className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-colors">
              <div className="flex flex-col items-center">
                <img 
                  src={companion.avatar_path} 
                  alt={companion.name}
                  className="w-24 h-24 rounded-full mb-4 bg-gray-600"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="w-24 h-24 rounded-full mb-4 bg-gray-600 items-center justify-center text-2xl font-bold hidden">
                  {companion.name[0]}
                </div>
                <h2 className="text-xl font-semibold mb-2">{companion.name}</h2>
                <p className="text-gray-300 text-center mb-3">{companion.short_bio}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {companion.traits.map((trait, index) => (
                    <span key={index} className="bg-blue-600 text-xs px-2 py-1 rounded">
                      {trait}
                    </span>
                  ))}
                </div>
                <Link 
                  to={`/chat/${companion.slug}`}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition-colors"
                >
                  Chat with {companion.name}
                </Link>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center mt-8">
          <Link to="/" className="text-blue-400 underline">Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

const Chat = () => {
  const { id } = useParams();
  const [companion, setCompanion] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCompanion = async () => {
      try {
        const response = await axios.get(`${API}/companions/${id}`);
        setCompanion(response.data);
      } catch (error) {
        console.error('Error fetching companion:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanion();
  }, [id]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-white">Loading...</div>;
  }

  if (!companion) {
    return <div className="min-h-screen flex items-center justify-center text-white">Companion not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="container mx-auto max-w-2xl">
        <div className="text-center mb-8">
          <img 
            src={companion.avatar_path} 
            alt={companion.name}
            className="w-32 h-32 rounded-full mx-auto mb-4 bg-gray-600"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
          <div className="w-32 h-32 rounded-full mx-auto mb-4 bg-gray-600 items-center justify-center text-4xl font-bold hidden">
            {companion.name[0]}
          </div>
          <h1 className="text-3xl font-bold mb-2">{companion.name}</h1>
          <p className="text-gray-300 mb-4">{companion.short_bio}</p>
          <div className="flex flex-wrap gap-2 justify-center mb-6">
            {companion.traits.map((trait, index) => (
              <span key={index} className="bg-blue-600 text-sm px-3 py-1 rounded">
                {trait}
              </span>
            ))}
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-3">About {companion.name}</h2>
          <p className="text-gray-300 leading-relaxed">{companion.long_backstory}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3">Chat (Coming Soon)</h3>
          <p className="text-gray-400">Chat functionality will be implemented here.</p>
        </div>

        <div className="text-center">
          <Link to="/companions" className="text-blue-400 underline mr-4">Back to Companions</Link>
          <Link to="/" className="text-blue-400 underline">Home</Link>
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
