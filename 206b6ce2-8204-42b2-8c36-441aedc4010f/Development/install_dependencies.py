import subprocess
import sys

# Install required packages for JWT authentication system
packages = [
    'PyJWT',
    'cryptography',
    'requests',
    'authlib',
    'python-dotenv'
]

for package in packages:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])

print("✅ All dependencies installed successfully:")
for pkg in packages:
    print(f"  - {pkg}")
