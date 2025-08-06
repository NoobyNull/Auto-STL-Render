#!/usr/bin/env python3
"""
Setup script for 3D Model Renderer
Professional 3D model rendering with intelligent front detection
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("3D Model Renderer Setup")
    print("=" * 50)
    print("Professional 3D model rendering with intelligent front detection")
    print("=" * 50)
    
    # Required packages
    required_packages = [
        ("pyvista", "pyvista"),
        ("numpy", "numpy"), 
        ("scikit-learn", "sklearn")
    ]
    
    # Optional packages for enhanced functionality
    optional_packages = [
        ("vtk", "vtk"),
        ("matplotlib", "matplotlib")
    ]
    
    print("\n🔍 Checking required dependencies...")
    missing_required = []
    
    for package_name, import_name in required_packages:
        if check_package(package_name, import_name):
            print(f"✅ {package_name:<15} - Installed")
        else:
            print(f"❌ {package_name:<15} - Missing")
            missing_required.append(package_name)
    
    print("\n🔍 Checking optional dependencies...")
    missing_optional = []
    
    for package_name, import_name in optional_packages:
        if check_package(package_name, import_name):
            print(f"✅ {package_name:<15} - Installed")
        else:
            print(f"⚪ {package_name:<15} - Not installed (optional)")
            missing_optional.append(package_name)
    
    if missing_required:
        print(f"\n⚠️  Missing required packages: {', '.join(missing_required)}")
        print("\n📦 Installation options:")
        print("1. Install from requirements file (recommended):")
        print("   pip install -r requirements.txt")
        print("\n2. Install individually:")
        for package in missing_required:
            print(f"   pip install {package}")
        
        response = input("\nWould you like to install missing packages now? (y/n): ").lower()
        if response == 'y':
            print("\n📦 Installing missing packages...")
            success = True
            for package in missing_required:
                print(f"Installing {package}...")
                if install_package(package):
                    print(f"✅ {package} installed successfully")
                else:
                    print(f"❌ Failed to install {package}")
                    success = False
            
            if success:
                print("\n🎉 All required packages installed successfully!")
            else:
                print("\n⚠️  Some packages failed to install. Please install manually.")
                return 1
    else:
        print("\n🎉 All required dependencies are installed!")
    
    if missing_optional:
        print(f"\n💡 Optional packages available for enhanced functionality:")
        for package in missing_optional:
            print(f"   • {package}")
        print(f"\n   Install with: pip install {' '.join(missing_optional)}")
    
    # Check if main scripts exist
    print("\n🔍 Checking project files...")
    required_files = [
        "render_3d.py",
        "model_renderer.py", 
        "interactive_viewer.py",
        "requirements.txt"
    ]
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ {file_name:<20} - Found")
        else:
            print(f"❌ {file_name:<20} - Missing")
    
    print("\n" + "=" * 50)
    print("🚀 Setup complete! Ready to render 3D models.")
    print("=" * 50)
    
    print("\n📖 Quick Start Guide:")
    print("  # Auto-detect and render (recommended)")
    print("  cd /path/to/stl/files")
    print("  python render_3d.py")
    print("")
    print("  # Explicit file with multiple views")
    print("  python render_3d.py model.stl")
    print("")
    print("  # Interactive viewer")
    print("  python render_3d.py model.stl -i")
    print("")
    print("  # High quality preset view")
    print("  python render_3d.py model.stl -p front -Q ultra")
    
    print("\n📚 Documentation:")
    print("  • README.md - Complete usage guide")
    print("  • example_usage.py - Python API examples") 
    print("  • Interactive help: python render_3d.py -h")
    
    print("\n✨ Features:")
    print("  • Auto-detection of 3D files")
    print("  • Intelligent front view detection")
    print("  • Professional rendering quality")
    print("  • Interactive 3D viewer")
    print("  • Multi-format support (STL, OBJ, PLY, etc.)")
    print("  • Large mesh optimization (500K+ faces)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
