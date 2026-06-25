BEGIN;

-- Seed inicial para Mediaciones RJZ
-- Ejecutar después de crear las tablas en Railway.

INSERT INTO businesses (id, name, phone_number_id, whatsapp_token, business_type, welcome_message, human_support_phone, is_active)
VALUES
('00000000-0000-0000-0000-000000000001', 'Mediaciones RJZ', 'DEMO_PHONE_NUMBER_ID', 'DEMO_TOKEN', 'law_firm',
 '¡Hola! Bienvenido a *Mediaciones RJZ* ⚖️\n\nSomos un estudio jurídico especializado en:\n• Derecho Penal (defensa, beneficios penitenciarios)\n• Derecho de Familia (VIF, custodia, mediación)\n• Derecho Civil (contratos, cobros, propiedades)\n\nEstamos aquí para ayudarte 24/7. ¿En qué podemos asesorarte hoy?',
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
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'penal', 'Derecho Penal',
 'Defensa penal en todas las etapas del proceso. Especialistas en Ley 20.000, VIF, delitos contra las personas, beneficios penitenciarios y recursos de apelación.', true),
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', 'familia', 'Derecho de Familia',
 'Mediación familiar, custodia de menores, pensión alimenticia, regulación de visitas, y casos de VIF con peritaje psicosocial.', true),
('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000001', 'civil', 'Derecho Civil',
 'Contratos, compraventa de inmuebles, cobranza judicial, escrituras públicas y asesoría en trámites civiles.', true)
ON CONFLICT DO NOTHING;

-- Servicios legales
INSERT INTO legal_services (id, business_id, category_id, name, description, base_price, estimated_timeframe, requirements, is_available)
VALUES
('00000000-0000-0000-0000-000000000100', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Defensa Penal - Ley 20.000 (Drogas)',
 'Defensa especializada en casos de tráfico y microtráfico de drogas. Incluye: análisis de pruebas, estrategia de defensa, audiencias, negociación con fiscalía.',
 800000, '3-6 meses',
 'Casos atendidos: Art. 3° (microtráfico), Art. 4° (tráfico simple), Art. 5° (tráfico agravado). ⚠️ Evaluación gratuita del caso.', true),
('00000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Defensa en VIF (Violencia Intrafamiliar)',
 'Defensa en casos de violencia intrafamiliar. Incluye: representación en audiencias, coordinación con peritaje psicosocial, estrategia de defensa o acuerdos reparatorios.',
 600000, '2-4 meses', 'Atendemos tanto a víctimas como a imputados.', true),
('00000000-0000-0000-0000-000000000102', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Delitos contra las Personas',
 'Defensa en homicidio, lesiones, amenazas y otros delitos contra las personas. Incluye: estrategia de defensa, recursos, audiencias.',
 1200000, '4-8 meses', 'Atención urgente para casos con prisión preventiva.', true),
('00000000-0000-0000-0000-000000000103', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Beneficios Penitenciarios',
 'Tramitación de libertad condicional, reclusión nocturna, salidas dominicales y otros beneficios de Ley 18.216.',
 450000, '1-2 meses', 'Requisitos: cumplir parte de condena, no tener sanciones, buena conducta.', true),
('00000000-0000-0000-0000-000000000104', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Apelaciones y Recursos Penales',
 'Recursos de apelación, nulidad y amparo en materia penal. Incluye: análisis de sentencia, fundamentación del recurso, audiencia ante Corte de Apelaciones.',
 700000, '2-4 meses', 'Requiere sentencia dictada. Plazos legales estrictos.', true),
('00000000-0000-0000-0000-000000000105', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010',
 'Calumnias e Injurias',
 'Querella o defensa en casos de calumnias e injurias. Común en contextos de VIF o conflictos laborales/familiares.',
 500000, '3-5 meses', 'Requiere presentar pruebas del daño o defensa de la acusación.', true),
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
 350000, '2-4 meses', 'Busca establecer relación estable entre padre/madre e hijo.', true),
('00000000-0000-0000-0000-000000000110', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000012',
 'Cobranza Judicial',
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
