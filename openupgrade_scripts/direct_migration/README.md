# Odoo Direct Migration Scripts

SQL-based migration scripts for direct Odoo version upgrades, bypassing intermediate versions.

## Supported Migration Paths

| From | To | Script(s) |
|------|-----|-----------|
| **v13** | **v19** | `DIRECT_v13_to_v19.sql` (all-in-one) |
| **v13** | **v14** | `MIGRATE_v13_to_v14.sql` |
| **v14** | **v16** | `MIGRATE_v14_to_v16.sql` |
| **v14** | **v19** | `MIGRATE_v14_to_v16.sql` + `MIGRATE_v16_to_v19.sql` |
| **v15** | **v19** | `MIGRATE_v14_to_v16.sql` + `MIGRATE_v16_to_v19.sql` |
| **v16** | **v19** | `MIGRATE_v16_to_v19.sql` |
| **v17** | **v19** | `MIGRATE_v16_to_v19.sql` (v17+ sections) |
| **v18** | **v19** | `MIGRATE_v16_to_v19.sql` (v18+ sections) |

## Why Direct Migration?

| Aspect | Traditional OpenUpgrade | This Approach |
|--------|------------------------|---------------|
| **Path** | v13→v14→v15→v16→v17→v18→v19 | Direct jump |
| **Migrations** | Up to 6 sequential | 1-2 scripts |
| **Dependencies** | Each Odoo version required | SQL only |
| **Time** | Hours | Minutes |

## Scripts Overview

### All-in-One
| Script | Description |
|--------|-------------|
| `DIRECT_v13_to_v19.sql` | Complete v13→v19 migration in one pass |

### Step-by-Step (for partial migrations)
| Script | Description |
|--------|-------------|
| `MIGRATE_v13_to_v14.sql` | v13→v14 changes only |
| `MIGRATE_v14_to_v16.sql` | v14→v16 (includes v15 changes) |
| `MIGRATE_v16_to_v19.sql` | v16→v19 (includes v17, v18, v19 changes) |

### Specialized
| Script | Description |
|--------|-------------|
| `MIGRATE_ATTACHMENTS_v13_to_v19.sql` | ir_attachment res_model fixes |
| `MIGRATE_FLEET_v13_to_v19.sql` | Fleet module migration |
| `VALIDATION_v19.sql` | Post-migration validation checks |

## Key Transformations

### Column Renames (cumulative)
```
v13 → v14:
  account_move.type → move_type
  account_move.invoice_payment_state → payment_state
  account_move.invoice_partner_bank_id → partner_bank_id

v14 → v16:
  account_account.user_type_id → account_type (VARCHAR enum)

v17:
  account_tax.description → invoice_label

v18:
  account_move.payment_id → origin_payment_id
```

### Type Conversions
```sql
-- auto_post: BOOLEAN → VARCHAR (v16)
TRUE  → 'at_date'
FALSE → 'no'

-- account_type: FK → VARCHAR enum (v16)
user_type_id (receivable) → 'asset_receivable'
user_type_id (payable)    → 'liability_payable'

-- Translated fields: VARCHAR → JSONB (v16)
name = 'Sales'  →  {"en_US": "Sales", "fr_FR": "Sales"}
```

### Model Renames (ir_attachment)
```
mail.channel → discuss.channel
payment.acquirer → payment.provider
hr.expense.sheet → hr.expense
```

## Usage Examples

### v13 → v19 (Direct)
```bash
psql -d odoo_v19 -f DIRECT_v13_to_v19.sql
psql -d odoo_v19 -f MIGRATE_ATTACHMENTS_v13_to_v19.sql
psql -d odoo_v19 -f VALIDATION_v19.sql
```

### v16 → v19
```bash
psql -d odoo_v19 -f MIGRATE_v16_to_v19.sql
psql -d odoo_v19 -f VALIDATION_v19.sql
```

### v14 → v19
```bash
psql -d odoo_v19 -f MIGRATE_v14_to_v16.sql
psql -d odoo_v19 -f MIGRATE_v16_to_v19.sql
psql -d odoo_v19 -f VALIDATION_v19.sql
```

## Features

- **Idempotent**: Scripts can be re-run safely
- **Logged**: Operations tracked in `migration_direct_log` table
- **Validated**: Built-in integrity checks
- **Documented**: Each transformation explained

## Tested On

- Source: Odoo 13.0, 14.0, 16.0 Community
- Target: Odoo 19.0 Community
- PostgreSQL 12-16

## License

LGPL-3.0 (same as Odoo)
