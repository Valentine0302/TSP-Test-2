import unittest
import sys
import os
import json
import sqlite3
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from shipping_api_integration import ShippingAPIClient
from db_schema import DatabaseManager

class TestSeaFreightImplementation(unittest.TestCase):
    """Test cases for the sea freight calculator implementation"""
    
    def setUp(self):
        """Set up test environment"""
        # Use in-memory database for testing
        self.db_path = ":memory:"
        self.db = DatabaseManager(self.db_path)
        
        # Create shipping API client
        self.shipping_client = ShippingAPIClient()
        
        # Test data
        self.test_email = "test@example.com"
        self.test_calculation = {
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
            "email": self.test_email,
            "phone": "+1234567890"
        }
        
        self.test_quotes = [
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
    
    def test_email_verification(self):
        """Test email verification functionality"""
        # Verify email
        result = self.db.verify_email(self.test_email)
        self.assertTrue(result, "Email verification should succeed")
        
        # Check if email is verified
        is_verified = self.db.is_email_verified(self.test_email)
        self.assertTrue(is_verified, "Email should be marked as verified")
        
        # Verify non-existent email
        non_existent = "nonexistent@example.com"
        self.assertFalse(self.db.is_email_verified(non_existent), 
                         "Non-existent email should not be verified")
    
    def test_save_calculation(self):
        """Test saving calculation data"""
        # Verify email first
        self.db.verify_email(self.test_email)
        
        # Save calculation
        calculation_id = self.db.save_calculation(self.test_calculation, self.test_quotes)
        self.assertIsNotNone(calculation_id, "Calculation ID should not be None")
        
        # Get calculation history
        history = self.db.get_calculation_history(self.test_email)
        self.assertEqual(len(history), 1, "Should have one calculation in history")
        self.assertEqual(history[0]['origin'], self.test_calculation['origin'], 
                         "Origin should match")
        self.assertEqual(history[0]['destination'], self.test_calculation['destination'], 
                         "Destination should match")
        
        # Check quotes
        self.assertEqual(len(history[0]['quotes']), 2, "Should have two quotes")
        self.assertEqual(history[0]['quotes'][0]['carrier'], self.test_quotes[0]['carrier'], 
                         "Carrier should match")
    
    @patch('shipping_api_integration.requests.post')
    def test_shipping_api_integration(self, mock_post):
        """Test shipping API integration"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'quotes': [
                {
                    'carrier': 'API Carrier 1',
                    'totalPrice': 2000.0,
                    'transitTime': 25
                },
                {
                    'carrier': 'API Carrier 2',
                    'totalPrice': 2200.0,
                    'transitTime': 22
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Set API keys for testing
        os.environ['SEARATES_API_KEY'] = 'test_key'
        
        # Get rates
        rates = self.shipping_client.get_rates(
            origin=self.test_calculation['origin'],
            destination=self.test_calculation['destination'],
            cargo_type=self.test_calculation['cargoType'],
            container_type=self.test_calculation['containerType'],
            weight=float(self.test_calculation['weight']),
            volume=float(self.test_calculation['volume']),
            goods_value=float(self.test_calculation['goodsValue']),
            dangerous=self.test_calculation['dangerous'] == 'yes',
            insurance=self.test_calculation['insurance'],
            customs=self.test_calculation['customs']
        )
        
        # Check if API was called
        mock_post.assert_called_once()
        
        # Check fallback mechanism when API fails
        mock_post.reset_mock()
        mock_post.side_effect = Exception("API Error")
        
        # Get rates with API error
        rates = self.shipping_client.get_rates(
            origin=self.test_calculation['origin'],
            destination=self.test_calculation['destination'],
            cargo_type=self.test_calculation['cargoType'],
            container_type=self.test_calculation['containerType'],
            weight=float(self.test_calculation['weight']),
            volume=float(self.test_calculation['volume'])
        )
        
        # Should still return results from simulation
        self.assertTrue(len(rates) > 0, "Should return simulated rates when API fails")
        self.assertEqual(rates[0]['source'], 'simulation', 
                         "Source should be simulation when API fails")
    
    def test_api_logging(self):
        """Test API call logging"""
        # Log an API call
        log_id = self.db.log_api_call(
            api_name="searates",
            endpoint="/rates",
            request_data={"origin": "Shanghai", "destination": "Rotterdam"},
            response_data={"quotes": [{"carrier": "Test", "cost": 1000}]},
            status_code=200,
            execution_time=0.5
        )
        
        self.assertIsNotNone(log_id, "Log ID should not be None")
        
        # Get API logs
        logs = self.db.get_api_logs(api_name="searates")
        self.assertEqual(len(logs), 1, "Should have one log entry")
        self.assertEqual(logs[0]['api_name'], "searates", "API name should match")
        self.assertEqual(logs[0]['status_code'], 200, "Status code should match")
    
    def test_end_to_end_flow(self):
        """Test the complete end-to-end flow"""
        # 1. Verify email
        self.db.verify_email(self.test_email)
        
        # 2. Get shipping rates
        with patch.object(self.shipping_client, '_get_searates_quotes', 
                         return_value=self.test_quotes):
            rates = self.shipping_client.get_rates(
                origin=self.test_calculation['origin'],
                destination=self.test_calculation['destination'],
                cargo_type=self.test_calculation['cargoType'],
                container_type=self.test_calculation['containerType'],
                weight=float(self.test_calculation['weight']),
                volume=float(self.test_calculation['volume']),
                goods_value=float(self.test_calculation['goodsValue']),
                dangerous=self.test_calculation['dangerous'] == 'yes',
                insurance=self.test_calculation['insurance'],
                customs=self.test_calculation['customs']
            )
        
        # 3. Save calculation with rates
        calculation_id = self.db.save_calculation(self.test_calculation, rates)
        
        # 4. Get calculation history
        history = self.db.get_calculation_history(self.test_email)
        
        # Verify the flow
        self.assertTrue(self.db.is_email_verified(self.test_email), 
                        "Email should be verified")
        self.assertEqual(len(rates), len(self.test_quotes), 
                         "Should return the correct number of rates")
        self.assertIsNotNone(calculation_id, 
                             "Calculation should be saved successfully")
        self.assertEqual(len(history), 1, 
                         "Should have one calculation in history")
        self.assertEqual(history[0]['recommended_carrier'], rates[0]['carrier'], 
                         "Recommended carrier should match best rate")

if __name__ == '__main__':
    unittest.main()
