-- =============================================================================
-- MIGRATION v14 → v16 (inclut v15)
-- =============================================================================
-- Changements majeurs:
-- - auto_post: BOOLEAN → VARCHAR
-- - account_type: FK user_type_id → VARCHAR enum
-- - Champs traduits: VARCHAR → JSONB
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'MIGRATION v14 → v16';
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 1. ACCOUNT_MOVE.AUTO_POST: BOOLEAN → VARCHAR                              ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_data_type TEXT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 1. AUTO_POST CONVERSION ━━━';

    SELECT data_type INTO v_data_type
    FROM information_schema.columns
    WHERE table_name = 'account_move' AND column_name = 'auto_post';

    IF v_data_type = 'boolean' THEN
        -- Créer colonne temporaire
        ALTER TABLE account_move ADD COLUMN auto_post_new VARCHAR;

        -- Convertir les valeurs
        UPDATE account_move SET auto_post_new = CASE
            WHEN auto_post = TRUE THEN 'at_date'
            ELSE 'no'
        END;

        -- Remplacer
        ALTER TABLE account_move DROP COLUMN auto_post;
        ALTER TABLE account_move RENAME COLUMN auto_post_new TO auto_post;

        RAISE NOTICE '  ✓ auto_post: BOOLEAN → VARCHAR';
    ELSE
        RAISE NOTICE '  ⊘ auto_post déjà VARCHAR';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 2. ACCOUNT_ACCOUNT.ACCOUNT_TYPE: FK → VARCHAR                             ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 2. ACCOUNT_TYPE MIGRATION ━━━';

    -- Vérifier si user_type_id existe (v13/v14)
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_account' AND column_name = 'user_type_id') THEN

        -- Créer account_type si n'existe pas
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'account_account' AND column_name = 'account_type') THEN
            ALTER TABLE account_account ADD COLUMN account_type VARCHAR;
        END IF;

        -- Mapper les valeurs depuis account_account_type
        IF EXISTS (SELECT 1 FROM information_schema.tables
                   WHERE table_name = 'account_account_type') THEN

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
                    WHEN aat.type = 'other' AND aat.internal_group = 'off_balance' THEN 'off_balance'
                    ELSE 'asset_current'
                END
            FROM account_account_type aat
            WHERE aa.user_type_id = aat.id
            AND aa.account_type IS NULL;

            GET DIAGNOSTICS v_count = ROW_COUNT;
            RAISE NOTICE '  ✓ account_type mappé: % comptes', v_count;

        ELSE
            RAISE NOTICE '  ⚠ account_account_type non trouvée, mapping par défaut';
            UPDATE account_account SET account_type = 'asset_current'
            WHERE account_type IS NULL;
        END IF;

        -- Supprimer user_type_id
        ALTER TABLE account_account DROP COLUMN IF EXISTS user_type_id;
        RAISE NOTICE '  ✓ user_type_id supprimé';

    ELSE
        RAISE NOTICE '  ⊘ user_type_id déjà supprimé';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 3. CHAMPS TRADUITS: VARCHAR → JSONB                                       ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_data_type TEXT;
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 3. CHAMPS JSONB (TRADUCTIONS) ━━━';

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_account.name
    -- ═══════════════════════════════════════════════════════════════════════
    SELECT data_type INTO v_data_type
    FROM information_schema.columns
    WHERE table_name = 'account_account' AND column_name = 'name';

    IF v_data_type = 'character varying' THEN
        ALTER TABLE account_account ADD COLUMN name_jsonb JSONB;
        UPDATE account_account SET name_jsonb = jsonb_build_object('en_US', name, 'fr_FR', name);
        ALTER TABLE account_account DROP COLUMN name;
        ALTER TABLE account_account RENAME COLUMN name_jsonb TO name;
        GET DIAGNOSTICS v_count = ROW_COUNT;
        RAISE NOTICE '  ✓ account_account.name → JSONB: %', v_count;
    ELSE
        RAISE NOTICE '  ⊘ account_account.name déjà JSONB';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_journal.name
    -- ═══════════════════════════════════════════════════════════════════════
    SELECT data_type INTO v_data_type
    FROM information_schema.columns
    WHERE table_name = 'account_journal' AND column_name = 'name';

    IF v_data_type = 'character varying' THEN
        ALTER TABLE account_journal ADD COLUMN name_jsonb JSONB;
        UPDATE account_journal SET name_jsonb = jsonb_build_object('en_US', name, 'fr_FR', name);
        ALTER TABLE account_journal DROP COLUMN name;
        ALTER TABLE account_journal RENAME COLUMN name_jsonb TO name;
        RAISE NOTICE '  ✓ account_journal.name → JSONB';
    ELSE
        RAISE NOTICE '  ⊘ account_journal.name déjà JSONB';
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account_tax.name
    -- ═══════════════════════════════════════════════════════════════════════
    SELECT data_type INTO v_data_type
    FROM information_schema.columns
    WHERE table_name = 'account_tax' AND column_name = 'name';

    IF v_data_type = 'character varying' THEN
        ALTER TABLE account_tax ADD COLUMN name_jsonb JSONB;
        UPDATE account_tax SET name_jsonb = jsonb_build_object('en_US', name, 'fr_FR', name);
        ALTER TABLE account_tax DROP COLUMN name;
        ALTER TABLE account_tax RENAME COLUMN name_jsonb TO name;
        RAISE NOTICE '  ✓ account_tax.name → JSONB';
    ELSE
        RAISE NOTICE '  ⊘ account_tax.name déjà JSONB';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 4. ACCOUNT_MOVE_LINE: Nouveaux champs v16                                 ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 4. ACCOUNT_MOVE_LINE v16 ━━━';

    -- is_storno (comptabilité par extourne)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_move_line' AND column_name = 'is_storno') THEN
        ALTER TABLE account_move_line ADD COLUMN is_storno BOOLEAN DEFAULT FALSE;
        RAISE NOTICE '  ✓ is_storno ajouté';
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ 5. IR_ATTACHMENT: res_model renommés                                      ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ 5. ATTACHMENTS RES_MODEL ━━━';

    -- mail.channel → discuss.channel
    UPDATE ir_attachment SET res_model = 'discuss.channel'
    WHERE res_model = 'mail.channel';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ mail.channel → discuss.channel: %', v_count;
    END IF;

    -- payment.acquirer → payment.provider
    UPDATE ir_attachment SET res_model = 'payment.provider'
    WHERE res_model = 'payment.acquirer';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ payment.acquirer → payment.provider: %', v_count;
    END IF;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ VALIDATION                                                                 ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_errors INTEGER := 0;
    v_data_type TEXT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ VALIDATION v16 ━━━';

    -- auto_post est VARCHAR
    SELECT data_type INTO v_data_type
    FROM information_schema.columns
    WHERE table_name = 'account_move' AND column_name = 'auto_post';

    IF v_data_type = 'character varying' THEN
        RAISE NOTICE '  ✓ auto_post VARCHAR';
    ELSE
        RAISE NOTICE '  ✗ auto_post devrait être VARCHAR, est: %', v_data_type;
        v_errors := v_errors + 1;
    END IF;

    -- account_type existe
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'account_account' AND column_name = 'account_type') THEN
        RAISE NOTICE '  ✓ account_account.account_type';
    ELSE
        RAISE NOTICE '  ✗ account_account.account_type manquant';
        v_errors := v_errors + 1;
    END IF;

    -- user_type_id supprimé
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'account_account' AND column_name = 'user_type_id') THEN
        RAISE NOTICE '  ✓ user_type_id supprimé';
    ELSE
        RAISE NOTICE '  ⚠ user_type_id encore présent';
    END IF;

    RAISE NOTICE '';
    IF v_errors = 0 THEN
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        RAISE NOTICE '✓ MIGRATION v14 → v16 TERMINÉE';
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    ELSE
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
        RAISE NOTICE '✗ MIGRATION v16 AVEC % ERREUR(S)', v_errors;
        RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    END IF;

END $$;
