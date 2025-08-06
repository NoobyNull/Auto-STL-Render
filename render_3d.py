#!/usr/bin/env python3
"""
Simple 3D Model Renderer - Wrapper Script

This script provides a simple interface to render 3D models with automatic
front detection or launch an interactive viewer.
"""

import argparse
import sys
from pathlib import Path
import numpy as np

def find_3d_files():
    """Find 3D model files in current directory."""
    from pathlib import Path
    
    # Common 3D file extensions
    extensions = {'.stl', '.obj', '.ply', '.3mf', '.off', '.vtk', '.vtp', '.vtu', '.x3d'}
    
    current_dir = Path('.')
    found_files = []
    
    for file_path in current_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            found_files.append(file_path)
    
    return found_files


def main():
    parser = argparse.ArgumentParser(
        description="Simple 3D Model Renderer",
        epilog="""
Examples:
  python render_3d.py model.stl                    # Render best front view
  python render_3d.py                              # Auto-detect single 3D file
  python render_3d.py model.stl -n 3               # Render 3 best views  
  python render_3d.py model.stl -i                 # Interactive viewer
  python render_3d.py model.stl -s 1 1 0.5         # Specific view direction
        """
    )
    
    parser.add_argument("input", nargs='?', help="Input 3D model file (STL, OBJ, PLY, etc.) - auto-detects if not specified")
    parser.add_argument("-i", "--interactive", action="store_true", 
                       help="Launch interactive viewer")
    parser.add_argument("-n", "--num-views", type=int, default=1, 
                       help="Number of best views to render (default: 1)")
    parser.add_argument("-s", "--single-view", nargs=3, type=float, metavar=('X', 'Y', 'Z'),
                       help="Render single view with direction [X, Y, Z]")
    parser.add_argument("-p", "--preset", choices=['front', 'back', 'top', 'bottom', 'left', 'right'],
                       help="Render using preset view (same as interactive viewer)")
    parser.add_argument("-o", "--output", help="Output directory (default: same as input)")
    parser.add_argument("-r", "--resolution", type=str, default="1080x1080", 
                       help="Image resolution WIDTHxHEIGHT (default: 1080x1080)")
    parser.add_argument("-Q", "--quality", choices=['low', 'medium', 'high', 'ultra'], 
                       default='high', help="Rendering quality (default: high)")
    parser.add_argument("-q", "--quiet", action="store_true", 
                       help="Quiet mode - minimal output")
    
    args = parser.parse_args()
    
    # Handle input file auto-detection
    input_file = args.input
    if input_file is None:
        # Auto-detect 3D files in current directory
        found_files = find_3d_files()
        
        if len(found_files) == 0:
            print("Error: No 3D model files found in current directory")
            print("Supported formats: STL, OBJ, PLY, 3MF, OFF, VTK, VTP, VTU, X3D")
            return 1
        elif len(found_files) > 1:
            print("Error: Multiple 3D model files found in current directory:")
            for f in sorted(found_files):
                print(f"  - {f}")
            print("Please specify which file to use:")
            print(f"  python render_3d.py {found_files[0]}")
            return 1
        else:
            input_file = str(found_files[0])
            if not args.quiet:
                print(f"🎯 Auto-detected 3D model: {input_file}")
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        return 1
    
    try:
        if args.interactive:
            # Launch interactive viewer
            from interactive_viewer import launch_interactive_viewer
            launch_interactive_viewer(input_file, args.quality)
            return 0
        else:
            # Use the main renderer
            from model_renderer import ModelRenderer
            
            # Parse resolution
            try:
                width, height = map(int, args.resolution.split('x'))
                resolution = (width, height)
            except:
                if not args.quiet:
                    print("Invalid resolution format. Using default 1080x1080")
                resolution = (1080, 1080)
            
            # Create renderer
            renderer = ModelRenderer(input_file, args.output, verbose=not args.quiet)
            
            if args.single_view:
                # Render specific view
                path = renderer.render_view(
                    view_direction=args.single_view,
                    resolution=resolution,
                    quality=args.quality
                )
                if args.quiet:
                    print(path)
            elif args.preset:
                # Render preset view (matching interactive viewer)
                path = renderer.render_view(
                    preset=args.preset,
                    resolution=resolution,
                    quality=args.quality
                )
                if args.quiet:
                    print(path)
            else:
                # Render standard 3 views + auto if different
                if args.num_views == 1 and not args.preset and not args.single_view:
                    # Default behavior: render front, top, back + auto if different
                    if not args.quiet:
                        print("Rendering standard views: front, top, back + auto-detected...")
                    
                    rendered_paths = []
                    standard_views = ['front', 'top', 'back']
                    
                    # Render the 3 standard views
                    for view_name in standard_views:
                        path = renderer.render_view(
                            preset=view_name,
                            resolution=resolution,
                            quality=args.quality
                        )
                        rendered_paths.append(path)
                    
                    # Get auto-detected best view
                    best_views = renderer.find_best_front_views(n_views=1)
                    if best_views:
                        auto_view_dir, auto_score = best_views[0]
                        
                        # Check if auto view is significantly different from standard views
                        standard_directions = {
                            'front': [0, -1, 0],
                            'top': [0, 0, 1], 
                            'back': [0, 1, 0]
                        }
                        
                        is_different = True
                        for view_name, std_dir in standard_directions.items():
                            similarity = abs(np.dot(auto_view_dir, std_dir))
                            if similarity > 0.9:  # Very similar to a standard view
                                is_different = False
                                if not args.quiet:
                                    print(f"  Auto-detected view is similar to {view_name} view (similarity: {similarity:.2f})")
                                break
                        
                        if is_different:
                            # Render the unique auto-detected view
                            auto_path = renderer.render_view(
                                view_direction=auto_view_dir,
                                filename=f"{renderer.base_filename}_auto.png",
                                resolution=resolution,
                                quality=args.quality
                            )
                            rendered_paths.append(auto_path)
                            if not args.quiet:
                                print(f"  Added unique auto-detected view")
                        else:
                            if not args.quiet:
                                print(f"  Skipped auto-detected view (similar to standard view)")
                    
                    if args.quiet:
                        for path in rendered_paths:
                            print(path)
                
                else:
                    # Original behavior for custom num_views
                    paths = renderer.render_best_views(
                        n_views=args.num_views,
                        quality=args.quality,
                        resolution=resolution
                    )
                    if args.quiet:
                        for path in paths:
                            print(path)
            
            return 0
            
    except ImportError as e:
        print(f"Error: Missing dependencies. Please install required packages:")
        print("  pip install pyvista numpy scikit-learn")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
