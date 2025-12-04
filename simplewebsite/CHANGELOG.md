# Changelog - Cosmos Predict 2.5 Simple Web Interface

## Version 1.1 - Enhanced Resolution Support (2025-12-03)

### Added Features

#### 1. Resolution Preset Dropdown
- Replaced manual height/width inputs with intelligent preset selector
- **40+ optimized resolutions** organized by quality level and aspect ratio
- Grouped by:
  - **720p Quality (Default)** - Recommended for 2B model
  - **720p Standard**
  - **480p Quality** - Faster generation
  - **480p Standard**
  - **512p Quality**
  - **1080p Quality** - High memory requirements
  - **Custom** - Manual resolution entry

#### 2. All Available Resolutions for 2B Model

Based on official Cosmos 2.5 specifications and codebase research:

**720p Quality (Default - Model Native Resolution)**
- 704 x 1280 (9:16 Vertical) ⭐ Default
- 1280 x 704 (16:9 Widescreen)
- 960 x 960 (1:1 Square)
- 960 x 704 (4:3 Landscape)
- 704 x 960 (3:4 Portrait)

**480p Quality (Faster Throughput)**
- 432 x 768 (9:16 Vertical)
- 768 x 432 (16:9 Widescreen)
- 640 x 480 (4:3 Landscape)
- 480 x 640 (3:4 Portrait)
- 480 x 480 (1:1 Square)

**1080p Quality (High Memory)**
- 1056 x 1920 (9:16 Vertical)
- 1920 x 1056 (16:9 Widescreen)
- 1440 x 1056 (4:3 Landscape)
- 1056 x 1440 (3:4 Portrait)
- 1024 x 1024 (1:1 Square)

Plus: 512p, 720p Standard, 480p Standard presets

#### 3. Custom Resolution Option
- Select "Custom Resolution..." from dropdown
- Reveals manual height/width input fields
- Supports resolutions from 128px to 2048px
- 8-pixel step increments for optimal compatibility

#### 4. Improved Autoregressive Mode
- ✓ **Enabled by default** (as per your configuration)
- Checkbox clearly labeled
- Chunk settings (size/overlap) automatically show/hide
- Better visual feedback

### UI Improvements

#### Enhanced Form Controls
- Modern dropdown with custom styling
- Green accent color for dropdown arrow
- Organized option groups with bold headers
- Full-width resolution selector for better readability
- Smooth transitions between preset and custom modes

#### Better Visual Hierarchy
- Help text under resolution selector explains memory requirements
- Aspect ratios clearly labeled (9:16, 16:9, 1:1, etc.)
- Quality indicators (Default, Faster, High Memory)

### Technical Details

#### Frontend (JavaScript)
- New `initializeResolutionSelector()` function
- Automatic sync between preset dropdown and hidden height/width fields
- Dynamic show/hide of custom resolution fields
- Preserves existing form validation

#### Styling (CSS)
- Custom select dropdown with SVG arrow icon
- Full-width form group support
- Responsive optgroup styling
- Dark theme consistency maintained

#### Backend (app.py)
- No changes required - seamless integration
- Hidden fields still send resolution_height and resolution_width
- Backward compatible with existing API

### Research Sources

Resolution specifications compiled from:
1. **Web Research**: Cosmos 2.5 2B model documentation
2. **Codebase Analysis**: `/cosmos_predict2/_src/predict2/datasets/utils.py`
3. **Model Config**: `/cosmos_predict2/_src/predict2/configs/video2world/experiment/`
4. **Example Configs**: `/assets/` directory

### Performance Notes

- **720p (704x1280)**: Native model resolution, best quality/speed balance
- **480p (432x768)**: ~30% faster, good for testing and iteration
- **1080p (1920x1056)**: Requires significant GPU memory (16GB+ recommended)

### Migration Guide

No migration needed! The interface automatically:
- Uses 704x1280 as the default (model's native resolution)
- Maintains your example config support (432x768 available as preset)
- Supports existing custom resolutions via "Custom" option

### Files Modified

1. `/simplewebsite/templates/index.html`
   - Added resolution preset dropdown
   - Added custom resolution toggle section
   - Marked autoregressive checkbox as checked by default

2. `/simplewebsite/static/js/main.js`
   - Added `initializeResolutionSelector()` function
   - Dynamic preset/custom resolution switching
   - Automatic field population

3. `/simplewebsite/static/css/styles.css`
   - Select element styling with custom arrow
   - Optgroup visual hierarchy
   - Full-width form group support

4. `/simplewebsite/README.md`
   - Updated with resolution preset information
   - Enhanced configuration examples
   - Added resolution quality comparison

5. `/simplewebsite/CHANGELOG.md` (this file)
   - Complete documentation of changes

### Known Limitations

- Maximum resolution limited to 2048px (configurable in code)
- Very high resolutions may cause out-of-memory errors on GPUs with <16GB VRAM
- Custom resolutions should use dimensions divisible by 8 for optimal performance

### Recommendations

**For Best Results:**
- Use default 704x1280 for production
- Use 432x768 for quick testing
- Enable autoregressive for videos longer than 3 seconds
- Keep chunk_size ≤ 77 for 2B model

**For Memory-Constrained GPUs (<8GB):**
- Stick to 480p or 512p presets
- Disable autoregressive if possible
- Consider offloading options in main Cosmos config

---

## Version 1.0 - Initial Release (2025-12-03)

### Features
- Simple web interface for Cosmos Predict 2.5 image2world generation
- Drag & drop image upload
- Manual prompt entry
- Advanced settings (frames, seed, guidance, etc.)
- Password authentication
- Real-time progress tracking
- Video preview and download
- Organized file storage
