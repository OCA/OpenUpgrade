-- =============================================================================
-- MIGRATION ATTACHMENTS v13 → v19
-- =============================================================================
-- Script spécialisé pour la migration des ir_attachment
-- Gère les renommages de res_model et les modèles supprimés
--
-- À exécuter APRÈS la migration principale des données
--
-- IMPORTANT: Ce script doit être exécuté en 2 phases:
--   1. Sur la BASE SOURCE (v13) AVANT export: Préparer les res_model
--   2. Sur la BASE CIBLE (v19) APRÈS import: Valider et corriger
--
-- Modèles renommés v13→v19:
--   mail.channel → discuss.channel (v16)
--   payment.acquirer → payment.provider (v16)
--   payment.icon → payment.method (v16)
--   im_livechat.channel → discuss.channel (v16)
--
-- Modèles supprimés v13→v19:
--   hr.expense.sheet → hr.expense (fusionné)
--   account.invoice.send → NULL (wizard transient)
--   account.bank.statement.import → NULL (wizard transient)
--
-- Modèles non installés (garder tel quel):
--   fleet.vehicle, fleet.vehicle.model.brand, fleet.vehicle.log.services
--   hr.contract (si module RH complet non installé)
-- =============================================================================

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 1: RENOMMAGES DE RES_MODEL (Modèles renommés entre v13 et v19)      ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
    v_total INTEGER := 0;
BEGIN
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'MIGRATION ATTACHMENTS v13 → v19';
    RAISE NOTICE '════════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '━━━ PHASE 1: RENOMMAGES RES_MODEL ━━━';

    -- ═══════════════════════════════════════════════════════════════════════
    -- mail.channel → discuss.channel (v16)
    -- ═══════════════════════════════════════════════════════════════════════
    UPDATE ir_attachment SET res_model = 'discuss.channel'
    WHERE res_model = 'mail.channel';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ mail.channel → discuss.channel: %', v_count;
        v_total := v_total + v_count;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- payment.acquirer → payment.provider (v16)
    -- ═══════════════════════════════════════════════════════════════════════
    UPDATE ir_attachment SET res_model = 'payment.provider'
    WHERE res_model = 'payment.acquirer';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ payment.acquirer → payment.provider: %', v_count;
        v_total := v_total + v_count;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- payment.icon → payment.method (v16+)
    -- Note: Les icônes de paiement sont maintenant sur payment.method
    -- ═══════════════════════════════════════════════════════════════════════
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'payment_method') THEN
        UPDATE ir_attachment SET res_model = 'payment.method'
        WHERE res_model = 'payment.icon';
        GET DIAGNOSTICS v_count = ROW_COUNT;
        IF v_count > 0 THEN
            RAISE NOTICE '  ✓ payment.icon → payment.method: %', v_count;
            v_total := v_total + v_count;
        END IF;
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE '  Total Phase 1: % attachments renommés', v_total;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 2: MODÈLES SUPPRIMÉS (Remapper vers équivalents)                    ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
    v_total INTEGER := 0;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ PHASE 2: MODÈLES SUPPRIMÉS ━━━';

    -- ═══════════════════════════════════════════════════════════════════════
    -- hr.expense.sheet → hr.expense (v19: sheets fusionnés dans expense)
    -- Nécessite que hr_expense existe avec une colonne sheet_id ou équivalent
    -- ═══════════════════════════════════════════════════════════════════════

    -- Vérifier si hr_expense existe et a les données
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hr_expense') THEN
        -- Pour les attachments qui ont hr.expense.sheet comme res_model
        -- On les associe à la première expense qui était dans ce sheet
        -- Note: Ceci suppose que les expense.id sont les mêmes qu'en v13

        UPDATE ir_attachment a
        SET res_model = 'hr.expense'
        WHERE a.res_model = 'hr.expense.sheet'
        AND EXISTS (SELECT 1 FROM hr_expense WHERE id = a.res_id);

        GET DIAGNOSTICS v_count = ROW_COUNT;
        IF v_count > 0 THEN
            RAISE NOTICE '  ✓ hr.expense.sheet → hr.expense: %', v_count;
            v_total := v_total + v_count;
        END IF;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account.invoice.send → account.move.send (v14+)
    -- Les wizards d'envoi de facture
    -- ═══════════════════════════════════════════════════════════════════════
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'account_move_send') THEN
        UPDATE ir_attachment SET res_model = 'account.move.send'
        WHERE res_model = 'account.invoice.send';
        GET DIAGNOSTICS v_count = ROW_COUNT;
        IF v_count > 0 THEN
            RAISE NOTICE '  ✓ account.invoice.send → account.move.send: %', v_count;
            v_total := v_total + v_count;
        END IF;
    ELSE
        -- Si account.move.send n'existe pas, nullifier le res_model
        UPDATE ir_attachment SET res_model = NULL, res_id = NULL
        WHERE res_model = 'account.invoice.send';
        GET DIAGNOSTICS v_count = ROW_COUNT;
        IF v_count > 0 THEN
            RAISE NOTICE '  ⚠ account.invoice.send → NULL (wizard transient): %', v_count;
        END IF;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- account.bank.statement.import → NULL (wizard transient)
    -- Les imports de relevés bancaires sont des données temporaires
    -- ═══════════════════════════════════════════════════════════════════════
    UPDATE ir_attachment SET res_model = NULL, res_id = NULL
    WHERE res_model = 'account.bank.statement.import';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ⚠ account.bank.statement.import → NULL (wizard): %', v_count;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════
    -- im_livechat.channel → discuss.channel (si livechat installé)
    -- ═══════════════════════════════════════════════════════════════════════
    UPDATE ir_attachment SET res_model = 'discuss.channel'
    WHERE res_model = 'im_livechat.channel';
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN
        RAISE NOTICE '  ✓ im_livechat.channel → discuss.channel: %', v_count;
        v_total := v_total + v_count;
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE '  Total Phase 2: % attachments remappés', v_total;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 3: MODULES NON INSTALLÉS (fleet, hr.contract, etc.)                 ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_count INTEGER;
    v_models TEXT[] := ARRAY[
        'fleet.vehicle',
        'fleet.vehicle.model.brand',
        'fleet.vehicle.log.services',
        'hr.contract'
    ];
    v_model TEXT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ PHASE 3: MODULES NON INSTALLÉS ━━━';

    FOREACH v_model IN ARRAY v_models
    LOOP
        -- Vérifier si la table existe
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = REPLACE(v_model, '.', '_')
        ) THEN
            -- La table n'existe pas, compter les attachments orphelins
            SELECT COUNT(*) INTO v_count
            FROM ir_attachment
            WHERE res_model = v_model;

            IF v_count > 0 THEN
                -- Option 1: Garder mais marquer comme orphelins
                -- (les fichiers physiques restent disponibles)
                RAISE NOTICE '  ⚠ %: % attachments (module non installé)', v_model, v_count;

                -- Option 2: Nullifier le lien (décommenter si souhaité)
                -- UPDATE ir_attachment SET res_model = NULL, res_id = NULL
                -- WHERE res_model = v_model;
            END IF;
        END IF;
    END LOOP;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 4: VALIDATION DES LIENS                                             ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

DO $$
DECLARE
    v_total INTEGER;
    v_linked INTEGER;
    v_orphan_model INTEGER;
    v_orphan_id INTEGER;
    v_no_model INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '━━━ PHASE 4: VALIDATION ━━━';

    -- Compter les totaux
    SELECT COUNT(*) INTO v_total FROM ir_attachment;

    SELECT COUNT(*) INTO v_linked
    FROM ir_attachment
    WHERE res_model IS NOT NULL AND res_id IS NOT NULL AND res_id > 0;

    SELECT COUNT(*) INTO v_no_model
    FROM ir_attachment WHERE res_model IS NULL;

    SELECT COUNT(*) INTO v_orphan_id
    FROM ir_attachment WHERE res_model IS NOT NULL AND (res_id IS NULL OR res_id = 0);

    RAISE NOTICE '';
    RAISE NOTICE '  Résumé:';
    RAISE NOTICE '  ────────────────────────────────────────';
    RAISE NOTICE '  Total attachments:        %', v_total;
    RAISE NOTICE '  ✓ Liés (model + id):     %', v_linked;
    RAISE NOTICE '  ⚠ Sans res_model:         %', v_no_model;
    RAISE NOTICE '  ⚠ Sans res_id:            %', v_orphan_id;
    RAISE NOTICE '';

    -- Détail par mimetype des sans res_model
    RAISE NOTICE '  Détail sans res_model par type:';
    FOR v_total, v_linked IN
        SELECT mimetype, COUNT(*)
        FROM ir_attachment
        WHERE res_model IS NULL
        GROUP BY mimetype
        ORDER BY COUNT(*) DESC
        LIMIT 10
    LOOP
        RAISE NOTICE '    - %: %', COALESCE(v_total::text, '(null)'), v_linked;
    END LOOP;

END $$;

-- ╔═══════════════════════════════════════════════════════════════════════════╗
-- ║ PHASE 5: RAPPORT FINAL                                                     ║
-- ╚═══════════════════════════════════════════════════════════════════════════╝

-- Vue résumée
SELECT
    'TOTAL' as category,
    COUNT(*) as nb,
    pg_size_pretty(SUM(file_size::bigint)) as size
FROM ir_attachment
UNION ALL
SELECT
    CASE
        WHEN res_model IS NULL THEN '⚠️ Sans res_model'
        WHEN res_id IS NULL OR res_id = 0 THEN '⚠️ Sans res_id'
        ELSE '✓ Liés correctement'
    END,
    COUNT(*),
    pg_size_pretty(SUM(file_size::bigint))
FROM ir_attachment
GROUP BY 1
ORDER BY 2 DESC;

-- Détail par modèle
SELECT
    COALESCE(res_model, '(NULL)') as res_model,
    COUNT(*) as nb,
    pg_size_pretty(SUM(file_size::bigint)) as size
FROM ir_attachment
GROUP BY res_model
ORDER BY COUNT(*) DESC
LIMIT 20;
