// src/App.js
import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import ConfigurationDisplay from './components/ConfigurationDisplay';
import ComponentExplorer from './components/ComponentExplorer';
import Header from './components/Header';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [configuration, setConfiguration] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex space-x-4 mb-8 border-b">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'chat'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            💬 Recomendador
          </button>
          
          <button
            onClick={() => setActiveTab('explore')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'explore'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            🔍 Explorar Componentes
          </button>
        </div>

        {/* Content */}
        {activeTab === 'chat' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ChatInterface onConfigurationGenerated={setConfiguration} />
            <ConfigurationDisplay configuration={configuration} />
          </div>
        )}

        {activeTab === 'explore' && (
          <ComponentExplorer />
        )}
      </div>
    </div>
  );
}

export default App;