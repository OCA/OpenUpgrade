-- =============================================================================
-- MIGRATION FLEET v13 → v19 (Sans module, tables manuelles)
-- =============================================================================
-- Ce script crée les tables fleet minimales et migre les données v13
-- Utilisé quand le module fleet ne peut pas être installé normalement
--
-- Tables créées:
--   - fleet_vehicle_model_brand (marques)
--   - fleet_vehicle_model (modèles)
--   - fleet_vehicle_state (états)
--   - fleet_vehicle (véhicules)
--   - fleet_vehicle_odometer (compteurs)
--   - fleet_vehicle_log_services (services)
-- =============================================================================

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 1: CRÉATION DES TABLES                                              ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- Table: fleet_vehicle_model_brand (marques de véhicules)
CREATE TABLE IF NOT EXISTS fleet_vehicle_model_brand (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    image_128 BYTEA,
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- Table: fleet_vehicle_state (états des véhicules)
CREATE TABLE IF NOT EXISTS fleet_vehicle_state (
    id SERIAL PRIMARY KEY,
    name JSONB NOT NULL,  -- v19 utilise JSONB pour les traductions
    sequence INTEGER DEFAULT 10,
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- Table: fleet_vehicle_model (modèles de véhicules)
CREATE TABLE IF NOT EXISTS fleet_vehicle_model (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    brand_id INTEGER REFERENCES fleet_vehicle_model_brand(id),
    manager_id INTEGER REFERENCES res_users(id),
    vehicle_type VARCHAR DEFAULT 'car',
    transmission VARCHAR,
    category_id INTEGER,
    image_128 BYTEA,
    horsepower INTEGER,
    horsepower_tax NUMERIC,
    power INTEGER,
    co2 NUMERIC,
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- Table: fleet_vehicle (véhicules)
CREATE TABLE IF NOT EXISTS fleet_vehicle (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    company_id INTEGER REFERENCES res_company(id),
    currency_id INTEGER REFERENCES res_currency(id),
    license_plate VARCHAR,
    vin_sn VARCHAR,
    driver_id INTEGER REFERENCES res_partner(id),
    future_driver_id INTEGER REFERENCES res_partner(id),
    model_id INTEGER NOT NULL REFERENCES fleet_vehicle_model(id),
    brand_id INTEGER REFERENCES fleet_vehicle_model_brand(id),
    state_id INTEGER REFERENCES fleet_vehicle_state(id),
    location VARCHAR,
    seats INTEGER,
    model_year VARCHAR,
    doors INTEGER,
    color VARCHAR,
    odometer NUMERIC DEFAULT 0,
    odometer_unit VARCHAR DEFAULT 'kilometers',
    acquisition_date DATE,
    first_contract_date DATE,
    car_value NUMERIC,
    net_car_value NUMERIC,
    residual_value NUMERIC,
    transmission VARCHAR,
    fuel_type VARCHAR,
    horsepower INTEGER,
    horsepower_tax NUMERIC,
    power INTEGER,
    co2 NUMERIC,
    plan_to_change_car BOOLEAN DEFAULT FALSE,
    plan_to_change_bike BOOLEAN DEFAULT FALSE,
    next_assignation_date DATE,
    message_main_attachment_id INTEGER,
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- Table: fleet_vehicle_odometer (relevés compteur)
CREATE TABLE IF NOT EXISTS fleet_vehicle_odometer (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    date DATE DEFAULT CURRENT_DATE,
    value NUMERIC NOT NULL,
    vehicle_id INTEGER NOT NULL REFERENCES fleet_vehicle(id) ON DELETE CASCADE,
    unit VARCHAR DEFAULT 'kilometers',
    driver_id INTEGER REFERENCES res_partner(id),
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- Table: fleet_vehicle_log_services (historique services)
CREATE TABLE IF NOT EXISTS fleet_vehicle_log_services (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    vehicle_id INTEGER NOT NULL REFERENCES fleet_vehicle(id) ON DELETE CASCADE,
    date DATE,
    amount NUMERIC DEFAULT 0,
    description TEXT,
    odometer_id INTEGER REFERENCES fleet_vehicle_odometer(id),
    vendor_id INTEGER REFERENCES res_partner(id),
    notes TEXT,
    service_type_id INTEGER,
    state VARCHAR DEFAULT 'new',
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- Table: fleet_vehicle_log_fuel (historique carburant)
CREATE TABLE IF NOT EXISTS fleet_vehicle_log_fuel (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES fleet_vehicle(id) ON DELETE CASCADE,
    date DATE,
    liter NUMERIC,
    price_per_liter NUMERIC,
    amount NUMERIC,
    odometer_id INTEGER REFERENCES fleet_vehicle_odometer(id),
    vendor_id INTEGER REFERENCES res_partner(id),
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 2: CRÉER LES INDEX                                                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

CREATE INDEX IF NOT EXISTS fleet_vehicle_model_brand_id_idx ON fleet_vehicle(brand_id);
CREATE INDEX IF NOT EXISTS fleet_vehicle_model_id_idx ON fleet_vehicle(model_id);
CREATE INDEX IF NOT EXISTS fleet_vehicle_driver_id_idx ON fleet_vehicle(driver_id);
CREATE INDEX IF NOT EXISTS fleet_vehicle_state_id_idx ON fleet_vehicle(state_id);
CREATE INDEX IF NOT EXISTS fleet_vehicle_odometer_vehicle_id_idx ON fleet_vehicle_odometer(vehicle_id);
CREATE INDEX IF NOT EXISTS fleet_vehicle_log_services_vehicle_id_idx ON fleet_vehicle_log_services(vehicle_id);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 3: ENREGISTRER LE "MODULE" DANS ir_module_module                    ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- Marquer le module fleet comme "installed" (manuel)
UPDATE ir_module_module
SET state = 'installed',
    latest_version = '19.0.1.0.0'
WHERE name = 'fleet';

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 4: CRÉER LES DROITS D'ACCÈS                                         ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- Ajouter les droits ir.model.access pour les tables fleet
-- (À compléter selon les groupes de sécurité existants)

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 5: RESTAURER LES ATTACHMENTS                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- Après import des données, restaurer res_model sur les attachments
-- Note: Le res_id doit être mappé depuis v13 avec +100000 offset
--
-- Exemple de requête pour restaurer (à adapter):
-- UPDATE ir_attachment a
-- SET res_model = 'fleet.vehicle',
--     res_id = (valeur depuis mapping v13)
-- WHERE a.id = v13_attachment_id + 100000;

DO $$
BEGIN
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'TABLES FLEET CRÉÉES - Prêt pour import des données';
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE 'Étapes suivantes:';
    RAISE NOTICE '1. Exporter les données de v13 (brands, models, vehicles, etc.)';
    RAISE NOTICE '2. Importer dans les tables créées ci-dessus';
    RAISE NOTICE '3. Restaurer les attachments avec le mapping res_id';
    RAISE NOTICE '4. Synchroniser les séquences';
END $$;
