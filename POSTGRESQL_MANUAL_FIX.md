# 🐘 PostgreSQL Manual Fix Guide

## ❌ **CURRENT ISSUE:**
PostgreSQL service failed to start, causing "Connection refused" errors.

## 🔧 **MANUAL FIX STEPS:**

### **Step 1: Check PostgreSQL Installation**
1. **Verify installation:**
   ```powershell
   Test-Path "C:\Program Files\PostgreSQL\17\bin\psql.exe"
   ```

2. **If not found, reinstall PostgreSQL:**
   - Download from: https://www.postgresql.org/download/windows/
   - Run installer as Administrator
   - Use default settings (port 5432)
   - Set password for postgres user

### **Step 2: Initialize PostgreSQL Data Directory**
1. **Open PowerShell as Administrator**
2. **Navigate to PostgreSQL bin:**
   ```powershell
   cd "C:\Program Files\PostgreSQL\17\bin"
   ```

3. **Initialize data directory:**
   ```powershell
   .\initdb.exe -D "C:\Program Files\PostgreSQL\17\data" -U postgres --pwprompt
   ```
   - Enter password when prompted

### **Step 3: Configure PostgreSQL**
1. **Edit pg_hba.conf:**
   ```powershell
   notepad "C:\Program Files\PostgreSQL\17\data\pg_hba.conf"
   ```

2. **Replace content with:**
   ```
   # PostgreSQL Client Authentication Configuration File
   # TYPE  DATABASE        USER            ADDRESS                 METHOD
   local   all             all                                     trust
   host    all             all             127.0.0.1/32            trust
   host    all             all             ::1/128                 trust
   ```

3. **Save and close**

### **Step 4: Start PostgreSQL Service**
1. **Start service:**
   ```powershell
   Start-Service -Name "postgresql-x64-17"
   ```

2. **Verify service is running:**
   ```powershell
   Get-Service -Name "*postgres*"
   ```

### **Step 5: Test Connection**
```powershell
psql -h localhost -p 5432 -U postgres -d postgres
```

### **Step 6: Create Database and User**
1. **Connect to PostgreSQL:**
   ```powershell
   psql -U postgres -h localhost
   ```

2. **Create database:**
   ```sql
   CREATE DATABASE sarvanom_db;
   ```

3. **Create user:**
   ```sql
   CREATE USER sarvanom_user WITH PASSWORD 'sarvanom_password';
   ```

4. **Grant privileges:**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE sarvanom_db TO sarvanom_user;
   ```

5. **Exit:**
   ```sql
   \q
   ```

### **Step 7: Test New Connection**
```powershell
psql -h localhost -p 5432 -U sarvanom_user -d sarvanom_db
```

### **Step 8: Update .env File**
Add this line to your `.env` file:
```bash
DATABASE_URL=postgresql://sarvanom_user:sarvanom_password@localhost:5432/sarvanom_db
```

---

## 🚨 **ALTERNATIVE: REINSTALL POSTGRESQL**

If manual fix doesn't work:

1. **Uninstall PostgreSQL:**
   - Control Panel → Programs → Uninstall
   - Remove PostgreSQL 17

2. **Clean up:**
   ```powershell
   Remove-Item "C:\Program Files\PostgreSQL" -Recurse -Force
   ```

3. **Reinstall PostgreSQL:**
   - Download PostgreSQL 17 from official website
   - Run installer as Administrator
   - Use default settings
   - Set password for postgres user

4. **Follow steps above**

---

## ✅ **VERIFICATION**

After completing the fix:
- [ ] PostgreSQL service is running
- [ ] Connection to localhost:5432 works
- [ ] Database sarvanom_db exists
- [ ] User sarvanom_user exists
- [ ] .env file updated
- [ ] SarvanOM can connect to database

**Status: Ready for manual implementation** 🛠️ 