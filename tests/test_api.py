import asyncio
import ssl
import socket
import sys
import subprocess
import urllib.parse
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

# Your MongoDB connection details
CLUSTER_HOST = "fitnessbooking.auyzqge.mongodb.net"
USERNAME = "sirishakatta1234"
PASSWORD = "ueTnJ2HUidhfqnNR"
DATABASE = "booking_app"

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def check_python_ssl_info():
    print_section("Python SSL Information")
    print(f"Python version: {sys.version}")
    print(f"SSL version: {ssl.ssl_version}")
    print(f"OpenSSL version: {ssl.ssl.OPENSSL_VERSION}")
    print(f"Default SSL context: {ssl.create_default_context()}")
    print(f"Certifi CA bundle location: {certifi.where()}")

def check_dns_resolution():
    print_section("DNS Resolution Test")
    try:
        ip = socket.gethostbyname(CLUSTER_HOST)
        print(f"✅ DNS resolution successful: {CLUSTER_HOST} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False

def check_port_connectivity():
    print_section("Port Connectivity Test")
    try:
        sock = socket.create_connection((CLUSTER_HOST, 27017), timeout=10)
        sock.close()
        print(f"✅ Port 27017 is reachable on {CLUSTER_HOST}")
        return True
    except (socket.timeout, socket.error) as e:
        print(f"❌ Cannot connect to port 27017: {e}")
        return False

def check_ssl_handshake():
    print_section("SSL Handshake Test")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((CLUSTER_HOST, 27017), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=CLUSTER_HOST) as ssock:
                print(f"✅ SSL handshake successful")
                print(f"SSL version: {ssock.version()}")
                print(f"Cipher: {ssock.cipher()}")
                return True
    except Exception as e:
        print(f"❌ SSL handshake failed: {e}")
        return False

def test_curl_connection():
    print_section("cURL Test (if available)")
    try:
        # Test basic connectivity with curl
        result = subprocess.run([
            'curl', '-I', '--connect-timeout', '10', 
            f'https://{CLUSTER_HOST}:27017'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ cURL connection successful")
            print(f"Response: {result.stdout[:200]}...")
        else:
            print(f"❌ cURL failed: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"⚠️  cURL test skipped: {e}")

async def test_basic_pymongo():
    print_section("Basic PyMongo Test")
    try:
        from pymongo import MongoClient
        
        # Simple connection test
        client = MongoClient(
            f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_HOST}/{DATABASE}",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Try to get server info
        info = client.server_info()
        print(f"✅ PyMongo connection successful")
        print(f"MongoDB version: {info.get('version', 'Unknown')}")
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ PyMongo connection failed: {e}")
        return False

async def test_alternative_connection_strings():
    print_section("Alternative Connection String Tests")
    
    # Test different connection string formats
    connection_strings = [
        # Standard format
        f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_HOST}/{DATABASE}?retryWrites=true&w=majority",
        
        # Without SSL/TLS explicitly
        f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_HOST}/{DATABASE}",
        
        # With SSL disabled (not recommended for Atlas)
        f"mongodb://{USERNAME}:{PASSWORD}@{CLUSTER_HOST}:27017/{DATABASE}?ssl=false",
        
        # With different SSL options
        f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_HOST}/{DATABASE}?ssl=true&ssl_cert_reqs=CERT_NONE",
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\nTesting connection string {i}:")
        print(f"URL: {conn_str[:50]}...")
        
        try:
            client = AsyncIOMotorClient(
                conn_str,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            db = client[DATABASE]
            collections = await db.list_collection_names()
            print(f"✅ Connection {i} successful! Collections: {collections}")
            await client.close()
            return True
            
        except Exception as e:
            print(f"❌ Connection {i} failed: {str(e)[:100]}...")
    
    return False

def check_network_proxy():
    print_section("Network Proxy Check")
    import os
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    
    for var in proxy_vars:
        if var in os.environ:
            print(f"⚠️  Proxy detected: {var} = {os.environ[var]}")
            proxy_found = True
    
    if not proxy_found:
        print("✅ No proxy environment variables found")

def install_certificates():
    print_section("Certificate Installation")
    try:
        # Try to run the certificate installation command for macOS
        cert_command = f"/Applications/Python\\ {sys.version_info.major}.{sys.version_info.minor}/Install\\ Certificates.command"
        print(f"Attempting to run: {cert_command}")
        
        result = subprocess.run(cert_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Certificate installation completed")
            print(result.stdout)
        else:
            print("⚠️  Certificate installation may have failed")
            print(result.stderr)
            
    except Exception as e:
        print(f"⚠️  Could not run certificate installation: {e}")
        print("Please manually run:")
        print(f"/Applications/Python\\ {sys.version_info.major}.{sys.version_info.minor}/Install\\ Certificates.command")

async def main():
    print("MongoDB Atlas Connection Diagnostic Tool")
    print("This will help identify the root cause of your connection issues")
    
    # System checks
    check_python_ssl_info()
    check_network_proxy()
    
    # Network connectivity checks
    if not check_dns_resolution():
        print("\n🚨 DNS resolution failed. Check your internet connection.")
        return
    
    if not check_port_connectivity():
        print("\n🚨 Port 27017 is not reachable. This could be:")
        print("   - Firewall blocking the connection")
        print("   - Network proxy issues")
        print("   - ISP blocking MongoDB ports")
        return
    
    # SSL checks
    check_ssl_handshake()
    test_curl_connection()
    
    # Certificate installation
    install_certificates()
    
    # MongoDB connection tests
    await test_basic_pymongo()
    success = await test_alternative_connection_strings()
    
    if not success:
        print_section("Troubleshooting Suggestions")
        print("1. Try connecting from a different network (mobile hotspot)")
        print("2. Check MongoDB Atlas Network Access settings")
        print("3. Verify your username/password are correct")
        print("4. Try using MongoDB Compass with the same connection string")
        print("5. Contact your network administrator about MongoDB Atlas access")
        print("\nIf the issue persists, please share the output of this diagnostic.")

if __name__ == "__main__":
    asyncio.run(main())