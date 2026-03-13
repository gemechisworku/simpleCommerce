# Mock Data Seeding Scripts

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

### Production

- **Full mock data (admin + categories + products):** Run the script once without `SEED_ADMIN_ONLY` (e.g. on Railway: `railway run -s backend python -m scripts.seed_mock_data`). Set `SUPERADMIN_PHONE` (and optional `SUPERADMIN_EMAIL`, etc.) in the environment. Prod will have the same sample data as local.
- **Admin only (no mock products):** Set `SEED_ADMIN_ONLY=1` in the environment, then run the script once. See [Deploy Backend on Railway](../../docs/DEPLOY_RAILWAY.md#9-first-time-setup-seed-admin-and-optional-mock-data-production).

### Notes:

- The script checks for existing data and skips if already present
- All products are set as active
- Featured products are marked appropriately
- Each product has multiple variants with different prices and stock quantities
- SKUs are generated for each variant
- Product images use Lorem Picsum URLs (free, reliable placeholders)

