# Photo → scan

Turn a phone photo of a paper document into a flatbed-style scan: rectified, cropped, even
paper tone, white surround, original ink colour. OpenCV **measures**, ImageMagick **edits**.

## Rules

- **Never Gemini on a document.** AI sharpening or cleanup invents digits, stamps and signatures.
- **Sharp input decides.** Blur and motion ghosting survive every filter. Ask for a retake with
  even light, no direct sun and no glare before tuning parameters.
- **Convert first:** `magick in.heic -auto-orient -quality 94 in.jpg`. Keep the original.
- **Keep a slip separate from what it hides.** A slip on top of a form hides text: use two photos,
  two PDF pages, one with the slip folded away and one with it on top.

## 1. Paper mask (work at 25 % scale, smooth with a 5 px Gaussian)

Brightness alone fails: wood and screen glare pass it, shadowed paper does not.

| Step | OpenCV | Purpose |
|---|---|---|
| Seed | HSV `V >= 100`, `S < 48`, Lab `b >= 129` | bright, colourless, warm; wood is saturated, glare is cool |
| Clean | close 21, open 11, largest component | closes text, drops specks |
| GrabCut labels | `dilate(seed, 41)` → PR_BGD · seed → PR_FGD · `erode(seed, 31)` → FGD · the rest BGD | fits the edge to the real paper |
| Hard background | `S >= 60`, `b >= 136`, `V > 70` → BGD, before FGD is written | wood must not leak in; a stain inside the paper stays |
| Finish | `grabCut` 5 iterations, open 5, largest contour, filled | holes from stamps and text disappear |

Keep the kernels at these sizes for a 3–5 k source; a closing kernel near 25 bridges gaps between
sheets and pulls in the background. If a patch survives above a known paper edge, paint it white in
the final image rather than re-tuning for one photo.

## 2. Rectify on the printed frame, not the paper edge

Paper edges are torn and curved; printed lines are straight.

- `adaptiveThreshold` (mean, inverted, block 51, C 18), masked with the eroded paper mask (61 px).
- `HoughLinesP(bw, 1, pi/720, 200, minLineLength=0.22*w, maxLineGap=30)`.
- Horizontal: `|dy| < 0.12*|dx|`, length `> 0.45*w`. Top and bottom = `fitLine` through **all**
  segments within 35 px of the outermost line; one short segment tilts the page.
- Vertical: `|dx| < 0.12*|dy|`, length `> 0.2*h`, in the outer 20 %. Otherwise fit the paper contour
  over the middle 40 % of its height.
- Output size = mean of opposite side lengths. Viewport = warped contour bounding box + 45 px, so
  paper outside the frame survives.

**Frame covered by a slip?** The extreme lines are wrong and the page skews. Photograph the form
free as well and transfer its frame: SIFT (12000 features, 50 % scale), ratio test 0.72,
`findHomography(RANSAC, 6.0)`, apply to the free photo's quad. Several hundred inliers is healthy.

## 3. ImageMagick pipeline

```bash
# Rectify image and mask with the same call; W, H = viewport, OX, OY = signed offset
VP=(-virtual-pixel black -define "distort:viewport=${W}x${H}${OX}${OY}"
    -distort Perspective "$PAIRS" +repage)     # PAIRS="x1,y1 X1,Y1  x2,y2 X2,Y2 ..."
magick in.jpg "${VP[@]}" warped.png
magick mask.png "${VP[@]}" -morphology Erode Disk:9 -blur 0x1.5 m.png

# Paper tone under the surround, so the dark table cannot distort the shading estimate
magick \( -size ${W}x${H} xc:'#d4d3cc' \) warped.png m.png -composite paper.png

# Remove shading: Close deletes the text, blur leaves only the light, Divide flattens
magick paper.png \( +clone -resize 25% -morphology Close Disk:12 -blur 0x18 -resize ${W}x${H}! \) \
  -compose Divide_Src -composite flat.png

# Ink and paper, then a slight tint so the sheet stays visible against pure white
magick flat.png -level 20%,93%,0.88 -modulate 100,135 -unsharp 0x2.2+1.0+0.02 \
  \( +clone -fill '#f4f3ee' -colorize 100 \) -compose Multiply -composite graded.png

# White scanner lid outside the paper, tight crop, no metadata
magick \( -size ${W}x${H} xc:white \) graded.png m.png -composite -strip \
  -fuzz 1.5% -trim +repage -bordercolor white -border 45 -quality 90 scan.jpg
```

| Symptom | Fix |
|---|---|
| Paper edge and slip outline vanish | white point too low: `-level` closer to `20%,93%`, not `22%,90%` |
| Mottled, dirty edges | white point too high: below `98%`, tint stays |
| Black crumbs at the edge | erode the mask further (`Disk:9`) |
| Stamp or signature looks pale | raise `-modulate` saturation, never redraw |

## 4. PDF and OCR

- `img2pdf --imgsize 370dpi a.jpg b.jpg -o out.pdf` embeds the JPEGs without re-encoding. Pick the
  dpi from the real paper width.
- Add the text layer with the `ocr` plugin (`/ocr-searchable`) and name the document language.
- **Verify IDs against the image.** List IBAN, IDs, amounts and times, read them in a 100 % crop,
  check each against the text layer. Sharpening can flip single digits (`5` → `6`). Correct only
  the invisible text; the image stays as photographed.

## 5. Check before delivery

- Contact sheet at `x1000` plus a 100 % crop of the smallest text. Write it to another folder: a
  `*_scan.jpg` glob picks up its own earlier `ctl_scan.jpg`.
- Process sheet for the user: original and each pipeline step side by side. `-font` needs a file
  path such as `/System/Library/Fonts/Supplemental/Arial.ttf` on macOS.
- Word splitting differs in zsh: run the array and `set --` parts under `bash`.
