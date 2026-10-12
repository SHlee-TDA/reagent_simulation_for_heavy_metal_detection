# References and provided material

Material provided by the project lead (S. Lee) and the chemistry lead (jiyou, W. Areekul).
Internal, unpublished data: keep this repository private.

| Path | What it is | Source |
| --- | --- | --- |
| `slides/2026-09-02_labprogress_SALSA_jiyou.pptx` | jiyou's lab-progress slides: chip, reagents (chitosan, poly-L-lysine, alginate, tannin, gallic acid), metal levels, surface-water limits | jiyou, 2026-09-02 |
| `slides/2026-09-14_flowprofile_report.pptx` | Flow-profile / AIC classification report (audit of the legacy pipeline) | 2026-09-14 report |
| `chip/chip_dimensions.png` | Chip geometry: 4 fingers 24 x 6 mm, collection pad 10 x 44 mm | jiyou |
| `lab_pipeline/EdgeMasterVideoPixelProcessing_2026_03_05.ipynb` | Lab video-processing notebook (outputs stripped): ROI, front detection, trimming, windowed slopes, IC subtraction | lab Google Drive, folder `jiyun` |
| `lab_pipeline/legacy_aic_analysis.py` | Legacy analysis/classification script used with `data/raw/legacy/20260828_AIC_combined.csv` | provided 2026-10-08 |
| `../data/raw/legacy/20260828_AIC_combined.csv` | Legacy windowed-slope table (Slope, WindowEdge, IC, Adjusted_Slope) | lab pipeline output |
| `../data/derived/video_lw_coefficients.csv` | Our re-analysis: full-curve LW coefficient b for every leg of 1,039 videos (42 experiments, 2026-03 to 2026-08) | computed 2026-10-12 from the raw flow profiles in Drive |
| `../data/derived/per_experiment_summary.csv` | Per-experiment medians: onset, b, front at 10 s and 60 s, extrapolated frames to 24 mm | same |
| `../data/derived/effect_scale_2026-10-12.json` | Effect-scale posterior (Bayes factor ~1:170 for the v2 prior vs no effect) | `pfid.calibration` |

Raw videos (about 123 MB each) stay in the lab Drive and are never committed.

## Not included (copyright)

- Tang, Y., Choi, S.-J., Thomas, C., Miller, A. M., Dresbach-Hill, G. R., Khanthaphixay, B., Reynolds, K. A., & Yoon, J.-Y. (2026).
  Dip and taste PFAS to detect and classify from environmental water samples. *Journal of Hazardous Materials*, 503, 141051.
  https://doi.org/10.1016/j.jhazmat.2026.141051 (the SALSA platform)

## Key literature

- Washburn, E. W. (1921). The dynamics of capillary flow. *Physical Review* 17, 273-283.
- Pearson, R. G. (1963). Hard and soft acids and bases. *JACS* 85, 3533.
- Chaloner, K. & Verdinelli, I. (1995). Bayesian experimental design: a review. *Statistical Science* 10, 273-304.
- Vlasov, Yu. et al. (2005). Nonspecific sensor arrays ("electronic tongue"). *Pure Appl. Chem.* 77, 1965-1983.
- Drinking-water standards: Korea (mokpo.go.kr comparison table), WHO GDWQ 4th ed. tables.
