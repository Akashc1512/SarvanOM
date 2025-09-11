# 🎯 SarvanOM Default Login Credentials

## 📋 **DEVELOPMENT CREDENTIALS**

### **👤 Regular User**
- **Username**: `user`
- **Password**: `UserPass123!`
- **Email**: `user@sarvanom.dev`
- **Role**: `user`

### **👑 Admin User**
- **Username**: `admin`
- **Password**: `AdminPass123!`
- **Email**: `admin@sarvanom.dev`
- **Role**: `admin`

### **🧠 Expert User**
- **Username**: `expert`
- **Password**: `ExpertPass123!`
- **Email**: `expert@sarvanom.dev`
- **Role**: `expert`

## 🌐 **ACCESS POINTS**

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8005
- **Login Page**: http://localhost:3000/login
- **Register Page**: http://localhost:3000/register
- **Admin Dashboard**: http://localhost:3000/admin

## ⚠️ **IMPORTANT NOTES**

1. **Development Only**: These credentials are for development and testing only
2. **Change in Production**: Always change these passwords before deploying to production
3. **Security**: Never commit real credentials to version control
4. **Environment Variables**: Use environment variables for production credentials

## 🚀 **QUICK START**

1. **Start the application**:
   ```bash
   # Backend
   uvicorn services.gateway.main:app --host 0.0.0.0 --port 8005
   
   # Frontend
   cd frontend && npm run dev
   ```

2. **Setup default users**:
   ```bash
   python scripts/setup_default_users.py
   ```

3. **Login with any of the credentials above**

## 🔧 **TROUBLESHOOTING**

- **Login redirects to login page**: Check if backend is running on port 8005
- **Registration fails**: Ensure database is running and accessible
- **Authentication errors**: Verify JWT configuration in environment variables
