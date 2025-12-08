#!/bin/bash
# Start Dashboard - Fixes EPERM error by changing to valid directory first

cd ~
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
echo "✅ Starting dashboard on port 3002..."
npx next dev -p 3002
