-- =============================================================================
-- SCRIPT DE VALIDATION POST-MIGRATION v19
-- =============================================================================
-- Vérifie que la base migrée est conforme aux spécifications Odoo v19
--
-- Usage: Exécuter après DIRECT_v13_to_v19.sql ou toute migration
-- Résultat: Table validation_results avec tous les tests
-- =============================================================================

-- Table pour stocker les résultats de validation
DROP TABLE IF EXISTS validation_results;
CREATE TABLE validation_results (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- PASS, FAIL, WARNING
    expected_value TEXT,
    actual_value TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ CATÉGORIE 1: STRUCTURE SCHÉMA                                              ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_exists BOOLEAN;
    v_type TEXT;
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔══════════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║ VALIDATION POST-MIGRATION v19                                        ║';
    RAISE NOTICE '╚══════════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 1. VALIDATION STRUCTURE SCHÉMA ━━━';

    -- 1.1 account_move.move_type existe (ex-type)
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_move' AND column_name = 'move_type'
    ) INTO v_exists;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('SCHEMA', 'account_move.move_type exists',
            CASE WHEN v_exists THEN 'PASS' ELSE 'FAIL' END,
            'true', v_exists::text);
    RAISE NOTICE '  [%] account_move.move_type', CASE WHEN v_exists THEN '✓' ELSE '✗' END;

    -- 1.2 account_move.type N'existe PAS (doit être renommé)
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_move' AND column_name = 'type'
    ) INTO v_exists;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('SCHEMA', 'account_move.type removed',
            CASE WHEN NOT v_exists THEN 'PASS' ELSE 'FAIL' END,
            'false', v_exists::text);
    RAISE NOTICE '  [%] account_move.type removed', CASE WHEN NOT v_exists THEN '✓' ELSE '✗' END;

    -- 1.3 account_move.payment_state existe
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_move' AND column_name = 'payment_state'
    ) INTO v_exists;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('SCHEMA', 'account_move.payment_state exists',
            CASE WHEN v_exists THEN 'PASS' ELSE 'FAIL' END,
            'true', v_exists::text);
    RAISE NOTICE '  [%] account_move.payment_state', CASE WHEN v_exists THEN '✓' ELSE '✗' END;

    -- 1.4 account_move.auto_post est VARCHAR (pas BOOLEAN)
    SELECT data_type INTO v_type
    FROM information_schema.columns
    WHERE table_name = 'account_move' AND column_name = 'auto_post';

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('SCHEMA', 'account_move.auto_post is VARCHAR',
            CASE WHEN v_type = 'character varying' THEN 'PASS' ELSE 'FAIL' END,
            'character varying', COALESCE(v_type, 'NOT FOUND'));
    RAISE NOTICE '  [%] account_move.auto_post type: %',
        CASE WHEN v_type = 'character varying' THEN '✓' ELSE '✗' END, COALESCE(v_type, 'NOT FOUND');

    -- 1.5 account_move.posted_before existe
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_move' AND column_name = 'posted_before'
    ) INTO v_exists;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('SCHEMA', 'account_move.posted_before exists',
            CASE WHEN v_exists THEN 'PASS' ELSE 'FAIL' END,
            'true', v_exists::text);
    RAISE NOTICE '  [%] account_move.posted_before', CASE WHEN v_exists THEN '✓' ELSE '✗' END;

    -- 1.6 account_move_line.parent_state existe (computed stored)
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_move_line' AND column_name = 'parent_state'
    ) INTO v_exists;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('SCHEMA', 'account_move_line.parent_state exists',
            CASE WHEN v_exists THEN 'PASS' ELSE 'FAIL' END,
            'true', v_exists::text);
    RAISE NOTICE '  [%] account_move_line.parent_state', CASE WHEN v_exists THEN '✓' ELSE '✗' END;

    -- 1.7 account_account.account_type existe
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_account' AND column_name = 'account_type'
    ) INTO v_exists;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('SCHEMA', 'account_account.account_type exists',
            CASE WHEN v_exists THEN 'PASS' ELSE 'FAIL' END,
            'true', v_exists::text);
    RAISE NOTICE '  [%] account_account.account_type', CASE WHEN v_exists THEN '✓' ELSE '✗' END;

    -- 1.8 Vérifier si account_account.name est JSONB (traductions v16+)
    SELECT data_type INTO v_type
    FROM information_schema.columns
    WHERE table_name = 'account_account' AND column_name = 'name';

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value, details)
    VALUES ('SCHEMA', 'account_account.name type',
            CASE WHEN v_type = 'jsonb' THEN 'PASS' ELSE 'WARNING' END,
            'jsonb', COALESCE(v_type, 'NOT FOUND'),
            'Si VARCHAR, les traductions ne fonctionneront pas');
    RAISE NOTICE '  [%] account_account.name type: %',
        CASE WHEN v_type = 'jsonb' THEN '✓' ELSE '⚠' END, COALESCE(v_type, 'NOT FOUND');

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ CATÉGORIE 2: INTÉGRITÉ DES DONNÉES                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
    v_total INTEGER;
    v_pct NUMERIC;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 2. VALIDATION INTÉGRITÉ DES DONNÉES ━━━';

    -- 2.1 Écritures équilibrées (debit = credit)
    SELECT COUNT(*) INTO v_count
    FROM (
        SELECT move_id, SUM(debit) as d, SUM(credit) as c
        FROM account_move_line
        GROUP BY move_id
        HAVING ABS(SUM(debit) - SUM(credit)) > 0.01
    ) x;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('DATA', 'Balanced journal entries',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] Écritures équilibrées: % déséquilibrées',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

    -- 2.2 Factures avec partner_id
    SELECT COUNT(*) INTO v_count
    FROM account_move
    WHERE move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
      AND partner_id IS NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('DATA', 'Invoices with partner',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'WARNING' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] Factures sans partner: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '⚠' END, v_count;

    -- 2.3 AML receivable/payable avec partner_id
    SELECT COUNT(*) INTO v_count
    FROM account_move_line aml
    JOIN account_account aa ON aa.id = aml.account_id
    WHERE aa.account_type IN ('asset_receivable', 'liability_payable')
      AND aml.partner_id IS NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('DATA', 'Receivable/payable lines with partner',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'WARNING' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] AML receivable/payable sans partner: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '⚠' END, v_count;

    -- 2.4 Moves posted avec move_type valide
    SELECT COUNT(*) INTO v_count
    FROM account_move
    WHERE state = 'posted'
      AND (move_type IS NULL OR move_type NOT IN
           ('entry', 'out_invoice', 'in_invoice', 'out_refund', 'in_refund',
            'out_receipt', 'in_receipt'));

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('DATA', 'Posted moves with valid move_type',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] Posted moves avec move_type invalide: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

    -- 2.5 AML orphelines (sans move_id valide)
    SELECT COUNT(*) INTO v_count
    FROM account_move_line aml
    LEFT JOIN account_move am ON am.id = aml.move_id
    WHERE am.id IS NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('DATA', 'No orphan AML',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] AML orphelines: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

    -- 2.6 Payments avec move_id (v14+)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_payment' AND column_name = 'move_id') THEN
        SELECT COUNT(*) INTO v_total FROM account_payment WHERE state = 'posted';
        SELECT COUNT(*) INTO v_count FROM account_payment WHERE state = 'posted' AND move_id IS NULL;

        INSERT INTO validation_results (category, test_name, status, expected_value, actual_value, details)
        VALUES ('DATA', 'Payments linked to moves',
                CASE WHEN v_count = 0 THEN 'PASS' ELSE 'WARNING' END,
                '0', v_count::text,
                v_total || ' paiements posted au total');
        RAISE NOTICE '  [%] Payments sans move_id: % / %',
            CASE WHEN v_count = 0 THEN '✓' ELSE '⚠' END, v_count, v_total;
    END IF;

    -- 2.7 Account avec account_type valide
    SELECT COUNT(*) INTO v_count
    FROM account_account
    WHERE account_type NOT IN (
        'asset_receivable', 'asset_cash', 'asset_current', 'asset_non_current', 'asset_prepayments', 'asset_fixed',
        'liability_payable', 'liability_credit_card', 'liability_current', 'liability_non_current',
        'equity', 'equity_unaffected',
        'income', 'income_other',
        'expense', 'expense_depreciation', 'expense_direct_cost',
        'off_balance'
    ) OR account_type IS NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('DATA', 'Accounts with valid account_type',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] Comptes avec account_type invalide: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ CATÉGORIE 3: COHÉRENCE RELATIONNELLE                                      ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 3. VALIDATION COHÉRENCE RELATIONNELLE ━━━';

    -- 3.1 AML avec account_id valide
    SELECT COUNT(*) INTO v_count
    FROM account_move_line aml
    LEFT JOIN account_account aa ON aa.id = aml.account_id
    WHERE aa.id IS NULL AND aml.account_id IS NOT NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('FK', 'AML account_id valid FK',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] AML avec account_id invalide: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

    -- 3.2 AML avec partner_id valide
    SELECT COUNT(*) INTO v_count
    FROM account_move_line aml
    LEFT JOIN res_partner rp ON rp.id = aml.partner_id
    WHERE rp.id IS NULL AND aml.partner_id IS NOT NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('FK', 'AML partner_id valid FK',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] AML avec partner_id invalide: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

    -- 3.3 Moves avec journal_id valide
    SELECT COUNT(*) INTO v_count
    FROM account_move am
    LEFT JOIN account_journal aj ON aj.id = am.journal_id
    WHERE aj.id IS NULL AND am.journal_id IS NOT NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('FK', 'Moves journal_id valid FK',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] Moves avec journal_id invalide: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

    -- 3.4 Moves avec company_id valide
    SELECT COUNT(*) INTO v_count
    FROM account_move am
    LEFT JOIN res_company rc ON rc.id = am.company_id
    WHERE rc.id IS NULL AND am.company_id IS NOT NULL;

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
    VALUES ('FK', 'Moves company_id valid FK',
            CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
            '0', v_count::text);
    RAISE NOTICE '  [%] Moves avec company_id invalide: %',
        CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;

    -- 3.5 Reconcile avec AML valides
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'account_partial_reconcile') THEN
        SELECT COUNT(*) INTO v_count
        FROM account_partial_reconcile apr
        LEFT JOIN account_move_line d ON d.id = apr.debit_move_id
        LEFT JOIN account_move_line c ON c.id = apr.credit_move_id
        WHERE d.id IS NULL OR c.id IS NULL;

        INSERT INTO validation_results (category, test_name, status, expected_value, actual_value)
        VALUES ('FK', 'Partial reconcile valid AML refs',
                CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END,
                '0', v_count::text);
        RAISE NOTICE '  [%] Reconciles avec AML invalide: %',
            CASE WHEN v_count = 0 THEN '✓' ELSE '✗' END, v_count;
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ CATÉGORIE 4: SÉQUENCES ET IDS                                             ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_max_id BIGINT;
    v_seq_val BIGINT;
    v_ok BOOLEAN;
    r RECORD;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 4. VALIDATION SÉQUENCES ━━━';

    -- Vérifier les séquences principales
    FOR r IN
        SELECT 'account_move' as tbl, 'account_move_id_seq' as seq
        UNION ALL SELECT 'account_move_line', 'account_move_line_id_seq'
        UNION ALL SELECT 'account_payment', 'account_payment_id_seq'
        UNION ALL SELECT 'res_partner', 'res_partner_id_seq'
    LOOP
        BEGIN
            EXECUTE format('SELECT MAX(id) FROM %I', r.tbl) INTO v_max_id;
            EXECUTE format('SELECT last_value FROM %I', r.seq) INTO v_seq_val;

            v_ok := (v_seq_val >= COALESCE(v_max_id, 0));

            INSERT INTO validation_results (category, test_name, status, expected_value, actual_value, details)
            VALUES ('SEQUENCE', r.tbl || ' sequence',
                    CASE WHEN v_ok THEN 'PASS' ELSE 'FAIL' END,
                    '>= ' || COALESCE(v_max_id, 0)::text,
                    v_seq_val::text,
                    'max_id=' || COALESCE(v_max_id, 0)::text || ', seq=' || v_seq_val::text);
            RAISE NOTICE '  [%] % seq: % (max_id=%)',
                CASE WHEN v_ok THEN '✓' ELSE '✗' END, r.tbl, v_seq_val, COALESCE(v_max_id, 0);
        EXCEPTION WHEN OTHERS THEN
            INSERT INTO validation_results (category, test_name, status, details)
            VALUES ('SEQUENCE', r.tbl || ' sequence', 'WARNING', 'Sequence not found');
            RAISE NOTICE '  [⚠] % seq: NOT FOUND', r.tbl;
        END;
    END LOOP;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ CATÉGORIE 5: COMPTABILITÉ                                                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_debit NUMERIC;
    v_credit NUMERIC;
    v_diff NUMERIC;
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 5. VALIDATION COMPTABILITÉ ━━━';

    -- 5.1 Balance globale
    SELECT COALESCE(SUM(debit), 0), COALESCE(SUM(credit), 0)
    INTO v_debit, v_credit
    FROM account_move_line;

    v_diff := ABS(v_debit - v_credit);

    INSERT INTO validation_results (category, test_name, status, expected_value, actual_value, details)
    VALUES ('ACCOUNTING', 'Global balance',
            CASE WHEN v_diff < 0.01 THEN 'PASS' ELSE 'FAIL' END,
            'debit = credit',
            'diff = ' || v_diff::text,
            'debit=' || v_debit::text || ', credit=' || v_credit::text);
    RAISE NOTICE '  [%] Balance globale: diff = %',
        CASE WHEN v_diff < 0.01 THEN '✓' ELSE '✗' END, v_diff;

    -- 5.2 Nombre de factures par état
    SELECT COUNT(*) INTO v_count FROM account_move
    WHERE move_type IN ('out_invoice', 'in_invoice') AND state = 'posted';

    INSERT INTO validation_results (category, test_name, status, actual_value)
    VALUES ('ACCOUNTING', 'Posted invoices count', 'INFO', v_count::text);
    RAISE NOTICE '  [i] Factures posted: %', v_count;

    -- 5.3 Rapprochements complets
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'account_full_reconcile') THEN
        SELECT COUNT(*) INTO v_count FROM account_full_reconcile;
        INSERT INTO validation_results (category, test_name, status, actual_value)
        VALUES ('ACCOUNTING', 'Full reconciles count', 'INFO', v_count::text);
        RAISE NOTICE '  [i] Rapprochements complets: %', v_count;
    END IF;

    -- 5.4 Paiements
    SELECT COUNT(*) INTO v_count FROM account_payment WHERE state = 'posted';
    INSERT INTO validation_results (category, test_name, status, actual_value)
    VALUES ('ACCOUNTING', 'Posted payments count', 'INFO', v_count::text);
    RAISE NOTICE '  [i] Paiements posted: %', v_count;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ RAPPORT FINAL                                                              ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_pass INTEGER;
    v_fail INTEGER;
    v_warn INTEGER;
BEGIN
    SELECT
        COUNT(*) FILTER (WHERE status = 'PASS'),
        COUNT(*) FILTER (WHERE status = 'FAIL'),
        COUNT(*) FILTER (WHERE status = 'WARNING')
    INTO v_pass, v_fail, v_warn
    FROM validation_results
    WHERE status IN ('PASS', 'FAIL', 'WARNING');

    RAISE NOTICE '';
    RAISE NOTICE '══════════════════════════════════════════════════════════════════════';
    RAISE NOTICE '                    RAPPORT DE VALIDATION v19                          ';
    RAISE NOTICE '══════════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '  ✓ Tests réussis:    %', v_pass;
    RAISE NOTICE '  ✗ Tests échoués:    %', v_fail;
    RAISE NOTICE '  ⚠ Avertissements:   %', v_warn;
    RAISE NOTICE '';

    IF v_fail = 0 THEN
        RAISE NOTICE '  ═══════════════════════════════════════════════════════════════════';
        RAISE NOTICE '  ✓✓✓ BASE CONFORME AUX SPÉCIFICATIONS ODOO v19 ✓✓✓';
        RAISE NOTICE '  ═══════════════════════════════════════════════════════════════════';
    ELSE
        RAISE NOTICE '  ═══════════════════════════════════════════════════════════════════';
        RAISE NOTICE '  ✗✗✗ ATTENTION: % TEST(S) ÉCHOUÉ(S) ✗✗✗', v_fail;
        RAISE NOTICE '  ═══════════════════════════════════════════════════════════════════';
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE 'Détail: SELECT * FROM validation_results ORDER BY id;';
    RAISE NOTICE '';

END $$;

-- Afficher le résumé par catégorie
SELECT
    category,
    COUNT(*) FILTER (WHERE status = 'PASS') as "✓ PASS",
    COUNT(*) FILTER (WHERE status = 'FAIL') as "✗ FAIL",
    COUNT(*) FILTER (WHERE status = 'WARNING') as "⚠ WARN",
    COUNT(*) FILTER (WHERE status = 'INFO') as "ℹ INFO"
FROM validation_results
GROUP BY category
ORDER BY category;

-- Afficher les échecs uniquement
SELECT test_name, expected_value, actual_value, details
FROM validation_results
WHERE status = 'FAIL'
ORDER BY id;
