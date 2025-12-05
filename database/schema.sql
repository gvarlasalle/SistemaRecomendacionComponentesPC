-- Tabla de componentes
CREATE TABLE IF NOT EXISTS components (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- CPU, GPU, RAM, MOTHERBOARD, STORAGE, PSU, CASE
    brand VARCHAR(100),
    price DECIMAL(10, 2),
    specs JSONB, -- Especificaciones técnicas en formato JSON
    compatibility_info JSONB, -- Información de compatibilidad
    url TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios (sintéticos para el modelo)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_type VARCHAR(50) NOT NULL, -- Gamer, Developer, Designer, Student, Office
    budget_range VARCHAR(50), -- low, medium, high, premium
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de interacciones (para entrenamiento del modelo)
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50), -- view, click, add_to_cart, purchase
    rating DECIMAL(3, 2), -- Rating implícito basado en interacciones
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de configuraciones completas
CREATE TABLE IF NOT EXISTS configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    config_name VARCHAR(255),
    components JSONB, -- IDs de componentes en formato JSON
    total_price DECIMAL(10, 2),
    is_compatible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_components_type ON components(type);
CREATE INDEX IF NOT EXISTS idx_components_price ON components(price);
CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_component ON interactions(component_id);
CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);