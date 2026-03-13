# Backend Scripts

## make_admin.py

Makes a user with the given phone an **admin** (or creates them as admin if they don't exist).

```bash
# From backend directory (set DATABASE_URL if needed)
python -m scripts.make_admin +251937745414

# With env
MAKE_ADMIN_PHONE=+251937745414 python -m scripts.make_admin
```

**Railway:** From Backend Shell (or `railway run` with DATABASE_URL):  
`python -m scripts.make_admin +251937745414`

---

## seed_mock_data.py

This script seeds the database with sample products, categories, and variants for development and testing purposes.

### Usage

Run the script from the backend directory:

```bash
# From backend directory
python scripts/seed_mock_data.py

# Or using Docker
docker exec -it simplecommerce_backend python scripts/seed_mock_data.py
```

### What it seeds:

1. **Superadmin** (first admin user):
   - Phone: `+251911111111` (configurable via `SUPERADMIN_PHONE`)
   - Role: admin (full access)
   - Login: Go to `/login`, enter phone, request OTP. In dev, OTP is logged in backend.
   - After login, go to `/admin` for the dashboard.
   - Env overrides: `SUPERADMIN_PHONE`, `SUPERADMIN_EMAIL`, `SUPERADMIN_FIRST_NAME`, `SUPERADMIN_LAST_NAME`

2. **Categories** (5 categories):
   - Coffee
   - Tea
   - Spices
   - Honey
   - Grains

2. **Products** (11 products with variants):
   - Ethiopian Yirgacheffe Coffee Beans (3 variants)
   - Sidamo Coffee Beans (3 variants)
   - Harrar Coffee Beans (2 variants)
   - Ethiopian Green Tea (2 variants)
   - Black Tea (2 variants)
   - Berbere Spice Mix (3 variants)
   - Mitmita Spice (2 variants)
   - Turmeric Powder (2 variants)
   - Wild Honey (3 variants)
   - Teff Flour (2 variants)
   - Quinoa (2 variants)

### Production (Railway)

- **Full mock data (admin + categories + products):** Do not set `SEED_ADMIN_ONLY`. Run the seed once:
  - **At startup (no Shell):** In Backend **Variables** add **`RUN_SEED_ON_STARTUP`** = **`1`**. Keep Start Command as `./scripts/start.sh`. Redeploy; the seed runs after migrations. Remove `RUN_SEED_ON_STARTUP` afterward to avoid running on every restart (optional).
  - **Shell:** If your plan has Shell, Backend → Shell → `python -m scripts.seed_mock_data`.
- **Admin only (no mock products):** Set `SEED_ADMIN_ONLY=1` in Backend variables, then use one of the options above. See [Deploy Backend on Railway](../../docs/DEPLOY_RAILWAY.md#9-first-time-setup-seed-admin-and-optional-mock-data-production).

### Notes:

- The script checks for existing data and skips if already present
- All products are set as active
- Featured products are marked appropriately
- Each product has multiple variants with different prices and stock quantities
- SKUs are generated for each variant
- Product images use Lorem Picsum URLs (free, reliable placeholders)

