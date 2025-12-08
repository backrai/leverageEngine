// Test Supabase connection for extension and dashboard
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Try to load from extension .env first, then dashboard
function loadEnv() {
  const envFiles = [
    path.join(__dirname, '../extension/.env'),
    path.join(__dirname, '../dashboard/.env.local'),
  ];

  for (const envFile of envFiles) {
    if (fs.existsSync(envFile)) {
      const content = fs.readFileSync(envFile, 'utf8');
      content.split('\n').forEach(line => {
        const match = line.match(/^([^#=]+)=(.*)$/);
        if (match) {
          const key = match[1].trim();
          const value = match[2].trim();
          if (!process.env[key]) {
            process.env[key] = value;
          }
        }
      });
    }
  }
}

loadEnv();

const supabaseUrl = process.env.PUBLIC_SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.PUBLIC_SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing Supabase credentials in environment variables');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  console.log('🔍 Testing Supabase connection...\n');
  console.log(`URL: ${supabaseUrl}\n`);

  try {
    // Test 1: Check if we can query brands table
    console.log('Test 1: Querying brands table...');
    const { data: brands, error: brandsError } = await supabase
      .from('brands')
      .select('id, name')
      .limit(5);

    if (brandsError) {
      console.error('❌ Error querying brands:', brandsError.message);
      if (brandsError.message.includes('relation') || brandsError.message.includes('does not exist')) {
        console.error('\n💡 Tip: Make sure you have run the database schema (database/schema.sql) in your Supabase SQL Editor');
      }
      return false;
    }

    console.log(`✅ Successfully queried brands table. Found ${brands?.length || 0} brands.`);
    if (brands && brands.length > 0) {
      console.log('   Sample brands:', brands.map(b => b.name).join(', '));
    }

    // Test 2: Check creators table
    console.log('\nTest 2: Querying creators table...');
    const { data: creators, error: creatorsError } = await supabase
      .from('creators')
      .select('id, display_name, affiliate_ref_code')
      .limit(5);

    if (creatorsError) {
      console.error('❌ Error querying creators:', creatorsError.message);
      return false;
    }

    console.log(`✅ Successfully queried creators table. Found ${creators?.length || 0} creators.`);
    if (creators && creators.length > 0) {
      console.log('   Sample creators:', creators.map(c => c.display_name).join(', '));
    }

    // Test 3: Check offers table
    console.log('\nTest 3: Querying offers table...');
    const { data: offers, error: offersError } = await supabase
      .from('offers')
      .select('id, code, discount_amount')
      .eq('is_active', true)
      .limit(5);

    if (offersError) {
      console.error('❌ Error querying offers:', offersError.message);
      return false;
    }

    console.log(`✅ Successfully queried offers table. Found ${offers?.length || 0} active offers.`);
    if (offers && offers.length > 0) {
      console.log('   Sample offers:', offers.map(o => `${o.code} (${o.discount_amount})`).join(', '));
    }

    // Test 4: Test insert (attribution_events)
    console.log('\nTest 4: Testing insert permission...');
    const testEvent = {
      creator_id: creators && creators.length > 0 ? creators[0].id : null,
      brand_id: brands && brands.length > 0 ? brands[0].id : null,
      event_type: 'CHECKOUT_CLICK',
      path_type: 'DISCOVERY',
      transaction_value: 100.00
    };

    const { data: insertData, error: insertError } = await supabase
      .from('attribution_events')
      .insert(testEvent)
      .select()
      .single();

    if (insertError) {
      console.error('❌ Error inserting test event:', insertError.message);
      if (insertError.message.includes('permission') || insertError.message.includes('policy')) {
        console.error('\n💡 Tip: Check your RLS (Row Level Security) policies in Supabase');
      }
      return false;
    }

    console.log('✅ Successfully inserted test attribution event');
    
    // Clean up test event
    if (insertData?.id) {
      await supabase.from('attribution_events').delete().eq('id', insertData.id);
      console.log('   (Test event cleaned up)');
    }

    console.log('\n🎉 All connection tests passed!');
    return true;

  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
    return false;
  }
}

testConnection()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });

