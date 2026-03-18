import os
from dotenv import load_dotenv
from clob_client import Client

# Load environment variables from .env file
load_dotenv()

# Read private key from the environment variables
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

if PRIVATE_KEY is None:
    raise ValueError('Private key not found in .env file')

try:
    # Initialize the client with the private key
    client = Client(private_key=PRIVATE_KEY)
    # Generate API credentials
    api_credentials = client.get_api_credentials()

    # Set the API credentials to environment variables
    os.environ['POLY_API_KEY'] = api_credentials['api_key']
    os.environ['POLY_SECRET_KEY'] = api_credentials['secret_key']

    print("API credentials generated and stored in environment variables.")
except Exception as e:
    print(f'Error generating API credentials: {e}')    

# Instructions:
# 1. Ensure you have a .env file in the repository root with the private key defined as 'PRIVATE_KEY=<your_private_key>'.
# 2. Install the required libraries using:
#    pip install python-dotenv clob-client
# 3. Run the script to generate and store the Polymarket API credentials in environment variables.