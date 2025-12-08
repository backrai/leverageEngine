import type { PlasmoManifest } from "plasmo";

export default {
  manifest: {
    name: "backrAI Leverage Engine",
    description: "Universal attribution layer for the creator economy",
    version: "1.1.0",
    permissions: ["storage", "tabs", "activeTab"],
    host_permissions: ["https://*/*", "http://*/*"]
    // Let Plasmo auto-detect content scripts from contents/ folder
  }
} satisfies PlasmoManifest;

