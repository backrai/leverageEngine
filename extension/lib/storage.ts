// Storage utilities for extension state
// Using browser localStorage as fallback for content scripts

async function getStorageValue(key: string): Promise<any> {
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    return new Promise((resolve) => {
      chrome.storage.local.get([key], (result) => {
        resolve(result[key]);
      });
    });
  }
  const value = localStorage.getItem(key);
  return value ? JSON.parse(value) : undefined;
}

async function setStorageValue(key: string, value: any): Promise<void> {
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [key]: value }, () => resolve());
    });
  }
  localStorage.setItem(key, JSON.stringify(value));
}

export interface UserState {
  userId: string;
  sessionId: string;
  currentBrandId?: string;
  currentPathType?: 'EARNED' | 'DISCOVERY';
  referringCreatorId?: string;
}

/**
 * Generate a UUID v4
 */
function generateUUID(): string {
  // Use crypto.randomUUID if available (modern browsers)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  
  // Fallback: Generate UUID v4 manually
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Get or create anonymous user ID (must be a valid UUID)
 */
export async function getUserId(): Promise<string> {
  let userId = await getStorageValue('userId');
  
  if (!userId) {
    // Generate a proper UUID v4 (required by database)
    userId = generateUUID();
    await setStorageValue('userId', userId);
  }
  
  // Validate it's a UUID format (in case old format exists)
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(userId)) {
    // Regenerate if it's not a valid UUID
    console.warn('[backrAI] Invalid UUID format, regenerating:', userId);
    userId = generateUUID();
    await setStorageValue('userId', userId);
  }
  
  return userId;
}

/**
 * Get or create session ID
 */
export async function getSessionId(): Promise<string> {
  let sessionId = await getStorageValue('sessionId');
  
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    await setStorageValue('sessionId', sessionId);
  }
  
  return sessionId;
}

/**
 * Store current page context
 */
export async function storePageContext(context: {
  brandId?: string;
  pathType?: 'EARNED' | 'DISCOVERY';
  referringCreatorId?: string;
}): Promise<void> {
  await setStorageValue('currentBrandId', context.brandId);
  await setStorageValue('currentPathType', context.pathType);
  await setStorageValue('referringCreatorId', context.referringCreatorId);
}

/**
 * Get stored page context
 */
export async function getStoredPageContext(): Promise<{
  brandId?: string;
  pathType?: 'EARNED' | 'DISCOVERY';
  referringCreatorId?: string;
}> {
  const brandId = await getStorageValue('currentBrandId');
  const pathType = await getStorageValue('currentPathType');
  const referringCreatorId = await getStorageValue('referringCreatorId');
  
  return {
    brandId,
    pathType,
    referringCreatorId
  };
}

/**
 * Store browsing history for AI suggestions
 */
export async function addToBrowsingHistory(creatorId: string, brandId: string): Promise<void> {
  const history = await getStorageValue('browsingHistory') || [];
  
  // Add to history (limit to last 50)
  history.unshift({ creatorId, brandId, timestamp: Date.now() });
  const limitedHistory = history.slice(0, 50);
  
  await setStorageValue('browsingHistory', limitedHistory);
}

/**
 * Get browsing history
 */
export async function getBrowsingHistory(): Promise<Array<{ creatorId: string; brandId: string; timestamp: number }>> {
  return await getStorageValue('browsingHistory') || [];
}

/**
 * Check if modal has been dismissed for this page
 * Uses URL + brandId as key to track per-page dismissals
 */
export async function isModalDismissed(brandId: string, modalType: 'incentive' | 'attribution'): Promise<boolean> {
  const url = window.location.href;
  const key = `modal_dismissed_${modalType}_${brandId}_${url}`;
  const dismissed = await getStorageValue(key);
  return dismissed === true;
}

/**
 * Mark modal as dismissed for this page
 */
export async function setModalDismissed(brandId: string, modalType: 'incentive' | 'attribution'): Promise<void> {
  const url = window.location.href;
  const key = `modal_dismissed_${modalType}_${brandId}_${url}`;
  await setStorageValue(key, true);
}

/**
 * Check if modal has been shown in this session (to prevent re-opening on same page)
 * Uses sessionStorage-like approach with a session key
 */
export async function hasModalBeenShown(brandId: string, modalType: 'incentive' | 'attribution'): Promise<boolean> {
  const sessionId = await getSessionId();
  const url = window.location.href;
  const key = `modal_shown_${modalType}_${brandId}_${url}_${sessionId}`;
  const shown = await getStorageValue(key);
  return shown === true;
}

/**
 * Mark modal as shown in this session
 */
export async function setModalShown(brandId: string, modalType: 'incentive' | 'attribution'): Promise<void> {
  const sessionId = await getSessionId();
  const url = window.location.href;
  const key = `modal_shown_${modalType}_${brandId}_${url}_${sessionId}`;
  await setStorageValue(key, true);
}

