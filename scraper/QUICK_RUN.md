# Quick Run - YouTube Scraper

## If scripts don't work, run these commands directly:

### Step 1: Navigate to scraper directory
```bash
cd ~
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/scraper
```

### Step 2: Install dependencies (if needed)
```bash
pip3 install playwright supabase python-dotenv requests beautifulsoup4
python3 -m playwright install chromium
```

### Step 3: Run the scraper
```bash
python3 youtube_scraper.py '9c376992-3baa-446d-a9b5-cf9e9e1e8ef1' 10
```

**Replace the brand ID with your actual brand ID!**

## All in one command:

```bash
cd ~ && cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/scraper && python3 youtube_scraper.py '9c376992-3baa-446d-a9b5-cf9e9e1e8ef1' 10
```

## Check if dependencies are installed:

```bash
python3 -c "import playwright, supabase, dotenv; print('✅ All dependencies installed')"
```

If you get an error, install missing packages:
```bash
pip3 install <missing_package>
```

