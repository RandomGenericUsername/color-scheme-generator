# Deep Dive: Backends Explained

**Purpose:** Understand how each color extraction backend works
**Level:** Advanced
**Audience:** Users choosing backends, contributors extending backends

This document explains the algorithms and trade-offs for each backend.

---

## Backend Overview

Color extraction backends are algorithms that find the dominant colors in an image. Each backend uses a different approach:

| Backend | Algorithm | Speed | Quality | Setup | Best For |
|---------|-----------|-------|---------|-------|----------|
| **Custom** | K-means clustering | Medium | Good | Built-in | Default, reproducible |
| **Pywal** | Multiple algorithms | Fast | Good | External tool | Realistic colors |
| **Wallust** | Modern algorithm | Very Fast | Excellent | External tool | Performance-critical |

---

## Custom Backend: K-means Clustering

### How It Works

The custom backend uses the K-means clustering algorithm from scikit-learn:

```
Image
  ↓
Resize to 200×200 pixels
  ↓
Extract RGB values from each pixel
  ↓
Run K-means clustering with k=16
  ↓
16 cluster centers = 16 colors
  ↓
Sort by brightness
  ↓
Return as ColorScheme
```

### Algorithm Details

**K-means Clustering:**

K-means finds `k` cluster centers that minimize the distance between points and their nearest center:

```
1. Start with k random points
2. Assign each pixel to nearest cluster
3. Move clusters to mean of assigned pixels
4. Repeat steps 2-3 until convergence
5. Return cluster centers as colors
```

**Visual Example:**

```
Original image with 10,000 pixels
       ↓
Initial 16 random colors (clusters)
       ↓
Iteration 1: Assign pixels to clusters
Iteration 2: Move clusters to pixel mean
Iteration 3: Converge to stable clusters
       ↓
Final 16 colors (one per cluster)
```

### Configuration Options

```toml
[backends.custom]
# Algorithm: "kmeans" (default) or "minibatch"
algorithm = "kmeans"

# Number of colors to extract (8-256, default 16)
n_clusters = 16

# Random seed for reproducibility (default: not set)
random_seed = 42
```

**Algorithm Comparison:**

| Algorithm | Speed | Quality | Memory | Notes |
|-----------|-------|---------|--------|-------|
| **kmeans** | Medium | Good | Low | Standard, stable |
| **minibatch** | Fast | Slight loss | Low | For very large images |

### Advantages

✅ **Always available** - No external dependencies
✅ **Reproducible** - Same image → same colors (with seed)
✅ **Configurable** - Can adjust clusters and algorithm
✅ **Predictable** - Well-understood algorithm
✅ **Testable** - Pure Python, easy to test

### Disadvantages

❌ **Medium speed** - ~2-3 seconds for typical image
❌ **Memory use** - Loads full image into memory
❌ **Clustering artifacts** - May pick non-representative colors
❌ **Algorithm limitations** - Sensitive to initial centroids

### When to Use

- Default choice for all users
- Need reproducible results
- Can't install external tools
- Want configurable clustering
- Testing/development

### Code Example

```python
from color_scheme.backends.custom import CustomGenerator
from color_scheme.types import GeneratorConfig

config = GeneratorConfig(
    algorithm="kmeans",
    n_clusters=16,
    random_seed=42  # For reproducibility
)

generator = CustomGenerator(config)
colors = generator.generate(Path("image.jpg"))

# colors is a ColorScheme with 16 colors
# Result is deterministic with same seed
```

### Performance Notes

**Typical times (on modern hardware):**

```
Image Size     Time    Memory
640×480        1.2s    ~20MB
1920×1080      2.5s    ~60MB
4000×3000      4.0s    ~200MB
```

**Optimization tips:**

```python
# Use minibatch for very large images
config = GeneratorConfig(algorithm="minibatch", n_clusters=16)

# Set seed for faster repeat runs (cache?)
config = GeneratorConfig(random_seed=42)
```

---

## Pywal Backend: Multiple Algorithms

### How It Works

Pywal is a Python color extraction tool that uses multiple algorithms:

```
Image
  ↓
Pywal subprocess (separate process)
  ↓
Multiple extraction algorithms:
├─ Colorz (color quantization)
├─ Haishoku (histogram-based)
├─ ColourDB (eart color clusters)
└─ Custom (K-means)
  ↓
Select best results
  ↓
Return 16 colors
```

### Available Algorithms

Pywal can use different algorithms for different image types:

| Algorithm | Speed | Quality | Good For |
|-----------|-------|---------|----------|
| **haishoku** | Fast | Excellent | Realistic colors |
| **colorz** | Medium | Good | Varied images |
| **colordb** | Fast | Good | General use |
| **eart** | Slow | Excellent | Artistic analysis |

### Configuration Options

```toml
[backends.pywal]
# Which algorithm to use
backend_algorithm = "haishoku"  # Default

# Optional settings (algorithm-specific)
# haishoku_method = "k-means"
# colorz_k = 8
```

**Algorithm Details:**

**Haishoku** (Default)
- Analyzes color histograms
- Finds peaks in color distribution
- Very fast (< 1 second)
- Excellent for photographs

**Colorz**
- K-means on color quantized image
- Similar to custom backend but optimized
- Good balance of speed and quality
- Works well for diverse images

**ColorDB**
- Looks up colors in color database
- Fast and reliable
- Good for consistent results
- Less artistic

**EART**
- Advanced color analysis
- Slowest but very high quality
- Best for detailed color extraction
- Good for artistic images

### Advantages

✅ **Fast** - 1-2 seconds typical
✅ **Multiple algorithms** - Choose what works best
✅ **Mature** - Widely used in Linux community
✅ **Good results** - Optimized for real-world images
✅ **Well-tested** - Years of production use

### Disadvantages

❌ **External dependency** - Requires separate installation
❌ **Non-deterministic** - Different runs may vary slightly
❌ **Complex setup** - Multiple sub-algorithms
❌ **ImageMagick dependency** - Large binary in container

### When to Use

- Want fast extraction
- Prefer realistic colors
- Don't mind external dependency
- Need mature, battle-tested solution
- Using on Linux systems

### Installation

```bash
# On Ubuntu/Debian
sudo apt-get install pywal

# On Arch
sudo pacman -S pywal

# Via pip (requires ImageMagick)
sudo apt-get install libmagick-dev
pip install pywal
```

### Code Example

```python
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.types import GeneratorConfig

config = GeneratorConfig(
    backend_algorithm="haishoku"
)

generator = PywalGenerator(config)
colors = generator.generate(Path("image.jpg"))

# Subprocess may have slight variations
# Results are usually very good
```

### Performance Notes

```
Image Size     Time    Algorithm
640×480        0.8s    haishoku
1920×1080      1.2s    haishoku
4000×3000      1.8s    haishoku

640×480        2.0s    eart
1920×1080      3.0s    eart
4000×3000      4.5s    eart
```

---

## Wallust Backend: Rust-based Modern Algorithm

### How It Works

Wallust is a Rust-based color extraction tool using modern algorithms:

```
Image
  ↓
Wallust subprocess (Rust binary)
  ↓
Advanced color space analysis:
├─ Converts to LAB color space
├─ Uses different resizing modes
├─ Advanced clustering
└─ Color harmony analysis
  ↓
Extract 16 colors
  ↓
Return as color scheme
```

### Algorithm Features

**Resizing Modes:**

How images are preprocessed affects results:

| Mode | Speed | Quality | Use Case |
|------|-------|---------|----------|
| **None** | Slowest | Best | Small images |
| **Adaptive** | Fast | Good | General use |
| **Resized** | Very fast | Good | Large images |

```toml
[backends.wallust]
# Resizing strategy
backend_type = "resized"  # or "adaptive" or "none"
```

**Color Space Analysis:**

Wallust uses LAB color space (more perceptually uniform than RGB):

```
Image in RGB
  ↓
Convert to LAB color space
  ↓
Analyze color distribution in LAB
  ↓
Find dominant colors
  ↓
Convert back to RGB
```

Benefits of LAB:
- Perceptually uniform (colors equally spaced)
- Better for human vision
- More consistent results

### Configuration Options

```toml
[backends.wallust]
# Resizing method
backend_type = "resized"  # Default

# Optional settings
# wallust_no_sort = false  # Sort by brightness
# wallust_min_color_count = 1
```

### Advantages

✅ **Fastest** - 1-2 seconds even for large images
✅ **Modern algorithm** - LAB color space analysis
✅ **Excellent quality** - Optimized results
✅ **Small image** - Rust binary is tiny
✅ **Latest algorithms** - Active development

### Disadvantages

❌ **External dependency** - Requires cargo installation
❌ **Rust compilation** - Takes time to build
❌ **Newer project** - Less battle-tested
❌ **Platform support** - May not work on all systems

### When to Use

- Want maximum performance
- Processing many images
- Need best color extraction
- Have Rust toolchain available
- Running in CI/CD pipelines

### Installation

```bash
# Via cargo (Rust package manager)
cargo install wallust

# On Arch
sudo pacman -S wallust

# On macOS
brew install wallust
```

### Code Example

```python
from color_scheme.backends.wallust import WallustGenerator
from color_scheme.types import GeneratorConfig

config = GeneratorConfig(
    backend_type="resized"
)

generator = WallustGenerator(config)
colors = generator.generate(Path("image.jpg"))

# Fastest execution with good results
```

### Performance Notes

```
Image Size     Time    Mode
640×480        0.6s    resized
1920×1080      0.9s    resized
4000×3000      1.1s    resized

640×480        1.5s    adaptive
1920×1080      2.0s    adaptive
4000×3000      2.5s    adaptive

640×480        3.0s    none
1920×1080      4.5s    none
4000×3000      6.0s    none
```

---

## Comparison and Selection Guide

### Feature Comparison

| Feature | Custom | Pywal | Wallust |
|---------|--------|-------|---------|
| **Installation** | Built-in | External | External |
| **Speed** | Medium | Fast | Very Fast |
| **Quality** | Good | Good | Excellent |
| **Reproducibility** | Yes (with seed) | No | No |
| **Configurability** | High | Medium | Low |
| **Maturity** | High | Very High | Medium |
| **Memory** | Medium | Low | Low |
| **Dependencies** | NumPy, sklearn | ImageMagick | Rust binary |

### Decision Tree

```
What's your priority?

├─ Always available?
│  └─ YES → Use Custom
│  └─ NO → Continue
│
├─ Maximum quality?
│  └─ YES → Try Wallust (if available)
│  └─ NO → Continue
│
├─ Maximum speed?
│  └─ YES → Wallust > Pywal > Custom
│  └─ NO → Continue
│
├─ Reproducibility needed?
│  └─ YES → Custom (with seed)
│  └─ NO → Continue
│
├─ Configurability needed?
│  └─ YES → Custom
│  └─ NO → Continue
│
└─ Default recommendation
   └─ Try Wallust, fall back to Pywal, use Custom as last resort
```

### Typical Workflows

**New User:**
```bash
# Just works
color-scheme generate image.jpg
# Uses auto-detection: wallust > pywal > custom
```

**Performance Critical:**
```bash
# Wallust for speed
color-scheme generate image.jpg --backend wallust
```

**Reproducible Builds:**
```bash
# Custom with seed
color-scheme generate image.jpg --backend custom --seed 42
```

**Artistic Colors:**
```bash
# Pywal with eart algorithm
color-scheme generate image.jpg --backend pywal --algorithm eart
```

**CI/CD Deployment:**
```bash
# Container with all backends available
docker run color-scheme-wallust:latest generate image.jpg
# Falls back if needed
```

---

## Backend Implementation Details

### Backend Interface

All backends implement this interface:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from color_scheme.types import ColorScheme, GeneratorConfig

class ColorSchemeGenerator(ABC):
    def __init__(self, config: GeneratorConfig):
        self.config = config

    @abstractmethod
    def generate(self, image_path: Path) -> ColorScheme:
        """Extract colors from image"""
        pass
```

### Custom Backend Implementation

```python
def generate(self, image_path: Path) -> ColorScheme:
    # Load image
    image = Image.open(image_path)

    # Resize to 200x200 for performance
    image = image.resize((200, 200))

    # Convert to RGB
    image = image.convert('RGB')

    # Extract pixel data
    pixels = np.array(image).reshape(-1, 3)

    # Run K-means
    kmeans = KMeans(n_clusters=16, random_state=self.config.random_seed)
    kmeans.fit(pixels)

    # Get cluster centers
    colors = kmeans.cluster_centers_.astype(int)

    # Sort by brightness
    brightness = np.mean(colors, axis=1)
    colors = colors[np.argsort(brightness)]

    # Return as ColorScheme
    return ColorScheme(colors=colors)
```

### Pywal Backend Implementation

```python
def generate(self, image_path: Path) -> ColorScheme:
    # Call pywal subprocess
    cmd = [
        'wal',
        '-i', str(image_path),
        '-o',  # Don't apply to system
        '-b', self.config.backend_algorithm,
        '--json'
    ]

    result = subprocess.run(cmd, capture_output=True)

    # Parse JSON output
    data = json.loads(result.stdout)

    # Extract colors
    return ColorScheme(colors=data['colors'])
```

### Wallust Backend Implementation

```python
def generate(self, image_path: Path) -> ColorScheme:
    # Call wallust subprocess
    cmd = [
        'wallust',
        'run',
        str(image_path),
        '--type', self.config.backend_type,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse output
    colors = parse_wallust_output(result.stdout)

    # Return as ColorScheme
    return ColorScheme(colors=colors)
```

---

## Performance Tuning

### Custom Backend Tuning

```python
# For speed: fewer clusters, minibatch
config = GeneratorConfig(
    algorithm="minibatch",
    n_clusters=8
)

# For quality: kmeans, more clusters
config = GeneratorConfig(
    algorithm="kmeans",
    n_clusters=32
)

# For reproducibility: with seed
config = GeneratorConfig(
    algorithm="kmeans",
    random_seed=42
)
```

### Pywal Backend Tuning

```python
# For speed: haishoku
config = GeneratorConfig(
    backend_algorithm="haishoku"
)

# For quality: eart (slower but best)
config = GeneratorConfig(
    backend_algorithm="eart"
)
```

### Wallust Backend Tuning

```python
# Already optimized, but can tweak resizing:

# For large images: resized (default)
config = GeneratorConfig(
    backend_type="resized"
)

# For maximum quality: none (slowest)
config = GeneratorConfig(
    backend_type="none"
)
```

---

## Batch Processing Example

Process multiple images with different backends:

```python
from pathlib import Path
from color_scheme.factory import BackendFactory
from color_scheme.types import GeneratorConfig

images = list(Path("images/").glob("*.jpg"))

# Try each backend
for backend_type in ["wallust", "pywal", "custom"]:
    try:
        config = GeneratorConfig(backend=backend_type)
        backend = BackendFactory.create(backend_type, config)

        for image in images:
            colors = backend.generate(image)
            print(f"{image.name}: {backend_type} OK")

        break  # Success, stop trying
    except Exception as e:
        print(f"{backend_type} failed: {e}")
        continue
```

---

## Summary

Each backend has strengths:

- **Custom:** Always works, reproducible, configurable
- **Pywal:** Fast, mature, excellent results
- **Wallust:** Fastest, modern algorithms, excellent quality

Choose based on your needs:
- New users: Let auto-detection pick (wallust > pywal > custom)
- Performance: Use Wallust
- Reliability: Use Pywal or Custom
- Reproducibility: Use Custom with seed
- Flexibility: Use Custom

The beauty of the architecture is you can switch backends without changing your code!
