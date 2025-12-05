// src/components/ComponentExplorer.jsx
import React, { useState, useEffect } from 'react';
import { componentAPI } from '../services/api';
import { Filter } from 'lucide-react';

function ComponentExplorer() {
  const [components, setComponents] = useState([]);
  const [types, setTypes] = useState([]);
  const [selectedType, setSelectedType] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTypes();
    loadComponents();
  }, []);

  const loadTypes = async () => {
    try {
      const response = await componentAPI.types();
      setTypes(response.data.types);
    } catch (error) {
      console.error('Error loading types:', error);
    }
  };

  const loadComponents = async () => {
    setLoading(true);
    try {
      const params = { limit: 50 };
      
      if (selectedType) params.component_type = selectedType;
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const response = await componentAPI.list(params);
      setComponents(response.data.components);
    } catch (error) {
      console.error('Error loading components:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = () => {
    loadComponents();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        🔍 Explorar Componentes
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Componente
          </label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los tipos</option>
            {types.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Precio Máximo (S/)
          </label>
          <input
            type="number"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            placeholder="Ej: 1500"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-end">
          <button
            onClick={handleFilter}
            className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
          >
            <Filter className="w-5 h-5" />
            <span>Filtrar</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">
          Cargando componentes...
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-600 mb-4">
            Mostrando {components.length} componentes
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {components.map(component => (
              <div key={component.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                    {component.type}
                  </span>
                  <span className="text-lg font-bold text-gray-900">
                    S/ {component.regular_price.toFixed(2)}
                  </span>
                </div>
                
                <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">
                  {component.name}
                </h3>
                
                <p className="text-sm text-gray-600 mb-2">{component.brand}</p>
                
                {component.stock && (
                  <p className="text-xs text-gray-500">
                    Stock: {component.stock}
                  </p>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default ComponentExplorer;