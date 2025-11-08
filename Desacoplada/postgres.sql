CREATE TABLE items (
    id VARCHAR(15) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    numero_telefono VARCHAR(20),
    puesto_trabajo VARCHAR(50) NOT NULL CHECK (puesto_trabajo IN ('desarrollador', 'administrativo', 'notario', 'comercial'))
);

-- Insertar datos Iniciales
INSERT INTO items (id, nombre, apellidos, numero_telefono, puesto_trabajo) VALUES 
('12345678A', 'Ana', 'García Pérez', '600112233', 'desarrollador'),
('98765432B', 'Carlos', 'López Martín', '611223344', 'administrativo'),
('45678901C', 'Elena', 'Ruiz Gómez', '622334455', 'notario'),
('01234567D', 'Javier', 'Sánchez Torres', '633445566', 'comercial');