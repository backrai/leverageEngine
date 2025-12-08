#!/usr/bin/env node
/**
 * Validate a coupon code on a brand's website
 * Usage: node scripts/validate-code.js <brand_url> <code>
 * Example: node scripts/validate-code.js https://www.gymshark.com/checkout SAVE15
 */

const puppeteer = require('puppeteer');

async function validateCode(brandUrl, code) {
  console.log(`\n🔍 Validating code "${code}" on ${brandUrl}\n`);

  const browser = await puppeteer.launch({ headless: false }); // Show browser for debugging
  const page = await browser.newPage();

  try {
    // Navigate to checkout/cart page
    await page.goto(brandUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    await page.waitForTimeout(2000);

    // Try to find coupon input field
    const couponSelectors = [
      'input[name*="coupon" i]',
      'input[name*="code" i]',
      'input[name*="promo" i]',
      'input[name*="discount" i]',
      'input[id*="coupon" i]',
      'input[id*="code" i]',
      'input[id*="promo" i]',
      'input[placeholder*="coupon" i]',
      'input[placeholder*="code" i]',
      'input[placeholder*="promo" i]',
    ];

    let inputFound = false;
    for (const selector of couponSelectors) {
      try {
        const input = await page.$(selector);
        if (input) {
          console.log(`✅ Found coupon input: ${selector}`);
          await input.type(code, { delay: 100 });
          await page.waitForTimeout(500);

          // Try to find and click apply button
          const applySelectors = [
            'button[type="submit"]',
            'button:has-text("Apply")',
            'button:has-text("apply")',
            'input[type="submit"]',
            'button[aria-label*="apply" i]',
          ];

          for (const btnSelector of applySelectors) {
            try {
              const button = await page.$(btnSelector);
              if (button) {
                console.log(`✅ Found apply button: ${btnSelector}`);
                await button.click();
                await page.waitForTimeout(3000);
                break;
              }
            } catch (e) {
              // Continue trying other selectors
            }
          }

          // Check for success/error messages
          await page.waitForTimeout(2000);
          const pageContent = await page.content();
          const bodyText = await page.evaluate(() => document.body.innerText);

          const errorIndicators = [
            'invalid',
            'expired',
            'not found',
            'does not exist',
            'error',
            'try again',
          ];

          const successIndicators = [
            'applied',
            'valid',
            'discount',
            'saved',
            'success',
          ];

          const hasError = errorIndicators.some(indicator =>
            bodyText.toLowerCase().includes(indicator)
          );
          const hasSuccess = successIndicators.some(indicator =>
            bodyText.toLowerCase().includes(indicator)
          );

          if (hasError) {
            console.log('❌ Code appears to be INVALID');
            console.log('   (Found error indicators on page)');
            return false;
          } else if (hasSuccess) {
            console.log('✅ Code appears to be VALID');
            console.log('   (Found success indicators on page)');
            return true;
          } else {
            console.log('⚠️  Unable to determine validity');
            console.log('   (No clear success/error indicators found)');
            console.log('   Code has been entered - please check manually');
            return null;
          }

          inputFound = true;
          break;
        }
      } catch (e) {
        // Continue trying other selectors
      }
    }

    if (!inputFound) {
      console.log('❌ Could not find coupon input field');
      console.log('   Please check the page manually');
      return null;
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    return null;
  } finally {
    // Keep browser open for 10 seconds so user can see result
    console.log('\n⏳ Keeping browser open for 10 seconds for inspection...');
    await page.waitForTimeout(10000);
    await browser.close();
  }
}

// Main
const args = process.argv.slice(2);

if (args.length !== 2) {
  console.log('Usage: node scripts/validate-code.js <brand_url> <code>');
  console.log('Example: node scripts/validate-code.js https://www.gymshark.com/checkout SAVE15');
  process.exit(1);
}

const [brandUrl, code] = args;
validateCode(brandUrl, code).then(result => {
  if (result === true) {
    process.exit(0);
  } else if (result === false) {
    process.exit(1);
  } else {
    process.exit(2);
  }
});

