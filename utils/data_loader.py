import json
import pandas as pd
import numpy as np


def load_player_data(json_path):
    with open(json_path) as f:
        data = json.load(f)

    player_lookup = {}
    for group in ["chelsea_squads", "opposition"]:
        for squad in data[group]:
            squads = data[group][squad] if group == "chelsea_squads" else [
                p for comp in data[group][squad].values() for team in comp.values() for p in team
            ]
            for p in squads:
                player_lookup[str(p["id"])] = p
    return player_lookup


def load_gps_data(csv_path):
    df = pd.read_csv(csv_path, encoding="latin-1")
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

    # Create match/training day flags
    df["is_training_day"] = (df["day_duration"] > 0) & (df["md_plus_code"] != 0)
    df["is_match_day"] = (df["day_duration"] > 0) & (df["md_plus_code"] == 0)

    # Distance per minute
    df["distance_per_min"] = df["distance"] / df["day_duration"].where(df["day_duration"] > 0)

    # Heart rate time in seconds
    def hms_to_seconds(hms):
        try:
            h, m, s = map(int, hms.split(":"))
            return h * 3600 + m * 60 + s
        except:
            return 0

    for i in range(1, 6):
        col = f"hr_zone_{i}_hms"
        df[f"hr_zone_{i}_sec"] = df[col].fillna("00:00:00").apply(hms_to_seconds)

    return df


def compute_gradient_df(df, metrics, max_segments=30):
    max_values = {metric: df[metric].max() for metric in metrics}
    gradient_data = []

    for _, row in df.iterrows():
        date = row["date"]
        for metric in metrics:
            total = row[metric]
            max_val = max_values[metric]
            if pd.isna(total) or not np.isfinite(total) or not np.isfinite(max_val) or max_val == 0:
                continue

            target_segment_height = max_val / max_segments
            full_segments = int(total // target_segment_height)
            remainder = total % target_segment_height

            for i in range(full_segments):
                y0 = i * target_segment_height
                y1 = y0 + target_segment_height
                color_val = y1 / max_val
                gradient_data.append({
                    "date": date,
                    "metric": metric,
                    "base": y0,
                    "height": target_segment_height,
                    "color_val": color_val,
                    "total": total
                })

            if remainder > 0:
                y0 = full_segments * target_segment_height
                y1 = y0 + remainder
                color_val = y1 / max_val
                gradient_data.append({
                    "date": date,
                    "metric": metric,
                    "base": y0,
                    "height": remainder,
                    "color_val": color_val,
                    "total": total
                })

    return pd.DataFrame(gradient_data)

# ACWR calculation
def compute_acwr(df, metric):
    df = df.sort_values("date")
    acwr = []
    for i in range(len(df)):
        acute = df.iloc[max(0, i - 6):i + 1][metric].mean()
        chronic = df.iloc[max(0, i - 27):i + 1][metric].mean()
        acwr.append(acute / chronic if chronic else 0)
    df = df.copy()
    df["acwr"] = acwr
    return df