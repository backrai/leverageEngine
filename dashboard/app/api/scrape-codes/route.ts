import { NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

/**
 * API endpoint to trigger scraper for a specific brand
 * POST /api/scrape-codes
 * Body: { brandId: string }
 */
export async function POST(request: NextRequest) {
  try {
    const { brandId } = await request.json();

    if (!brandId) {
      return NextResponse.json(
        { error: 'brandId is required' },
        { status: 400 }
      );
    }

    const supabase = createServerClient();

    // Check if brand exists
    const { data: brand, error: brandError } = await supabase
      .from('brands')
      .select('id, name, domain_pattern')
      .eq('id', brandId)
      .single();

    if (brandError || !brand) {
      return NextResponse.json(
        { error: 'Brand not found' },
        { status: 404 }
      );
    }

    // Check if offers already exist for this brand
    const { data: existingOffers, error: offersError } = await supabase
      .from('offers')
      .select('id')
      .eq('brand_id', brandId)
      .eq('is_active', true)
      .limit(1);

    if (offersError) {
      console.error('Error checking offers:', offersError);
    }

    // If offers exist, return early
    if (existingOffers && existingOffers.length > 0) {
      return NextResponse.json({
        success: true,
        message: 'Offers already exist for this brand',
        offersFound: existingOffers.length
      });
    }

    // Trigger scraper for this specific brand
    console.log(`[Scraper API] Triggering scraper for brand: ${brand.name} (${brand.domain_pattern})`);

    // Get the scraper directory path (sibling to dashboard)
    const dashboardPath = process.cwd();
    const scraperPath = path.join(dashboardPath, '..', 'scraper');
    const scraperScript = path.join(scraperPath, 'scraper.py');

    console.log('[Scraper API] Scraper path:', scraperPath);

    // Run scraper for this specific brand
    // Note: This runs the scraper synchronously, which might take time
    // For production, consider using a queue system (Bull, etc.)
    try {
      // Use absolute path and ensure we're in the right directory
      const command = `cd "${scraperPath}" && source venv/bin/activate && python scraper.py --brand-id ${brandId}`;
      console.log('[Scraper API] Running command:', command);
      
      const { stdout, stderr } = await execAsync(
        command,
        { 
          timeout: 60000, // 60 second timeout
          cwd: scraperPath,
          shell: '/bin/bash' // Use bash to support source command
        }
      );

      console.log('[Scraper API] Scraper output:', stdout);
      if (stderr) {
        console.warn('[Scraper API] Scraper warnings:', stderr);
      }

      // Check if new offers were created
      const { data: newOffers, error: newOffersError } = await supabase
        .from('offers')
        .select('id, code, discount_amount')
        .eq('brand_id', brandId)
        .eq('is_active', true);

      if (newOffersError) {
        console.error('Error checking new offers:', newOffersError);
      }

      return NextResponse.json({
        success: true,
        message: 'Scraper completed',
        offersFound: newOffers?.length || 0,
        offers: newOffers || []
      });
    } catch (execError: any) {
      console.error('[Scraper API] Error running scraper:', execError);
      
      // Return partial success - scraper might have found some codes before error
      const { data: newOffers } = await supabase
        .from('offers')
        .select('id, code, discount_amount')
        .eq('brand_id', brandId)
        .eq('is_active', true);

      return NextResponse.json({
        success: false,
        message: 'Scraper encountered an error',
        error: execError.message,
        offersFound: newOffers?.length || 0,
        offers: newOffers || []
      }, { status: 500 });
    }
  } catch (error: any) {
    console.error('[Scraper API] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * GET endpoint to check scraping status
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const brandId = searchParams.get('brandId');

  if (!brandId) {
    return NextResponse.json(
      { error: 'brandId is required' },
      { status: 400 }
    );
  }

  const supabase = createServerClient();

  // Check if offers exist
  const { data: offers, error } = await supabase
    .from('offers')
    .select('id, code, discount_amount, is_active')
    .eq('brand_id', brandId);

  if (error) {
    return NextResponse.json(
      { error: 'Error checking offers' },
      { status: 500 }
    );
  }

  return NextResponse.json({
    brandId,
    hasOffers: offers && offers.length > 0,
    offersCount: offers?.length || 0,
    activeOffersCount: offers?.filter(o => o.is_active).length || 0
  });
}

