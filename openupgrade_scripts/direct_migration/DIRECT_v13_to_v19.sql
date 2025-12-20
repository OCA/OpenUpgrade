-- =============================================================================
-- MIGRATION DIRECTE v13 → v19 (Skip Intermédiaires)
-- =============================================================================
-- Basé sur l'analyse des scripts OpenUpgrade v14, v15, v16, v17, v18
--
-- Ce script applique TOUTES les transformations cumulatives en une seule passe.
-- Évite les 6 migrations intermédiaires et leurs problèmes potentiels.
--
-- Sources: https://github.com/OCA/OpenUpgrade
-- Généré: 2025-12-19
-- =============================================================================

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 0: PRÉPARATION                                                      ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'MIGRATION DIRECTE: Odoo v13 → v19';
    RAISE NOTICE 'Début: %', NOW();
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
END $$;

-- Table de log pour tracer les opérations
CREATE TABLE IF NOT EXISTS migration_direct_log (
    id SERIAL PRIMARY KEY,
    step VARCHAR(100),
    operation VARCHAR(255),
    affected_rows INTEGER,
    status VARCHAR(20),
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 1: RENOMMAGES DE COLONNES (Cumulatif v13→v19)                       ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 1: RENOMMAGES DE COLONNES                                    │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_move: v13→v14 renames
    -- ═══════════════════════════════════════════════════════════════════════

    -- type → move_type (v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'type') THEN
        ALTER TABLE account_move RENAME COLUMN type TO move_type;
        RAISE NOTICE '  ✓ account_move: type → move_type';
    END IF;

    -- invoice_payment_state → payment_state (v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_payment_state') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_payment_state TO payment_state;
        RAISE NOTICE '  ✓ account_move: invoice_payment_state → payment_state';
    END IF;

    -- invoice_partner_bank_id → partner_bank_id (v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_partner_bank_id') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_partner_bank_id TO partner_bank_id;
        RAISE NOTICE '  ✓ account_move: invoice_partner_bank_id → partner_bank_id';
    END IF;

    -- invoice_payment_ref → payment_reference (v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_payment_ref') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_payment_ref TO payment_reference;
        RAISE NOTICE '  ✓ account_move: invoice_payment_ref → payment_reference';
    END IF;

    -- invoice_sent → is_move_sent (v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_sent') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_sent TO is_move_sent;
        RAISE NOTICE '  ✓ account_move: invoice_sent → is_move_sent';
    END IF;

    -- payment_id → origin_payment_id (v18)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'payment_id')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'origin_payment_id') THEN
        ALTER TABLE account_move RENAME COLUMN payment_id TO origin_payment_id;
        RAISE NOTICE '  ✓ account_move: payment_id → origin_payment_id';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_move_line: v13→v14 renames
    -- ═══════════════════════════════════════════════════════════════════════

    -- tag_ids → tax_tag_ids (v14, relation table)
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'account_move_line_account_tax_tag_rel') THEN
        RAISE NOTICE '  ⊘ account_move_line: tag_ids relation déjà migrée';
    ELSIF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'account_move_line_account_tag_rel') THEN
        ALTER TABLE account_move_line_account_tag_rel
        RENAME TO account_move_line_account_tax_tag_rel;
        RAISE NOTICE '  ✓ account_move_line: tag_ids → tax_tag_ids (relation)';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_bank_statement_line: v13→v14 renames
    -- ═══════════════════════════════════════════════════════════════════════

    -- name → payment_ref (v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_bank_statement_line' AND column_name = 'name')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_bank_statement_line' AND column_name = 'payment_ref') THEN
        ALTER TABLE account_bank_statement_line RENAME COLUMN name TO payment_ref;
        RAISE NOTICE '  ✓ account_bank_statement_line: name → payment_ref';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_tax: v16→v17 renames
    -- ═══════════════════════════════════════════════════════════════════════

    -- description → invoice_label (v17)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_tax' AND column_name = 'description')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_tax' AND column_name = 'invoice_label') THEN
        ALTER TABLE account_tax RENAME COLUMN description TO invoice_label;
        RAISE NOTICE '  ✓ account_tax: description → invoice_label';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- res_company: v13→v14 renames
    -- ═══════════════════════════════════════════════════════════════════════

    -- accrual_default_journal_id → automatic_entry_default_journal_id (v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'res_company' AND column_name = 'accrual_default_journal_id') THEN
        ALTER TABLE res_company RENAME COLUMN accrual_default_journal_id TO automatic_entry_default_journal_id;
        RAISE NOTICE '  ✓ res_company: accrual_default_journal_id → automatic_entry_default_journal_id';
    END IF;

    -- invoice_is_print → invoice_is_download (v17)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'res_company' AND column_name = 'invoice_is_print') THEN
        ALTER TABLE res_company RENAME COLUMN invoice_is_print TO invoice_is_download;
        RAISE NOTICE '  ✓ res_company: invoice_is_print → invoice_is_download';
    END IF;

    INSERT INTO migration_direct_log (step, operation, status)
    VALUES ('PHASE_1', 'Column renames completed', 'SUCCESS');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 2: NOUVELLES COLONNES v19                                           ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 2: NOUVELLES COLONNES v19                                    │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_move: Colonnes v14→v19
    -- ═══════════════════════════════════════════════════════════════════════

    -- posted_before (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'posted_before') THEN
        ALTER TABLE account_move ADD COLUMN posted_before BOOLEAN DEFAULT FALSE;
        UPDATE account_move SET posted_before = TRUE WHERE state = 'posted';
        RAISE NOTICE '  ✓ account_move.posted_before (initialisé depuis state)';
    END IF;

    -- sequence_number (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'sequence_number') THEN
        ALTER TABLE account_move ADD COLUMN sequence_number INTEGER;
        RAISE NOTICE '  ✓ account_move.sequence_number';
    END IF;

    -- sequence_prefix (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'sequence_prefix') THEN
        ALTER TABLE account_move ADD COLUMN sequence_prefix VARCHAR;
        RAISE NOTICE '  ✓ account_move.sequence_prefix';
    END IF;

    -- made_sequence_gap (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'made_sequence_gap') THEN
        ALTER TABLE account_move ADD COLUMN made_sequence_gap BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ account_move.made_sequence_gap';
    END IF;

    -- delivery_date (v17)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'delivery_date') THEN
        ALTER TABLE account_move ADD COLUMN delivery_date DATE;
        RAISE NOTICE '  ✓ account_move.delivery_date';
    END IF;

    -- invoice_currency_rate (v18)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'invoice_currency_rate') THEN
        ALTER TABLE account_move ADD COLUMN invoice_currency_rate NUMERIC DEFAULT 1.0;
        RAISE NOTICE '  ✓ account_move.invoice_currency_rate';
    END IF;

    -- sending_data (v18, ex send_and_print_values)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'sending_data') THEN
        ALTER TABLE account_move ADD COLUMN sending_data JSONB;
        RAISE NOTICE '  ✓ account_move.sending_data';
    END IF;

    -- amount_total_in_currency_signed (v19)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'amount_total_in_currency_signed') THEN
        ALTER TABLE account_move ADD COLUMN amount_total_in_currency_signed NUMERIC;
        UPDATE account_move SET amount_total_in_currency_signed = amount_total_signed;
        RAISE NOTICE '  ✓ account_move.amount_total_in_currency_signed';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_move_line: Colonnes v14→v19
    -- ═══════════════════════════════════════════════════════════════════════

    -- matching_number (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'matching_number') THEN
        ALTER TABLE account_move_line ADD COLUMN matching_number VARCHAR;
        RAISE NOTICE '  ✓ account_move_line.matching_number';
    END IF;

    -- is_storno (v16)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'is_storno') THEN
        ALTER TABLE account_move_line ADD COLUMN is_storno BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ account_move_line.is_storno';
    END IF;

    -- is_imported (v18)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'is_imported') THEN
        ALTER TABLE account_move_line ADD COLUMN is_imported BOOLEAN DEFAULT FALSE;
        UPDATE account_move_line SET is_imported = TRUE;  -- Marquer comme importé
        RAISE NOTICE '  ✓ account_move_line.is_imported (marqué TRUE)';
    END IF;

    -- invoice_date (v17)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'invoice_date') THEN
        ALTER TABLE account_move_line ADD COLUMN invoice_date DATE;
        UPDATE account_move_line aml SET invoice_date = am.invoice_date
        FROM account_move am WHERE aml.move_id = am.id;
        RAISE NOTICE '  ✓ account_move_line.invoice_date (copié depuis move)';
    END IF;

    -- discount_date, discount_balance, discount_amount_currency (v18)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'discount_date') THEN
        ALTER TABLE account_move_line ADD COLUMN discount_date DATE;
        ALTER TABLE account_move_line ADD COLUMN discount_balance NUMERIC DEFAULT 0;
        ALTER TABLE account_move_line ADD COLUMN discount_amount_currency NUMERIC DEFAULT 0;
        RAISE NOTICE '  ✓ account_move_line.discount_* columns';
    END IF;

    -- is_downpayment (v19)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'is_downpayment') THEN
        ALTER TABLE account_move_line ADD COLUMN is_downpayment BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ account_move_line.is_downpayment';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_payment: Colonnes v14→v19
    -- ═══════════════════════════════════════════════════════════════════════

    -- is_internal_transfer (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'is_internal_transfer') THEN
        ALTER TABLE account_payment ADD COLUMN is_internal_transfer BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ account_payment.is_internal_transfer';
    END IF;

    -- is_matched (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'is_matched') THEN
        ALTER TABLE account_payment ADD COLUMN is_matched BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ account_payment.is_matched';
    END IF;

    -- is_reconciled (v14)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'is_reconciled') THEN
        ALTER TABLE account_payment ADD COLUMN is_reconciled BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ account_payment.is_reconciled';
    END IF;

    INSERT INTO migration_direct_log (step, operation, status)
    VALUES ('PHASE_2', 'New columns added', 'SUCCESS');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 3: CONVERSION TYPES (auto_post, account_type, JSONB)                ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 3: CONVERSION DE TYPES                                       │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- ═══════════════════════════════════════════════════════════════════════
    -- auto_post: BOOLEAN → VARCHAR (v16)
    -- ═══════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'auto_post'
               AND data_type = 'boolean') THEN
        ALTER TABLE account_move ADD COLUMN auto_post_new VARCHAR;
        UPDATE account_move SET auto_post_new = CASE
            WHEN auto_post = TRUE THEN 'at_date'
            ELSE 'no'
        END;
        ALTER TABLE account_move DROP COLUMN auto_post;
        ALTER TABLE account_move RENAME COLUMN auto_post_new TO auto_post;
        RAISE NOTICE '  ✓ account_move.auto_post: BOOLEAN → VARCHAR';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_type mapping (v16)
    -- account.account.type → account_account.account_type
    -- ═══════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_account' AND column_name = 'user_type_id') THEN
        -- Créer colonne account_type si elle n'existe pas
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'account_account' AND column_name = 'account_type') THEN
            ALTER TABLE account_account ADD COLUMN account_type VARCHAR;
        END IF;

        -- Mapper les types (basé sur xml_id des account.account.type)
        UPDATE account_account aa SET account_type =
            CASE
                WHEN aat.type = 'receivable' THEN 'asset_receivable'
                WHEN aat.type = 'payable' THEN 'liability_payable'
                WHEN aat.type = 'liquidity' THEN 'asset_cash'
                WHEN aat.type = 'other' AND aat.internal_group = 'asset' THEN 'asset_current'
                WHEN aat.type = 'other' AND aat.internal_group = 'liability' THEN 'liability_current'
                WHEN aat.type = 'other' AND aat.internal_group = 'equity' THEN 'equity'
                WHEN aat.type = 'other' AND aat.internal_group = 'income' THEN 'income'
                WHEN aat.type = 'other' AND aat.internal_group = 'expense' THEN 'expense'
                ELSE 'asset_current'
            END
        FROM account_account_type aat
        WHERE aa.user_type_id = aat.id AND aa.account_type IS NULL;

        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ account_account.account_type mappé: % comptes', v_count;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- JSONB translations (v16+)
    -- Les champs traduits passent de VARCHAR à JSONB
    -- ═══════════════════════════════════════════════════════════════════════

    -- Note: En Odoo v19, les champs suivants sont JSONB pour les traductions:
    -- - account_account.name
    -- - account_journal.name
    -- - product_template.name
    -- - account_tax.name
    --
    -- MAIS res_partner.name reste VARCHAR (ce n'est pas un champ traduisible)

    -- account_account.name VARCHAR → JSONB
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_account' AND column_name = 'name'
               AND data_type = 'character varying') THEN
        ALTER TABLE account_account ADD COLUMN name_jsonb JSONB;
        UPDATE account_account SET name_jsonb = jsonb_build_object('en_US', name, 'fr_FR', name);
        ALTER TABLE account_account DROP COLUMN name;
        ALTER TABLE account_account RENAME COLUMN name_jsonb TO name;
        RAISE NOTICE '  ✓ account_account.name: VARCHAR → JSONB';
    END IF;

    -- account_journal.name VARCHAR → JSONB
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_journal' AND column_name = 'name'
               AND data_type = 'character varying') THEN
        ALTER TABLE account_journal ADD COLUMN name_jsonb JSONB;
        UPDATE account_journal SET name_jsonb = jsonb_build_object('en_US', name, 'fr_FR', name);
        ALTER TABLE account_journal DROP COLUMN name;
        ALTER TABLE account_journal RENAME COLUMN name_jsonb TO name;
        RAISE NOTICE '  ✓ account_journal.name: VARCHAR → JSONB';
    END IF;

    -- account_tax.name VARCHAR → JSONB
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_tax' AND column_name = 'name'
               AND data_type = 'character varying') THEN
        ALTER TABLE account_tax ADD COLUMN name_jsonb JSONB;
        UPDATE account_tax SET name_jsonb = jsonb_build_object('en_US', name, 'fr_FR', name);
        ALTER TABLE account_tax DROP COLUMN name;
        ALTER TABLE account_tax RENAME COLUMN name_jsonb TO name;
        RAISE NOTICE '  ✓ account_tax.name: VARCHAR → JSONB';
    END IF;

    INSERT INTO migration_direct_log (step, operation, status)
    VALUES ('PHASE_3', 'Type conversions completed', 'SUCCESS');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 4: RELATIONS ET FK CRITIQUES                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 4: RELATIONS ET FK CRITIQUES                                 │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_bank_statement_line.move_id (v14: obligatoire)
    -- ═══════════════════════════════════════════════════════════════════════

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_bank_statement_line' AND column_name = 'move_id') THEN
        ALTER TABLE account_bank_statement_line ADD COLUMN move_id INTEGER;
        RAISE NOTICE '  ✓ account_bank_statement_line.move_id ajouté';

        -- Note: Le mapping move_name → move_id doit être fait séparément
        -- car il nécessite une jointure avec account_move
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_payment.move_id (v14: obligatoire)
    -- ═══════════════════════════════════════════════════════════════════════

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'move_id') THEN
        ALTER TABLE account_payment ADD COLUMN move_id INTEGER;
        RAISE NOTICE '  ✓ account_payment.move_id ajouté';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_move_line: champs computed stockés
    -- ═══════════════════════════════════════════════════════════════════════

    -- parent_state (stocké en v14+)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'parent_state') THEN
        ALTER TABLE account_move_line ADD COLUMN parent_state VARCHAR;
        UPDATE account_move_line aml SET parent_state = am.state
        FROM account_move am WHERE aml.move_id = am.id;
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ account_move_line.parent_state: % lignes', v_count;
    END IF;

    -- move_name (stocké en v14+)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'move_name') THEN
        ALTER TABLE account_move_line ADD COLUMN move_name VARCHAR;
        UPDATE account_move_line aml SET move_name = am.name
        FROM account_move am WHERE aml.move_id = am.id;
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ account_move_line.move_name: % lignes', v_count;
    END IF;

    INSERT INTO migration_direct_log (step, operation, status)
    VALUES ('PHASE_4', 'Relations and FK completed', 'SUCCESS');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 5: NETTOYAGE COLONNES OBSOLÈTES                                     ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 5: NETTOYAGE COLONNES OBSOLÈTES                              │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_journal: colonnes supprimées en v14
    -- ═══════════════════════════════════════════════════════════════════════

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_journal' AND column_name = 'default_credit_account_id') THEN
        -- Sauvegarder dans default_account_id si nécessaire
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'account_journal' AND column_name = 'default_account_id') THEN
            ALTER TABLE account_journal ADD COLUMN default_account_id INTEGER;
            UPDATE account_journal SET default_account_id = COALESCE(default_debit_account_id, default_credit_account_id);
        END IF;

        ALTER TABLE account_journal DROP COLUMN IF EXISTS default_credit_account_id;
        ALTER TABLE account_journal DROP COLUMN IF EXISTS default_debit_account_id;
        RAISE NOTICE '  ✓ account_journal: supprimé default_credit/debit_account_id';
    END IF;

    -- refund_sequence_id (supprimé v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_journal' AND column_name = 'refund_sequence_id') THEN
        ALTER TABLE account_journal DROP COLUMN refund_sequence_id;
        RAISE NOTICE '  ✓ account_journal: supprimé refund_sequence_id';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_move: colonnes obsolètes
    -- ═══════════════════════════════════════════════════════════════════════

    -- to_check (remplacé par checked en v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'to_check') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'account_move' AND column_name = 'checked') THEN
            ALTER TABLE account_move ADD COLUMN checked BOOLEAN DEFAULT TRUE;
            UPDATE account_move SET checked = NOT COALESCE(to_check, FALSE);
        END IF;
        ALTER TABLE account_move DROP COLUMN to_check;
        RAISE NOTICE '  ✓ account_move: to_check → checked (inverted)';
    END IF;

    INSERT INTO migration_direct_log (step, operation, status)
    VALUES ('PHASE_5', 'Obsolete columns cleaned', 'SUCCESS');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 5B: MIGRATION ATTACHMENTS (res_model renommés v13→v19)              ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 5B: MIGRATION ATTACHMENTS                                    │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- ═══════════════════════════════════════════════════════════════════════
    -- Renommer res_model pour les modèles renommés entre v13 et v19
    -- ═══════════════════════════════════════════════════════════════════════

    -- mail.channel → discuss.channel (v16)
    UPDATE ir_attachment SET res_model = 'discuss.channel'
    WHERE res_model = 'mail.channel';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ mail.channel → discuss.channel: % attachments', v_count;
    END IF;

    -- payment.acquirer → payment.provider (v16)
    UPDATE ir_attachment SET res_model = 'payment.provider'
    WHERE res_model = 'payment.acquirer';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ payment.acquirer → payment.provider: % attachments', v_count;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- hr.expense.sheet → hr.expense (les sheets n'existent plus en v19)
    -- Mapper vers la première expense du sheet
    -- ═══════════════════════════════════════════════════════════════════════

    -- Cette migration nécessite la table hr_expense avec sheet_id
    -- À exécuter sur la base source avant migration:
    --
    -- UPDATE ir_attachment a
    -- SET res_model = 'hr.expense',
    --     res_id = (SELECT MIN(he.id) FROM hr_expense he WHERE he.sheet_id = a.res_id)
    -- WHERE a.res_model = 'hr.expense.sheet'
    -- AND EXISTS (SELECT 1 FROM hr_expense he WHERE he.sheet_id = a.res_id);

    -- ═══════════════════════════════════════════════════════════════════════
    -- Nettoyer les attachments orphelins (res_model existe mais table non)
    -- ═══════════════════════════════════════════════════════════════════════

    -- Modèles v13 qui n'existent plus en v19 (modules non installés)
    -- fleet.vehicle, fleet.vehicle.model.brand, etc. → garder mais marquer

    -- Vérifier les attachments sans res_model valide
    SELECT COUNT(*) INTO v_count
    FROM ir_attachment a
    WHERE a.res_model IS NOT NULL
    AND a.res_id IS NOT NULL
    AND a.res_id > 0
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.tables t
        WHERE t.table_name = REPLACE(a.res_model, '.', '_')
    );

    IF v_count > 0 THEN
        RAISE NOTICE '  ⚠ % attachments liés à des modèles non installés', v_count;
    END IF;

    INSERT INTO migration_direct_log (step, operation, affected_rows, status)
    VALUES ('PHASE_5B', 'Attachments res_model migration', v_count, 'SUCCESS');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 6: SYNCHRONISATION SÉQUENCES                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    r RECORD;
    v_max_id BIGINT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 6: SYNCHRONISATION SÉQUENCES                                 │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- Synchroniser toutes les séquences des tables principales
    FOR r IN
        SELECT c.relname AS table_name,
               a.attname AS pk_column,
               pg_get_serial_sequence(c.relname::text, a.attname::text) AS seq_name
        FROM pg_class c
        JOIN pg_attribute a ON a.attrelid = c.oid
        JOIN pg_index i ON i.indrelid = c.oid AND a.attnum = ANY(i.indkey)
        WHERE c.relkind = 'r'
        AND c.relname IN (
            'account_move', 'account_move_line', 'account_payment',
            'account_bank_statement', 'account_bank_statement_line',
            'account_partial_reconcile', 'account_full_reconcile',
            'res_partner', 'ir_attachment', 'mail_message', 'mail_followers'
        )
        AND i.indisprimary
        AND pg_get_serial_sequence(c.relname::text, a.attname::text) IS NOT NULL
    LOOP
        EXECUTE format('SELECT COALESCE(MAX(%I), 0) FROM %I', r.pk_column, r.table_name) INTO v_max_id;
        IF v_max_id > 0 THEN
            EXECUTE format('SELECT setval(%L, %s)', r.seq_name, v_max_id + 1);
            RAISE NOTICE '  ✓ %: séquence → %', r.table_name, v_max_id + 1;
        END IF;
    END LOOP;

    INSERT INTO migration_direct_log (step, operation, status)
    VALUES ('PHASE_6', 'Sequences synchronized', 'SUCCESS');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 7: VALIDATION FINALE                                                ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_errors INTEGER := 0;
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '┌─────────────────────────────────────────────────────────────────────┐';
    RAISE NOTICE '│ PHASE 7: VALIDATION FINALE                                         │';
    RAISE NOTICE '└─────────────────────────────────────────────────────────────────────┘';

    -- Vérifier les colonnes obligatoires
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'move_type') THEN
        RAISE NOTICE '  ✗ ERREUR: account_move.move_type manquant';
        v_errors := v_errors + 1;
    ELSE
        RAISE NOTICE '  ✓ account_move.move_type présent';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'payment_state') THEN
        RAISE NOTICE '  ✗ ERREUR: account_move.payment_state manquant';
        v_errors := v_errors + 1;
    ELSE
        RAISE NOTICE '  ✓ account_move.payment_state présent';
    END IF;

    -- Vérifier balance comptable
    SELECT COUNT(*) INTO v_count
    FROM (
        SELECT move_id, SUM(debit) as d, SUM(credit) as c
        FROM account_move_line
        GROUP BY move_id
        HAVING ABS(SUM(debit) - SUM(credit)) > 0.01
    ) x;

    IF v_count > 0 THEN
        RAISE NOTICE '  ✗ ERREUR: % écritures déséquilibrées', v_count;
        v_errors := v_errors + 1;
    ELSE
        RAISE NOTICE '  ✓ Balance comptable OK';
    END IF;

    -- Résumé
    RAISE NOTICE '';
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    IF v_errors = 0 THEN
        RAISE NOTICE 'MIGRATION DIRECTE v13 → v19 TERMINÉE AVEC SUCCÈS';
        INSERT INTO migration_direct_log (step, operation, status)
        VALUES ('COMPLETE', 'Migration successful', 'SUCCESS');
    ELSE
        RAISE NOTICE 'MIGRATION TERMINÉE AVEC % ERREUR(S)', v_errors;
        INSERT INTO migration_direct_log (step, operation, status, details)
        VALUES ('COMPLETE', 'Migration with errors', 'WARNING', v_errors || ' errors found');
    END IF;
    RAISE NOTICE 'Fin: %', NOW();
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';

END $$;

-- Afficher le résumé des opérations
SELECT step, operation, status, created_at FROM migration_direct_log ORDER BY id;
