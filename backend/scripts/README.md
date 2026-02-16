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

1. **Categories** (5 categories):
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

### Notes:

- The script checks for existing data and skips if already present
- All products are set as active
- Featured products are marked appropriately
- Each product has multiple variants with different prices and stock quantities
- SKUs are generated for each variant

