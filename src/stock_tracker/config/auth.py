import json
import hashlib
import os
import secrets
import string
from typing import Dict, Optional
import streamlit as st
from datetime import datetime, timedelta
from ..services.email_service import EmailService

class UserAuth:
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.email_service = EmailService()
        self.init_database()
    
    def init_database(self):
        """Initialize the JSON database file if it doesn't exist"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({}, f)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self) -> Dict:
        """Load users from JSON database"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_users(self, users: Dict):
        """Save users to JSON database"""
        with open(self.db_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def create_user(self, username: str, password: str, email: str) -> tuple[bool, str]:
        """Create a new user account"""
        users = self.load_users()
        
        # Check if username already exists
        if username in users:
            return False, "Username already exists"
        
        # Check if email already exists
        for user_data in users.values():
            if user_data.get('email') == email:
                return False, "Email already registered"
        
        # Create new user
        users[username] = {
            'password': self.hash_password(password),
            'email': email,
            'created_at': str(datetime.now()),
            'last_login': None,
            'favorite_stocks': [],
            'analysis_history': [],
            'failed_login_attempts': 0,
            'account_locked': False,
            'last_failed_attempt': None,
            'reset_token': None,
            'reset_token_expires': None
        }
        
        self.save_users(users)
        
        # Send welcome email if email service is configured
        if self.email_service.is_configured():
            try:
                self.email_service.send_welcome_email(email, username)
            except Exception:
                pass  # Don't fail account creation if email fails
        
        return True, "Account created successfully"
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, str]:
        """Authenticate user login with attempt tracking"""
        users = self.load_users()
        
        if username not in users:
            return False, "Username not found"
        
        user = users[username]
        
        # Check if account is locked
        if user.get('account_locked', False):
            last_attempt = user.get('last_failed_attempt')
            if last_attempt:
                try:
                    last_attempt_time = datetime.fromisoformat(last_attempt)
                    # Unlock after 30 minutes
                    if datetime.now() - last_attempt_time > timedelta(minutes=30):
                        user['account_locked'] = False
                        user['failed_login_attempts'] = 0
                        self.save_users(users)
                    else:
                        time_left = 30 - int((datetime.now() - last_attempt_time).total_seconds() / 60)
                        return False, f"Account locked due to multiple failed attempts. Try again in {time_left} minutes."
                except:
                    # Reset if there's an issue with the timestamp
                    user['account_locked'] = False
                    user['failed_login_attempts'] = 0
        
        # Check password
        if user['password'] != self.hash_password(password):
            # Increment failed attempts
            user['failed_login_attempts'] = user.get('failed_login_attempts', 0) + 1
            user['last_failed_attempt'] = str(datetime.now())
            
            # Lock account after 5 failed attempts
            if user['failed_login_attempts'] >= 5:
                user['account_locked'] = True
                self.save_users(users)
                return False, "Account locked due to multiple failed login attempts. Please try again in 30 minutes or reset your password."
            
            self.save_users(users)
            remaining_attempts = 5 - user['failed_login_attempts']
            return False, f"Invalid password. {remaining_attempts} attempts remaining before account lock."
        
        # Successful login - reset failed attempts
        user['failed_login_attempts'] = 0
        user['account_locked'] = False
        user['last_failed_attempt'] = None
        user['last_login'] = str(datetime.now())
        self.save_users(users)
        
        return True, "Login successful"
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        users = self.load_users()
        return users.get(username)
    
    def add_favorite_stock(self, username: str, symbol: str) -> bool:
        """Add stock to user's favorites"""
        users = self.load_users()
        if username in users:
            if symbol not in users[username].get('favorite_stocks', []):
                users[username].setdefault('favorite_stocks', []).append(symbol.upper())
                self.save_users(users)
                return True
        return False
    
    def remove_favorite_stock(self, username: str, symbol: str) -> bool:
        """Remove stock from user's favorites"""
        users = self.load_users()
        if username in users and symbol.upper() in users[username].get('favorite_stocks', []):
            users[username]['favorite_stocks'].remove(symbol.upper())
            self.save_users(users)
            return True
        return False
    
    def get_favorite_stocks(self, username: str) -> list:
        """Get user's favorite stocks"""
        users = self.load_users()
        return users.get(username, {}).get('favorite_stocks', [])
    
    def add_analysis_history(self, username: str, symbol: str, analysis_type: str):
        """Add analysis to user's history"""
        users = self.load_users()
        if username in users:
            history_entry = {
                'symbol': symbol.upper(),
                'analysis_type': analysis_type,
                'timestamp': str(datetime.now())
            }
            users[username].setdefault('analysis_history', []).append(history_entry)
            # Keep only last 50 entries
            users[username]['analysis_history'] = users[username]['analysis_history'][-50:]
            self.save_users(users)
    
    def get_analysis_history(self, username: str) -> list:
        """Get user's analysis history"""
        users = self.load_users()
        return users.get(username, {}).get('analysis_history', [])
    
    def generate_reset_token(self, username: str) -> tuple[bool, str]:
        """Generate a password reset token and send email"""
        users = self.load_users()
        if username not in users:
            return False, "Username not found"
        
        # Generate secure random token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        expires = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
        
        users[username]['reset_token'] = token
        users[username]['reset_token_expires'] = str(expires)
        self.save_users(users)
        
        # Send email if configured
        if self.email_service.is_configured():
            user_email = users[username]['email']
            email_success, email_message = self.email_service.send_reset_email(user_email, token, username)
            if email_success:
                return True, "EMAIL_SENT"
            else:
                return True, f"TOKEN_GENERATED|{token}|EMAIL_FAILED: {email_message}"
        else:
            return True, f"TOKEN_GENERATED|{token}|EMAIL_NOT_CONFIGURED"
    
    def reset_password(self, username: str, token: str, new_password: str) -> tuple[bool, str]:
        """Reset password using reset token"""
        users = self.load_users()
        if username not in users:
            return False, "Username not found"
        
        user = users[username]
        stored_token = user.get('reset_token')
        token_expires = user.get('reset_token_expires')
        
        if not stored_token or stored_token != token:
            return False, "Invalid reset token"
        
        if token_expires:
            try:
                expires_time = datetime.fromisoformat(token_expires)
                if datetime.now() > expires_time:
                    return False, "Reset token has expired"
            except:
                return False, "Invalid token expiration"
        
        # Reset password and clear token
        user['password'] = self.hash_password(new_password)
        user['reset_token'] = None
        user['reset_token_expires'] = None
        user['failed_login_attempts'] = 0
        user['account_locked'] = False
        user['last_failed_attempt'] = None
        
        self.save_users(users)
        return True, "Password reset successfully"
    
    def find_user_by_email(self, email: str) -> Optional[str]:
        """Find username by email address"""
        users = self.load_users()
        for username, user_data in users.items():
            if user_data.get('email') == email:
                return username
        return None

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    if 'show_reset' not in st.session_state:
        st.session_state.show_reset = False
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 'email'  # email, token, password

def login_form(auth_system: UserAuth):
    """Display login form"""
    st.subheader("Login to Stock Analysis Tool")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                success, message = auth_system.authenticate_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter both username and password")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Don't have an account? Sign up"):
            st.session_state.show_signup = True
            st.session_state.show_reset = False
            st.rerun()
    with col2:
        if st.button("Forgot Password?"):
            st.session_state.show_reset = True
            st.session_state.show_signup = False
            st.session_state.reset_step = 'email'
            st.rerun()

def signup_form(auth_system: UserAuth):
    """Display signup form"""
    st.subheader("Create New Account")
    
    with st.form("signup_form"):
        username = st.text_input("Choose Username")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Create Account")
        
        if submit_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    success, message = auth_system.create_user(username, password, email)
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials")
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all fields")
    
    st.markdown("---")
    if st.button("Already have an account? Login"):
        st.session_state.show_signup = False
        st.session_state.show_reset = False
        st.rerun()

def logout():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.show_signup = False
    st.rerun()

def show_user_profile(auth_system: UserAuth):
    """Display enhanced user profile information"""
    user_info = auth_system.get_user_info(st.session_state.username)
    
    if user_info:
        # Enhanced user profile section
        st.sidebar.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; 
                    border-radius: 15px; 
                    margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h3 style="color: white; margin: 0; text-align: center;">
                👤 User Profile
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # User welcome section with styling
        st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin-bottom: 15px;
                    border: 1px solid rgba(255,255,255,0.2);">
            <h4 style="margin: 0; color: #333;">👋 Welcome back!</h4>
            <p style="margin: 5px 0; font-size: 18px; font-weight: bold; color: #4CAF50;">
                {st.session_state.username}
            </p>
            <p style="margin: 5px 0; color: #666;">
                📧 {user_info['email']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Last login info with better formatting
        if user_info['last_login']:
            try:
                last_login = datetime.fromisoformat(user_info['last_login']).strftime("%Y-%m-%d %H:%M")
                st.sidebar.markdown(f"""
                <div style="background: rgba(76, 175, 80, 0.1); 
                            padding: 10px; 
                            border-radius: 8px; 
                            margin-bottom: 15px;
                            border-left: 4px solid #4CAF50;">
                    <small style="color: #666;">🕒 Last login: {last_login}</small>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.sidebar.markdown(f"""
                <div style="background: rgba(76, 175, 80, 0.1); 
                            padding: 10px; 
                            border-radius: 8px; 
                            margin-bottom: 15px;
                            border-left: 4px solid #4CAF50;">
                    <small style="color: #666;">🕒 Last login: {user_info['last_login']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # User stats
        favorite_count = len(user_info.get('favorite_stocks', []))
        analysis_count = len(user_info.get('analysis_history', []))
        
        st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin-bottom: 15px;">
            <h5 style="margin: 0 0 10px 0; color: #333;">📊 Quick Stats</h5>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #666;">⭐ Favorites:</span>
                <span style="font-weight: bold; color: #FF9800;">{favorite_count}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #666;">📈 Analyses:</span>
                <span style="font-weight: bold; color: #2196F3;">{analysis_count}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced logout button
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                logout()
        with col2:
            if st.button("⚙️ Settings", type="secondary", use_container_width=True):
                st.sidebar.info("Settings coming soon!")
        
        # Separator
        st.sidebar.markdown("""
        <div style="border-top: 2px solid rgba(255,255,255,0.1); 
                    margin: 20px 0;"></div>
        """, unsafe_allow_html=True)

def password_reset_form(auth_system: UserAuth):
    """Display password reset form"""
    st.subheader("Reset Password")
    
    if st.session_state.reset_step == 'email':
        st.write("Enter your email address to receive a password reset token.")
        
        with st.form("reset_email_form"):
            email = st.text_input("Email Address")
            submit_button = st.form_submit_button("Send Reset Token")
            
            if submit_button:
                if email:
                    username = auth_system.find_user_by_email(email)
                    if username:
                        success, result = auth_system.generate_reset_token(username)
                        if success:
                            if result == "EMAIL_SENT":
                                st.success("Password reset email sent!")
                                st.info("📧 Check your email for the reset token.")
                            elif result.startswith("TOKEN_GENERATED"):
                                parts = result.split("|")
                                token = parts[1]
                                reason = parts[2] if len(parts) > 2 else ""
                                
                                if "EMAIL_NOT_CONFIGURED" in reason:
                                    st.warning("Email service not configured.")
                                    with st.expander("🔧 Demo Mode - Click here to see your reset token"):
                                        st.info("Your reset token:")
                                        st.code(token)
                                        st.info("Copy this token and use it in the next step.")
                                elif "EMAIL_FAILED" in reason:
                                    st.warning("Failed to send email, but token was generated.")
                                    with st.expander("Your reset token is available here"):
                                        st.code(token)
                                        st.error(reason.replace("EMAIL_FAILED: ", ""))
                            
                            st.session_state.reset_username = username
                            st.session_state.reset_step = 'token'
                            st.rerun()
                        else:
                            st.error("Error generating reset token")
                    else:
                        st.error("No account found with this email address")
                else:
                    st.error("Please enter your email address")
    
    elif st.session_state.reset_step == 'token':
        st.write("Enter the reset token from your email and choose a new password.")
        st.info("💡 If you didn't receive the email, check your spam folder or go back to request a new token.")
        
        with st.form("reset_token_form"):
            token = st.text_input("Reset Token")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            submit_button = st.form_submit_button("Reset Password")
            
            if submit_button:
                if token and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        username = st.session_state.get('reset_username')
                        if username:
                            success, message = auth_system.reset_password(username, token, new_password)
                            if success:
                                st.success(message)
                                st.info("You can now login with your new password")
                                st.session_state.show_reset = False
                                st.session_state.reset_step = 'email'
                                if 'reset_username' in st.session_state:
                                    del st.session_state.reset_username
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Session expired. Please start over.")
                            st.session_state.reset_step = 'email'
                            st.rerun()
                else:
                    st.error("Please fill in all fields")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Login"):
            st.session_state.show_reset = False
            st.session_state.show_signup = False
            st.session_state.reset_step = 'email'
            if 'reset_username' in st.session_state:
                del st.session_state.reset_username
            st.rerun()
    
    with col2:
        if st.session_state.reset_step == 'token':
            if st.button("Request New Token"):
                st.session_state.reset_step = 'email'
                if 'reset_username' in st.session_state:
                    del st.session_state.reset_username
                st.rerun()