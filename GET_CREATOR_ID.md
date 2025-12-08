# Get Creator ID for Dashboard

## 🎯 You Need a Creator ID

To view the dashboard, you need a creator ID from your database.

## 📋 Step-by-Step: Get Creator ID

### Option 1: From Supabase Table Editor

1. **Go to Supabase Dashboard**:
   - https://supabase.com/dashboard/project/vuwkkhmkbtawyqvvqanu

2. **Click "Table Editor"** in left sidebar

3. **Click on "creators" table**

4. **Find "Alex Chen"** row

5. **Copy the `id` column** (it's a UUID like: `a1b2c3d4-e5f6-...`)

### Option 2: Run SQL Query

In Supabase SQL Editor, run:
```sql
SELECT id, display_name, affiliate_ref_code 
FROM creators;
```

Copy the `id` for "Alex Chen"

## 🚀 Use the Creator ID

Once you have the ID, you'll use it to view the dashboard:
```
http://localhost:3000?creator_id=YOUR_CREATOR_ID_HERE
```

