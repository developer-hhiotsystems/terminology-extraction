# Glossary App - Complete Testing Procedure

## Pre-Testing Checklist

### 1. Verify Environment Setup

```bash
# Check Python version (should be 3.8+)
python --version

# Check Node.js version (should be 14+)
node --version

# Check if virtual environment exists
ls venv/Scripts/python.exe
```

### 2. Install Dependencies (if needed)

```bash
# Backend dependencies
.\venv\Scripts\activate
pip install -r requirements.txt

# Frontend dependencies
cd src/frontend
npm install
cd ../..
```

---

## Testing Phase 1: Backend Server

### Step 1: Start Backend Server

```bash
# Method 1: Using the dev script
scripts\backend-dev.bat

# Method 2: Direct command
venv\Scripts\python.exe src\backend\app.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9123
```

**What to Check:**
- ✓ Server starts without errors
- ✓ No import errors
- ✓ Port 9123 is listening

### Step 2: Test Backend Health

**Open a new terminal and run:**

```bash
# Test health endpoint
curl http://localhost:9123/health

# Expected response:
# {"status": "healthy", "database": "connected", "fts5": "available"}
```

### Step 3: Test API Endpoints

```bash
# Test glossary endpoint (should return entries)
curl http://localhost:9123/api/glossary?limit=5

# Test search endpoint (Phase A - FTS5 Search)
curl http://localhost:9123/api/search/autocomplete?query=bio

# Test search stats (Phase E - Performance monitoring)
curl http://localhost:9123/api/search/stats

# Test performance stats (Phase E)
curl http://localhost:9123/api/performance/stats
```

**Expected Results:**
- All endpoints return JSON data
- No 500 errors
- Search returns relevant results

---

## Testing Phase 2: Frontend Application

### Step 4: Start Frontend Dev Server

**Open a new terminal:**

```bash
cd src/frontend
npm run dev
```

**Expected Output:**
```
VITE v4.x.x ready in XXX ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**What to Check:**
- ✓ Vite dev server starts
- ✓ No compilation errors
- ✓ Port 3000 is available

### Step 5: Open Application in Browser

1. Open browser: `http://localhost:3000`
2. You should see the Glossary App homepage

**Expected UI Elements:**
- Navigation tabs: Home, Glossary, Documents, Statistics, Admin
- Clean, responsive layout
- No console errors (press F12 to check)

---

## Testing Phase 3: Core Features

### Step 6: Test Glossary List (Basic Feature)

1. Click on **"Glossary"** tab
2. You should see a list of glossary entries

**What to Test:**
- ✓ Entries display with English and German terms
- ✓ Pagination works (if more than 50 entries)
- ✓ Each entry shows: term, translation, definition, source

**Expected Result:**
- List of bilingual glossary entries loads successfully

### Step 7: Test Search (Phase A - FTS5 Search)

1. Look for the **Search Bar** at the top of the Glossary page
2. Type a search term (e.g., "reactor", "bio", "process")

**What to Test:**
- ✓ Autocomplete suggestions appear as you type
- ✓ Search results appear quickly (should be 10.6x faster)
- ✓ Results are relevant to your search term
- ✓ Highlighting of matching terms

**Expected Result:**
- Fast, accurate search with autocomplete

### Step 8: Test Advanced Search (Phase A)

1. Click **"Advanced Search"** button or toggle
2. Try different search modes:
   - Simple search
   - Phrase search ("exact phrase")
   - Boolean search (term1 AND term2)
   - Proximity search (terms near each other)

**What to Test:**
- ✓ Different search modes work correctly
- ✓ Filters can be applied (language, validation status)
- ✓ Results update in real-time

**Expected Result:**
- Multiple search modes with accurate filtering

---

## Testing Phase 4: New Features (Phase B - UI/UX)

### Step 9: Test Bilingual Card View (Phase B)

1. In the Glossary list, look for **Card View** toggle/option
2. Switch to card view

**What to Test:**
- ✓ Terms display in bilingual card format
- ✓ English and German side-by-side
- ✓ Clean, readable layout
- ✓ Responsive design (resize browser window)

**Expected Result:**
- Beautiful bilingual card display

### Step 10: Test Term Detail View (Phase B)

1. Click on any glossary entry
2. Term detail view should open

**What to Test:**
- ✓ Full term information displayed
- ✓ Both languages visible
- ✓ Source document information
- ✓ Related terms (if available)
- ✓ Edit functionality (if permissions allow)

**Expected Result:**
- Detailed term view with all information

### Step 11: Test Extraction Progress (Phase B)

1. Go to **Documents** tab
2. Upload a PDF document (use test-data/*.pdf)

**What to Test:**
- ✓ Upload progress bar appears
- ✓ Extraction progress shows percentage
- ✓ Status updates in real-time
- ✓ Completion notification

**Expected Result:**
- Real-time extraction progress tracking

---

## Testing Phase 5: Relationship Features (Phase C)

### Step 12: Test Relationship Extraction (Phase C)

1. Navigate to a term with relationships
2. Look for **"Relationships"** section

**What to Test:**
- ✓ Relationships are displayed (uses, measures, part_of, etc.)
- ✓ Relationship types are labeled
- ✓ Related terms are clickable

**Expected Result:**
- Terms show meaningful relationships

### Step 13: Test Graph Visualization (Phase C)

1. Look for **"Relationship Graph"** or **"Explore Relationships"** button
2. Click to open graph visualization

**What to Test:**
- ✓ D3.js graph renders correctly
- ✓ Nodes represent terms
- ✓ Edges represent relationships
- ✓ Interactive: zoom, pan, drag nodes
- ✓ Click nodes to view term details
- ✓ Filter by relationship type

**Expected Result:**
- Interactive relationship graph with D3.js visualization

---

## Testing Phase 6: Performance Features (Phase E)

### Step 14: Test Search Performance (Phase E)

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Perform a search query
4. Check the response time

**What to Test:**
- ✓ Search queries return in < 100ms (cached)
- ✓ First search may be slower (~500ms)
- ✓ Subsequent searches are very fast (10-50x faster)

**Expected Result:**
- Noticeably fast search performance

### Step 15: Test Cache Statistics (Phase E)

```bash
# Check cache stats via API
curl http://localhost:9123/api/cache/stats
```

**What to Test:**
- ✓ Cache hit rate > 70% (after some usage)
- ✓ LRU cache statistics displayed
- ✓ Memory usage reasonable

**Expected Result:**
- High cache hit rate indicating effective caching

### Step 16: Test Performance Monitoring (Phase E)

```bash
# Get performance statistics
curl http://localhost:9123/api/performance/stats
```

**What to Test:**
- ✓ Query performance metrics (avg, median, p95, p99)
- ✓ Endpoint latency tracking
- ✓ Slow query detection

**Expected Result:**
- Detailed performance metrics with percentiles

---

## Testing Phase 7: Production Features (Phase D)

### Step 17: Test Health Monitoring (Phase D)

```bash
# Check health endpoint
curl http://localhost:9123/api/health

# Check database health
curl http://localhost:9123/api/health/database
```

**What to Test:**
- ✓ Health checks return status
- ✓ Database connectivity confirmed
- ✓ FTS5 availability verified

**Expected Result:**
- All health checks pass

### Step 18: Test Error Tracking (Phase D)

1. Intentionally cause an error (e.g., invalid search query)
2. Check error statistics:

```bash
curl http://localhost:9123/api/errors/stats
```

**What to Test:**
- ✓ Errors are logged
- ✓ Error statistics tracked
- ✓ Error types categorized

**Expected Result:**
- Comprehensive error tracking

---

## Testing Phase 8: Database Features

### Step 19: Test Database Indexes (Phase E)

```bash
# Run database optimization
venv\Scripts\python.exe scripts\optimize_database.py
```

**What to Test:**
- ✓ Script runs without errors
- ✓ Reports index creation
- ✓ Shows performance improvements

**Expected Result:**
- Database optimized with 15+ indexes

### Step 20: Test FTS5 Search Index (Phase A)

```bash
# Verify FTS5 index
venv\Scripts\python.exe scripts\check_fts5.py
```

**What to Test:**
- ✓ FTS5 index exists
- ✓ Index has entries
- ✓ Search functionality works

**Expected Result:**
- FTS5 index fully functional

---

## Testing Phase 9: Document Upload & Extraction

### Step 21: Test PDF Upload

1. Go to **Documents** tab
2. Click **"Upload Document"** or **"New Document"**
3. Upload a PDF from `test-data/` folder

**What to Test:**
- ✓ File upload works
- ✓ File validation (PDF only)
- ✓ Progress indicator shows
- ✓ Document appears in list after upload

**Expected Result:**
- PDF uploads successfully

### Step 22: Test Term Extraction

1. After uploading PDF, check extraction status
2. Wait for extraction to complete

**What to Test:**
- ✓ Extraction starts automatically
- ✓ Progress updates in real-time
- ✓ Terms are extracted and added to glossary
- ✓ New terms appear in glossary list

**Expected Result:**
- Terms automatically extracted from PDF

---

## Testing Phase 10: Admin & Statistics

### Step 23: Test Statistics Page

1. Click **"Statistics"** tab
2. View glossary statistics

**What to Test:**
- ✓ Total terms count
- ✓ Language distribution
- ✓ Validation status breakdown
- ✓ Source documents count
- ✓ Charts/graphs display correctly

**Expected Result:**
- Comprehensive statistics dashboard

### Step 24: Test Admin Functions (if available)

1. Click **"Admin"** tab
2. Test admin features:
   - Database reset (use with caution!)
   - Cache management
   - System health

**What to Test:**
- ✓ Admin controls work
- ✓ Confirmations appear for destructive actions
- ✓ System responds correctly

**Expected Result:**
- Admin functions work as expected

---

## Performance Benchmarks

### Expected Performance Metrics:

| Feature | Expected Speed | Notes |
|---------|---------------|-------|
| **Search (FTS5)** | < 100ms | 10.6x faster than LIKE |
| **Autocomplete** | < 50ms | Cached results |
| **API Response** | < 200ms | First request |
| **Cached API** | < 20ms | Subsequent requests |
| **Page Load** | < 2s | Initial load |
| **Graph Render** | < 1s | D3.js visualization |

### Cache Hit Rates (Phase E):

| Cache Type | Target Hit Rate |
|-----------|----------------|
| **Query Cache** | > 70% |
| **Search Cache** | > 80% |
| **API Cache** | > 60% |

---

## Troubleshooting

### Backend Won't Start

```bash
# Check if port is in use
netstat -ano | findstr :9123

# Kill process if needed
taskkill /F /PID <PID>

# Restart backend
venv\Scripts\python.exe src\backend\app.py
```

### Frontend Won't Start

```bash
# Check if port is in use
netstat -ano | findstr :3000

# Kill process if needed
taskkill /F /PID <PID>

# Clear node_modules and reinstall
cd src/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database Issues

```bash
# Reinitialize FTS5
venv\Scripts\python.exe scripts\initialize_fts5.py

# Optimize database
venv\Scripts\python.exe scripts\optimize_database.py

# Check database health
venv\Scripts\python.exe scripts\check_fts5.py
```

### Search Not Working

```bash
# Verify FTS5 index
venv\Scripts\python.exe scripts\verify_fts5_direct.py

# Rebuild index if needed
venv\Scripts\python.exe scripts\initialize_fts5.py
```

---

## Quick Test Summary Checklist

### Backend Tests:
- [ ] Backend server starts (port 9123)
- [ ] Health endpoint responds
- [ ] API endpoints return data
- [ ] Search API works
- [ ] Performance monitoring active

### Frontend Tests:
- [ ] Frontend dev server starts (port 3000)
- [ ] Homepage loads
- [ ] Navigation works
- [ ] No console errors

### Feature Tests:
- [ ] Glossary list displays
- [ ] Search works (FTS5)
- [ ] Autocomplete works
- [ ] Advanced search modes work
- [ ] Bilingual card view works
- [ ] Term detail view works
- [ ] Relationship graph renders
- [ ] Document upload works
- [ ] Term extraction works
- [ ] Statistics page displays

### Performance Tests:
- [ ] Search < 100ms
- [ ] Cache hit rate > 70%
- [ ] Page load < 2s
- [ ] API response < 200ms

---

## Next Steps After Testing

1. **If all tests pass:**
   - Your application is ready for production!
   - Review `docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md` for deployment

2. **If some tests fail:**
   - Check troubleshooting section above
   - Review error logs in browser console (F12)
   - Check backend logs in terminal
   - Verify all dependencies installed

3. **For production deployment:**
   - Follow `docs/PHASE_D_COMPLETION_GUIDE.md`
   - Set up production environment variables
   - Configure CDN (see `config/cloudflare-cdn.md`)
   - Run performance optimization scripts

---

## Additional Resources

- **Phase Documentation:**
  - Phase A: `docs/PHASE_A_COMPLETION_GUIDE.md`
  - Phase B: `docs/PHASE_B_COMPLETION_GUIDE.md`
  - Phase C: `docs/PHASE_C_COMPLETION_GUIDE.md`
  - Phase D: `docs/PHASE_D_COMPLETION_GUIDE.md`
  - Phase E: `docs/PHASE_E_COMPLETION_GUIDE.md`

- **API Documentation:**
  - FTS5 Search: `docs/FTS5_SEARCH_API_GUIDE.md`
  - Performance: `docs/PHASE_E_COMPLETION_GUIDE.md`

- **Deployment:**
  - Checklist: `docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md`
  - Security: `docs/SECURITY_GUIDE.md`
  - Monitoring: `docs/HEALTH_MONITORING_GUIDE.md`

---

**Ready to test? Start with Step 1 above!** 🚀
