# 3D Model Renderer with Intelligent Front Detection

A professional 3D model rendering tool that automatically identifies optimal viewing angles and generates high-quality images. Perfect for product photography, technical documentation, and automated 3D asset processing.

## ✨ Features

- **🎯 Auto-Detection**: Automatically detects 3D models in the current directory
- **🧠 Intelligent Front Detection**: Uses PCA analysis and face visibility scoring to find the best views
- **📸 Multi-View Rendering**: Generates front, top, back views + unique auto-detected angle
- **🎨 Professional Quality**: Dark backgrounds, proper lighting, intelligent zoom (87.5% fill)
- **🖱️ Interactive Viewer**: Real-time 3D exploration with camera position saving
- **⚡ Large Mesh Support**: Efficiently handles models with 500K+ faces
- **📋 Multiple Formats**: STL, OBJ, PLY, VTK, 3MF, X3D and more

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Auto-detect 3D file and render 3 standard views + auto view
cd /path/to/your/stl/files
python render_3d.py

# Explicit file with preset view
python render_3d.py model.stl -p front

# Interactive viewer
python render_3d.py model.stl -i

# High resolution rendering
python render_3d.py model.stl -r 2048x2048 -Q ultra
```

## 📖 Usage Guide

### Auto-Detection Mode (Recommended)

Place your 3D file in a directory and run the script from there:

```bash
cd /path/to/stl/directory
python render_3d.py
```

**Output**: 3 standard views + auto-detected view (if unique)
- `ModelName_front.png` - Front view
- `ModelName_top.png` - Top view  
- `ModelName_back.png` - Back view
- `ModelName_auto.png` - Auto-detected view (only if significantly different)

### Manual File Specification

```bash
# Single best auto-detected view
python render_3d.py model.stl

# Specific preset views (matches interactive viewer)
python render_3d.py model.stl -p front
python render_3d.py model.stl -p top
python render_3d.py model.stl -p back

# Custom view direction [X, Y, Z]
python render_3d.py model.stl -s 1 1 0.5

# Multiple auto-detected views
python render_3d.py model.stl -n 5
```

### Interactive Mode

```bash
python render_3d.py model.stl -i
```

**Interactive Controls:**
- Mouse: Rotate, zoom, pan
- Save perfect camera position to JSON
- Copy camera settings to use in batch rendering

### Quality & Resolution Options

```bash
# Quality levels: low, medium, high, ultra
python render_3d.py model.stl -Q ultra

# Custom resolution
python render_3d.py model.stl -r 3840x2160

# Output directory
python render_3d.py model.stl -o ./renders/
```

## 🎯 How Front Detection Works

### Intelligent Multi-Algorithm Analysis

1. **PCA Analysis**: Identifies major axes of the 3D model
2. **Face Visibility Scoring**: Calculates visible surface area from each angle
3. **Priority Views**: Front and top views get +1.0 bonus scoring
4. **Large Mesh Optimization**: Simplified scoring for models >100K faces
5. **Similarity Detection**: Avoids duplicate views (90% similarity threshold)

### Professional Rendering Quality

- **Dark Professional Background**: No bright white washout
- **Dark Goldenrod Materials**: Excellent contrast and visibility
- **Intelligent Camera Positioning**: Geometry-based distance calculation
- **Smart Zoom**: Consistent 87.5% screen fill for all views
- **Optimal Lighting**: Default PyVista lighting proven for quality

## 📁 Project Structure

```
3d-model-renderer/
├── render_3d.py              # Main CLI interface with auto-detection
├── model_renderer.py         # Core rendering engine
├── interactive_viewer.py     # Interactive 3D viewer
├── example_usage.py          # Usage examples
├── requirements.txt          # Python dependencies
├── setup.py                 # Package setup
└── README.md               # This file
```

## 📋 Command Line Reference

```bash
# Auto-detection and rendering
python render_3d.py                              # Auto-detect, 3+auto views
python render_3d.py -q                           # Quiet mode

# File specification
python render_3d.py model.stl                    # Explicit file, 3+auto views
python render_3d.py model.stl -n 1               # Single best view only

# View presets (matching interactive viewer)
python render_3d.py model.stl -p front           # Front view
python render_3d.py model.stl -p top             # Top view
python render_3d.py model.stl -p back            # Back view
python render_3d.py model.stl -p left            # Left view
python render_3d.py model.stl -p right           # Right view
python render_3d.py model.stl -p bottom          # Bottom view

# Custom views
python render_3d.py model.stl -s 1 1 0.5         # Custom direction [X,Y,Z]
python render_3d.py model.stl -n 5               # 5 best auto views

# Quality options
python render_3d.py model.stl -Q low             # Fast preview
python render_3d.py model.stl -Q high            # Production quality
python render_3d.py model.stl -Q ultra           # Maximum quality

# Resolution options
python render_3d.py model.stl -r 512x512         # Lower resolution
python render_3d.py model.stl -r 2048x2048       # High resolution
python render_3d.py model.stl -r 3840x2160       # 4K resolution

# Interactive viewer
python render_3d.py model.stl -i                 # Launch interactive viewer

# Output options
python render_3d.py model.stl -o ./renders/      # Custom output directory
```

## 🧪 Python API

```python
from model_renderer import ModelRenderer

# Create renderer
renderer = ModelRenderer("model.stl", verbose=True)

# Render preset views
renderer.render_view(preset="front", quality="high")
renderer.render_view(preset="top", resolution=(2048, 2048))

# Custom view directions
renderer.render_view(view_direction=[1, 1, 0.5])

# Auto-detect best views
paths = renderer.render_best_views(n_views=3, quality="ultra")

# Analysis only (no rendering)
best_views = renderer.find_best_front_views(n_views=5)
for view_direction, score in best_views:
    print(f"View: {view_direction}, Score: {score:.2f}")
```

## 🎨 Output Examples

### Standard Multi-View Output
```
ModelName_front.png    # Front view (professional contrast)
ModelName_top.png      # Top view (87.5% screen fill)
ModelName_back.png     # Back view (consistent quality)
ModelName_auto.png     # Auto-detected (only if unique)
```

### Quality Comparison
- **Low**: Fast preview rendering
- **Medium**: Smooth shading enabled
- **High**: Anti-aliasing + enhanced lighting *(recommended)*
- **Ultra**: Maximum quality with advanced effects

## 🔧 Supported 3D Formats

**Primary Formats:**
- **STL** - STereoLithography (most common 3D printing format)
- **OBJ** - Wavefront OBJ (with materials)
- **PLY** - Polygon File Format

**Additional Formats:**
- VTK, VTP, VTU - Visualization Toolkit formats
- 3MF - 3D Manufacturing Format
- X3D - Extensible 3D Graphics
- OFF - Object File Format

## ⚡ Performance Features

### Large Mesh Optimization
- **Efficient Processing**: Handles 500K+ face models smoothly
- **Smart Scoring**: Simplified algorithms for complex geometry
- **Memory Management**: Optimized for large CAD files
- **Progress Feedback**: Real-time processing updates

### Quality vs Speed Balance
- **Preview Mode**: Use `-Q low` for quick iterations
- **Production Mode**: Use `-Q high` for final output
- **Batch Processing**: Auto-detection for multiple files
- **Intelligent Caching**: Mesh preprocessing optimizations

## 🐛 Troubleshooting

### Common Issues

**"No 3D model files found"**
```bash
# Make sure you're in the directory with your 3D files
cd /path/to/stl/files
python render_3d.py
```

**Memory issues with large models**
```bash
# Use lower quality for large models
python render_3d.py large_model.stl -Q medium
```

**Poor contrast/visibility**
- The dark background and gold material provide excellent contrast
- Use `-Q high` or `-Q ultra` for best visual quality
- Check that your model has proper geometry

**Auto-detection finds wrong view**
```bash
# Use preset views for consistent results
python render_3d.py model.stl -p front
python render_3d.py model.stl -p top
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [PyVista](https://pyvista.org/) for 3D visualization
- Uses [scikit-learn](https://scikit-learn.org/) for PCA analysis
- Inspired by automated product photography workflows
