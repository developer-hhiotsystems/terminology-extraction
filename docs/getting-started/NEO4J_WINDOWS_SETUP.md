# Neo4j Setup for Windows (Without Docker)

**Guide for installing and running Neo4j locally on Windows**

---

## 📋 Overview

This guide provides instructions for installing Neo4j Community Edition directly on Windows without using Docker.

---

## 🚀 Installation Methods

Choose one of these methods:

### **Method 1: Neo4j Desktop (Recommended for Development)**

Neo4j Desktop is the easiest way to get started on Windows.

#### Step 1: Download Neo4j Desktop

1. Visit: https://neo4j.com/download/
2. Click "Download Neo4j Desktop"
3. Fill in the form (optional) or click "Download without form"
4. Save the installer (e.g., `neo4j-desktop-1.5.9-setup.exe`)

#### Step 2: Install Neo4j Desktop

1. Run the installer
2. Follow the installation wizard
3. Accept the license agreement
4. Choose installation directory (default: `C:\Users\YourName\AppData\Local\Programs\Neo4j Desktop`)
5. Complete installation

#### Step 3: Create a Database

1. **Open Neo4j Desktop**
2. Click **"New"** → **"Create project"**
3. Name your project (e.g., "Glossary App")
4. Click **"Add"** → **"Local DBMS"**
5. Set database name: `glossary-dev`
6. Set password: `devpassword` (or your choice)
7. Version: Select **Neo4j 5.x** (latest)
8. Click **"Create"**

#### Step 4: Configure Database

1. Click the **"..."** menu on your database
2. Select **"Settings"**
3. Add these lines at the end:

```properties
# Allow connections from your app
dbms.connector.bolt.listen_address=0.0.0.0:7687
dbms.connector.http.listen_address=0.0.0.0:7474

# Memory settings (adjust based on your RAM)
dbms.memory.heap.max_size=2G
dbms.memory.pagecache.size=1G

# Enable APOC plugin (optional but useful)
dbms.security.procedures.unrestricted=apoc.*
```

4. Click **"Apply"**

#### Step 5: Install APOC Plugin (Optional)

1. Click the **"Plugins"** tab
2. Find **"APOC"** in the list
3. Click **"Install"**
4. Wait for installation to complete

#### Step 6: Start the Database

1. Click the **"Start"** button
2. Wait for status to show **"Running"** (green dot)
3. Note the connection details:
   - **Bolt URL:** `bolt://localhost:7687`
   - **HTTP URL:** `http://localhost:7474`

#### Step 7: Test Connection

1. Click **"Open with Browser"** or visit `http://localhost:7474`
2. Login credentials:
   - **Username:** `neo4j`
   - **Password:** `devpassword` (or what you set)
3. Run test query:
   ```cypher
   RETURN "Neo4j is running!" AS message
   ```

---

### **Method 2: Neo4j Community Server (Manual Installation)**

For a more traditional server setup:

#### Step 1: Download Neo4j Community

1. Visit: https://neo4j.com/download-center/#community
2. Select **"Neo4j Community Server"**
3. Choose **Windows** tab
4. Download the ZIP file (e.g., `neo4j-community-5.14.0-windows.zip`)

#### Step 2: Extract Neo4j

1. Extract ZIP to a folder (e.g., `C:\neo4j`)
2. Your structure should look like:
   ```
   C:\neo4j\
     ├── bin\
     ├── conf\
     ├── data\
     ├── lib\
     └── ...
   ```

#### Step 3: Configure Neo4j

1. Open `C:\neo4j\conf\neo4j.conf` in a text editor
2. Find and uncomment these lines (remove `#`):

```properties
# Bolt connector
server.bolt.enabled=true
server.bolt.listen_address=0.0.0.0:7687

# HTTP connector
server.http.enabled=true
server.http.listen_address=0.0.0.0:7474

# Memory settings
server.memory.heap.max_size=2G
server.memory.pagecache.size=1G

# Default database
initial.dbms.default_database=neo4j

# Security
dbms.security.auth_enabled=true
```

3. Save the file

#### Step 4: Set Initial Password

Open PowerShell or Command Prompt and run:

```bash
cd C:\neo4j
bin\neo4j-admin.bat set-initial-password devpassword
```

#### Step 5: Start Neo4j Server

```bash
cd C:\neo4j
bin\neo4j.bat console
```

Or to install as a Windows service:

```bash
cd C:\neo4j
bin\neo4j.bat install-service
bin\neo4j.bat start
```

#### Step 6: Verify Installation

1. Open browser: `http://localhost:7474`
2. Login with:
   - Username: `neo4j`
   - Password: `devpassword`
3. Run test query:
   ```cypher
   RETURN 1 AS test
   ```

---

## ⚙️ Configure Your Application

### Step 1: Update .env File

Create or update `.env` in your project root:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=devpassword
```

### Step 2: Install Python Driver

```bash
# Activate virtual environment
venv\Scripts\activate

# Install neo4j driver
pip install neo4j==5.14.1
```

### Step 3: Start Your Application

```bash
python src\backend\app.py
```

You should see:
```
✓ Connected to Neo4j at bolt://localhost:7687
Neo4j initialized successfully
```

### Step 4: Verify Connection

```bash
curl http://localhost:9123/health
```

Expected response:
```json
{
  "neo4j": {
    "status": "connected",
    "message": "Knowledge graph active"
  }
}
```

---

## 🔧 Troubleshooting

### Problem: "Connection refused" error

**Solution 1: Check if Neo4j is running**

**Neo4j Desktop:**
- Open Neo4j Desktop
- Check if database shows green "Running" status
- If not, click "Start"

**Neo4j Server:**
```bash
# Check if process is running
tasklist | findstr neo4j

# Or check services
services.msc
# Look for "Neo4j" service
```

**Solution 2: Verify port is listening**

```bash
netstat -ano | findstr :7687
netstat -ano | findstr :7474
```

Should show something like:
```
TCP    0.0.0.0:7687           0.0.0.0:0              LISTENING       12345
TCP    0.0.0.0:7474           0.0.0.0:0              LISTENING       12345
```

**Solution 3: Check firewall**

```bash
# Allow Neo4j through Windows Firewall
# Run as Administrator
netsh advfirewall firewall add rule name="Neo4j Bolt" dir=in action=allow protocol=TCP localport=7687
netsh advfirewall firewall add rule name="Neo4j HTTP" dir=in action=allow protocol=TCP localport=7474
```

### Problem: "Authentication failed"

**Solution:**

Reset password:

**Neo4j Desktop:**
1. Stop the database
2. Click "..." menu → "Terminal"
3. Run:
   ```bash
   bin/cypher-shell -u neo4j -p neo4j
   ALTER USER neo4j SET PASSWORD 'devpassword'
   ```

**Neo4j Server:**
```bash
cd C:\neo4j
bin\neo4j-admin.bat set-initial-password devpassword
```

Then restart Neo4j.

### Problem: Port already in use

**Find what's using the port:**

```bash
netstat -ano | findstr :7687
```

Note the PID (last column), then:

```bash
tasklist | findstr <PID>
```

**Kill the process:**

```bash
taskkill /PID <PID> /F
```

Or change Neo4j port in `neo4j.conf`:

```properties
server.bolt.listen_address=0.0.0.0:7688
```

Don't forget to update `.env`:
```bash
NEO4J_URI=bolt://localhost:7688
```

### Problem: Out of memory errors

**Increase memory allocation:**

**Neo4j Desktop:**
- Database Settings → Add/modify:
  ```properties
  dbms.memory.heap.max_size=4G
  dbms.memory.pagecache.size=2G
  ```

**Neo4j Server:**
- Edit `conf\neo4j.conf`:
  ```properties
  server.memory.heap.max_size=4G
  server.memory.pagecache.size=2G
  ```

---

## 🎯 Quick Commands Reference

### Neo4j Desktop

```bash
# Open database terminal
Right-click database → "Open Terminal"

# Check status
bin\neo4j status

# View logs
Right-click database → "Logs"
```

### Neo4j Server (Command Line)

```bash
# Start server (console mode)
cd C:\neo4j
bin\neo4j.bat console

# Start server (background)
bin\neo4j.bat start

# Stop server
bin\neo4j.bat stop

# Status
bin\neo4j.bat status

# Install as service
bin\neo4j.bat install-service

# Uninstall service
bin\neo4j.bat uninstall-service

# View logs
type data\logs\neo4j.log
```

### Application Commands

```bash
# Test connection
curl http://localhost:9123/health

# Sync terms to Neo4j
curl -X POST http://localhost:9123/api/graph/sync ^
  -H "Content-Type: application/json" ^
  -d "{\"detect_relationships\": true}"

# Check graph status
curl http://localhost:9123/api/graph/status
```

---

## 📚 Useful Neo4j Browser Queries

Access Neo4j Browser at `http://localhost:7474`

### Check database status
```cypher
CALL dbms.showCurrentUser()
```

### Count all nodes
```cypher
MATCH (n) RETURN count(n)
```

### View all relationship types
```cypher
CALL db.relationshipTypes()
```

### View sample terms
```cypher
MATCH (t:Term)
RETURN t
LIMIT 10
```

### Find most connected terms
```cypher
MATCH (t:Term)-[r]-()
RETURN t.term_text, count(r) AS connections
ORDER BY connections DESC
LIMIT 10
```

---

## 🔄 Updating Neo4j

### Neo4j Desktop

1. Open Neo4j Desktop
2. Click "Help" → "Check for updates"
3. Follow update wizard

### Neo4j Server

1. Download new version
2. Stop Neo4j: `bin\neo4j.bat stop`
3. Backup data: Copy `C:\neo4j\data` folder
4. Extract new version to new folder
5. Copy `data` and `conf` folders to new installation
6. Start new version

---

## 🎓 Learning Resources

- **Neo4j Docs:** https://neo4j.com/docs/
- **Cypher Manual:** https://neo4j.com/docs/cypher-manual/
- **Neo4j Desktop Guide:** https://neo4j.com/docs/desktop-manual/
- **Graph Academy:** https://graphacademy.neo4j.com/

---

## ✅ Setup Checklist

- [ ] Neo4j installed (Desktop or Server)
- [ ] Database created and running
- [ ] Can access Neo4j Browser (http://localhost:7474)
- [ ] Authentication working (neo4j/devpassword)
- [ ] Ports 7687 and 7474 accessible
- [ ] Python driver installed (`pip install neo4j`)
- [ ] `.env` file configured
- [ ] Application can connect (check `/health`)
- [ ] Successfully synced terms (`POST /api/graph/sync`)

---

## 💡 Performance Tips

### For Development

```properties
# Lower memory for development
dbms.memory.heap.max_size=1G
dbms.memory.pagecache.size=512M
```

### For Production (3,000+ terms)

```properties
# Higher memory for better performance
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G
```

---

## 📞 Support

If you encounter issues:

1. **Check Neo4j logs:**
   - Desktop: Right-click database → "Logs"
   - Server: `C:\neo4j\data\logs\neo4j.log`

2. **Check application logs:**
   - Backend console output

3. **Test connection manually:**
   ```bash
   curl http://localhost:7474
   ```

4. **Community support:**
   - Neo4j Community Forum: https://community.neo4j.com/
   - Stack Overflow: Tag `neo4j`

---

**Status:** ✅ **Complete Windows Setup Guide**
**Version:** 1.0
**Last Updated:** 2025-10-18
