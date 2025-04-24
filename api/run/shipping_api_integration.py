import requests
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='shipping_api.log'
)
logger = logging.getLogger('shipping_api_integration')

# API Configuration
API_CONFIG = {
    'searates': {
        'base_url': 'https://api.searates.com/v1',
        'api_key': os.environ.get('SEARATES_API_KEY', ''),
        'enabled': True
    },
    'freightos': {
        'base_url': 'https://api.freightos.com/v2',
        'api_key': os.environ.get('FREIGHTOS_API_KEY', ''),
        'enabled': True
    },
    'worldfreightrates': {
        'base_url': 'https://api.worldfreightrates.com/v1',
        'api_key': os.environ.get('WORLDFREIGHTRATES_API_KEY', ''),
        'enabled': True
    }
}

class ShippingAPIClient:
    """Client for integrating with multiple shipping APIs"""
    
    def __init__(self):
        """Initialize the shipping API client"""
        self.apis = {}
        
        # Initialize API clients
        for api_name, config in API_CONFIG.items():
            if config['enabled'] and config['api_key']:
                self.apis[api_name] = {
                    'base_url': config['base_url'],
                    'api_key': config['api_key']
                }
        
        if not self.apis:
            logger.warning("No shipping APIs configured. Using fallback simulation.")
    
    def get_rates(self, origin, destination, cargo_type, container_type, weight, volume, 
                  goods_value=0, dangerous=False, insurance='no', customs='no'):
        """
        Get shipping rates from all configured APIs
        
        Args:
            origin (str): Origin port/location
            destination (str): Destination port/location
            cargo_type (str): Type of cargo (fcl, lcl, bulk, etc.)
            container_type (str): Type of container (20dv, 40hc, etc.)
            weight (float): Weight in kg
            volume (float): Volume in cubic meters
            goods_value (float, optional): Value of goods in USD
            dangerous (bool, optional): Whether cargo is dangerous
            insurance (str, optional): Insurance type (no, basic, full)
            customs (str, optional): Customs clearance (no, export, import, both)
            
        Returns:
            list: List of rate quotes from different carriers
        """
        results = []
        
        # Try to get rates from each configured API
        for api_name, api_config in self.apis.items():
            try:
                if api_name == 'searates':
                    api_results = self._get_searates_quotes(api_config, origin, destination, 
                                                           cargo_type, container_type, weight, 
                                                           volume, goods_value, dangerous, 
                                                           insurance, customs)
                elif api_name == 'freightos':
                    api_results = self._get_freightos_quotes(api_config, origin, destination, 
                                                            cargo_type, container_type, weight, 
                                                            volume, goods_value, dangerous, 
                                                            insurance, customs)
                elif api_name == 'worldfreightrates':
                    api_results = self._get_worldfreightrates_quotes(api_config, origin, destination, 
                                                                    cargo_type, container_type, weight, 
                                                                    volume, goods_value, dangerous, 
                                                                    insurance, customs)
                else:
                    continue
                
                # Add API results to combined results
                results.extend(api_results)
                
            except Exception as e:
                logger.error(f"Error getting rates from {api_name}: {str(e)}")
        
        # If no results from APIs or no APIs configured, use fallback simulation
        if not results:
            logger.info("No results from shipping APIs. Using fallback simulation.")
            results = self._simulate_rates(origin, destination, cargo_type, container_type, 
                                          weight, volume, goods_value, dangerous, 
                                          insurance, customs)
        
        # Sort results by cost
        results.sort(key=lambda x: x['cost'])
        
        return results
    
    def _get_searates_quotes(self, api_config, origin, destination, cargo_type, container_type, 
                            weight, volume, goods_value, dangerous, insurance, customs):
        """Get quotes from Searates API"""
        try:
            # Prepare request data
            payload = {
                'origin': origin,
                'destination': destination,
                'cargoType': cargo_type,
                'containerType': container_type if cargo_type == 'fcl' else None,
                'weight': weight,
                'volume': volume,
                'goodsValue': goods_value,
                'dangerous': dangerous,
                'insurance': insurance != 'no',
                'customs': customs != 'no'
            }
            
            # Make API request
            response = requests.post(
                f"{api_config['base_url']}/rates",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {api_config['api_key']}"
                },
                json=payload,
                timeout=30
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                # Transform API response to our standard format
                results = []
                for quote in data.get('quotes', []):
                    results.append({
                        'carrier': quote.get('carrier', 'Unknown'),
                        'cost': float(quote.get('totalPrice', 0)),
                        'transit_time': int(quote.get('transitTime', 0)),
                        'source': 'searates'
                    })
                
                return results
            else:
                logger.warning(f"Searates API returned status code {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error in Searates API request: {str(e)}")
            return []
    
    def _get_freightos_quotes(self, api_config, origin, destination, cargo_type, container_type, 
                             weight, volume, goods_value, dangerous, insurance, customs):
        """Get quotes from Freightos API"""
        try:
            # Prepare request data
            payload = {
                'originLocation': origin,
                'destinationLocation': destination,
                'cargoDetails': {
                    'type': cargo_type,
                    'containerType': container_type if cargo_type == 'fcl' else None,
                    'weight': weight,
                    'volume': volume,
                    'value': goods_value,
                    'isDangerous': dangerous
                },
                'services': {
                    'insurance': insurance != 'no',
                    'customsClearance': customs
                }
            }
            
            # Make API request
            response = requests.post(
                f"{api_config['base_url']}/quotes",
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': api_config['api_key']
                },
                json=payload,
                timeout=30
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                # Transform API response to our standard format
                results = []
                for quote in data.get('quotes', []):
                    results.append({
                        'carrier': quote.get('carrierName', 'Unknown'),
                        'cost': float(quote.get('totalAmount', 0)),
                        'transit_time': int(quote.get('transitDays', 0)),
                        'source': 'freightos'
                    })
                
                return results
            else:
                logger.warning(f"Freightos API returned status code {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error in Freightos API request: {str(e)}")
            return []
    
    def _get_worldfreightrates_quotes(self, api_config, origin, destination, cargo_type, container_type, 
                                     weight, volume, goods_value, dangerous, insurance, customs):
        """Get quotes from WorldFreightRates API"""
        try:
            # Prepare request data
            payload = {
                'from': origin,
                'to': destination,
                'type': cargo_type,
                'container': container_type if cargo_type == 'fcl' else None,
                'weight': weight,
                'volume': volume,
                'value': goods_value,
                'hazardous': dangerous,
                'insurance': insurance != 'no',
                'customs': customs != 'no'
            }
            
            # Make API request
            response = requests.post(
                f"{api_config['base_url']}/calculate",
                headers={
                    'Content-Type': 'application/json',
                    'API-Key': api_config['api_key']
                },
                json=payload,
                timeout=30
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                # Transform API response to our standard format
                results = []
                for quote in data.get('rates', []):
                    results.append({
                        'carrier': quote.get('carrier', 'Unknown'),
                        'cost': float(quote.get('total', 0)),
                        'transit_time': int(quote.get('transit_time', 0)),
                        'source': 'worldfreightrates'
                    })
                
                return results
            else:
                logger.warning(f"WorldFreightRates API returned status code {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error in WorldFreightRates API request: {str(e)}")
            return []
    
    def _simulate_rates(self, origin, destination, cargo_type, container_type, weight, volume, 
                       goods_value, dangerous, insurance, customs):
        """
        Simulate shipping rates when APIs are not available
        This is a fallback mechanism to ensure the system always returns results
        """
        import random
        
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
            
            # Apply additional costs
            # Dangerous goods surcharge
            if dangerous:
                cost *= 1.5
                transit_time += 3
            
            # Insurance
            if insurance == 'basic':
                cost += goods_value * 0.01  # 1% of goods value
            elif insurance == 'full':
                cost += goods_value * 0.025  # 2.5% of goods value
            
            # Customs
            if customs == 'export':
                cost += 150
                transit_time += 1
            elif customs == 'import':
                cost += 200
                transit_time += 1
            elif customs == 'both':
                cost += 300
                transit_time += 2
            
            # Add to results
            results.append({
                'carrier': carrier_name,
                'cost': round(cost, 2),
                'transit_time': transit_time,
                'source': 'simulation'
            })
        
        # Sort by cost
        results.sort(key=lambda x: x['cost'])
        
        return results

# Example usage
if __name__ == "__main__":
    client = ShippingAPIClient()
    
    # Example calculation
    rates = client.get_rates(
        origin="Shanghai, China",
        destination="Rotterdam, Netherlands",
        cargo_type="fcl",
        container_type="40hc",
        weight=5000,
        volume=30,
        goods_value=50000,
        dangerous=False,
        insurance="basic",
        customs="both"
    )
    
    print(json.dumps(rates, indent=2))
