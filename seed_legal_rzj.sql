BEGIN;

-- Seed inicial para Mediaciones RJZ
-- Ejecutar después de crear las tablas en Railway.

INSERT INTO businesses (id, name, phone_number_id, whatsapp_token, business_type, welcome_message, human_support_phone, is_active)
VALUES
('00000000-0000-0000-0000-000000000001', 'Mediaciones RJZ', '1158066464056590', 'DEMO_TOKEN', 'law_firm',
 '¡Hola! Bienvenido a *Mediaciones RJZ* ⚖️\n\nSomos un estudio jurídico especializado en Derecho de Familia:\n• Custodia de menores\n• Pensión alimenticia\n• Regulación de visitas y mediación familiar\n\nEstamos aquí para ayudarte a encontrar una solución rápida y cercana. ¿En qué podemos asesorarte hoy?',
 '+56912345678', true)
ON CONFLICT DO NOTHING;

INSERT INTO business_settings (id, business_id, address, city, maps_url, hours, currency, currency_symbol)
VALUES
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001',
 'Av. Libertador Bernardo O''Higgins 1234, Oficina 501',
 'Santiago',
 'https://maps.google.com/?q=Mediaciones+RJZ+Santiago',
 '{"lunes":"09:00-18:00","martes":"09:00-18:00","miércoles":"09:00-18:00","jueves":"09:00-18:00","viernes":"09:00-18:00","sábado":"10:00-14:00","domingo":"Cerrado"}'::json,
 'CLP', '$')
ON CONFLICT DO NOTHING;

-- Categorías legales
INSERT INTO legal_categories (id, business_id, area, name, description, is_active)
VALUES
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', 'familia', 'Derecho de Familia',
 'Mediación familiar, custodia de menores, pensión alimenticia, regulación de visitas y acuerdos de convivencia.', true)
ON CONFLICT DO NOTHING;

-- Servicios legales
INSERT INTO legal_services (id, business_id, category_id, name, description, base_price, estimated_timeframe, requirements, is_available)
VALUES
('00000000-0000-0000-0000-000000000106', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000011',
 'Mediación Familiar',
 'Proceso de mediación obligatoria para alimentos, custodia y visitas. Facilitamos acuerdos entre las partes evitando litigio.',
 300000, '1-2 meses', 'Requisito previo a demandas de familia. Incluye sesiones de mediación.', true),
('00000000-0000-0000-0000-000000000107', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000011',
 'Custodia y Cuidado Personal',
 'Demanda o defensa en casos de custodia de menores. Incluye: mediación previa, demanda judicial, peritaje psicosocial, audiencias preparatorias y de juicio.',
 800000, '4-8 meses', 'Requiere mediación previa. Puede incluir peritaje psicológico del menor.', true),
('00000000-0000-0000-0000-000000000108', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000011',
 'Pensión de Alimentos',
 'Demanda de pensión alimenticia para hijos o defensa. Incluye: cálculo de pensión, mediación, audiencias.',
 400000, '3-5 meses', 'Se puede solicitar pensión provisoria urgente. Requiere mediación previa.', true),
('00000000-0000-0000-0000-000000000109', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000011',
 'Regulación de Visitas (Relación Directa y Regular)',
 'Establecimiento o modificación del régimen de visitas. Incluye: mediación, demanda judicial si no hay acuerdo.',
 350000, '2-4 meses', 'Busca establecer relación estable entre padre/madre e hijo.', true)
ON CONFLICT DO NOTHING;
 'Cobranza de deudas mediante juicio ejecutivo o cobranza ordinaria. Incluye: demanda, embargo, remate si es necesario.',
 400000, '4-12 meses', 'Honorarios variables según monto a cobrar. Requiere título ejecutivo.', true),
('00000000-0000-0000-0000-000000000111', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000012',
 'Compraventa de Inmuebles - Escrituración',
 'Redacción y tramitación de escrituras de compraventa. Incluye: revisión de títulos, inscripción en Conservador de Bienes Raíces.',
 350000, '1-2 meses', 'No incluye impuestos ni tasas notariales (corren por cuenta del cliente).', true),
('00000000-0000-0000-0000-000000000112', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000012',
 'Regularización de Propiedades',
 'Tramitación de posesión efectiva, inscripciones pendientes, saneamiento de títulos.',
 600000, '3-6 meses', 'Búsqueda de antecedentes, gestiones ante Conservador de Bienes Raíces.', true),
('00000000-0000-0000-0000-000000000113', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000012',
 'Redacción de Contratos',
 'Redacción y revisión de contratos (arriendo, compraventa, prestación de servicios). Incluye: análisis de cláusulas, asesoría legal.',
 200000, '1-2 semanas', 'Entrega rápida. Consulta gratuita para evaluar necesidades.', true),
('00000000-0000-0000-0000-000000000114', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Consulta Legal Presencial',
 'Reunión presencial de 1 hora con abogado especialista. Evaluación de tu caso, estrategia legal recomendada, presupuesto detallado.',
 50000, '1 hora', '⚠️ PRIMERA CONSULTA GRATUITA para nuevos clientes.', true),
('00000000-0000-0000-0000-000000000115', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Traslado de Imputados',
 'Coordinación de traslado de imputados detenidos a audiencias u otras diligencias. Incluye: gestión con Gendarmería, seguimiento del traslado.',
 400000, 'Inmediato', '⚠️ Servicio de emergencia - disponibilidad inmediata.', true)
ON CONFLICT DO NOTHING;

COMMIT;
