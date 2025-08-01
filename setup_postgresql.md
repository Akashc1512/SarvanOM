# 🗄️ PostgreSQL Setup Guide (Without Chocolatey)

## **Option 1: Direct Download (Recommended)**

### **Step 1: Download PostgreSQL**
1. Go to: https://www.postgresql.org/download/windows/
2. Click "Download the installer"
3. Choose the latest version (15.x or 16.x)
4. Download the Windows x86-64 installer

### **Step 2: Install PostgreSQL**
1. Run the downloaded installer
2. **Important settings:**
   - Installation directory: `C:\Program Files\PostgreSQL\16\`
   - Data directory: `C:\Program Files\PostgreSQL\16\data\`
   - Password: Set a strong password (remember this!)
   - Port: `5432` (default)
   - Locale: `Default locale`

### **Step 3: Add to PATH**
1. Open System Properties → Advanced → Environment Variables
2. Edit "Path" variable
3. Add: `C:\Program Files\PostgreSQL\16\bin`
4. Click OK

### **Step 4: Create Database and User**
Open Command Prompt as Administrator and run:

```bash
# Create database
createdb -U postgres sarvanom_db

# Create user
createuser -U postgres -P sarvanom_user
# Enter password when prompted

# Grant privileges
psql -U postgres -d sarvanom_db -c "GRANT ALL PRIVILEGES ON DATABASE sarvanom_db TO sarvanom_user;"
```

### **Step 5: Update .env**
Add this to your `.env` file:
```bash
DATABASE_URL=postgresql://sarvanom_user:your_password@localhost:5432/sarvanom_db
```

---

## **Option 2: Using Docker (Alternative)**

If you have Docker installed:

```bash
# Pull PostgreSQL image
docker pull postgres:16

# Run PostgreSQL container
docker run -d \
  --name postgres-sarvanom \
  -e POSTGRES_DB=sarvanom_db \
  -e POSTGRES_USER=sarvanom_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:16

# Update .env
DATABASE_URL=postgresql://sarvanom_user:your_password@localhost:5432/sarvanom_db
```

---

## **Option 3: Cloud PostgreSQL (Production)**

### **AWS RDS**
1. Go to AWS Console → RDS
2. Create PostgreSQL instance
3. Get connection details
4. Update .env with cloud URL

### **Google Cloud SQL**
1. Go to Google Cloud Console → SQL
2. Create PostgreSQL instance
3. Get connection details
4. Update .env with cloud URL

---

## **Verification**

After setup, test the connection:
```bash
python -c "import psycopg2; conn=psycopg2.connect('postgresql://sarvanom_user:your_password@localhost:5432/sarvanom_db'); print('✅ PostgreSQL connected'); conn.close()"
``` 