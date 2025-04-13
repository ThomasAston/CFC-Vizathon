import matplotlib.colors as mcolors


colors = [mcolors.to_hex(c) for c in ['tab:blue', 'tab:orange', 'tab:green']]
zone_colors = ["rgba(173, 216, 230, 0.6)",  # LightBlue (Zone 1)
                "rgba(135, 206, 250, 0.6)",  # SkyBlue
                "rgba(100, 149, 237, 0.6)",  # CornflowerBlue
                "rgba(65, 105, 225, 0.6)",   # RoyalBlue
                "rgba(0, 0, 139, 0.6)"      # DarkBlue (Zone 5)
                ]

# Metrics to apply gradients to
metrics = [
    "distance", "distance_per_min",
    "distance_over_21", "distance_over_24", "distance_over_27",
    "accel_decel_over_2_5", "accel_decel_over_3_5", "accel_decel_over_4_5",
    "day_duration", "peak_speed",
    "hr_zone_1_sec", "hr_zone_2_sec", "hr_zone_3_sec", "hr_zone_4_sec", "hr_zone_5_sec"
]

# Time string metrics to be converted
time_metrics = {
    "hr_zone_1_sec", "hr_zone_2_sec", "hr_zone_3_sec", "hr_zone_4_sec", "hr_zone_5_sec"
}

# HR zone totals (for the entire dataset)
zone_cols = [
    "hr_zone_1_sec", "hr_zone_2_sec", "hr_zone_3_sec", "hr_zone_4_sec", "hr_zone_5_sec"
]

body_markers = [[0.5, 0.46, 0.54], [0.93, 0.53, 0.53]]