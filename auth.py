import json
import hashlib
import os
from typing import Dict, Optional
import streamlit as st
from datetime import datetime

class UserAuth:
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
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
            'analysis_history': []
        }
        
        self.save_users(users)
        return True, "Account created successfully"
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, str]:
        """Authenticate user login"""
        users = self.load_users()
        
        if username not in users:
            return False, "Username not found"
        
        if users[username]['password'] != self.hash_password(password):
            return False, "Invalid password"
        
        # Update last login
        users[username]['last_login'] = str(datetime.now())
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

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

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
    if st.button("Don't have an account? Sign up"):
        st.session_state.show_signup = True
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
        st.rerun()

def logout():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.show_signup = False
    st.rerun()

def show_user_profile(auth_system: UserAuth):
    """Display user profile information"""
    user_info = auth_system.get_user_info(st.session_state.username)
    
    if user_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Welcome, {st.session_state.username}!**")
        st.sidebar.markdown(f"📧 {user_info['email']}")
        
        if user_info['last_login']:
            try:
                last_login = datetime.fromisoformat(user_info['last_login']).strftime("%Y-%m-%d %H:%M")
                st.sidebar.markdown(f"🕒 Last login: {last_login}")
            except:
                st.sidebar.markdown(f"🕒 Last login: {user_info['last_login']}")
        
        if st.sidebar.button("Logout", type="secondary"):
            logout()