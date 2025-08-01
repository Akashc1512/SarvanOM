# 🐘 PostgreSQL Setup Guide for SarvanOM

## ❌ **CURRENT ISSUES IDENTIFIED**

1. **PostgreSQL service not running** - Requires administrator privileges
2. **psql command not in PATH** - PostgreSQL bin directory not accessible
3. **Connection refused** - Service not accepting connections

---

## 🔧 **STEP-BY-STEP SOLUTION**

### **Step 1: Start PostgreSQL Service (Administrator Required)**

1. **Open PowerShell as Administrator:**
   - Right-click on PowerShell
   - Select "Run as Administrator"

2. **Start the PostgreSQL service:**
   ```powershell
   Start-Service -Name "postgresql-x64-17"
   ```

3. **Verify service is running:**
   ```powershell
   Get-Service -Name "*postgres*"
   ```

### **Step 2: Add PostgreSQL to PATH**

1. **Add PostgreSQL bin to PATH:**
   ```powershell
   $env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
   ```

2. **Test psql command:**
   ```powershell
   psql --version
   ```

### **Step 3: Create Database and User**

1. **Connect as postgres user:**
   ```powershell
   psql -U postgres -h localhost
   ```
   - Enter the password you set during installation

2. **Create the database:**
   ```sql
   CREATE DATABASE sarvanom_db;
   ```

3. **Create the user:**
   ```sql
   CREATE USER sarvanom_user WITH PASSWORD 'your_secure_password';
   ```

4. **Grant privileges:**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE sarvanom_db TO sarvanom_user;
   ```

5. **Exit psql:**
   ```sql
   \q
   ```

### **Step 4: Update Your .env File**

Add this line to your `.env` file:
```bash
DATABASE_URL=postgresql://sarvanom_user:your_secure_password@localhost:5432/sarvanom_db
```

### **Step 5: Test Connection**

```powershell
psql -h localhost -p 5432 -U sarvanom_user -d sarvanom_db
```

---

## 🚀 **QUICK FIX SCRIPT**

Run this PowerShell script as **Administrator**:

```powershell
# Start PostgreSQL service
Start-Service -Name "postgresql-x64-17"

# Add to PATH
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"

# Test connection
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();"
```

---

## 🔍 **TROUBLESHOOTING**

### **If service won't start:**
1. Check if PostgreSQL is properly installed
2. Reinstall PostgreSQL as Administrator
3. Check Windows Event Viewer for errors

### **If psql not found:**
1. Verify PostgreSQL is installed in `C:\Program Files\PostgreSQL\17\`
2. Add the bin directory to PATH permanently
3. Restart PowerShell after adding to PATH

### **If connection refused:**
1. Ensure service is running
2. Check if port 5432 is not blocked by firewall
3. Verify PostgreSQL is configured to accept connections

---

## 📋 **PERMANENT PATH SETUP**

To permanently add PostgreSQL to PATH:

1. **Open System Properties:**
   - Right-click on "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"

2. **Edit PATH:**
   - Find "Path" in System Variables
   - Click "Edit"
   - Click "New"
   - Add: `C:\Program Files\PostgreSQL\17\bin`
   - Click "OK" on all dialogs

3. **Restart PowerShell** and test:
   ```powershell
   psql --version
   ```

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] PostgreSQL service is running
- [ ] psql command is available
- [ ] Database `sarvanom_db` exists
- [ ] User `sarvanom_user` exists
- [ ] User has proper privileges
- [ ] Connection test successful
- [ ] .env file updated with DATABASE_URL

---

## 🎯 **NEXT STEPS**

1. **Run the quick fix script as Administrator**
2. **Create database and user**
3. **Update your .env file**
4. **Test the connection**
5. **Start your SarvanOM application**

**Status: Ready to implement** 🚀 