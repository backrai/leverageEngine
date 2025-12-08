#!/usr/bin/env node
/**
 * Update coupon codes in Supabase
 * Usage: node scripts/update-codes.js <creator_ref> <brand_name> <code> <discount>
 * Example: node scripts/update-codes.js alex_chen Gymshark SAVE15 "15% OFF"
 */

require('dotenv').config({ path: require('path').join(__dirname, '../extension/.env') });
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.PLASMO_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.PLASMO_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing Supabase credentials');
  console.error('Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function updateCode(creatorRef, brandName, code, discount) {
  try {
    // Get creator ID
    const { data: creator, error: creatorError } = await supabase
      .from('creators')
      .select('id')
      .eq('affiliate_ref_code', creatorRef)
      .single();

    if (creatorError || !creator) {
      console.error(`❌ Creator not found: ${creatorRef}`);
      return;
    }

    // Get brand ID
    const { data: brand, error: brandError } = await supabase
      .from('brands')
      .select('id')
      .ilike('name', brandName)
      .single();

    if (brandError || !brand) {
      console.error(`❌ Brand not found: ${brandName}`);
      return;
    }

    // Check if offer exists
    const { data: existing } = await supabase
      .from('offers')
      .select('id')
      .eq('creator_id', creator.id)
      .eq('brand_id', brand.id)
      .eq('code', code)
      .single();

    if (existing) {
      // Update existing
      const { error } = await supabase
        .from('offers')
        .update({
          code,
          discount_amount: discount,
          is_active: true,
          updated_at: new Date().toISOString()
        })
        .eq('id', existing.id);

      if (error) {
        console.error('❌ Error updating offer:', error);
        return;
      }

      console.log(`✅ Updated offer: ${code} (${discount})`);
    } else {
      // Create new
      const { error } = await supabase
        .from('offers')
        .insert({
          creator_id: creator.id,
          brand_id: brand.id,
          code,
          discount_amount: discount,
          discount_type: 'percentage',
          is_active: true
        });

      if (error) {
        console.error('❌ Error creating offer:', error);
        return;
      }

      console.log(`✅ Created offer: ${code} (${discount})`);
    }
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

async function listOffers() {
  const { data, error } = await supabase
    .from('offers')
    .select(`
      code,
      discount_amount,
      is_active,
      creator:creators(display_name, affiliate_ref_code),
      brand:brands(name)
    `)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('❌ Error listing offers:', error);
    return;
  }

  console.log('\n📋 Current Offers:\n');
  data.forEach(offer => {
    const status = offer.is_active ? '✅' : '❌';
    console.log(`${status} ${offer.brand.name} - ${offer.creator.display_name} (${offer.creator.affiliate_ref_code})`);
    console.log(`   Code: ${offer.code} | Discount: ${offer.discount_amount}\n`);
  });
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === 'list') {
  listOffers();
} else if (args.length === 4) {
  const [creatorRef, brandName, code, discount] = args;
  updateCode(creatorRef, brandName, code, discount);
} else {
  console.log('Usage:');
  console.log('  node scripts/update-codes.js list                    # List all offers');
  console.log('  node scripts/update-codes.js <creator_ref> <brand> <code> <discount>');
  console.log('');
  console.log('Examples:');
  console.log('  node scripts/update-codes.js alex_chen Gymshark SAVE15 "15% OFF"');
  console.log('  node scripts/update-codes.js sarah_fitness "Athletic Greens" AG10 "10% OFF"');
}

