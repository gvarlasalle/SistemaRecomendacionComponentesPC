// src/components/ChatInterface.jsx
import React, { useState } from 'react';
import { Send, Loader } from 'lucide-react';
import { recommendAPI } from '../services/api';

function ChatInterface({ onConfigurationGenerated }) {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);

  const examples = [
    "Quiero una PC para jugar Valorant, tengo 2000 soles",
    "PC para programar Python y machine learning, 1800 soles",
    "Computadora para diseño gráfico con Photoshop, 2500 soles",
    "PC básica para oficina, Excel y Word, 900 soles"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError(null);

    const userMessage = { type: 'user', text: message };
    setChatHistory(prev => [...prev, userMessage]);

    try {
      // No especificar model_type para usar el mejor modelo automáticamente
      const response = await recommendAPI.getRecommendation(message);
      const config = response.data;

      const botMessage = { 
        type: 'bot', 
        text: '¡Configuración generada! Mira los detalles a la derecha →',
        config 
      };
      setChatHistory(prev => [...prev, botMessage]);

      onConfigurationGenerated(config);
      setMessage('');

    } catch (err) {
      setError('Error al generar la configuración. Intenta de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (example) => {
    setMessage(example);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">
        💬 Cuéntame qué PC necesitas
      </h2>

      <div className="h-96 overflow-y-auto mb-4 space-y-4 p-4 bg-gray-50 rounded-lg">
        {chatHistory.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <p className="mb-4">👋 ¡Hola! Describe tu PC ideal</p>
            <p className="text-sm">
              Puedes decirme tu presupuesto, para qué la usarás, 
              qué juegos quieres jugar, etc.
            </p>
          </div>
        )}

        {chatHistory.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 px-4 py-2 rounded-lg flex items-center space-x-2">
              <Loader className="w-4 h-4 animate-spin" />
              <span>Generando configuración...</span>
            </div>
          </div>
        )}
      </div>

      {chatHistory.length === 0 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Ejemplos:</p>
          <div className="space-y-2">
            {examples.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="w-full text-left px-3 py-2 text-sm bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-gray-700"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ej: Quiero una PC para gaming, 2500 soles"
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}

export default ChatInterface;