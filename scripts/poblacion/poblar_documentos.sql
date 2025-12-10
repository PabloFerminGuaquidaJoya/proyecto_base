-- Script SQL para poblar tipos y categorías de documentos

-- Insertar Tipos de Documento
INSERT INTO documentos_tipodocumento (nombre, descripcion, extensiones_permitidas, tamaño_maximo_mb, icono, color, activo, created_at, updated_at)
VALUES
('Manual de Operacion', 'Manuales de operacion y uso de maquinaria', '[".pdf", ".doc", ".docx"]', 50, 'bi-book', '#007bff', 1, datetime('now'), datetime('now')),
('Manual de Mantenimiento', 'Manuales de mantenimiento preventivo y correctivo', '[".pdf", ".doc", ".docx"]', 50, 'bi-tools', '#28a745', 1, datetime('now'), datetime('now')),
('Ficha Tecnica', 'Fichas tecnicas y especificaciones', '[".pdf", ".doc", ".docx", ".xlsx"]', 25, 'bi-file-earmark-text', '#17a2b8', 1, datetime('now'), datetime('now')),
('Planos', 'Planos tecnicos y diagramas', '[".pdf", ".dwg", ".dxf"]', 100, 'bi-diagram-3', '#ffc107', 1, datetime('now'), datetime('now')),
('Certificado', 'Certificados de calibracion, calidad, etc.', '[".pdf"]', 10, 'bi-award', '#fd7e14', 1, datetime('now'), datetime('now')),
('Procedimiento', 'Procedimientos operativos estandar', '[".pdf", ".doc", ".docx"]', 25, 'bi-list-check', '#6610f2', 1, datetime('now'), datetime('now')),
('Reporte', 'Reportes de inspeccion, auditoria, etc.', '[".pdf", ".doc", ".docx", ".xlsx"]', 30, 'bi-file-earmark-bar-graph', '#e83e8c', 1, datetime('now'), datetime('now')),
('Otro', 'Otros documentos', '[".pdf", ".doc", ".docx", ".txt", ".xlsx", ".ppt", ".pptx"]', 50, 'bi-file-earmark', '#6c757d', 1, datetime('now'), datetime('now'));

-- Insertar Categorías de Documento
INSERT INTO documentos_categoriadocumento (nombre, descripcion, icono, color, orden, activo, parent_id)
VALUES
('Maquinaria', 'Documentos relacionados con maquinaria', 'bi-gear-fill', '#007bff', 1, 1, NULL),
('Seguridad', 'Documentos de seguridad industrial', 'bi-shield-check', '#28a745', 2, 1, NULL),
('Calidad', 'Documentos de control de calidad', 'bi-clipboard-check', '#17a2b8', 3, 1, NULL),
('Mantenimiento', 'Documentos de mantenimiento', 'bi-tools', '#ffc107', 4, 1, NULL),
('Operacion', 'Documentos de operacion', 'bi-play-circle', '#fd7e14', 5, 1, NULL),
('Tecnica', 'Documentos tecnicos generales', 'bi-file-earmark-code', '#6610f2', 6, 1, NULL),
('Administrativa', 'Documentos administrativos', 'bi-briefcase', '#e83e8c', 7, 1, NULL),
('General', 'Documentos generales', 'bi-folder', '#6c757d', 8, 1, NULL);
