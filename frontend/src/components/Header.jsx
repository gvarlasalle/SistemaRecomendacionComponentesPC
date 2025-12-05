// src/components/Header.jsx
import React from 'react';
import { Monitor } from 'lucide-react';

function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center space-x-3">
          <Monitor className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Sistema de Recomendación de PC
            </h1>
            <p className="text-sm text-gray-600">
              Construye tu PC ideal con IA - Mercado Peruano
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;