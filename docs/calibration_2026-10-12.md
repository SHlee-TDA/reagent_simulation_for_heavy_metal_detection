# Video calibration from jiyun Drive folder (read 2026-10-12, in-browser; no videos downloaded)
Source: EdgeMasterVideoPixelProcessing_2026_03_05.ipynb + Full_Data/*/<exp>/Data/*.csv (raw flow profiles) + video thumbnails (frame image only)

## Processing code facts
- ROI: vertical lane, rows 645..974 (329 px), columns location=333 (+142 px per channel; single-file cell uses 313), 3-px wide line
- front = count of lane pixels whose gray value dropped >= 5 vs frame 1 (threshold=5)
- video FPS 29.99 (nb output), ~1790-1801 frames = 60 s
- Trim_Data: start at last frame with count <= 50 px; keep 780 frames (Pos.csv)
- Step_Calc: 15-frame windows, edges 15..300, fit vs sqrt(frame index after trim) -> Slope (px/sqrt(frame)); IC = mean of 0/0 combos per 4-channel group

## Geometry (thumbnails, 1080x1920 portrait; 18 videos measurable)
- fingers point down; tip y ~945-1003, bar bottom y ~626-672; finger length 304-334 px (median ~318) for 24 mm
- finger width 73-83 px for 6 mm; pitch ~147 px
- => 13.3 px/mm (+-5% between sessions); ROI 645..974 ~= finger (24 mm ~ 320 px)

## Raw flow profiles: 42 experiments, 1039 videos, 4156 legs
onset (first frame >=20 px): median 71 (p5-p95 48-86)
h after onset [px] (p5/p25/p50/p75/p95):
  +15 fr: 9/35/45/52/60 ; +30: 32/46/54/61/70 ; +150: 68/82/90/97/108
  +300: 93/108/115/123/136 ; +900: 151/168/176/185/201 ; +1500: 191/207/217/228/245
  end (~1730 fr after onset): 203/220/230/242/259 ; max 203..260 ; no leg >= 315 px
LW fit h = a + b sqrt(t - onset), t >= onset+30:
  b = 4.28/4.59/4.83/5.06/5.42 px/sqrt(frame)  (= 1.99 mm/sqrt(s) median; D ~ 4.0 mm^2/s)
  a = 8.7/23/32/39/49 px ; residual SD 0.8/1.1/1.5/2.0/3.2 px
  frames after onset to reach 321 px (extrapolated): 2800/3265/3633/3999/4648  (~93/109/121/133/155 s)
Noise in log b (full-curve LW fit):
  leg (within video, same condition) SD 0.041
  video means, same condition & day: SD 0.042 (incl. leg/2)
  day (0/0 controls across 41 experiments): SD 0.058
