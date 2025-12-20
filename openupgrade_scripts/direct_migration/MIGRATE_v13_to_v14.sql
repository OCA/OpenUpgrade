-- =============================================================================
-- MIGRATION v13 → v14
-- =============================================================================
-- Première étape de migration - changements majeurs v14
-- Peut être exécuté séparément ou comme partie de la migration directe v13→v19
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'MIGRATION v13 → v14';
    RAISE NOTICE 'Début: %', NOW();
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
END $$;

-- Table de log
CREATE TABLE IF NOT EXISTS migration_log (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10),
    step VARCHAR(100),
    operation VARCHAR(255),
    affected_rows INTEGER,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 1. ACCOUNT_MOVE: Renommages principaux                                    ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 1. ACCOUNT_MOVE ━━━';

    -- type → move_type
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'type')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'move_type') THEN
        ALTER TABLE account_move RENAME COLUMN type TO move_type;
        RAISE NOTICE '  ✓ type → move_type';
        INSERT INTO migration_log (version, step, operation, status)
        VALUES ('v14', 'account_move', 'type → move_type', 'SUCCESS');
    END IF;

    -- invoice_payment_state → payment_state
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_payment_state') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_payment_state TO payment_state;
        RAISE NOTICE '  ✓ invoice_payment_state → payment_state';
    END IF;

    -- invoice_partner_bank_id → partner_bank_id
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_partner_bank_id') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_partner_bank_id TO partner_bank_id;
        RAISE NOTICE '  ✓ invoice_partner_bank_id → partner_bank_id';
    END IF;

    -- invoice_payment_ref → payment_reference
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_payment_ref') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_payment_ref TO payment_reference;
        RAISE NOTICE '  ✓ invoice_payment_ref → payment_reference';
    END IF;

    -- invoice_sent → is_move_sent
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'invoice_sent') THEN
        ALTER TABLE account_move RENAME COLUMN invoice_sent TO is_move_sent;
        RAISE NOTICE '  ✓ invoice_sent → is_move_sent';
    END IF;

    -- Nouvelles colonnes
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'posted_before') THEN
        ALTER TABLE account_move ADD COLUMN posted_before BOOLEAN DEFAULT FALSE;
        UPDATE account_move SET posted_before = TRUE WHERE state = 'posted';
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ posted_before ajouté (% initialisés)', v_count;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'sequence_number') THEN
        ALTER TABLE account_move ADD COLUMN sequence_number INTEGER;
        ALTER TABLE account_move ADD COLUMN sequence_prefix VARCHAR;
        ALTER TABLE account_move ADD COLUMN made_sequence_gap BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ sequence_number, sequence_prefix, made_sequence_gap ajoutés';
    END IF;

    -- to_check → checked (logique inversée)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'to_check') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'account_move' AND column_name = 'checked') THEN
            ALTER TABLE account_move ADD COLUMN checked BOOLEAN DEFAULT TRUE;
            UPDATE account_move SET checked = NOT COALESCE(to_check, FALSE);
        END IF;
        ALTER TABLE account_move DROP COLUMN to_check;
        RAISE NOTICE '  ✓ to_check → checked (inversé)';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 2. ACCOUNT_MOVE_LINE: Nouveaux champs computed stored                     ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 2. ACCOUNT_MOVE_LINE ━━━';

    -- matching_number
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'matching_number') THEN
        ALTER TABLE account_move_line ADD COLUMN matching_number VARCHAR;
        RAISE NOTICE '  ✓ matching_number ajouté';
    END IF;

    -- parent_state (computed stored)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'parent_state') THEN
        ALTER TABLE account_move_line ADD COLUMN parent_state VARCHAR;
        UPDATE account_move_line aml SET parent_state = am.state
        FROM account_move am WHERE aml.move_id = am.id;
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ parent_state ajouté et initialisé: %', v_count;
    END IF;

    -- move_name (computed stored)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'move_name') THEN
        ALTER TABLE account_move_line ADD COLUMN move_name VARCHAR;
        UPDATE account_move_line aml SET move_name = am.name
        FROM account_move am WHERE aml.move_id = am.id;
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ move_name ajouté et initialisé: %', v_count;
    END IF;

    -- Renommer tag_ids → tax_tag_ids (table de relation)
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'account_move_line_account_tag_rel')
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'account_move_line_account_tax_tag_rel') THEN
        ALTER TABLE account_move_line_account_tag_rel
        RENAME TO account_move_line_account_tax_tag_rel;
        RAISE NOTICE '  ✓ tag_ids → tax_tag_ids (relation)';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 3. ACCOUNT_PAYMENT: move_id obligatoire                                   ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 3. ACCOUNT_PAYMENT ━━━';

    -- move_id (obligatoire en v14+)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'move_id') THEN
        ALTER TABLE account_payment ADD COLUMN move_id INTEGER;
        RAISE NOTICE '  ✓ move_id ajouté';
    END IF;

    -- Tenter de lier paiements aux moves
    UPDATE account_payment ap
    SET move_id = am.id
    FROM account_move am
    WHERE ap.move_id IS NULL
    AND am.name = ap.name
    AND am.company_id = ap.company_id;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ Liés via name: %', v_count;
    END IF;

    -- is_internal_transfer
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'is_internal_transfer') THEN
        ALTER TABLE account_payment ADD COLUMN is_internal_transfer BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ is_internal_transfer ajouté';
    END IF;

    -- is_matched
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'is_matched') THEN
        ALTER TABLE account_payment ADD COLUMN is_matched BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ is_matched ajouté';
    END IF;

    -- is_reconciled
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_payment' AND column_name = 'is_reconciled') THEN
        ALTER TABLE account_payment ADD COLUMN is_reconciled BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ is_reconciled ajouté';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 4. ACCOUNT_BANK_STATEMENT_LINE: move_id obligatoire                       ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 4. ACCOUNT_BANK_STATEMENT_LINE ━━━';

    -- name → payment_ref
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_bank_statement_line' AND column_name = 'name')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_bank_statement_line' AND column_name = 'payment_ref') THEN
        ALTER TABLE account_bank_statement_line RENAME COLUMN name TO payment_ref;
        RAISE NOTICE '  ✓ name → payment_ref';
    END IF;

    -- move_id (obligatoire en v14+)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_bank_statement_line' AND column_name = 'move_id') THEN
        ALTER TABLE account_bank_statement_line ADD COLUMN move_id INTEGER;
        RAISE NOTICE '  ✓ move_id ajouté';
    END IF;

    -- Tenter de lier via account_move_line.statement_line_id
    UPDATE account_bank_statement_line bsl
    SET move_id = aml.move_id
    FROM account_move_line aml
    WHERE aml.statement_line_id = bsl.id
    AND bsl.move_id IS NULL;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ Liés via AML: %', v_count;
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 5. ACCOUNT_JOURNAL: Fusion default_debit/credit_account_id                ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 5. ACCOUNT_JOURNAL ━━━';

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_journal' AND column_name = 'default_credit_account_id') THEN

        -- Créer default_account_id si n'existe pas
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'account_journal' AND column_name = 'default_account_id') THEN
            ALTER TABLE account_journal ADD COLUMN default_account_id INTEGER;
            UPDATE account_journal SET default_account_id =
                COALESCE(default_debit_account_id, default_credit_account_id);
            RAISE NOTICE '  ✓ default_account_id créé';
        END IF;

        -- Supprimer les anciens
        ALTER TABLE account_journal DROP COLUMN IF EXISTS default_credit_account_id;
        ALTER TABLE account_journal DROP COLUMN IF EXISTS default_debit_account_id;
        RAISE NOTICE '  ✓ default_credit/debit_account_id supprimés';
    END IF;

    -- refund_sequence_id supprimé
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_journal' AND column_name = 'refund_sequence_id') THEN
        ALTER TABLE account_journal DROP COLUMN refund_sequence_id;
        RAISE NOTICE '  ✓ refund_sequence_id supprimé';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 6. RES_COMPANY: Renommages                                                ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 6. RES_COMPANY ━━━';

    -- accrual_default_journal_id → automatic_entry_default_journal_id
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'res_company' AND column_name = 'accrual_default_journal_id') THEN
        ALTER TABLE res_company RENAME COLUMN accrual_default_journal_id TO automatic_entry_default_journal_id;
        RAISE NOTICE '  ✓ accrual_default_journal_id → automatic_entry_default_journal_id';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ VALIDATION                                                                 ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_errors INTEGER := 0;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ VALIDATION v14 ━━━';

    -- move_type existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'move_type') THEN
        RAISE NOTICE '  ✗ account_move.move_type manquant';
        v_errors := v_errors + 1;
    ELSE
        RAISE NOTICE '  ✓ account_move.move_type';
    END IF;

    -- payment_state existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'payment_state') THEN
        RAISE NOTICE '  ✗ account_move.payment_state manquant';
        v_errors := v_errors + 1;
    ELSE
        RAISE NOTICE '  ✓ account_move.payment_state';
    END IF;

    -- posted_before existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'posted_before') THEN
        RAISE NOTICE '  ✗ account_move.posted_before manquant';
        v_errors := v_errors + 1;
    ELSE
        RAISE NOTICE '  ✓ account_move.posted_before';
    END IF;

    RAISE NOTICE '';
    IF v_errors = 0 THEN
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        RAISE NOTICE '✓ MIGRATION v13 → v14 TERMINÉE';
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        INSERT INTO migration_log (version, step, operation, status)
        VALUES ('v14', 'COMPLETE', 'Migration v13→v14 successful', 'SUCCESS');
    ELSE
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        RAISE NOTICE '✗ MIGRATION v14 AVEC % ERREUR(S)', v_errors;
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        INSERT INTO migration_log (version, step, operation, status)
        VALUES ('v14', 'COMPLETE', 'Migration v13→v14 with errors', 'WARNING');
    END IF;

END $$;
