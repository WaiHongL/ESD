import requests
import yaml

# Load the Kong configuration from the YAML file
with open('kong.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Base URL for the Kong Admin API
base_url = 'http://localhost:8001'

# print(config)

# Create services
for service in config['services']:
    response = requests.post(f'{base_url}/services', json=service)
    print(response.json())
    
# Create routes
for route in config['routes']:
    response = requests.post(f'{base_url}/routes', json=route)
    print(response.json())    

# # Create routes [zhijie]
# for route in config['routes']:
#     service, routename = route['name'].split(",")
#     response = requests.put(f'{base_url}/services/{service}/routes', data=route)
#     print(response.json())