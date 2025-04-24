import sqlite3
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='database.log'
)
logger = logging.getLogger('database')

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'sea_freight.db')

class DatabaseManager:
    """Manager for database operations"""
    
    def __init__(self, db_path=DB_PATH):
        """Initialize the database manager"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                company TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0
            )
            ''')
            
            # Create verified_emails table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS verified_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                verified BOOLEAN DEFAULT TRUE,
                verification_method TEXT DEFAULT 'automatic',
                verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verification_attempts INTEGER DEFAULT 0,
                last_attempt_date TIMESTAMP
            )
            ''')
            
            # Create calculations table with expanded fields
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                cargo_type TEXT NOT NULL,
                container_type TEXT,
                weight REAL NOT NULL,
                volume REAL NOT NULL,
                goods_value REAL,
                incoterms TEXT,
                dangerous BOOLEAN,
                insurance TEXT,
                customs TEXT,
                additional_info TEXT,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT NOT NULL,
                phone TEXT,
                estimated_cost REAL NOT NULL,
                estimated_time INTEGER NOT NULL,
                recommended_carrier TEXT NOT NULL,
                calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')
            
            # Create quotes table to store individual carrier quotes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calculation_id INTEGER NOT NULL,
                carrier TEXT NOT NULL,
                cost REAL NOT NULL,
                transit_time INTEGER NOT NULL,
                source TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (calculation_id) REFERENCES calculations(id)
            )
            ''')
            
            # Create api_logs table to track API calls
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_data TEXT,
                response_data TEXT,
                status_code INTEGER,
                error_message TEXT,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def verify_email(self, email, method='automatic'):
        """
        Verify an email address
        
        Args:
            email (str): Email address to verify
            method (str): Verification method used
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT verified FROM verified_emails WHERE email = ?', (email,))
            result = cursor.fetchone()
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if result:
                # Email exists, update verification if needed
                if not result[0]:  # If not already verified
                    cursor.execute('''
                    UPDATE verified_emails 
                    SET verified = TRUE, 
                        verification_method = ?, 
                        verification_date = ?,
                        verification_attempts = verification_attempts + 1,
                        last_attempt_date = ?
                    WHERE email = ?
                    ''', (method, now, now, email))
                else:
                    # Just update the attempt count
                    cursor.execute('''
                    UPDATE verified_emails 
                    SET verification_attempts = verification_attempts + 1,
                        last_attempt_date = ?
                    WHERE email = ?
                    ''', (now, email))
            else:
                # New email, insert record
                cursor.execute('''
                INSERT INTO verified_emails 
                (email, verified, verification_method, verification_date, verification_attempts, last_attempt_date) 
                VALUES (?, TRUE, ?, ?, 1, ?)
                ''', (email, method, now, now))
                
                # Also add to users table if not exists
                cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                if not cursor.fetchone():
                    cursor.execute('''
                    INSERT INTO users (email, created_at) VALUES (?, ?)
                    ''', (email, now))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            return False
    
    def is_email_verified(self, email):
        """
        Check if an email is verified
        
        Args:
            email (str): Email address to check
            
        Returns:
            bool: True if verified, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT verified FROM verified_emails WHERE email = ?', (email,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result and result[0]:
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error checking email verification: {str(e)}")
            return False
    
    def save_calculation(self, calculation_data, quotes):
        """
        Save calculation and quotes to database
        
        Args:
            calculation_data (dict): Calculation form data
            quotes (list): List of carrier quotes
            
        Returns:
            int: ID of saved calculation, or None if error
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user_id if exists
            email = calculation_data.get('email')
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user_result = cursor.fetchone()
            user_id = user_result[0] if user_result else None
            
            # If user doesn't exist, create one
            if not user_id:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                INSERT INTO users (email, name, company, phone, created_at) 
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    email,
                    calculation_data.get('name'),
                    calculation_data.get('company'),
                    calculation_data.get('phone'),
                    now
                ))
                user_id = cursor.lastrowid
            
            # Update user info if provided
            if user_id:
                cursor.execute('''
                UPDATE users 
                SET name = COALESCE(?, name),
                    company = COALESCE(?, company),
                    phone = COALESCE(?, phone),
                    last_login = CURRENT_TIMESTAMP,
                    login_count = login_count + 1
                WHERE id = ?
                ''', (
                    calculation_data.get('name'),
                    calculation_data.get('company'),
                    calculation_data.get('phone'),
                    user_id
                ))
            
            # Insert calculation
            best_quote = quotes[0] if quotes else None
            
            cursor.execute('''
            INSERT INTO calculations (
                user_id, origin, destination, cargo_type, container_type, 
                weight, volume, goods_value, incoterms, dangerous, 
                insurance, customs, additional_info, name, company, 
                email, phone, estimated_cost, estimated_time, recommended_carrier,
                ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                calculation_data.get('origin'),
                calculation_data.get('destination'),
                calculation_data.get('cargoType'),
                calculation_data.get('containerType'),
                float(calculation_data.get('weight', 0)),
                float(calculation_data.get('volume', 0)),
                float(calculation_data.get('goodsValue', 0)) if calculation_data.get('goodsValue') else 0,
                calculation_data.get('incoterms'),
                calculation_data.get('dangerous') == 'yes',
                calculation_data.get('insurance'),
                calculation_data.get('customs'),
                calculation_data.get('additionalInfo'),
                calculation_data.get('name'),
                calculation_data.get('company'),
                email,
                calculation_data.get('phone'),
                best_quote['cost'] if best_quote else 0,
                best_quote['transit_time'] if best_quote else 0,
                best_quote['carrier'] if best_quote else 'Unknown',
                calculation_data.get('ip_address'),
                calculation_data.get('user_agent')
            ))
            
            calculation_id = cursor.lastrowid
            
            # Insert quotes
            for quote in quotes:
                cursor.execute('''
                INSERT INTO quotes (
                    calculation_id, carrier, cost, transit_time, source, details
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    calculation_id,
                    quote['carrier'],
                    quote['cost'],
                    quote['transit_time'],
                    quote['source'],
                    json.dumps(quote) if 'details' in quote else None
                ))
            
            conn.commit()
            conn.close()
            
            return calculation_id
            
        except Exception as e:
            logger.error(f"Error saving calculation: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None
    
    def get_calculation_history(self, email, limit=10):
        """
        Get calculation history for an email
        
        Args:
            email (str): Email to get history for
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of calculation history records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT c.id, c.origin, c.destination, c.cargo_type, c.container_type, 
                   c.weight, c.volume, c.estimated_cost, c.estimated_time, 
                   c.recommended_carrier, c.calculation_date
            FROM calculations c
            WHERE c.email = ?
            ORDER BY c.calculation_date DESC
            LIMIT ?
            ''', (email, limit))
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            history = []
            for row in rows:
                history.append(dict(row))
                
                # Get quotes for this calculation
                cursor.execute('''
                SELECT carrier, cost, transit_time, source
                FROM quotes
                WHERE calculation_id = ?
                ORDER BY cost ASC
                ''', (row['id'],))
                
                quotes = []
                for quote_row in cursor.fetchall():
                    quotes.append(dict(quote_row))
                
                history[-1]['quotes'] = quotes
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"Error getting calculation history: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def log_api_call(self, api_name, endpoint, request_data, response_data, status_code, error_message=None, execution_time=0):
        """
        Log an API call
        
        Args:
            api_name (str): Name of the API
            endpoint (str): API endpoint
            request_data (dict): Request data
            response_data (dict): Response data
            status_code (int): HTTP status code
            error_message (str, optional): Error message if any
            execution_time (float, optional): Execution time in seconds
            
        Returns:
            int: ID of log entry, or None if error
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO api_logs (
                api_name, endpoint, request_data, response_data, 
                status_code, error_message, execution_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                api_name,
                endpoint,
                json.dumps(request_data) if request_data else None,
                json.dumps(response_data) if response_data else None,
                status_code,
                error_message,
                execution_time
            ))
            
            log_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return log_id
            
        except Exception as e:
            logger.error(f"Error logging API call: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None
    
    def get_api_logs(self, api_name=None, limit=100):
        """
        Get API logs
        
        Args:
            api_name (str, optional): Filter by API name
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of API log records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if api_name:
                cursor.execute('''
                SELECT id, api_name, endpoint, status_code, error_message, 
                       execution_time, created_at
                FROM api_logs
                WHERE api_name = ?
                ORDER BY created_at DESC
                LIMIT ?
                ''', (api_name, limit))
            else:
                cursor.execute('''
                SELECT id, api_name, endpoint, status_code, error_message, 
                       execution_time, created_at
                FROM api_logs
                ORDER BY created_at DESC
                LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            logs = [dict(row) for row in rows]
            
            conn.close()
            return logs
            
        except Exception as e:
            logger.error(f"Error getting API logs: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return []

# Example usage
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Example: Verify an email
    db.verify_email("test@example.com")
    
    # Example: Check if email is verified
    is_verified = db.is_email_verified("test@example.com")
    print(f"Email verified: {is_verified}")
    
    # Example: Save a calculation
    calculation_data = {
        "origin": "Shanghai, China",
        "destination": "Rotterdam, Netherlands",
        "cargoType": "fcl",
        "containerType": "40hc",
        "weight": 5000,
        "volume": 30,
        "goodsValue": 50000,
        "incoterms": "fob",
        "dangerous": "no",
        "insurance": "basic",
        "customs": "both",
        "additionalInfo": "Test calculation",
        "name": "Test User",
        "company": "Test Company",
        "email": "test@example.com",
        "phone": "+1234567890"
    }
    
    quotes = [
        {
            "carrier": "Maersk",
            "cost": 2500.50,
            "transit_time": 30,
            "source": "simulation"
        },
        {
            "carrier": "MSC",
            "cost": 2300.75,
            "transit_time": 32,
            "source": "simulation"
        }
    ]
    
    calculation_id = db.save_calculation(calculation_data, quotes)
    print(f"Saved calculation ID: {calculation_id}")
    
    # Example: Get calculation history
    history = db.get_calculation_history("test@example.com")
    print(f"Calculation history: {json.dumps(history, indent=2)}")
