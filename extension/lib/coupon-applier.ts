// Coupon code application logic

/**
 * Checks if an input field is likely a coupon code field (not zip code, etc.)
 */
function isCouponField(input: HTMLInputElement): boolean {
  const name = (input.name || '').toLowerCase();
  const id = (input.id || '').toLowerCase();
  const placeholder = (input.placeholder || '').toLowerCase();
  const ariaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
  const type = input.type.toLowerCase();
  const maxLength = input.maxLength;
  
  // Exclude zip/postal code fields
  const zipCodeIndicators = [
    'zip', 'postal', 'postcode', 'pincode', 'zipcode', 'postalcode',
    'billing.*zip', 'shipping.*zip', 'address.*zip'
  ];
  
  const allText = `${name} ${id} ${placeholder} ${ariaLabel}`.toLowerCase();
  
  for (const indicator of zipCodeIndicators) {
    const regex = new RegExp(indicator.replace('*', '.*'), 'i');
    if (regex.test(allText)) {
      console.log('[backrAI] Excluding zip/postal code field:', { name, id, placeholder });
      return false;
    }
  }
  
  // Exclude fields that are clearly not coupon fields
  if (type === 'tel' || type === 'email' || type === 'password') {
    return false;
  }
  
  // Exclude fields with very short maxLength (likely zip codes)
  if (maxLength > 0 && maxLength <= 10 && !allText.includes('coupon') && !allText.includes('promo') && !allText.includes('code')) {
    // Might be zip code, but check context
    const label = findLabelText(input);
    if (label && (label.includes('zip') || label.includes('postal') || label.includes('postcode'))) {
      return false;
    }
  }
  
  // Prefer fields that explicitly mention coupon/promo/discount
  const couponIndicators = ['coupon', 'promo', 'discount', 'voucher', 'code'];
  const hasCouponIndicator = couponIndicators.some(indicator => 
    allText.includes(indicator) && !allText.includes('zip') && !allText.includes('postal')
  );
  
  return hasCouponIndicator;
}

/**
 * Finds label text associated with an input field
 */
function findLabelText(input: HTMLInputElement): string {
  // Check for associated label
  if (input.id) {
    const label = document.querySelector(`label[for="${input.id}"]`);
    if (label) return label.textContent || '';
  }
  
  // Check for parent label
  const parentLabel = input.closest('label');
  if (parentLabel) return parentLabel.textContent || '';
  
  // Check for nearby label
  const container = input.closest('div, fieldset, section');
  if (container) {
    const label = container.querySelector('label');
    if (label) return label.textContent || '';
  }
  
  return '';
}

/**
 * Attempts to apply a coupon code to the current checkout page
 * Tries multiple strategies to find and fill the coupon input field
 */
export async function applyCouponCode(code: string): Promise<void> {
  // Debug: Log what code we're trying to apply
  console.log('[backrAI] applyCouponCode called with:', code);
  
  // Validate code is not empty and looks like a code (not discount text)
  if (!code || code.trim().length === 0) {
    throw new Error('Coupon code is empty');
  }
  
  // Check if code looks like discount text (contains % or "OFF")
  if (code.includes('%') || code.toUpperCase().includes('OFF')) {
    console.warn('[backrAI] WARNING: Code appears to be discount text, not a code:', code);
    // Don't throw, but log warning - might be intentional
  }
  
  // Strategy 1: Find input by common name attributes (with validation)
  const nameSelectors = [
    'input[name*="coupon" i]',
    'input[name*="promo" i]',
    'input[name*="discount" i]',
    'input[name*="voucher" i]',
    'input[name*="code" i]' // Check this last to avoid zip codes
  ];

  for (const selector of nameSelectors) {
    const inputs = document.querySelectorAll<HTMLInputElement>(selector);
    
    // Filter to only coupon fields
    for (const input of Array.from(inputs)) {
      if (isCouponField(input)) {
        console.log('[backrAI] Found coupon input field:', selector, { name: input.name, id: input.id });
        // Clear any existing value first
        input.value = '';
        // Set the code value (trimmed to remove whitespace)
        input.value = code.trim();
        // Trigger events to ensure the value is recognized
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
        
        console.log('[backrAI] Set input value to:', input.value);
        
        // Try to find and click apply button
        const applyButton = findApplyButton(input);
        if (applyButton) {
          applyButton.click();
        }
        
        return;
      }
    }
  }

  // Strategy 2: Find input by common id attributes (with validation)
  const idSelectors = [
    'input[id*="coupon" i]',
    'input[id*="promo" i]',
    'input[id*="discount" i]',
    'input[id*="voucher" i]',
    'input[id*="code" i]' // Check this last
  ];

  for (const selector of idSelectors) {
    const inputs = document.querySelectorAll<HTMLInputElement>(selector);
    
    // Filter to only coupon fields
    for (const input of Array.from(inputs)) {
      if (isCouponField(input)) {
        console.log('[backrAI] Found coupon input field (by ID):', selector, { name: input.name, id: input.id });
        input.value = '';
        input.value = code.trim();
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
        console.log('[backrAI] Set input value to:', input.value);
        
        const applyButton = findApplyButton(input);
        if (applyButton) {
          applyButton.click();
        }
        
        return;
      }
    }
  }

  // Strategy 3: Find input by placeholder text (with validation)
  const placeholderSelectors = [
    'input[placeholder*="coupon" i]',
    'input[placeholder*="promo" i]',
    'input[placeholder*="discount" i]',
    'input[placeholder*="voucher" i]',
    'input[placeholder*="code" i]' // Check this last
  ];

  for (const selector of placeholderSelectors) {
    const inputs = document.querySelectorAll<HTMLInputElement>(selector);
    
    // Filter to only coupon fields
    for (const input of Array.from(inputs)) {
      if (isCouponField(input)) {
        console.log('[backrAI] Found coupon input field (by placeholder):', selector, { name: input.name, id: input.id });
        input.value = '';
        input.value = code.trim();
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
        console.log('[backrAI] Set input value to:', input.value);
        
        const applyButton = findApplyButton(input);
        if (applyButton) {
          applyButton.click();
        }
        
        return;
      }
    }
  }

  // Strategy 4: Copy to clipboard as fallback
  try {
    // Check if clipboard API is available and we have permission
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(code);
        // Show a notification that code was copied
        showNotification(`Coupon code "${code}" copied to clipboard! Paste it in the coupon field.`);
        return;
      } catch (clipboardError: any) {
        // Clipboard might require permissions or be unavailable
        console.warn('[backrAI] Clipboard API failed, trying fallback method:', clipboardError);
        
        // Fallback: Use execCommand (deprecated but more compatible)
        const textArea = document.createElement('textarea');
        textArea.value = code;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          const successful = document.execCommand('copy');
          document.body.removeChild(textArea);
          
          if (successful) {
            showNotification(`Coupon code "${code}" copied to clipboard! Paste it in the coupon field.`);
            return;
          }
        } catch (execError) {
          document.body.removeChild(textArea);
          console.error('[backrAI] execCommand also failed:', execError);
        }
      }
    }
    
    // If all clipboard methods fail, show the code in an alert
    alert(`Coupon code: ${code}\n\nPlease copy this code and paste it in the coupon field.`);
  } catch (error) {
    console.error('[backrAI] Failed to copy to clipboard:', error);
    // Don't throw - just show the code to user
    alert(`Coupon code: ${code}\n\nPlease copy this code and paste it in the coupon field.`);
  }
}

/**
 * Finds the apply/submit button near a coupon input field
 */
function findApplyButton(input: HTMLElement): HTMLElement | null {
  // Look for button in the same form or parent container
  const form = input.closest('form');
  if (form) {
    const button = form.querySelector<HTMLElement>(
      'button[type="submit"], ' +
      'button:contains("apply"), ' +
      'button:contains("Apply"), ' +
      'input[type="submit"]'
    );
    if (button) return button;
  }

  // Look for button with common text
  const container = input.closest('div, section, fieldset');
  if (container) {
    const buttons = container.querySelectorAll<HTMLElement>('button, input[type="button"]');
    for (const button of Array.from(buttons)) {
      const text = button.textContent?.toLowerCase() || '';
      if (text.includes('apply') || text.includes('submit') || text.includes('use')) {
        return button;
      }
    }
  }

  return null;
}

/**
 * Shows a temporary notification to the user
 */
function showNotification(message: string): void {
  // Create notification element
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #007bff;
    color: white;
    padding: 16px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    max-width: 300px;
  `;

  document.body.appendChild(notification);

  // Remove after 3 seconds
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

