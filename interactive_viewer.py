import pyvista as pv
import numpy as np
import argparse
from pathlib import Path


def launch_interactive_viewer(model_path, quality='high'):
    """Launch a simple interactive 3D viewer."""
    print("🎮 Loading interactive 3D viewer...")
    print("Controls:")
    print("  • Mouse: Left=Rotate, Right=Pan, Scroll=Zoom")
    print("  • F=Front, B=Back, T=Top, O=Bottom, L=Left, R=Right")
    print("  • 's' key: Save current view as PNG")
    print("  • 'q' key: Quit")
    
    # Load mesh
    try:
        mesh = pv.read(str(model_path))
        print(f"✓ Loaded: {mesh.n_points:,} points, {mesh.n_cells:,} cells")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Get output directory and filename
    model_path = Path(model_path)
    output_dir = model_path.parent
    base_filename = model_path.stem
    
    # Center the mesh
    mesh.translate(-np.array(mesh.center))
    
    # Check for existing camera settings (hidden file)
    settings_file = output_dir / f".{base_filename}_camera_settings.json"
    saved_camera_settings = None
    if settings_file.exists():
        try:
            import json
            with open(settings_file, 'r') as f:
                saved_camera_settings = json.load(f)
            print(f"📁 Found previous camera settings: {settings_file}")
        except Exception as e:
            print(f"⚠ Could not load camera settings: {e}")
    
    # Create interactive plotter
    plotter = pv.Plotter(window_size=(1024, 768))
    plotter.background_color = '#2A2D35'
    
    # Enable panning and proper mouse interaction
    plotter.enable_trackball_style()
    
    # Add proper lighting for better visibility (matching renderer)
    plotter.add_light(pv.Light(position=(10, 10, 10), focal_point=(0, 0, 0), color='white'))
    plotter.add_light(pv.Light(position=(-10, -10, 10), focal_point=(0, 0, 0), color='white', intensity=0.6))
    plotter.add_light(pv.Light(position=(0, 0, -10), focal_point=(0, 0, 0), color='white', intensity=0.4))
    
    # Add mesh with enhanced bronze material (matching renderer)
    plotter.add_mesh(
        mesh,
        color='#CD7F32',  # Better bronze color
        smooth_shading=True,
        ambient=0.3,      # Increased ambient for better visibility
        diffuse=0.7,      # Increased diffuse
        specular=0.8,     # Increased specular
        specular_power=50,
        metallic=0.8,     # Add metallic property
        roughness=0.3     # Add roughness for realism
    )
    
    # Position camera for good initial view
    bounds = mesh.bounds
    max_dimension = max(
        bounds[1] - bounds[0],  # x
        bounds[3] - bounds[2],  # y
        bounds[5] - bounds[4]   # z
    )
    
    camera_distance = max_dimension * 4.0
    
    # Apply saved camera settings if available, otherwise use defaults
    if saved_camera_settings:
        print("🔄 Restoring previous camera position...")
        plotter.camera.position = saved_camera_settings["position"]
        plotter.camera.focal_point = saved_camera_settings["focal_point"]
        plotter.camera.up = saved_camera_settings["up_vector"]
        plotter.camera.clipping_range = saved_camera_settings["clipping_range"]
        if "view_angle" in saved_camera_settings:
            plotter.camera.view_angle = saved_camera_settings["view_angle"]
    else:
        # Default camera position
        plotter.camera.position = [camera_distance, 0, 0]
        plotter.camera.focal_point = [0, 0, 0]
        plotter.camera.up = [0, 0, 1]
        # Set clipping range to prevent clipping
        plotter.camera.clipping_range = (camera_distance * 0.01, camera_distance * 100.0)
    
    # Save current view function
    def save_current_view():
        filename = f"{base_filename}_interactive.png"
        output_path = output_dir / filename
        plotter.screenshot(str(output_path))
        
        # Get current camera settings
        camera = plotter.camera
        position = camera.position
        focal_point = camera.focal_point
        up_vector = camera.up
        clipping_range = camera.clipping_range
        view_angle = camera.view_angle
        
        print(f"✓ Saved current view: {output_path}")
        print("📷 Camera Settings:")
        print(f"   Position: [{position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f}]")
        print(f"   Focal Point: [{focal_point[0]:.3f}, {focal_point[1]:.3f}, {focal_point[2]:.3f}]")
        print(f"   Up Vector: [{up_vector[0]:.3f}, {up_vector[1]:.3f}, {up_vector[2]:.3f}]")
        print(f"   View Angle: {view_angle:.1f}°")
        print(f"   Clipping Range: [{clipping_range[0]:.1f}, {clipping_range[1]:.1f}]")
        print(f"   Distance: {np.linalg.norm(np.array(position) - np.array(focal_point)):.3f}")
        
        # Save camera settings to hidden file (force overwrite)
        camera_settings = {
            "position": [float(x) for x in position],
            "focal_point": [float(x) for x in focal_point],
            "up_vector": [float(x) for x in up_vector],
            "view_angle": float(view_angle),
            "clipping_range": [float(x) for x in clipping_range],
            "distance": float(np.linalg.norm(np.array(position) - np.array(focal_point))),
            "model_file": str(model_path),
            "timestamp": str(np.datetime64('now'))
        }
        
        # Use hidden file (starts with .) and force overwrite
        hidden_settings_file = output_dir / f".{base_filename}_camera_settings.json"
        import json
        with open(hidden_settings_file, 'w') as f:  # 'w' mode forces overwrite
            json.dump(camera_settings, f, indent=2)
        print(f"💾 Camera settings saved to hidden file: {hidden_settings_file.name}")
    
    # Camera preset functions
    def view_front():
        plotter.camera.position = [0, -camera_distance, 0]
        plotter.camera.focal_point = [0, 0, 0]
        plotter.camera.up = [0, 0, 1]
        print("📷 Front view")
    
    def view_back():
        plotter.camera.position = [0, camera_distance, 0]
        plotter.camera.focal_point = [0, 0, 0]
        plotter.camera.up = [0, 0, 1]
        print("📷 Back view")
    
    def view_top():
        plotter.camera.position = [0, 0, camera_distance]
        plotter.camera.focal_point = [0, 0, 0]
        plotter.camera.up = [0, 1, 0]
        print("📷 Top view")
    
    def view_bottom():
        plotter.camera.position = [0, 0, -camera_distance]
        plotter.camera.focal_point = [0, 0, 0]
        plotter.camera.up = [0, 1, 0]
        print("📷 Bottom view")
    
    def view_left():
        plotter.camera.position = [-camera_distance, 0, 0]
        plotter.camera.focal_point = [0, 0, 0]
        plotter.camera.up = [0, 0, 1]
        print("📷 Left view")
    
    def view_right():
        plotter.camera.position = [camera_distance, 0, 0]
        plotter.camera.focal_point = [0, 0, 0]
        plotter.camera.up = [0, 0, 1]
        print("📷 Right view")
    
    # Add key bindings
    plotter.add_key_event('s', save_current_view)
    plotter.add_key_event('f', view_front)
    plotter.add_key_event('b', view_back)
    plotter.add_key_event('t', view_top)
    plotter.add_key_event('o', view_bottom)
    plotter.add_key_event('l', view_left)
    plotter.add_key_event('r', view_right)
    
    # Show interactive window
    print("✓ Interactive viewer ready!")
    plotter.show()
    print("✅ Interactive session closed")


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
    parser = argparse.ArgumentParser(description="Interactive 3D Model Viewer")
    parser.add_argument("input", nargs='?', help="Input 3D model file - auto-detects if not specified")
    parser.add_argument("-Q", "--quality", choices=['low', 'medium', 'high', 'ultra'], 
                       default='high', help="Material quality")
    
    args = parser.parse_args()
    
    # Handle input file auto-detection
    input_file = args.input
    if input_file is None:
        # Auto-detect 3D files in current directory
        found_files = find_3d_files()
        
        if len(found_files) == 0:
            print("Error: No 3D model files found in current directory")
            print("Supported formats: STL, OBJ, PLY, 3MF, OFF, VTK, VTP, VTU, X3D")
            return
        elif len(found_files) > 1:
            print("Error: Multiple 3D model files found in current directory:")
            for f in sorted(found_files):
                print(f"  - {f}")
            print("Please specify which file to use:")
            print(f"  python interactive_viewer.py {found_files[0]}")
            return
        else:
            input_file = str(found_files[0])
            print(f"🎯 Auto-detected 3D model: {input_file}")
    
    launch_interactive_viewer(input_file, args.quality)


if __name__ == "__main__":
    main()
