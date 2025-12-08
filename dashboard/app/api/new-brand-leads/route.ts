import { NextRequest, NextResponse } from 'next/server';
import { getNewBrandLeads } from '@/lib/leverage-data';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const creatorId = searchParams.get('creator_id');

    if (!creatorId) {
      return NextResponse.json(
        { error: 'creator_id is required' },
        { status: 400 }
      );
    }

    const leads = await getNewBrandLeads(creatorId);
    return NextResponse.json(leads);
  } catch (error) {
    console.error('Error in new-brand-leads API:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

