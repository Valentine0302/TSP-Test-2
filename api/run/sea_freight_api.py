#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import json
import os
import re
import requests
import sqlite3
import time
from datetime import datetime
import random
import argparse

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'sea_freight.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verified_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        verified BOOLEAN DEFAULT TRUE,
        verification_method TEXT DEFAULT 'automatic',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper functions
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_disposable_email(email):
    """Check if email is from a disposable domain"""
    disposable_domains = [
        'tempmail.com', 'throwawaymail.com', 'mailinator.com', 'guerrillamail.com',
        'yopmail.com', '10minutemail.com', 'trashmail.com', 'mailnesia.com',
        'temp-mail.org', 'fakeinbox.com', 'sharklasers.com', 'guerrillamail.info',
        'spam4.me', 'dispostable.com', 'maildrop.cc', 'getairmail.com',
        'mailnull.com', 'spamgourmet.com', 'tempinbox.com', 'spamfree24.org'
    ]
    
    domain = email.split('@')[-1].lower()
    return domain in disposable_domains

def check_mx_record(email):
    """
    Check if the email domain has valid MX records
    This is a simplified version - in production, use DNS libraries
    """
    try:
        domain = email.split('@')[-1]
        # Simulate MX record check - in production use DNS libraries
        # For example: dns.resolver.resolve(domain, 'MX')
        return True  # Assume all domains have valid MX records for the prototype
    except:
        return False

def auto_verify_email(email):
    """
    Automatically verify email without requiring confirmation code
    Uses multiple checks to validate the email
    """
    # Check if email is already in the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT verified FROM verified_emails WHERE email = ?', (email,))
    result = cursor.fetchone()
    
    if result:
        # Email already exists in database
        conn.close()
        return {'verified': True}
    
    # Perform validation checks
    if not is_valid_email(email):
        conn.close()
        return {'verified': False, 'error': 'Invalid email format'}
    
    if is_disposable_email(email):
        conn.close()
        return {'verified': False, 'error': 'Disposable email addresses are not allowed'}
    
    if not check_mx_record(email):
        conn.close()
        return {'verified': False, 'error': 'Invalid email domain'}
    
    # All checks passed, automatically verify the email
    cursor.execute('INSERT INTO verified_emails (email, verified, verification_method) VALUES (?, TRUE, ?)', 
                  (email, 'automatic'))
    
    conn.commit()
    conn.close()
    
    return {'verified': True, 'message': 'Email automatically verified'}

def get_carrier_rates(origin, destination, cargo_type, container_type, weight, volume):
    """
    Simulate getting rates from different carriers
    In a production environment, this would call actual carrier APIs
    """
    carriers = {
        'Maersk': {
            'base_rate': random.uniform(1400, 1800),
            'weight_factor': 0.3,
            'volume_factor': 7.5,
            'container_multipliers': {
                '20dv': 1.0,
                '40dv': 1.7,
                '40hc': 1.9,
                '20fr': 1.2,
                '40fr': 2.0,
                '20ot': 1.3,
                '40ot': 2.1,
                '20rf': 1.8,
                '40rf': 2.5,
                'none': 1.0
            },
            'transit_time_base': 28,
            'transit_time_variance': 4
        },
        'MSC': {
            'base_rate': random.uniform(1300, 1700),
            'weight_factor': 0.28,
            'volume_factor': 7.8,
            'container_multipliers': {
                '20dv': 1.0,
                '40dv': 1.65,
                '40hc': 1.85,
                '20fr': 1.25,
                '40fr': 2.1,
                '20ot': 1.35,
                '40ot': 2.2,
                '20rf': 1.9,
                '40rf': 2.6,
                'none': 1.0
            },
            'transit_time_base': 30,
            'transit_time_variance': 5
        },
        'CMA CGM': {
            'base_rate': random.uniform(1350, 1750),
            'weight_factor': 0.32,
            'volume_factor': 7.2,
            'container_multipliers': {
                '20dv': 1.0,
                '40dv': 1.75,
                '40hc': 1.95,
                '20fr': 1.15,
                '40fr': 1.9,
                '20ot': 1.25,
                '40ot': 2.0,
                '20rf': 1.75,
                '40rf': 2.4,
                'none': 1.0
            },
            'transit_time_base': 29,
            'transit_time_variance': 3
        },
        'COSCO': {
            'base_rate': random.uniform(1250, 1650),
            'weight_factor': 0.25,
            'volume_factor': 8.0,
            'container_multipliers': {
                '20dv': 1.0,
                '40dv': 1.6,
                '40hc': 1.8,
                '20fr': 1.3,
                '40fr': 2.2,
                '20ot': 1.4,
                '40ot': 2.3,
                '20rf': 2.0,
                '40rf': 2.7,
                'none': 1.0
            },
            'transit_time_base': 32,
            'transit_time_variance': 6
        },
        'Hapag-Lloyd': {
            'base_rate': random.uniform(1500, 1900),
            'weight_factor': 0.35,
            'volume_factor': 7.0,
            'container_multipliers': {
                '20dv': 1.0,
                '40dv': 1.8,
                '40hc': 2.0,
                '20fr': 1.1,
                '40fr': 1.85,
                '20ot': 1.2,
                '40ot': 1.95,
                '20rf': 1.7,
                '40rf': 2.3,
                'none': 1.0
            },
            'transit_time_base': 27,
            'transit_time_variance': 3
        }
    }
    
    results = []
    
    for carrier_name, carrier_data in carriers.items():
        # Calculate base cost
        if container_type != 'none' and cargo_type == 'fcl':
            # FCL calculation
            cost = carrier_data['base_rate'] * carrier_data['container_multipliers'].get(container_type, 1.0)
        else:
            # LCL calculation
            weight_cost = weight * carrier_data['weight_factor']
            volume_cost = volume * carrier_data['volume_factor']
            cost = max(weight_cost, volume_cost)
            
            # Minimum charge
            if cost < carrier_data['base_rate'] * 0.3:
                cost = carrier_data['base_rate'] * 0.3
        
        # Calculate transit time
        transit_time = carrier_data['transit_time_base'] + random.randint(-carrier_data['transit_time_variance'], carrier_data['transit_time_variance'])
        
        # Add to results
        results.append({
            'carrier': carrier_name,
            'cost': round(cost, 2),
            'transit_time': transit_time
        })
    
    # Sort by cost
    results.sort(key=lambda x: x['cost'])
    
    return results

def calculate_sea_freight(data):
    """Calculate sea freight costs and transit times"""
    origin = data.get('origin')
    destination = data.get('destination')
    cargo_type = data.get('cargoType')
    container_type = data.get('containerType', 'none')
    weight = float(data.get('weight', 0))
    volume = float(data.get('volume', 0))
    goods_value = float(data.get('goodsValue', 0))
    incoterms = data.get('incoterms')
    dangerous = data.get('dangerous') == 'yes'
    insurance = data.get('insurance')
    customs = data.get('customs')
    
    # Get carrier rates
    carrier_rates = get_carrier_rates(origin, destination, cargo_type, container_type, weight, volume)
    
    # Apply additional costs
    for rate in carrier_rates:
        # Dangerous goods surcharge
        if dangerous:
            rate['cost'] *= 1.5
            rate['transit_time'] += 3
        
        # Insurance
        if insurance == 'basic':
            rate['cost'] += goods_value * 0.01  # 1% of goods value
        elif insurance == 'full':
            rate['cost'] += goods_value * 0.025  # 2.5% of goods value
        
        # Customs
        if customs == 'export':
            rate['cost'] += 150
            rate['transit_time'] += 1
        elif customs == 'import':
            rate['cost'] += 200
            rate['transit_time'] += 1
        elif customs == 'both':
            rate['cost'] += 300
            rate['transit_time'] += 2
        
        # Round the final cost
        rate['cost'] = round(rate['cost'], 2)
    
    return carrier_rates

def save_calculation(data, result):
    """Save calculation to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO calculations (
        origin, destination, cargo_type, container_type, weight, volume, 
        goods_value, incoterms, dangerous, insurance, customs, additional_info,
        name, company, email, phone, estimated_cost, estimated_time, recommended_carrier
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('origin'),
        data.get('destination'),
        data.get('cargoType'),
        data.get('containerType'),
        float(data.get('weight', 0)),
        float(data.get('volume', 0)),
        float(data.get('goodsValue', 0)) if data.get('goodsValue') else 0,
        data.get('incoterms'),
        data.get('dangerous') == 'yes',
        data.get('insurance'),
        data.get('customs'),
        data.get('additionalInfo'),
        data.get('name'),
        data.get('company'),
        data.get('email'),
        data.get('phone'),
        result[0]['cost'],  # Best rate cost
        result[0]['transit_time'],  # Best rate transit time
        result[0]['carrier']  # Best rate carrier
    ))
    
    conn.commit()
    conn.close()

# API Routes
@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@app.route('/api/sea-freight/calculate', methods=['POST'])
def api_calculate():
    """Calculate sea freight rates"""
    data = request.json
    
    # Validate required fields
    required_fields = ['origin', 'destination', 'cargoType', 'weight', 'volume', 'email', 'name']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate and automatically verify email
    email = data['email']
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Auto-verify the email if not already verified
    verification_result = auto_verify_email(email)
    
    if not verification_result.get('verified', False):
        return jsonify({
            'error': verification_result.get('error', 'Email verification failed'),
            'require_verification': False  # No manual verification required
        }), 403
    
    # Calculate rates
    try:
        results = calculate_sea_freight(data)
        
        # Save calculation to database
        save_calculation(data, results)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sea-freight/verify-email', methods=['POST'])
def api_verify_email():
    """Automatically verify user email"""
    data = request.json
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    email = data['email']
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Perform automatic verification
    result = auto_verify_email(email)
    
    return jsonify(result)

@app.route('/api/sea-freight/history', methods=['GET'])
def api_history():
    """Get calculation history for an email"""
    email = request.args.get('email')
    
    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Auto-verify the email if not already verified
    verification_result = auto_verify_email(email)
    
    if not verification_result.get('verified', False):
        return jsonify({'error': verification_result.get('error', 'Email verification failed')}), 403
    
    # Get history
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, origin, destination, cargo_type, container_type, weight, volume,
           estimated_cost, estimated_time, recommended_carrier, created_at
    FROM calculations
    WHERE email = ?
    ORDER BY created_at DESC
    LIMIT 10
    ''', (email,))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'origin': row[1],
            'destination': row[2],
            'cargo_type': row[3],
            'container_type': row[4],
            'weight': row[5],
            'volume': row[6],
            'estimated_cost': row[7],
            'estimated_time': row[8],
            'recommended_carrier': row[9],
            'created_at': row[10]
        })
    
    return jsonify({'success': True, 'history': history})

# Run the app
if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Sea Freight API Server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    app.run(host='0.0.0.0', port=args.port, debug=True)
