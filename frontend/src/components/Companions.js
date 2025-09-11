import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import Navigation from "./Navigation";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Companions = () => {
  const [companions, setCompanions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCompanions();
  }, []);

  const fetchCompanions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/companions`);
      setCompanions(response.data);
    } catch (err) {
      console.error("Error fetching companions:", err);
      setError("Failed to load companions. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const getTraitColor = (trait) => {
    const colors = {
      empathetic: "bg-pink-100 text-pink-800",
      poetic: "bg-purple-100 text-purple-800",
      wise: "bg-green-100 text-green-800",
      strategic: "bg-blue-100 text-blue-800",
      composed: "bg-indigo-100 text-indigo-800",
      influential: "bg-yellow-100 text-yellow-800",
      magnetic: "bg-red-100 text-red-800",
      direct: "bg-orange-100 text-orange-800",
      playful: "bg-teal-100 text-teal-800",
    };
    return colors[trait] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center min-h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading companions...</p>
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
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-md mx-auto">
              {error}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Your AI Companions
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Choose a companion to start your conversation. Each has a unique personality and perspective.
          </p>
        </header>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {companions.map((companion) => (
            <div
              key={companion.slug}
              className="bg-white rounded-xl shadow-lg hover:shadow-xl transition duration-300 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <img
                    src={companion.avatar_path}
                    alt={companion.name}
                    className="w-16 h-16 rounded-full border-2 border-gray-200 mr-4"
                    onError={(e) => {
                      e.target.src = `data:image/svg+xml,<svg width="64" height="64" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" fill="%23f0f0f0"/><circle cx="32" cy="24" r="10" fill="%23ddd"/><circle cx="32" cy="48" r="14" fill="%23ddd"/></svg>`;
                    }}
                  />
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">
                      {companion.name}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      @{companion.slug}
                    </p>
                  </div>
                </div>

                <p className="text-gray-700 mb-4 leading-relaxed">
                  {companion.short_bio}
                </p>

                <div className="flex flex-wrap gap-2 mb-6">
                  {companion.traits.map((trait) => (
                    <span
                      key={trait}
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getTraitColor(trait)}`}
                    >
                      {trait}
                    </span>
                  ))}
                </div>

                <Link
                  to={`/chat/${companion.slug}`}
                  className="block w-full bg-blue-600 text-white text-center py-3 rounded-lg hover:bg-blue-700 transition duration-300 font-semibold"
                >
                  Start Conversation
                </Link>
              </div>
            </div>
          ))}
        </div>

        {companions.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No companions available at the moment.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Companions;