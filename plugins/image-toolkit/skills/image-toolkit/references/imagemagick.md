# 🧰 ImageMagick 7 — Vollständige Kommando-Referenz

> **Wichtig:** ImageMagick 7 verwendet `magick` als Hauptbefehl. Der alte `convert` ist veraltet.

## Inhaltsverzeichnis
1. [Geometrie-Syntax](#geometrie-syntax)
2. [Format-Konvertierung](#format-konvertierung)
3. [Resize](#resize)
4. [Crop](#crop)
5. [Rotate & Flip](#rotate--flip)
6. [Hintergrund-Operationen](#hintergrund-operationen)
7. [Compositing & Overlays](#compositing--overlays)
8. [Text & Annotationen](#text--annotationen)
9. [Formen zeichnen](#formen-zeichnen)
10. [Farboperationen](#farboperationen)
11. [Graustufen & Schwarz-Weiß](#graustufen--schwarz-weiß)
12. [Spezialeffekte](#spezialeffekte)
13. [Alpha-Kanal & Masken](#alpha-kanal--masken)
14. [Mogrify (Batch-Verarbeitung)](#mogrify-batch-verarbeitung)
15. [Montage (Bild-Grids)](#montage-bild-grids)
16. [GIF-Animation](#gif-animation)
17. [Format-spezifische Tipps](#format-spezifische-tipps)
18. [Häufige Rezepte](#häufige-rezepte)
19. [Performance-Tipps](#performance-tipps)
20. [Flags-Schnellreferenz](#flags-schnellreferenz)

---

## Geometrie-Syntax

Used by `-resize`, `-crop`, `-extent`, `-geometry`:

| Syntax | Meaning |
|--------|---------|
| `500x300` | Fit in 500×300, keep aspect ratio |
| `500x300!` | Exact 500×300, ignore aspect ratio |
| `500x` | Width = 500, height proportional |
| `x300` | Height = 300, width proportional |
| `50%` | 50% of original |
| `500x300^` | Fill area (smallest dimension determines) |
| `500x300>` | Only shrink, never enlarge |
| `500x300<` | Only enlarge, never shrink |
| `4096@` | Max total pixel count |

---

## Format-Konvertierung

```bash
magick input.png output.jpg
magick input.jpg output.webp
magick input.bmp output.png

# With quality
magick input.png -quality 85 output.jpg

# PDF pages to images
magick input.pdf output_%03d.png
magick 'input.pdf[0]' first_page.png
magick 'input.gif[0-3]' frame_%d.png
```

---

## Resize

```bash
# Proportional, fit in 800x600
magick input.jpg -resize 800x600 output.jpg

# Exact size (ignores aspect ratio)
magick input.jpg -resize 800x600! output.jpg

# Width only
magick input.jpg -resize 800x output.jpg

# Height only
magick input.jpg -resize x600 output.jpg

# Percentage
magick input.jpg -resize 50% output.jpg

# Only shrink (never enlarge)
magick input.jpg -resize 800x600\> output.jpg

# Fit with padding (white background)
magick input.jpg -resize 200x200 -background white \
  -gravity center -extent 200x200 thumbnail.jpg

# Fill and crop (no padding)
magick input.jpg -resize 200x200^ \
  -gravity center -extent 200x200 fill_crop.jpg

# Fast thumbnail (strips metadata)
magick input.jpg -thumbnail 200x200 thumb.jpg

# Resize + sharpen (quality-conscious)
magick input.jpg -resize 200x200 -unsharp 0x1 output.jpg
```

---

## Crop

```bash
# Crop 400x300 starting at x=50, y=20
magick input.jpg -crop 400x300+50+20 output.jpg

# Square from center
magick input.jpg -gravity center -crop 400x400+0+0 +repage output.jpg

# Remove uniform border
magick input.jpg -shave 10x10 output.jpg

# Auto-trim whitespace
magick input.jpg -trim output.jpg

# Trim with fuzz tolerance
magick input.jpg -fuzz 5% -trim output.jpg

# Split into 3 equal horizontal tiles
magick input.jpg -crop 3x1@ +repage tile_%d.png
```

---

## Rotate & Flip

```bash
# Rotate
magick input.jpg -rotate 90 output.jpg
magick input.jpg -rotate 180 output.jpg
magick input.jpg -background white -rotate 45 output.jpg

# Auto-orient (fix EXIF rotation)
magick input.jpg -auto-orient output.jpg

# Mirror
magick input.jpg -flip output.jpg   # Vertical
magick input.jpg -flop output.jpg   # Horizontal

# Transpose / Transverse
magick input.jpg -transpose output.jpg
magick input.jpg -transverse output.jpg
```

---

## Hintergrund-Operationen

### Make background transparent

```bash
# Transparent canvas
magick -size 400x300 xc:transparent output.png

# Make exact color transparent
magick input.png -transparent white output.png

# With fuzz tolerance
magick input.png -fuzz 10% -transparent white output.png

# Floodfill from corner
magick input.png -bordercolor white -border 1x1 \
  -alpha set -channel RGBA -fuzz 20% \
  -fill none -floodfill +0+0 white \
  -shave 1x1 output.png
```

### Change background color

```bash
# Replace transparency with color
magick input.png -background skyblue -alpha remove -alpha off output.jpg

# Flatten with background
magick input.png -background red -flatten output.jpg

# Add colored canvas behind image
magick -size 800x600 xc:navy input.png \
  -gravity center -composite output.png
```

### Advanced background removal

```bash
# Floodfill method (flat colors)
magick input.jpg -fuzz 15% \
  -bordercolor white -border 1 \
  -fill none -draw "alpha 0,0 floodfill" \
  -shave 1x1 result.png
```

---

## Compositing & Overlays

### Overlay images

```bash
# Basic overlay (top-left)
magick background.jpg overlay.png -composite output.jpg

# Centered
magick background.jpg overlay.png -gravity center -composite output.jpg

# Bottom-right with offset
magick background.jpg overlay.png \
  -gravity southeast -geometry +20+20 -composite output.jpg
```

### Watermarks

```bash
# Logo watermark bottom-right
magick input.jpg logo.png \
  -gravity southeast -geometry +10+10 \
  -composite output.jpg

# Semi-transparent logo (50% opacity)
magick input.jpg \
  \( logo.png -alpha set -evaluate Multiply 0.5 \) \
  -gravity center -composite output.jpg

# Dissolve composite
magick img.jpg watermark.png \
  -gravity southwest -geometry -10-10 \
  -define compose:args=50,100 \
  -compose Dissolve -composite result.jpg
```

### Combine images

```bash
# Side by side (horizontal)
magick img1.jpg img2.jpg img3.jpg +append output.jpg

# Stacked (vertical)
magick img1.jpg img2.jpg img3.jpg -append output.jpg

# With spacing
magick img1.jpg img2.jpg \
  -bordercolor white -border 5x5 \
  +append output.jpg
```

### Compose operators

| Operator | Effect |
|----------|--------|
| `Over` | Standard alpha overlay |
| `Multiply` | Darker colors remain |
| `Screen` | Lighter colors remain |
| `Overlay` | Contrast-enhancing |
| `Dissolve` | Soft blend via args |
| `CopyOpacity` | Copy alpha from source |
| `Difference` | Color difference |

---

## Text & Annotationen

```bash
# Simple text
magick input.jpg \
  -gravity south -fill white \
  -font Arial -pointsize 36 \
  -annotate +0+10 "My Text" output.jpg

# Text with outline (shadow trick)
magick input.jpg -gravity south \
  -stroke '#000C' -strokewidth 2 -annotate 0 'Caption' \
  -stroke none -fill white -annotate 0 'Caption' \
  output.jpg

# Text with background box
magick input.jpg -fill white -undercolor '#00000080' \
  -gravity south -font Arial -pointsize 30 \
  -annotate +0+5 ' Title ' output.jpg

# Rotated text
magick input.jpg -gravity center \
  -fill blue -font Arial -pointsize 40 \
  -annotate 45x45+0+0 'Watermark' output.jpg

# Transparent text label
magick -background transparent \
  -fill white -font Arial -pointsize 40 \
  label:"Watermark" watermark.png

# Caption with auto-wrap
magick -background '#0008' -fill white \
  -gravity center -size 400x50 \
  caption:"Long text with automatic line wrapping" \
  caption.png
```

---

## Formen zeichnen

```bash
# Line
magick input.jpg -fill none -stroke red -strokewidth 3 \
  -draw "line 10,10 200,200" output.jpg

# Rectangle (outline)
magick input.jpg -fill none -stroke blue -strokewidth 2 \
  -draw "rectangle 50,50 250,150" output.jpg

# Rectangle (filled, semi-transparent)
magick input.jpg -fill 'rgba(255,0,0,0.5)' \
  -draw "rectangle 50,50 250,150" output.jpg

# Circle
magick input.jpg -fill yellow -stroke black \
  -draw "circle 100,100 100,150" output.jpg

# Ellipse
magick input.jpg -fill none -stroke green \
  -draw "ellipse 200,150 80,50 0,360" output.jpg

# Polygon (triangle)
magick input.jpg -fill orange \
  -draw "polygon 100,10 190,190 10,190" output.jpg
```

---

## Farboperationen

### Brightness, Contrast, Saturation

```bash
# Modulate: brightness,saturation,hue (100 = no change)
magick input.jpg -modulate 120,100,100 brighter.jpg    # +20% bright
magick input.jpg -modulate 80,100,100 darker.jpg       # -20% bright
magick input.jpg -modulate 100,150,100 saturated.jpg    # +50% saturation
magick input.jpg -modulate 100,50,100 desaturated.jpg   # -50% saturation

# Direct brightness-contrast (-100 to +100)
magick input.jpg -brightness-contrast 20x10 output.jpg

# Levels
magick input.jpg -level 10%,90% output.jpg     # Increase contrast
magick input.jpg -level 0%,75% output.jpg      # Brighten

# Gamma correction
magick input.jpg -gamma 1.5 output.jpg   # Brighten
magick input.jpg -gamma 0.7 output.jpg   # Darken

# Sigmoidal contrast (natural-looking)
magick input.jpg -sigmoidal-contrast 5,50% output.jpg
```

### Normalize & equalize

```bash
magick input.jpg -normalize output.jpg
magick input.jpg -contrast-stretch 1%x1% output.jpg
magick input.jpg -equalize output.jpg
magick input.jpg -negate output.jpg   # Invert colors
```

### Colorize & tint

```bash
magick input.jpg -fill 'rgba(0,0,255,0.3)' -colorize 100 blue_tint.jpg
magick input.jpg -fill white -colorize 30 lighter.jpg
magick input.jpg -sepia-tone 80% sepia.jpg
```

---

## Graustufen & Schwarz-Weiß

```bash
# Grayscale (recommended)
magick input.jpg -colorspace Gray output.jpg

# Specific weighting
magick input.jpg -grayscale Rec709Luma output.jpg

# Via saturation
magick input.jpg -modulate 100,0 output.jpg

# True black & white (threshold)
magick input.jpg -colorspace Gray -threshold 50% output.png

# Dithered black & white
magick input.jpg -colorspace Gray -ordered-dither o8x8 output.png
```

---

## Spezialeffekte

```bash
# Blur
magick input.jpg -blur 0x5 blurred.jpg

# Sharpen
magick input.jpg -sharpen 0x2 sharpened.jpg

# Unsharp mask (natural sharpening)
magick input.jpg -unsharp 0x1+0.5+0 output.jpg

# Vignette
magick input.jpg -background black -vignette 0x10+5+5 output.jpg

# Charcoal drawing
magick input.jpg -charcoal 2 output.jpg

# Oil painting
magick input.jpg -paint 4 output.jpg

# Emboss
magick input.jpg -emboss 2 output.jpg

# Edge detection
magick input.jpg -edge 2 output.jpg

# Polaroid
magick input.jpg -background grey30 +polaroid output.png
```

---

## Alpha-Kanal & Masken

```bash
# Enable alpha channel
magick input.png -alpha set output.png

# Disable alpha (remove transparency)
magick input.png -alpha off output.jpg

# Replace transparency with color
magick input.png -background white -alpha remove output.jpg

# Extract alpha as grayscale image
magick input.png -alpha extract alpha.png

# Make fully transparent / opaque
magick input.png -alpha transparent output.png
magick input.png -alpha opaque output.png

# Apply grayscale image as mask (white = visible)
magick input.png mask.png -alpha off \
  -compose CopyOpacity -composite output.png

# Make specific region transparent
magick input.png -alpha set \
  -region 100x100+50+50 -alpha transparent output.png
```

---

## Mogrify (Batch-Verarbeitung)

```bash
# Resize all JPGs (OVERWRITES originals!)
magick mogrify -resize 800x *.jpg

# Convert all PNGs to JPG (originals kept)
magick mogrify -format jpg *.png

# Output to subdirectory (recommended, protects originals)
mkdir thumbnails
magick mogrify -path thumbnails -resize 200x200 *.jpg

# Format + path + quality
magick mogrify -path web/ -format webp -quality 80 -resize 1920x *.jpg

# Strip metadata from all
magick mogrify -strip *.jpg
```

---

## Montage (Bild-Grids)

```bash
# Simple 3×4 grid
magick montage *.jpg -tile 3x4 -geometry 200x150+4+4 montage.jpg

# With filename labels
magick montage -label '%f' *.jpg \
  -tile 4x3 -geometry 150x150+5+5 \
  -font Arial -pointsize 12 grid.jpg

# With frame and background
magick montage -label '%f' *.jpg \
  -frame 5 -background '#336699' \
  -geometry 120x120+4+4 framed.jpg

# With shadow
magick montage *.jpg -shadow -geometry 200x150+10+10 -tile 4x grid.jpg

# Polaroid style
magick montage *.jpg \
  -auto-orient +polaroid \
  -tile 4x -geometry +10+10 \
  -background grey30 polaroid.jpg

# Uniform fill (crop to fit cells)
magick montage *.jpg \
  -resize 200x200^ -gravity center -extent 200x200 \
  -tile 4x4 -geometry +2+2 grid.jpg
```

---

## GIF-Animation

```bash
# Create GIF from frames
magick -delay 10 -loop 0 frame_*.png animation.gif
# -delay: time in 1/100 seconds (10 = 100ms)
# -loop 0: infinite; -loop 1: play once

# Individual delays
magick -delay 50 f1.jpg -delay 100 f2.jpg -delay 50 f3.jpg -loop 0 anim.gif

# Optimize existing GIF
magick input.gif -coalesce -layers Optimize output.gif

# Extract frames
magick input.gif +adjoin frame_%03d.png

# Extract coalesced frames (resolved)
magick input.gif -coalesce +adjoin frame_%03d.png

# Change framerate
magick input.gif -set delay 5 faster.gif

# Resize GIF (all frames)
magick input.gif -coalesce -resize 50% -layers Optimize small.gif
```

---

## Format-spezifische Tipps

### JPEG

```bash
magick input.png -quality 85 output.jpg                    # Standard quality
magick input.jpg -interlace Plane -quality 85 progressive.jpg  # Progressive
magick input.jpg -strip output.jpg                          # Remove metadata
magick input.jpg -sampling-factor 2x2 -quality 80 output.jpg  # Stronger compression
```

### PNG

```bash
magick input.png -define png:compression-level=9 output.png   # Max compression
magick input.png -strip output.png                             # Remove metadata
magick input.png -depth 8 output.png                           # 8-bit
magick input.png -colors 256 -depth 8 output.png              # Palette (smallest)
magick input.gif -background none output.png                   # Keep transparency
```

### WebP

```bash
magick input.jpg -quality 80 output.webp                          # Lossy
magick input.png -define webp:lossless=true output.webp           # Lossless
magick input.gif -quality 80 output.webp                          # Animated WebP
magick mogrify -format webp -quality 80 -path webp/ *.jpg        # Batch
```

### SVG → raster

```bash
magick -density 96 input.svg output.png                           # 96 DPI
magick -density 300 input.svg output.png                          # Print quality
magick -density 300 input.svg -resize 1024x1024 output.png       # Specific size
magick -density 96 -background none input.svg output.png          # Keep transparency
```

### PDF → image

```bash
magick -density 150 'input.pdf[0]' output.png                    # First page
magick -density 150 input.pdf page_%03d.png                      # All pages
magick -density 300 -quality 100 input.pdf output.png             # High quality
magick -density 150 input.pdf -background white -alpha remove output.jpg
```

---

## Häufige Rezepte

### Favicon

```bash
# Multi-size .ico from PNG
magick input.png \
  -define icon:auto-resize=256,128,64,48,32,16 \
  favicon.ico

# From SVG
magick -density 256 -background transparent input.svg \
  -define icon:auto-resize=256,128,64,48,32,16 \
  favicon.ico
```

### Thumbnails

```bash
# Square with white padding
magick input.jpg -thumbnail 150x150 \
  -background white -gravity center -extent 150x150 thumb.jpg

# Square cropped (no padding)
magick input.jpg -resize 150x150^ \
  -gravity center -extent 150x150 -strip thumb.jpg

# Batch into subdirectory
mkdir -p thumbs
magick mogrify -path thumbs \
  -thumbnail 200x200^ -gravity center -extent 200x200 -strip *.jpg
```

### Image comparison

```bash
# Visual diff
magick compare image1.jpg image2.jpg diff.png

# With metric
magick compare -metric PSNR image1.jpg image2.jpg diff.png

# Side-by-side
magick image1.jpg image2.jpg +append comparison.jpg

# Metrics: AE, MAE, MEPP, MSE, NCC, PAE, PSNR, RMSE, SSIM
magick compare -metric SSIM image1.jpg image2.jpg null:
```

### Image info

```bash
magick identify input.jpg                                          # Basic
magick identify -verbose input.jpg                                 # Detailed
magick identify -format "%wx%h %[colorspace] %[depth]bit\n" input.jpg
magick identify -format "%f: %wx%h (%b)\n" *.jpg                  # Batch info
magick identify -format "%[EXIF:*]" input.jpg                     # EXIF data
```

---

## Performance-Tipps

### Resource limits

```bash
magick -limit memory 512MB input.tif -resize 50% output.jpg
magick -limit disk 4GB -limit memory 2GB large.tif output.png
magick -limit thread 4 input.jpg -resize 50% output.jpg
magick -list resource   # Show current limits
```

### Parallel processing

```bash
# GNU Parallel
parallel magick {} -resize 800x -quality 85 thumbs/{/} ::: *.jpg

# xargs
ls *.jpg | xargs -P 4 -I{} magick {} -resize 800x thumbs/{}

# Background jobs
for f in *.jpg; do
  magick "$f" -resize 800x -quality 85 "out_${f}" &
done
wait
```

### Memory-efficient techniques

```bash
# Scale while reading (saves memory)
magick 'input.jpg[800x]' output.jpg

# Ping (metadata only, no image loading)
magick identify -ping input.jpg
```

---

## Flags-Schnellreferenz

| Flag | Description | Example |
|------|-------------|---------|
| `-resize` | Scale | `-resize 800x600` |
| `-crop` | Crop | `-crop 400x300+10+10` |
| `-rotate` | Rotate | `-rotate 90` |
| `-flip` / `-flop` | Mirror | `-flip` |
| `-quality` | JPEG/WebP quality | `-quality 85` |
| `-strip` | Remove metadata | `-strip` |
| `-gravity` | Alignment | `-gravity center` |
| `-composite` | Overlay | `-composite` |
| `-annotate` | Text | `-annotate 0 'Text'` |
| `-font` | Font | `-font Arial` |
| `-pointsize` | Font size | `-pointsize 36` |
| `-fill` | Fill color | `-fill white` |
| `-background` | Background color | `-background black` |
| `-transparent` | Make color transparent | `-transparent white` |
| `-fuzz` | Color tolerance | `-fuzz 10%` |
| `-modulate` | Brightness/Sat/Hue | `-modulate 120,80,100` |
| `-colorspace` | Color space | `-colorspace Gray` |
| `-density` | DPI (SVG/PDF) | `-density 300` |
| `-delay` | GIF frame delay | `-delay 10` |
| `-loop` | GIF loops | `-loop 0` |
| `-limit` | Resource limit | `-limit memory 1GB` |
| `-tile` | Montage grid | `-tile 4x3` |
| `-geometry` | Size+position | `-geometry 200x200+5+5` |
