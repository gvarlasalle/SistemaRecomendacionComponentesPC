// src/components/ConfigurationDisplay.jsx
import React from 'react';
import { Cpu, HardDrive, MemoryStick, CheckCircle, AlertCircle, Monitor } from 'lucide-react';

function ConfigurationDisplay({ configuration }) {
  if (!configuration) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800">
          🖥️ Tu Configuración
        </h2>
        <div className="flex items-center justify-center h-96 text-gray-400">
          <div className="text-center">
            <Monitor className="w-16 h-16 mx-auto mb-4" />
            <p>Aún no hay configuración generada</p>
            <p className="text-sm mt-2">Escribe tu requerimiento en el chat</p>
          </div>
        </div>
      </div>
    );
  }

  const { configuration: components, costs, compatibility } = configuration;

  const componentIcons = {
    CPU: <Cpu className="w-5 h-5" />,
    GPU: <Cpu className="w-5 h-5" />,
    RAM: <MemoryStick className="w-5 h-5" />,
    STORAGE: <HardDrive className="w-5 h-5" />,
    MOTHERBOARD: <Cpu className="w-5 h-5" />,
    PSU: <Cpu className="w-5 h-5" />,
    CASE: <Cpu className="w-5 h-5" />,
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">
        🖥️ Tu Configuración
      </h2>

      <div className="space-y-3 mb-6">
        {Object.entries(components).map(([type, component]) => (
          <div key={type} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div className="mt-1 text-blue-600">
                  {componentIcons[type]}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-gray-700">{type}</span>
                    <span className="text-lg font-bold text-gray-900">
                      S/ {component.price.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{component.name}</p>
                  <p className="text-xs text-gray-500 mt-1">{component.brand}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t pt-4 mb-4">
        <div className="space-y-2">
          <div className="flex justify-between text-gray-700">
            <span>Presupuesto:</span>
            <span className="font-semibold">S/ {costs.budget.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-lg font-bold text-gray-900">
            <span>Total:</span>
            <span>S/ {costs.total.toFixed(2)}</span>
          </div>
          <div className={`flex justify-between text-sm ${
            costs.remaining >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            <span>{costs.remaining >= 0 ? 'Te sobran:' : 'Te faltan:'}</span>
            <span className="font-semibold">
              S/ {Math.abs(costs.remaining).toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between text-sm text-gray-600">
            <span>Uso del presupuesto:</span>
            <span className={`font-semibold ${
              costs.compliance_percentage > 110 ? 'text-red-600' : 
              costs.compliance_percentage > 100 ? 'text-yellow-600' : 'text-green-600'
            }`}>
              {costs.compliance_percentage.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      <div className={`p-4 rounded-lg ${
        compatibility.is_valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
      }`}>
        <div className="flex items-center space-x-2 mb-2">
          {compatibility.is_valid ? (
            <>
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="font-semibold text-green-800">✓ Configuración compatible</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="font-semibold text-red-800">⚠ Problemas de compatibilidad</span>
            </>
          )}
        </div>

        {compatibility.errors && compatibility.errors.length > 0 && (
          <div className="mt-2 space-y-1">
            {compatibility.errors.map((error, index) => (
              <p key={index} className="text-sm text-red-700">• {error}</p>
            ))}
          </div>
        )}

        {compatibility.warnings && compatibility.warnings.length > 0 && (
          <div className="mt-2 space-y-1">
            {compatibility.warnings.map((warning, index) => (
              <p key={index} className="text-sm text-yellow-700">⚠ {warning}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ConfigurationDisplay;