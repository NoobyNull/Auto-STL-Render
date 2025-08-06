#!/usr/bin/env python3
"""
Example usage of the 3D Model Renderer
Professional 3D model rendering with intelligent front detection
"""

from model_renderer import ModelRenderer
from interactive_viewer import launch_interactive_viewer
import sys
from pathlib import Path
import numpy as np

def example_basic_rendering():
    """Example: Basic rendering with intelligent front detection."""
    print("=== Basic Rendering Example ===")
    
    # Example model path (replace with your 3D file)
    model_path = "example_model.stl"
    
    try:
        # Create renderer
        renderer = ModelRenderer(model_path, verbose=True)
        
        # Render best front view (prioritizes top and front views)
        print("Rendering best view with intelligent front detection...")
        paths = renderer.render_best_views(n_views=1, quality='high')
        print(f"✓ Rendered: {paths[0]}")
        print("  Features: Dark background, 87.5% screen fill, professional quality")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have a 3D model file to test with.")

def example_multi_view_standard():
    """Example: Render 3 standard views + auto (default behavior)."""
    print("\n=== Multi-View Standard Example ===")
    
    model_path = "example_model.stl"
    
    try:
        renderer = ModelRenderer(model_path, verbose=True)
        
        # This creates the same output as: python render_3d.py model.stl
        print("Rendering front, top, back + auto-detected view...")
        
        # Standard views
        views = ['front', 'top', 'back']
        rendered_paths = []
        
        for view in views:
            path = renderer.render_view(preset=view, quality='high')
            rendered_paths.append(path)
            print(f"✓ {view.title()} view: {path}")
        
        # Auto-detected view (if unique)
        best_views = renderer.find_best_front_views(n_views=1)
        if best_views:
            auto_view_dir, score = best_views[0]
            print(f"✓ Auto-detected view score: {score:.2f}")
            
            # Check if different from standard views
            standard_dirs = {
                'front': [0, -1, 0],
                'top': [0, 0, 1],
                'back': [0, 1, 0]
            }
            
            is_unique = True
            for view_name, std_dir in standard_dirs.items():
                similarity = abs(np.dot(auto_view_dir, std_dir))
                if similarity > 0.9:
                    print(f"  Auto view similar to {view_name} ({similarity:.2f}), skipping")
                    is_unique = False
                    break
            
            if is_unique:
                auto_path = renderer.render_view(
                    view_direction=auto_view_dir,
                    filename=f"{renderer.base_filename}_auto.png"
                )
                rendered_paths.append(auto_path)
                print(f"✓ Unique auto view: {auto_path}")
        
        print(f"Total rendered: {len(rendered_paths)} images")
            
    except Exception as e:
        print(f"Error: {e}")

def example_preset_views():
    """Example: Render using preset views (matches interactive viewer)."""
    print("\n=== Preset Views Example ===")
    
    model_path = "example_model.stl"
    
    try:
        renderer = ModelRenderer(model_path, verbose=True)
        
        # All available preset views
        presets = ['front', 'back', 'top', 'bottom', 'left', 'right']
        
        print("Rendering all preset views...")
        for preset in presets:
            path = renderer.render_view(
                preset=preset,
                resolution=(1080, 1080),
                quality='high'
            )
            print(f"✓ {preset.title()} view: {path}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_custom_view():
    """Example: Render specific view direction."""
    print("\n=== Custom View Example ===")
    
    model_path = "example_model.stl"
    
    try:
        renderer = ModelRenderer(model_path, verbose=True)
        
        # Custom view directions
        custom_views = [
            ([1, 1, 0.5], "diagonal_view"),
            ([1, 0, 1], "side_angle"),
            ([0.5, -1, 0.3], "perspective")
        ]
        
        for view_direction, name in custom_views:
            print(f"Rendering {name}: {view_direction}")
            path = renderer.render_view(
                view_direction=view_direction,
                filename=f"{name}.png",
                resolution=(1080, 1080),
                quality='high'
            )
            print(f"✓ {name}: {path}")
        
    except Exception as e:
        print(f"Error: {e}")

def example_high_resolution():
    """Example: High resolution rendering with intelligent zoom."""
    print("\n=== High Resolution Example ===")
    
    model_path = "example_model.stl"
    
    try:
        renderer = ModelRenderer(model_path, verbose=True)
        
        # 4K rendering with ultra quality
        print("Rendering 4K image with ultra quality...")
        path = renderer.render_view(
            preset='front',
            filename="4k_front_view.png",
            resolution=(3840, 2160),
            quality='ultra'
        )
        print(f"✓ 4K render: {path}")
        print("  Features:")
        print("  - Intelligent 87.5% screen fill")
        print("  - Dark goldenrod material on dark background")
        print("  - Geometry-aware camera positioning")
        print("  - Professional lighting")
        
    except Exception as e:
        print(f"Error: {e}")

def example_interactive():
    """Example: Launch interactive viewer."""
    print("\n=== Interactive Viewer Example ===")
    
    model_path = "example_model.stl"
    
    try:
        print("Launching interactive viewer...")
        print("\nControls:")
        print("  • Mouse: Left=Rotate, Right=Pan, Scroll=Zoom")
        print("  • Keys: F=Front, B=Back, T=Top, O=Bottom, L=Left, R=Right")
        print("  • 's' key: Save current view as PNG")
        print("  • 'q' key: Quit")
        
        print("\nFeatures:")
        print("  • Real-time 3D exploration")
        print("  • Camera position saving to JSON")
        print("  • Same materials as batch renderer")
        print("  • Perfect for finding optimal angles")
        
        launch_interactive_viewer(model_path, quality='high')
        
    except Exception as e:
        print(f"Error: {e}")

def example_auto_detection():
    """Example: Auto-detect 3D files (CLI equivalent)."""
    print("\n=== Auto-Detection Example ===")
    
    # Simulate the CLI auto-detection logic
    extensions = {'.stl', '.obj', '.ply', '.3mf', '.off', '.vtk', '.vtp', '.vtu', '.x3d'}
    current_dir = Path('.')
    found_files = []
    
    for file_path in current_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            found_files.append(file_path)
    
    print(f"Scanning current directory...")
    print(f"Found {len(found_files)} 3D model files:")
    for f in found_files:
        print(f"  - {f.name}")
    
    if len(found_files) == 1:
        print(f"\n🎯 Auto-detected: {found_files[0].name}")
        print("This is equivalent to running:")
        print(f"  python render_3d.py")
        print("Which renders 3 standard views + auto view if unique")
        
        try:
            renderer = ModelRenderer(str(found_files[0]), verbose=True)
            # Just analyze, don't render in example
            best_views = renderer.find_best_front_views(n_views=1)
            if best_views:
                _, score = best_views[0]
                print(f"✓ Best view analysis complete (score: {score:.2f})")
        except Exception as e:
            print(f"Error: {e}")
            
    elif len(found_files) == 0:
        print("\nNo 3D files found in current directory.")
        print("Supported formats: STL, OBJ, PLY, 3MF, OFF, VTK, VTP, VTU, X3D")
        print("\nTo test:")
        print("1. Copy a 3D model file to this directory")
        print("2. Run: python render_3d.py")
    else:
        print(f"\nMultiple files found. CLI would show:")
        print("Error: Multiple 3D model files found in current directory:")
        for f in sorted(found_files):
            print(f"  - {f.name}")
        print("Please specify which file to use:")
        print(f"  python render_3d.py {found_files[0].name}")

def example_python_api():
    """Example: Complete Python API usage."""
    print("\n=== Python API Example ===")
    
    model_path = "example_model.stl"
    
    try:
        # Create renderer with custom output directory
        renderer = ModelRenderer(model_path, output_dir="./my_renders", verbose=True)
        
        print(f"Model info:")
        print(f"  File: {renderer.model_path}")
        print(f"  Max dimension: {renderer.max_dimension:.2f}")
        print(f"  Output directory: {renderer.output_dir}")
        
        # Analysis without rendering
        print("\nAnalyzing geometry...")
        best_views = renderer.find_best_front_views(n_views=3)
        for i, (view_dir, score) in enumerate(best_views, 1):
            print(f"  View {i}: direction={view_dir}, score={score:.2f}")
        
        # Render using API
        print("\nRendering via API...")
        
        # Single preset view
        front_path = renderer.render_view(preset="front", quality="high")
        print(f"✓ Front view API: {front_path}")
        
        # Multiple best views
        best_paths = renderer.render_best_views(n_views=2, quality="medium")
        for i, path in enumerate(best_paths, 1):
            print(f"✓ Best view {i}: {path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("3D Model Renderer - Example Usage")
    print("=" * 60)
    print("Professional 3D model rendering with intelligent front detection")
    print("=" * 60)
    
    # Check for 3D files
    print("Checking for 3D model files...")
    example_auto_detection()
    
    print("\n" + "=" * 60)
    print("Additional Examples (uncomment to test):")
    print("=" * 60)
    
    # Uncomment to run examples:
    # example_basic_rendering()
    # example_multi_view_standard()
    # example_preset_views()
    # example_custom_view()
    # example_high_resolution()
    # example_python_api()
    
    # Interactive example (uncomment to test)
    # example_interactive()
    
    print("\n" + "=" * 60)
    print("🚀 Example guide completed!")
    print("=" * 60)
    
    print("\n📖 To test with your own model:")
    print("1. Place a 3D model file (.stl, .obj, .ply) in this directory")
    print("2. Uncomment the example functions above")
    print("3. Run: python example_usage.py")
    
    print("\n📋 Or use the command-line interface:")
    print("  python render_3d.py                    # Auto-detect, 3+auto views")
    print("  python render_3d.py model.stl          # Explicit file, 3+auto views")
    print("  python render_3d.py model.stl -p front # Front view only")
    print("  python render_3d.py model.stl -i       # Interactive viewer")
    print("  python render_3d.py model.stl -n 5     # 5 best auto views")
    print("  python render_3d.py model.stl -Q ultra # Ultra quality")
    
    print("\n✨ Key Features Demonstrated:")
    print("  • Auto-detection of 3D files")
    print("  • Intelligent front view detection")
    print("  • Professional rendering quality (87.5% fill)")
    print("  • Multi-view standard output")
    print("  • Interactive 3D exploration")
    print("  • Large mesh optimization")
    print("  • High-resolution output")
