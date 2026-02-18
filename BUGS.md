# Bug List — Affiliate Autopilot Pipeline

**Last Updated:** 2026-02-18 07:45 UTC  
**Tested By:** VIGIL

---

## P0 Bugs (Critical — Blocking Deployment)

**None** ✅

---

## P1 Bugs (High Severity — Should Fix Before Launch)

**None** ✅

---

## P2 Bugs (Medium Severity — Non-Blocking, Recommended Fixes)

### P2-001: Malformed JSON Error Message Not Specific Enough

**Component:** Dashboard (`index.html` — `loadData()` error handling)

**Issue:**  
When `launches_data.json` contains invalid JSON syntax (e.g., trailing comma, missing quote), the error message is identical to when the file is missing:

```
"Could not load launches_data.json. Please check the file exists and is valid JSON."
```

**Impact:**  
Makes debugging harder. Developers cannot distinguish between:
- File not found (404)
- Invalid JSON syntax (SyntaxError)

**Recommended Fix:**
```javascript
catch (error) {
  let message = 'Could not load launches_data.json.';
  if (error.message.includes('Failed to fetch')) {
    message += ' File not found (404).';
  } else if (error instanceof SyntaxError) {
    message += ' Invalid JSON syntax. Check for trailing commas, quotes, or brackets.';
  } else {
    message += ` Error: ${error.message}`;
  }
  console.error('Failed to load data:', error);
  document.getElementById('grid').innerHTML = `
    <div style="grid-column:1/-1;text-align:center;padding:48px;color:#ef4444">
      <h3>Failed to Load Data</h3>
      <p>${message}</p>
    </div>
  `;
}
```

**Status:** Non-blocking (can ship without this fix)

---

### P2-002: No Loading Indicator While Fetching Data

**Component:** Dashboard (`index.html` — initial load UX)

**Issue:**  
When the page first loads, there's a 0.5-2 second window (depending on network speed) where:
- The grid is empty
- Stats show zeros
- No visual feedback that data is loading

On slow connections, users might think the page is broken.

**Recommended Fix:**

Add loading spinner in HTML:
```html
<div id="loading" style="display:flex; align-items:center; justify-content:center; min-height:50vh">
  <div style="text-align:center">
    <div style="font-size:48px; margin-bottom:16px">⏳</div>
    <p style="color:#94a3b8">Loading launches...</p>
  </div>
</div>
```

Update `loadData()`:
```javascript
async function loadData() {
  const loadingEl = document.getElementById('loading');
  const gridEl = document.getElementById('grid');
  
  try {
    loadingEl.style.display = 'flex';
    gridEl.style.display = 'none';
    
    const response = await fetch('launches_data.json');
    // ... rest of fetch logic ...
    
    loadingEl.style.display = 'none';
    gridEl.style.display = 'grid';
  } catch (error) {
    loadingEl.style.display = 'none';
    // ... error handling ...
  }
}
```

**Status:** Non-blocking (but recommended for professional polish)

---

## P3 Improvements (Nice-to-Have — Post-Launch Enhancements)

### P3-001: Add Search/Filter by Product Name

**Benefit:** Quickly find a specific launch by typing (e.g., "InstaDoodle")

**Implementation:**
- Add text input above filter buttons
- Filter `DATA` array by `product_name.toLowerCase().includes(searchTerm.toLowerCase())`
- Update grid in real-time as user types

**Priority:** Low (manual scrolling works fine for 51 launches)

---

### P3-002: Campaign Progress Indicator

**Benefit:** At-a-glance view of which launches have complete campaign materials

**Implementation:**
- Add badge on card corner showing campaign completeness (e.g., "📝 3/3" if brief, bonuses, emails all exist)
- Badge turns green when campaign is complete, gray when incomplete

**Priority:** Low (users can click to check)

---

### P3-003: Export Launch List to CSV

**Benefit:** Affiliates can export the launch calendar to Excel/Google Sheets

**Implementation:**
- Add "Export CSV" button in header
- Generate CSV from `DATA` array with columns: Product, Vendor, Date, Score, Platform, Price, Commission
- Trigger download via `Blob` + `URL.createObjectURL`

**Priority:** Low (current format is sufficient for browsing)

---

### P3-004: Accessibility Improvements (WCAG Compliance)

**Issues:**
- No `aria-label` attributes on buttons
- No `role="dialog"` on modal
- No focus trap in modal (can tab out)
- No visible focus indicators on filter buttons

**Recommended Fixes:**
- Add ARIA attributes for screen readers
- Implement focus trap in modal
- Add `:focus` styles to buttons

**Priority:** Low (not critical for internal tool)

---

## Edge Cases Already Handled ✅

| Scenario | Status |
|----------|--------|
| Empty `launches_data.json` | ✅ Displays "0 launches", no errors |
| Missing campaign markdown files | ✅ Modal shows "not yet created" placeholders |
| Product name with quotes/apostrophes | ✅ Escaped via `.replace(/'/g, "\\'")` |
| Network error fetching JSON | ✅ Error message displayed in grid |
| Multiple clicks on same card | ✅ Modal re-populates correctly |

---

## Summary

**Total Bugs Found:** 2 (P2)  
**Blocking Bugs:** 0  
**Production Status:** ✅ Ready to deploy

All critical functionality works correctly. The 2 P2 bugs are UX improvements that do not impact core functionality. Recommend deploying to production and addressing P2/P3 items in a future sprint.
