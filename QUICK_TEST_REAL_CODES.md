# Quick Test with Real Codes - Step by Step

## 🚀 Fast Track (5 minutes)

### 1. Find a Real Code (2 min)

**For Gymshark:**
- Visit: https://www.retailmenot.com/view/gymshark.com
- Or try common codes: `STUDENT15`, `WELCOME10`, `NEW10`
- Test it manually on gymshark.com/checkout

**For Athletic Greens:**
- Visit: https://www.athleticgreens.com
- Look for first-time customer offers
- Or check podcast sponsor codes

### 2. Install Dependencies (1 min)

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
npm install
```

### 3. Update Database (1 min)

Replace `YOUR_REAL_CODE` with an actual working code:

```bash
# Example: Update Alex Chen's Gymshark code
npm run codes:update alex_chen Gymshark YOUR_REAL_CODE "15% OFF"

# Verify it was added
npm run codes:list
```

### 4. Rebuild & Test Extension (1 min)

```bash
cd extension
npm run build
```

Then:
1. Reload extension in Chrome (chrome://extensions/)
2. Visit: `https://www.gymshark.com/checkout?ref=alex_chen`
3. Modal should appear with your real code
4. Click the offer - code should apply!

---

## 🔍 Validate Codes First (Optional but Recommended)

Before adding to database, test if code works:

```bash
npm run codes:validate https://www.gymshark.com/checkout YOUR_CODE
```

This opens a browser and tests the code automatically.

---

## 📝 Example Workflow

```bash
# 1. List current offers
npm run codes:list

# 2. Find a real code (manually or via scraper)
# Let's say you found: "STUDENT15" works for Gymshark

# 3. Validate it (optional)
npm run codes:validate https://www.gymshark.com/checkout STUDENT15

# 4. Add to database
npm run codes:update alex_chen Gymshark STUDENT15 "15% OFF"

# 5. Rebuild extension
cd extension && npm run build

# 6. Test in browser
# Visit: https://www.gymshark.com/checkout?ref=alex_chen
```

---

## ✅ Success Checklist

- [ ] Found a real working code
- [ ] Validated code works (optional)
- [ ] Updated database with `npm run codes:update`
- [ ] Verified with `npm run codes:list`
- [ ] Rebuilt extension
- [ ] Reloaded extension in Chrome
- [ ] Tested on checkout page
- [ ] Code applies successfully
- [ ] Attribution event logged in Supabase

---

## 🆘 Troubleshooting

**Code doesn't appear in modal:**
- Check: `npm run codes:list` - is code in database?
- Check: Is code `is_active = true`?
- Check: Does creator and brand match?

**Code doesn't apply:**
- Check browser console (F12) for errors
- Try manual paste (code should be in clipboard)
- Verify code works manually on website

**Can't find codes:**
- Try different coupon sites
- Check creator's social media
- Use the Python scraper: `cd scraper && python scraper.py`

---

## 💡 Pro Tips

1. **Use multiple codes per creator** - Have backups
2. **Test regularly** - Codes expire
3. **Track what works** - Monitor Supabase for successful applications
4. **Start simple** - Use one brand/creator first, then expand

