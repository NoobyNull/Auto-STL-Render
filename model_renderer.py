import pyvista as pv
import numpy as np
import argparse
import os
from pathlib import Path
import json
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


class ModelRenderer:
    def __init__(self, model_path, output_dir=None, verbose=True):
        """Basic 3D model renderer with front detection."""
        self.model_path = Path(model_path)
        self.verbose = verbose
        
        # Set output directory
        if output_dir is None:
            self.output_dir = self.model_path.parent
        else:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(exist_ok=True)
        
        self.base_filename = self.model_path.stem
        
        # Load mesh
        try:
            if self.verbose:
                print(f"Loading model: {model_path}")
            self.mesh = pv.read(str(model_path))
            if self.verbose:
                print(f"✓ Successfully loaded: {self.mesh.n_points:,} points, {self.mesh.n_cells:,} cells")
        except Exception as e:
            raise Exception(f"Failed to load model: {e}")
        
        # Calculate dimensions
        bounds = self.mesh.bounds
        self.max_dimension = max(
            bounds[1] - bounds[0],  # x
            bounds[3] - bounds[2],  # y
            bounds[5] - bounds[4]   # z
        )
        
        # Center the mesh
        self.mesh.translate(-np.array(self.mesh.center))
        
        if self.verbose:
            print(f"  Max dimension: {self.max_dimension:.2f}")
    
    def find_best_front_views(self, n_views=3):
        """Find best viewing angles, prioritizing top and front views first."""
        if self.verbose:
            print("Finding optimal viewing angles...")
        
        # Get points for PCA
        points = self.mesh.points
        pca = PCA(n_components=3)
        pca.fit(points)
        
        # Priority views to test first (top and front)
        priority_views = [
            ([0, 0, 1], "top"),      # Top view
            ([0, -1, 0], "front"),   # Front view
        ]
        
        # Generate all candidate views including PCA-based
        all_candidates = []
        
        # Add priority views first
        for view_dir, name in priority_views:
            all_candidates.append((np.array(view_dir), name, True))  # True = priority
        
        # PCA-based views
        for i, component in enumerate(pca.components_):
            all_candidates.append((component, f"pca_{i}_pos", False))
            all_candidates.append((-component, f"pca_{i}_neg", False))
        
        # Standard orthographic views
        standard_views = [
            ([1, 0, 0], "right"), ([-1, 0, 0], "left"),    # sides
            ([0, 1, 0], "back"),                            # back
            ([0, 0, -1], "bottom"),                         # bottom
            ([1, 1, 0], "diag_1"), ([1, 0, 1], "diag_2"),  # diagonals
        ]
        for view_dir, name in standard_views:
            all_candidates.append((np.array(view_dir) / np.linalg.norm(view_dir), name, False))
        
        # Score all views
        scored_views = []
        for view_dir, name, is_priority in all_candidates:
            view_dir = view_dir / np.linalg.norm(view_dir)
            
            # Score based on PCA alignment and face visibility
            pca_score = max([abs(np.dot(view_dir, comp)) for comp in pca.components_])
            
            # Face visibility score - optimized for large meshes
            try:
                if self.mesh.n_cells > 0 and self.mesh.n_cells < 100000:  # Only for reasonably sized meshes
                    if self.verbose and self.mesh.n_cells > 10000:
                        print(f"    Computing face normals for {self.mesh.n_cells:,} cells...")
                    
                    # Use existing normals if available, otherwise compute
                    if 'Normals' in self.mesh.cell_data:
                        face_normals = self.mesh.cell_data['Normals']
                    else:
                        # For large meshes, use a simpler approach
                        face_normals = self.mesh.face_normals
                    
                    dot_products = np.dot(face_normals, view_dir)
                    visibility_score = np.sum(dot_products > 0) / len(face_normals)
                else:
                    # For very large meshes, use simplified scoring
                    if self.verbose and self.mesh.n_cells >= 100000:
                        print(f"    Large mesh ({self.mesh.n_cells:,} cells) - using simplified scoring")
                    visibility_score = 0.6  # Reasonable default
            except Exception as e:
                if self.verbose:
                    print(f"    Face normal computation failed: {e}")
                    print("    Using simplified scoring...")
                visibility_score = 0.6  # Fallback score
            
            # Calculate total score with priority boost
            base_score = pca_score * 2.0 + visibility_score * 3.0
            
            # Boost priority views (top and front)
            if is_priority:
                final_score = base_score + 1.0  # Priority bonus
                if self.verbose:
                    print(f"  Priority view '{name}': base={base_score:.2f}, final={final_score:.2f}")
            else:
                final_score = base_score
            
            scored_views.append((view_dir, final_score, name))
        
        # Sort by score and remove duplicates
        scored_views.sort(key=lambda x: x[1], reverse=True)
        unique_views = []
        
        for view_dir, score, name in scored_views:
            is_unique = True
            for existing_view, _, _ in unique_views:
                if np.dot(view_dir, existing_view) > 0.9:
                    is_unique = False
                    break
            if is_unique:
                unique_views.append((view_dir, score, name))
                if self.verbose:
                    print(f"  Selected view '{name}': score={score:.2f}")
            if len(unique_views) >= n_views:
                break
        
        if self.verbose:
            print(f"✓ Found {len(unique_views)} best views")
        
        # Return in the old format for compatibility
        return [(view_dir, score) for view_dir, score, name in unique_views]
    
    def get_preset_view(self, preset_name):
        """Get camera position and up vector for preset views (matching interactive viewer)."""
        camera_distance = self.max_dimension * 4.0  # Match interactive viewer distance
        
        presets = {
            'front': {
                'position': [0, -camera_distance, 0],
                'up': [0, 0, 1]
            },
            'back': {
                'position': [0, camera_distance, 0],
                'up': [0, 0, 1]
            },
            'top': {
                'position': [0, 0, camera_distance],
                'up': [0, 1, 0]
            },
            'bottom': {
                'position': [0, 0, -camera_distance],
                'up': [0, 1, 0]
            },
            'left': {
                'position': [-camera_distance, 0, 0],
                'up': [0, 0, 1]
            },
            'right': {
                'position': [camera_distance, 0, 0],
                'up': [0, 0, 1]
            }
        }
        
        return presets.get(preset_name.lower())
    
    def render_view(self, view_direction=None, preset=None, filename=None, resolution=(1080, 1080), quality='high'):
        """Render a single view using either custom direction or preset."""
        
        if preset:
            # Use preset view (matching interactive viewer)
            preset_data = self.get_preset_view(preset)
            if not preset_data:
                raise ValueError(f"Unknown preset '{preset}'. Available: front, back, top, bottom, left, right")
            
            camera_position = preset_data['position']
            camera_up = preset_data['up']
            
            if self.verbose:
                print(f"  Using preset view: {preset}")
        else:
            # Use custom view direction
            if view_direction is None:
                raise ValueError("Must specify either view_direction or preset")
            
            view_direction = np.array(view_direction) / np.linalg.norm(view_direction)
            
            # Calculate camera position
            camera_distance = self.max_dimension * 5.5
            camera_position = -view_direction * camera_distance
            camera_up = [0, 0, 1]
        
        # Generate filename
        if filename is None:
            if preset:
                filename = f"{self.base_filename}_{preset}.png"
            else:
                filename = f"{self.base_filename}.png"
        output_path = self.output_dir / filename
        
        if self.verbose:
            print(f"  Rendering {filename}...")
        
        # Create plotter
        plotter = pv.Plotter(off_screen=True, window_size=resolution)
        plotter.background_color = '#2A2D35'  # Match interactive viewer
        
        # Use the same lighting as interactive viewer
        plotter.add_light(pv.Light())  # Default lighting that works well
        
        # Add mesh with settings that match interactive viewer
        plotter.add_mesh(
            self.mesh,
            color='#B8860B',  # Dark goldenrod - better than bright gold
            smooth_shading=True,
            ambient=0.3,
            diffuse=0.7,
            specular=0.5,
            specular_power=30
        )
        
        # Since mesh is already centered at origin, mesh center is [0,0,0]
        bounds = self.mesh.bounds
        mesh_center = [0, 0, 0]  # Already centered in __init__
        
        # Calculate mesh dimensions
        x_size = bounds[1] - bounds[0]
        y_size = bounds[3] - bounds[2]
        z_size = bounds[5] - bounds[4]
        max_size = max(x_size, y_size, z_size)
        
        # Calculate optimal camera distance for good framing
        # Use the actual diagonal size of the bounding box
        diagonal_size = np.sqrt(x_size**2 + y_size**2 + z_size**2)
        camera_distance = diagonal_size * 1.8  # Optimal distance for full view
        
        if preset:
            if preset.lower() == 'top':
                # Position camera above the actual mesh center
                camera_position = [mesh_center[0], mesh_center[1], mesh_center[2] + camera_distance]
                focal_point = mesh_center
                camera_up = [0, 1, 0]
            elif preset.lower() == 'front':
                camera_position = [mesh_center[0], mesh_center[1] - camera_distance, mesh_center[2]]
                focal_point = mesh_center
                camera_up = [0, 0, 1]
            elif preset.lower() == 'back':
                camera_position = [mesh_center[0], mesh_center[1] + camera_distance, mesh_center[2]]
                focal_point = mesh_center
                camera_up = [0, 0, 1]
            elif preset.lower() == 'left':
                camera_position = [mesh_center[0] - camera_distance, mesh_center[1], mesh_center[2]]
                focal_point = mesh_center
                camera_up = [0, 0, 1]
            elif preset.lower() == 'right':
                camera_position = [mesh_center[0] + camera_distance, mesh_center[1], mesh_center[2]]
                focal_point = mesh_center
                camera_up = [0, 0, 1]
            elif preset.lower() == 'bottom':
                camera_position = [mesh_center[0], mesh_center[1], mesh_center[2] - camera_distance]
                focal_point = mesh_center
                camera_up = [0, 1, 0]
            else:
                raise ValueError(f"Unknown preset '{preset}'. Available: front, back, top, bottom, left, right")
        else:
            # Custom view direction - position relative to actual mesh center
            view_direction = np.array(view_direction) / np.linalg.norm(view_direction)
            camera_position = np.array(mesh_center) - view_direction * camera_distance
            focal_point = mesh_center
            camera_up = [0, 0, 1]
        
        # Set camera with intelligent positioning
        plotter.camera.position = camera_position
        plotter.camera.focal_point = focal_point
        plotter.camera.up = camera_up
        plotter.camera.view_angle = 30.0
        
        # Calculate optimal clipping range based on actual geometry
        distance = np.linalg.norm(np.array(camera_position) - np.array(focal_point))
        near_clip = max(distance - diagonal_size, distance * 0.1)
        far_clip = distance + diagonal_size
        plotter.camera.clipping_range = (near_clip, far_clip)
        
        # Use automatic framing but with better zoom calculation
        plotter.reset_camera()
        
        # Calculate zoom to get 85-90% fill based on model's actual projected size
        # This ensures consistent framing regardless of model orientation
        current_bounds = plotter.renderer.ComputeVisiblePropBounds()
        if current_bounds and len(current_bounds) >= 6:
            visible_width = max(
                current_bounds[1] - current_bounds[0],  # x span
                current_bounds[3] - current_bounds[2],  # y span
            )
            # Target 87.5% fill of the viewport
            target_fill = 0.875
            if visible_width > 0:
                zoom_factor = target_fill / (visible_width / max_size)
                zoom_factor = max(0.5, min(3.0, zoom_factor))  # Clamp zoom
                plotter.camera.zoom(zoom_factor)
                
                if self.verbose:
                    print(f"  Applied intelligent zoom: {zoom_factor:.2f} for {target_fill*100:.1f}% fill")
        
        # Render
        plotter.show(screenshot=str(output_path), return_cpos=False)
        plotter.close()
        
        if self.verbose:
            print(f"✓ Saved: {output_path}")
        
        return str(output_path)
    
    def render_best_views(self, n_views=1, quality='high', resolution=(1080, 1080)):
        """Render the best front views."""
        best_views = self.find_best_front_views(n_views)
        rendered_paths = []
        
        for i, (view_dir, score) in enumerate(best_views):
            if n_views == 1:
                filename = f"{self.base_filename}.png"
            else:
                filename = f"{self.base_filename}_view{i+1:02d}.png"
            
            path = self.render_view(
                view_direction=view_dir, 
                filename=filename, 
                resolution=resolution, 
                quality=quality
            )
            rendered_paths.append(path)
        
        return rendered_paths


def main():
    parser = argparse.ArgumentParser(description="3D Model Front Detection and Rendering")
    parser.add_argument("input", help="Input 3D model file")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-n", "--num-views", type=int, default=1, help="Number of views to render")
    parser.add_argument("-Q", "--quality", choices=['low', 'medium', 'high', 'ultra'], 
                       default='high', help="Rendering quality")
    parser.add_argument("-r", "--resolution", type=str, default="1080x1080", 
                       help="Resolution (WIDTHxHEIGHT)")
    parser.add_argument("-s", "--single-view", nargs=3, type=float, metavar=('X', 'Y', 'Z'),
                       help="Render specific view direction")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
        resolution = (width, height)
    except:
        resolution = (1080, 1080)
    
    try:
        renderer = ModelRenderer(args.input, args.output, verbose=not args.quiet)
        
        if args.single_view:
            # Render specific view
            path = renderer.render_view(
                view_direction=args.single_view,
                resolution=resolution,
                quality=args.quality
            )
            if args.quiet:
                print(path)
        else:
            # Render best views
            paths = renderer.render_best_views(
                n_views=args.num_views,
                quality=args.quality,
                resolution=resolution
            )
            if args.quiet:
                for path in paths:
                    print(path)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
