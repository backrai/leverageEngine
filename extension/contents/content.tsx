import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { detectPageContext } from "../lib/context-detector";
import { 
  storePageContext, 
  getStoredPageContext,
  isModalDismissed,
  setModalDismissed,
  hasModalBeenShown,
  setModalShown
} from "../lib/storage";
import { IncentiveModal } from "../components/IncentiveModal";
import { AttributionModal } from "../components/AttributionModal";

// Early log to verify script is loading
console.log('[backrAI] Content script loaded!', {
  React: typeof React,
  createRoot: typeof createRoot,
  IncentiveModal: typeof IncentiveModal,
  AttributionModal: typeof AttributionModal,
  timestamp: new Date().toISOString()
});

function Content() {
  const [context, setContext] = useState<{
    pathType: 'EARNED' | 'DISCOVERY';
    referringCreatorId?: string;
    brandId?: string;
    isCheckoutPage: boolean;
    isConfirmationPage: boolean;
  } | null>(null);
  const [showIncentiveModal, setShowIncentiveModal] = useState(false);
  const [showAttributionModal, setShowAttributionModal] = useState(false);
  const [hasShownModal, setHasShownModal] = useState(false);

  useEffect(() => {
    initializeContext();
    
    // Re-check context on URL changes (SPA navigation)
    const observer = new MutationObserver(() => {
      initializeContext();
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    return () => observer.disconnect();
  }, []);

  async function initializeContext() {
    try {
      const pageContext = await detectPageContext();
      setContext(pageContext);
      
      // Store context for later use
      await storePageContext({
        brandId: pageContext.brandId,
        pathType: pageContext.pathType,
        referringCreatorId: pageContext.referringCreatorId
      });

      // Show Incentive Modal on checkout page
      if (pageContext.isCheckoutPage && pageContext.brandId) {
        // Check if modal has been dismissed or already shown
        const dismissed = await isModalDismissed(pageContext.brandId, 'incentive');
        const alreadyShown = await hasModalBeenShown(pageContext.brandId, 'incentive');
        
        if (!dismissed && !alreadyShown) {
          setShowIncentiveModal(true);
          setHasShownModal(true);
          await setModalShown(pageContext.brandId, 'incentive');
        }
      }

      // Show Attribution Modal on confirmation page (only for Discovery path)
      if (
        pageContext.isConfirmationPage &&
        pageContext.brandId &&
        pageContext.pathType === 'DISCOVERY'
      ) {
        // Check if modal has been dismissed or already shown
        const dismissed = await isModalDismissed(pageContext.brandId, 'attribution');
        const alreadyShown = await hasModalBeenShown(pageContext.brandId, 'attribution');
        
        if (!dismissed && !alreadyShown) {
          setShowAttributionModal(true);
          setHasShownModal(true);
          await setModalShown(pageContext.brandId, 'attribution');
        }
      }
    } catch (error) {
      console.error('Error initializing context:', error);
    }
  }

  // Close handlers - defined before early return
  const handleIncentiveModalClose = () => {
    setShowIncentiveModal(false);
    // Mark as dismissed asynchronously (don't await to keep handler sync)
    if (context?.brandId) {
      setModalDismissed(context.brandId, 'incentive').catch(err => {
        console.error('[backrAI] Error marking incentive modal as dismissed:', err);
      });
    }
  };

  const handleAttributionModalClose = () => {
    setShowAttributionModal(false);
    // Mark as dismissed asynchronously (don't await to keep handler sync)
    if (context?.brandId) {
      setModalDismissed(context.brandId, 'attribution').catch(err => {
        console.error('[backrAI] Error marking attribution modal as dismissed:', err);
      });
    }
  };

  if (!context || !context.brandId) {
    return null; // Don't show anything if we can't detect the brand
  }

  // Safety check: ensure components are defined
  if (typeof IncentiveModal === 'undefined' || typeof AttributionModal === 'undefined') {
    console.error('[backrAI] Modal components are not defined', {
      IncentiveModal: typeof IncentiveModal,
      AttributionModal: typeof AttributionModal
    });
    return null;
  }

  // Ensure pathType has a valid value to prevent undefined
  const pathType: 'EARNED' | 'DISCOVERY' = context.pathType || 'DISCOVERY';
  
  // Ensure brandId is a string (not undefined)
  if (!context.brandId || typeof context.brandId !== 'string') {
    console.error('[backrAI] Invalid brandId:', context.brandId);
    return null;
  }

  // Double-check components are functions before rendering
  console.log('[backrAI] Content render - checking components:', {
    showIncentiveModal,
    showAttributionModal,
    brandId: context.brandId,
    IncentiveModalType: typeof IncentiveModal,
    AttributionModalType: typeof AttributionModal,
    IncentiveModalIsFunction: typeof IncentiveModal === 'function',
    AttributionModalIsFunction: typeof AttributionModal === 'function'
  });

  if (typeof IncentiveModal !== 'function') {
    console.error('[backrAI] IncentiveModal is not a function:', typeof IncentiveModal, IncentiveModal);
    return null;
  }

  if (typeof AttributionModal !== 'function') {
    console.error('[backrAI] AttributionModal is not a function:', typeof AttributionModal, AttributionModal);
    return null;
  }

  try {
    // Use React.createElement to be more explicit and avoid JSX issues
    const modalElements: React.ReactElement[] = [];

    if (showIncentiveModal && context.brandId) {
      console.log('[backrAI] Creating IncentiveModal element...');
      try {
        const element = React.createElement(IncentiveModal, {
          key: 'incentive-modal',
          brandId: context.brandId,
          referringCreatorId: context.referringCreatorId,
          pathType: pathType,
          onClose: handleIncentiveModalClose
        });
        console.log('[backrAI] IncentiveModal element created:', element);
        modalElements.push(element);
      } catch (createError) {
        console.error('[backrAI] Error creating IncentiveModal element:', createError);
        throw createError;
      }
    }

    if (showAttributionModal && context.brandId) {
      console.log('[backrAI] Creating AttributionModal element...');
      try {
        const element = React.createElement(AttributionModal, {
          key: 'attribution-modal',
          brandId: context.brandId,
          pathType: pathType,
          onClose: handleAttributionModalClose
        });
        console.log('[backrAI] AttributionModal element created:', element);
        modalElements.push(element);
      } catch (createError) {
        console.error('[backrAI] Error creating AttributionModal element:', createError);
        throw createError;
      }
    }

    if (modalElements.length === 0) {
      return null;
    }

    console.log('[backrAI] Creating fragment with', modalElements.length, 'elements');
    return React.createElement(React.Fragment, null, ...modalElements);
  } catch (error) {
    console.error('[backrAI] Error rendering modals:', error);
    if (error instanceof Error) {
      console.error('[backrAI] Error stack:', error.stack);
    }
    return null;
  }
}

// Wait for DOM to be ready
function initExtension() {
  try {
    console.log('[backrAI] Initializing extension...');
    
    // Verify React is available
    if (typeof React === 'undefined') {
      console.error('[backrAI] React is not available');
      return;
    }
    console.log('[backrAI] React is available:', typeof React, React.version || 'unknown version');

    // Verify createRoot is available
    if (typeof createRoot === 'undefined') {
      console.error('[backrAI] createRoot is not available');
      return;
    }
    console.log('[backrAI] createRoot is available:', typeof createRoot);

    // Verify components are imported - log them
    console.log('[backrAI] Checking components...', {
      IncentiveModal: typeof IncentiveModal,
      AttributionModal: typeof AttributionModal,
      IncentiveModalValue: IncentiveModal,
      AttributionModalValue: AttributionModal
    });

    if (typeof IncentiveModal === 'undefined') {
      console.error('[backrAI] IncentiveModal is not imported correctly');
      return;
    }

    if (typeof AttributionModal === 'undefined') {
      console.error('[backrAI] AttributionModal is not imported correctly');
      return;
    }

    // Check if root already exists (prevent duplicate mounts)
    let container = document.getElementById("backrai-root");
    if (container) {
      // Root already exists, don't mount again
      console.warn('[backrAI] Root already exists, skipping mount');
      return;
    }

    container = document.createElement("div");
    container.id = "backrai-root";
    document.body.appendChild(container);
    
    console.log('[backrAI] Creating root and rendering Content...');
    const root = createRoot(container);
    
    // Try rendering with explicit error handling
    try {
      root.render(React.createElement(Content));
      console.log('[backrAI] Extension mounted successfully');
    } catch (renderError) {
      console.error('[backrAI] Error during render:', renderError);
      if (renderError instanceof Error) {
        console.error('[backrAI] Render error details:', {
          message: renderError.message,
          name: renderError.name,
          stack: renderError.stack
        });
      }
      throw renderError;
    }
  } catch (error) {
    console.error('[backrAI] Error mounting extension:', error);
    if (error instanceof Error) {
      console.error('[backrAI] Error details:', {
        message: error.message,
        name: error.name,
        stack: error.stack,
        React: typeof React,
        createRoot: typeof createRoot,
        IncentiveModal: typeof IncentiveModal,
        AttributionModal: typeof AttributionModal
      });
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initExtension);
} else {
  // DOM is already ready
  initExtension();
}

