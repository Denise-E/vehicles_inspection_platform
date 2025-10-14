-- ===========================================================
--  Proyecto: Control de Inspección Vehicular
--  Autora: Denise Eichenblat
--  Materia: Técnicas Avanzadas de Programación
--  Fecha: Octubre 2025
-- ===========================================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS vehicles_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vehicles_db;

-- Roles de usuario
CREATE TABLE usuario_rol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO usuario_rol (nombre)
VALUES ('DUENIO'), ('INSPECTOR'), ('ADMIN');

-- Estados de turno
CREATE TABLE estado_turno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO estado_turno (nombre)
VALUES ('RESERVADO'), ('CONFIRMADO'), ('COMPLETADO'), ('CANCELADO');

-- Resultado de inspección
CREATE TABLE resultado_inspeccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO resultado_inspeccion (nombre)
VALUES ('SEGURO'), ('RECHEQUEAR');

-- Estado del vehículo
CREATE TABLE estado_vehiculo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO estado_vehiculo (nombre)
VALUES ('ACTIVO'), ('INACTIVO'), ('RECHEQUEAR');

-- ===========================================================
-- TABLAS PRINCIPALES
-- ===========================================================

-- Usuarios del sistema
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    mail VARCHAR(100) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    hash_password VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (rol_id) REFERENCES usuario_rol(id)
);

-- Vehículos registrados
CREATE TABLE vehiculo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    anio YEAR NOT NULL,
    duenio_id INT NOT NULL,
    estado_id INT NOT NULL,
    FOREIGN KEY (duenio_id) REFERENCES usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (estado_id) REFERENCES estado_vehiculo(id)
);

-- Turnos para revisión
CREATE TABLE turno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    fecha DATETIME NOT NULL,
    estado_id INT NOT NULL,
    creado_por INT NOT NULL,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculo(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (estado_id) REFERENCES estado_turno(id),
    FOREIGN KEY (creado_por) REFERENCES usuario(id)
);

-- Inspecciones de vehículos
CREATE TABLE inspeccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    turno_id INT UNIQUE,
    inspector_id INT,
    fecha DATETIME NOT NULL,
    puntuacion_total INT DEFAULT 0,
    resultado_id INT,
    observacion TEXT,
    estado VARCHAR(50),
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculo(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (turno_id) REFERENCES turno(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES usuario(id),
    FOREIGN KEY (resultado_id) REFERENCES resultado_inspeccion(id)
);

-- Chequeos dentro de una inspección
CREATE TABLE chequeo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspeccion_id INT,
    fecha DATETIME NOT NULL,
    puntuacion INT CHECK (puntuacion BETWEEN 1 AND 10),
    FOREIGN KEY (inspeccion_id) REFERENCES inspeccion(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ===========================================================
-- ÍNDICES Y VISTAS AUXILIARES
-- ===========================================================
CREATE INDEX idx_usuario_mail ON usuario(mail);
CREATE INDEX idx_vehiculo_matricula ON vehiculo(matricula);
CREATE INDEX idx_turno_fecha ON turno(fecha);
CREATE INDEX idx_inspeccion_fecha ON inspeccion(fecha);




