// Context Detection Logic for Dual Path System
// Detects Path A (Earned) vs Path B (Discovery)

import type { PathType } from "../../shared/types";

export interface PageContext {
  pathType: PathType;
  referringCreatorId?: string;
  brandId?: string;
  isCheckoutPage: boolean;
  isConfirmationPage: boolean;
}

/**
 * Detects affiliate parameters in URL (Path A: Earned)
 * Looks for common affiliate parameters: ?ref=, ?affiliate=, ?code=, etc.
 */
export async function detectAffiliateParams(url: string): Promise<string | null> {
  try {
    const urlObj = new URL(url);
    const params = urlObj.searchParams;
    
    // Common affiliate parameter names
    const affiliateParams = ['ref', 'affiliate', 'code', 'creator', 'influencer', 'partner'];
    
    for (const param of affiliateParams) {
      const value = params.get(param);
      if (value) {
        return value;
      }
    }
    
    return null;
  } catch (error) {
    console.error('Error detecting affiliate params:', error);
    return null;
  }
}

/**
 * Gets creator ID from affiliate ref code
 */
export async function getCreatorIdFromRef(refCode: string): Promise<string | null> {
  try {
    const { supabase } = await import('./supabase');
    const { data, error } = await supabase
      .from('creators')
      .select('id')
      .eq('affiliate_ref_code', refCode)
      .single();
    
    if (error || !data) {
      return null;
    }
    
    return data.id;
  } catch (error) {
    console.error('Error getting creator ID:', error);
    return null;
  }
}

/**
 * Detects if current page is a checkout page
 * Looks for common checkout indicators
 */
export function detectCheckoutPage(): boolean {
  const url = window.location.href.toLowerCase();
  const pathname = window.location.pathname.toLowerCase();
  
  // Common checkout page patterns
  const checkoutPatterns = [
    '/checkout',
    '/cart',
    '/basket',
    '/payment',
    '/review',
    '/order'
  ];
  
  // Check URL patterns
  if (checkoutPatterns.some(pattern => pathname.includes(pattern))) {
    return true;
  }
  
  // Check for coupon code input fields
  const couponInputs = document.querySelectorAll(
    'input[type="text"][name*="coupon"], ' +
    'input[type="text"][name*="code"], ' +
    'input[type="text"][name*="promo"], ' +
    'input[type="text"][id*="coupon"], ' +
    'input[type="text"][id*="code"], ' +
    'input[type="text"][id*="promo"]'
  );
  
  return couponInputs.length > 0;
}

/**
 * Detects if current page is an order confirmation page
 * Looks for common confirmation indicators
 */
export function detectConfirmationPage(): boolean {
  const url = window.location.href.toLowerCase();
  const pathname = window.location.pathname.toLowerCase();
  const bodyText = document.body.textContent?.toLowerCase() || '';
  
  // Common confirmation page patterns
  const confirmationPatterns = [
    '/thank-you',
    '/thankyou',
    '/confirmation',
    '/order-confirmed',
    '/success',
    '/complete'
  ];
  
  // Check URL patterns
  if (confirmationPatterns.some(pattern => pathname.includes(pattern))) {
    return true;
  }
  
  // Check for confirmation text
  const confirmationText = [
    'thank you for your order',
    'order confirmed',
    'your order has been placed',
    'order number',
    'confirmation number'
  ];
  
  return confirmationText.some(text => bodyText.includes(text));
}

/**
 * Extracts the root domain from a hostname (removes www. and subdomains)
 * Example: "www.gymshark.com" -> "gymshark.com"
 */
function extractRootDomain(hostname: string): string {
  // Remove www. prefix if present
  let domain = hostname.replace(/^www\./, '');
  
  // Split by dots and get the last two parts (domain + TLD)
  // This handles cases like "gymshark.com" or "subdomain.gymshark.com"
  const parts = domain.split('.');
  if (parts.length >= 2) {
    return parts.slice(-2).join('.');
  }
  
  return domain;
}

/**
 * Gets brand ID from current domain
 */
export async function getBrandIdFromDomain(domain: string): Promise<string | null> {
  try {
    const { supabase } = await import('./supabase');
    
    // Extract root domain (e.g., "www.gymshark.com" -> "gymshark.com")
    const rootDomain = extractRootDomain(domain);
    
    // Try exact match first
    let { data, error } = await supabase
      .from('brands')
      .select('id')
      .ilike('domain_pattern', rootDomain)
      .single();
    
    // If no exact match, try pattern matching
    if (error || !data) {
      const { data: patternData, error: patternError } = await supabase
        .from('brands')
        .select('id, domain_pattern')
        .ilike('domain_pattern', `%${rootDomain}%`);
      
      if (!patternError && patternData && patternData.length > 0) {
        // Check if any pattern matches (handles cases where pattern is stored with/without www)
        const match = patternData.find(brand => {
          const brandDomain = extractRootDomain(brand.domain_pattern);
          return brandDomain === rootDomain;
        });
        
        if (match) {
          return match.id;
        }
      }
      
      return null;
    }
    
    return data.id;
  } catch (error) {
    console.error('Error getting brand ID:', error);
    return null;
  }
}

/**
 * Main context detection function
 */
export async function detectPageContext(): Promise<PageContext> {
  const url = window.location.href;
  const domain = window.location.hostname;
  
  // Detect affiliate params (Path A: Earned)
  const refCode = await detectAffiliateParams(url);
  let referringCreatorId: string | undefined;
  let pathType: PathType = 'DISCOVERY';
  
  if (refCode) {
    const creatorId = await getCreatorIdFromRef(refCode);
    if (creatorId) {
      referringCreatorId = creatorId;
      pathType = 'EARNED';
    }
  }
  
  // Get brand ID
  const brandId = await getBrandIdFromDomain(domain) || undefined;
  
  // Detect page type
  const isCheckoutPage = detectCheckoutPage();
  const isConfirmationPage = detectConfirmationPage();
  
  return {
    pathType,
    referringCreatorId,
    brandId,
    isCheckoutPage,
    isConfirmationPage
  };
}

