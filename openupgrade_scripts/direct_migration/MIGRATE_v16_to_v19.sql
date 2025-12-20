-- =============================================================================
-- MIGRATION v16 → v19 (inclut v17, v18)
-- =============================================================================
-- Changements v17: description → invoice_label, delivery_date
-- Changements v18: payment_id → origin_payment_id, sending_data
-- Changements v19: amount_total_in_currency_signed, is_downpayment
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'MIGRATION v16 → v19 (via v17, v18)';
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 1. CHANGEMENTS v17                                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 1. CHANGEMENTS v17 ━━━';

    -- account_tax: description → invoice_label
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_tax' AND column_name = 'description')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_tax' AND column_name = 'invoice_label') THEN
        ALTER TABLE account_tax RENAME COLUMN description TO invoice_label;
        RAISE NOTICE '  ✓ account_tax: description → invoice_label';
    END IF;

    -- account_move: delivery_date
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'delivery_date') THEN
        ALTER TABLE account_move ADD COLUMN delivery_date DATE;
        RAISE NOTICE '  ✓ account_move.delivery_date ajouté';
    END IF;

    -- account_move_line: invoice_date (copie depuis move)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'invoice_date') THEN
        ALTER TABLE account_move_line ADD COLUMN invoice_date DATE;
        UPDATE account_move_line aml SET invoice_date = am.invoice_date
        FROM account_move am WHERE aml.move_id = am.id AND am.invoice_date IS NOT NULL;
        RAISE NOTICE '  ✓ account_move_line.invoice_date ajouté';
    END IF;

    -- res_company: invoice_is_print → invoice_is_download
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'res_company' AND column_name = 'invoice_is_print') THEN
        ALTER TABLE res_company RENAME COLUMN invoice_is_print TO invoice_is_download;
        RAISE NOTICE '  ✓ res_company: invoice_is_print → invoice_is_download';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 2. CHANGEMENTS v18                                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 2. CHANGEMENTS v18 ━━━';

    -- account_move: payment_id → origin_payment_id
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'payment_id')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'origin_payment_id') THEN
        ALTER TABLE account_move RENAME COLUMN payment_id TO origin_payment_id;
        RAISE NOTICE '  ✓ account_move: payment_id → origin_payment_id';
    END IF;

    -- account_move: invoice_currency_rate
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'invoice_currency_rate') THEN
        ALTER TABLE account_move ADD COLUMN invoice_currency_rate NUMERIC DEFAULT 1.0;
        RAISE NOTICE '  ✓ account_move.invoice_currency_rate ajouté';
    END IF;

    -- account_move: sending_data (JSONB, ex send_and_print_values)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'sending_data') THEN
        ALTER TABLE account_move ADD COLUMN sending_data JSONB;
        RAISE NOTICE '  ✓ account_move.sending_data ajouté';
    END IF;

    -- account_move_line: is_imported
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'is_imported') THEN
        ALTER TABLE account_move_line ADD COLUMN is_imported BOOLEAN DEFAULT FALSE;
        -- Marquer toutes les lignes migrées comme importées
        UPDATE account_move_line SET is_imported = TRUE;
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ account_move_line.is_imported: % lignes marquées', v_count;
    END IF;

    -- account_move_line: discount_date, discount_balance, discount_amount_currency
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'discount_date') THEN
        ALTER TABLE account_move_line ADD COLUMN discount_date DATE;
        ALTER TABLE account_move_line ADD COLUMN discount_balance NUMERIC DEFAULT 0;
        ALTER TABLE account_move_line ADD COLUMN discount_amount_currency NUMERIC DEFAULT 0;
        RAISE NOTICE '  ✓ account_move_line.discount_* ajoutés';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 3. CHANGEMENTS v19                                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 3. CHANGEMENTS v19 ━━━';

    -- account_move: amount_total_in_currency_signed
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move' AND column_name = 'amount_total_in_currency_signed') THEN
        ALTER TABLE account_move ADD COLUMN amount_total_in_currency_signed NUMERIC;
        UPDATE account_move SET amount_total_in_currency_signed = amount_total_signed;
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ account_move.amount_total_in_currency_signed: %', v_count;
    END IF;

    -- account_move_line: is_downpayment
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'is_downpayment') THEN
        ALTER TABLE account_move_line ADD COLUMN is_downpayment BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ account_move_line.is_downpayment ajouté';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 4. NETTOYAGE COLONNES OBSOLÈTES                                           ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 4. NETTOYAGE ━━━';

    -- Colonnes supprimées entre v16 et v19
    -- (Ajouter ici les colonnes à supprimer si nécessaire)

    RAISE NOTICE '  ✓ Nettoyage terminé';

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 5. HR_EXPENSE: Attachments hr.expense.sheet                               ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 5. HR_EXPENSE ATTACHMENTS ━━━';

    -- hr.expense.sheet n'existe plus en v19
    -- Remapper les attachments vers hr.expense si possible

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hr_expense') THEN
        -- Mettre à NULL les attachments hr.expense.sheet (le mapping doit être fait avant migration)
        SELECT COUNT(*) INTO v_count
        FROM ir_attachment WHERE res_model = 'hr.expense.sheet';

        IF v_count > 0 THEN
            RAISE NOTICE '  ⚠ % attachments hr.expense.sheet à remapper', v_count;
            RAISE NOTICE '    → Exécuter le script MIGRATE_ATTACHMENTS_v13_to_v19.sql';
        ELSE
            RAISE NOTICE '  ✓ Aucun attachment hr.expense.sheet orphelin';
        END IF;
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
    RAISE NOTICE '━━━ VALIDATION v19 ━━━';

    -- Colonnes v17
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'delivery_date') THEN
        RAISE NOTICE '  ✓ delivery_date';
    ELSE
        RAISE NOTICE '  ✗ delivery_date manquant';
        v_errors := v_errors + 1;
    END IF;

    -- Colonnes v18
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'sending_data') THEN
        RAISE NOTICE '  ✓ sending_data';
    ELSE
        RAISE NOTICE '  ✗ sending_data manquant';
        v_errors := v_errors + 1;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move_line' AND column_name = 'is_imported') THEN
        RAISE NOTICE '  ✓ is_imported';
    ELSE
        RAISE NOTICE '  ✗ is_imported manquant';
        v_errors := v_errors + 1;
    END IF;

    -- Colonnes v19
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move' AND column_name = 'amount_total_in_currency_signed') THEN
        RAISE NOTICE '  ✓ amount_total_in_currency_signed';
    ELSE
        RAISE NOTICE '  ✗ amount_total_in_currency_signed manquant';
        v_errors := v_errors + 1;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_move_line' AND column_name = 'is_downpayment') THEN
        RAISE NOTICE '  ✓ is_downpayment';
    ELSE
        RAISE NOTICE '  ✗ is_downpayment manquant';
        v_errors := v_errors + 1;
    END IF;

    RAISE NOTICE '';
    IF v_errors = 0 THEN
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        RAISE NOTICE '✓ MIGRATION v16 → v19 TERMINÉE';
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    ELSE
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        RAISE NOTICE '✗ MIGRATION v19 AVEC % ERREUR(S)', v_errors;
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    END IF;

END $$;
