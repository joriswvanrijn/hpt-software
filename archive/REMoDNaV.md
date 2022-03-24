# Stappenplan

1. data transformeren naar gelijke tijdseenheid op de X-as (interpolatie)
   -> zouden stuk code kunnen gebruiken in
   `./hpt-software/4_gaze_roi_analysis/TODO_detect_saccades.backup.py` (interpolate_gaze)
2. conf <.8 NaN en off_screen == True naar NaN
3. Alle gaps < 60 ms, interpoleren
4. TSV bestand maken met: X Y
5. REMoDNaV

- https://github.com/psychoinformatics-de/remodnav
- https://link.springer.com/article/10.3758/s13428-020-01428-x
- https://github.com/psychoinformatics-de/paper-remodnav/
