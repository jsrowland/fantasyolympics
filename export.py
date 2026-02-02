import csv

# Updated 116 Event List with Custom Discipline Mapping
OLYMPIC_EVENTS = [
    # --- ALPINE SKIING (10 events) ---
    {"event": "Men's Downhill", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": True},
    {"event": "Men's Slalom", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Giant Slalom", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Super-G", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Alpine Combined", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Downhill", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": True},
    {"event": "Women's Slalom", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Giant Slalom", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Super-G", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Alpine Combined", "sport": "Alpine Skiing", "discipline": "Alpine Skiing", "is_team": False, "is_prestige": False},

    # --- ENDURANCE SNOW (26 events: Biathlon, XC, SkiMo) ---
    {"event": "Men's 10km Sprint Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Men's 12.5km Pursuit Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Men's 20km Individual Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Men's 15km Mass Start Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Men's 4x7.5km Relay Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},
    {"event": "Women's 7.5km Sprint Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's 10km Pursuit Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's 15km Individual Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's 12.5km Mass Start Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's 4x6km Relay Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},
    {"event": "Mixed Relay Biathlon", "sport": "Biathlon", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},
    {"event": "Men's 15km + 15km Skiathlon", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Men's 15km Free", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Men's 50km Mass Start", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": True},
    {"event": "Men's 4x10km Relay", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},
    {"event": "Men's Sprint Free", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Men's Team Sprint", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},
    {"event": "Women's 7.5km + 7.5km Skiathlon", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's 10km Free", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's 30km Mass Start", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": True},
    {"event": "Women's 4x5km Relay", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},
    {"event": "Women's Sprint Free", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's Team Sprint", "sport": "Cross-Country Skiing", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},
    {"event": "Men's Sprint SkiMo", "sport": "Ski Mountaineering", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Women's Sprint SkiMo", "sport": "Ski Mountaineering", "discipline": "Endurance Snow", "is_team": False, "is_prestige": False},
    {"event": "Mixed Relay SkiMo", "sport": "Ski Mountaineering", "discipline": "Endurance Snow", "is_team": True, "is_prestige": False},

    # --- SLIDING (12 events: Bobsleigh, Luge, Skeleton) ---
    {"event": "Two-man Bobsleigh", "sport": "Bobsleigh", "discipline": "Sliding", "is_team": True, "is_prestige": False},
    {"event": "Four-man Bobsleigh", "sport": "Bobsleigh", "discipline": "Sliding", "is_team": True, "is_prestige": True},
    {"event": "Women's Monobob", "sport": "Bobsleigh", "discipline": "Sliding", "is_team": False, "is_prestige": False},
    {"event": "Two-woman Bobsleigh", "sport": "Bobsleigh", "discipline": "Sliding", "is_team": True, "is_prestige": False},
    {"event": "Men's Singles Luge", "sport": "Luge", "discipline": "Sliding", "is_team": False, "is_prestige": False},
    {"event": "Men's Doubles Luge", "sport": "Luge", "discipline": "Sliding", "is_team": True, "is_prestige": False},
    {"event": "Women's Singles Luge", "sport": "Luge", "discipline": "Sliding", "is_team": False, "is_prestige": False},
    {"event": "Women's Doubles Luge", "sport": "Luge", "discipline": "Sliding", "is_team": True, "is_prestige": False},
    {"event": "Team Relay Luge", "sport": "Luge", "discipline": "Sliding", "is_team": True, "is_prestige": False},
    {"event": "Men's Skeleton", "sport": "Skeleton", "discipline": "Sliding", "is_team": False, "is_prestige": False},
    {"event": "Women's Skeleton", "sport": "Skeleton", "discipline": "Sliding", "is_team": False, "is_prestige": False},
    {"event": "Mixed Team Skeleton", "sport": "Skeleton", "discipline": "Sliding", "is_team": True, "is_prestige": False},

    # --- SPEED SKATING (14 events) ---
    {"event": "Men's 500m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Men's 1000m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Men's 1500m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Men's 5000m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Men's 10,000m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Men's Mass Start Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Men's Team Pursuit Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": True, "is_prestige": False},
    {"event": "Women's 500m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Women's 1000m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Women's 1500m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Women's 3000m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Women's 5000m Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Women's Mass Start Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": False, "is_prestige": False},
    {"event": "Women's Team Pursuit Speed Skating", "sport": "Speed Skating", "discipline": "Speed Skating", "is_team": True, "is_prestige": False},

    # --- FIGURE SKATING (5 events) ---
    {"event": "Men's Singles Figure Skating", "sport": "Figure Skating", "discipline": "Figure Skating", "is_team": False, "is_prestige": True},
    {"event": "Women's Singles Figure Skating", "sport": "Figure Skating", "discipline": "Figure Skating", "is_team": False, "is_prestige": True},
    {"event": "Pairs Figure Skating", "sport": "Figure Skating", "discipline": "Figure Skating", "is_team": True, "is_prestige": False},
    {"event": "Ice Dance", "sport": "Figure Skating", "discipline": "Figure Skating", "is_team": True, "is_prestige": False},
    {"event": "Team Event Figure Skating", "sport": "Figure Skating", "discipline": "Figure Skating", "is_team": True, "is_prestige": False},

    # --- SHORT TRACK (9 events) ---
    {"event": "Men's 500m Short Track", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": False, "is_prestige": False},
    {"event": "Men's 1000m Short Track", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": False, "is_prestige": False},
    {"event": "Men's 1500m Short Track", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": False, "is_prestige": False},
    {"event": "Men's 5000m Relay", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": True, "is_prestige": False},
    {"event": "Women's 500m Short Track", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": False, "is_prestige": False},
    {"event": "Women's 1000m Short Track", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": False, "is_prestige": False},
    {"event": "Women's 1500m Short Track", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": False, "is_prestige": False},
    {"event": "Women's 3000m Relay", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": True, "is_prestige": False},
    {"event": "Mixed Team Relay Short Track", "sport": "Short Track Speed Skating", "discipline": "Short Track", "is_team": True, "is_prestige": False},

    # --- AIR & ASCENT (9 events: Ski Jumping, Nordic Combined) ---
    {"event": "Men's Normal Hill Ski Jumping", "sport": "Ski Jumping", "discipline": "Air & Ascent", "is_team": False, "is_prestige": False},
    {"event": "Men's Large Hill Ski Jumping", "sport": "Ski Jumping", "discipline": "Air & Ascent", "is_team": False, "is_prestige": False},
    {"event": "Men's Super Team Ski Jumping", "sport": "Ski Jumping", "discipline": "Air & Ascent", "is_team": True, "is_prestige": False},
    {"event": "Women's Normal Hill Ski Jumping", "sport": "Ski Jumping", "discipline": "Air & Ascent", "is_team": False, "is_prestige": False},
    {"event": "Women's Large Hill Ski Jumping", "sport": "Ski Jumping", "discipline": "Air & Ascent", "is_team": False, "is_prestige": False},
    {"event": "Women's Super Team Ski Jumping", "sport": "Ski Jumping", "discipline": "Air & Ascent", "is_team": True, "is_prestige": False},
    {"event": "Men's Individual Normal Hill Nordic Combined", "sport": "Nordic Combined", "discipline": "Air & Ascent", "is_team": False, "is_prestige": False},
    {"event": "Men's Individual Large Hill Nordic Combined", "sport": "Nordic Combined", "discipline": "Air & Ascent", "is_team": False, "is_prestige": False},
    {"event": "Men's Team Sprint Large Hill Nordic Combined", "sport": "Nordic Combined", "discipline": "Air & Ascent", "is_team": True, "is_prestige": False},

    # --- FREESTYLE SKIING (15 events) ---
    {"event": "Men's Aerials", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Moguls", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Dual Moguls", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Ski Cross", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Slopestyle Freestyle", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Halfpipe Freestyle", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Men's Big Air Freestyle", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Aerials", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Moguls", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Dual Moguls", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Ski Cross", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Slopestyle Freestyle", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Halfpipe Freestyle", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Women's Big Air Freestyle", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": False, "is_prestige": False},
    {"event": "Mixed Team Aerials", "sport": "Freestyle Skiing", "discipline": "Freestyle Skiing", "is_team": True, "is_prestige": False},

    # --- SNOWBOARDING (11 events) ---
    {"event": "Men's Parallel Giant Slalom", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Men's Snowboard Cross", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Men's Slopestyle Snowboard", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Men's Halfpipe Snowboard", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Men's Big Air Snowboard", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Women's Parallel Giant Slalom", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Women's Snowboard Cross", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Women's Slopestyle Snowboard", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Women's Halfpipe Snowboard", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Women's Big Air Snowboard", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": False, "is_prestige": False},
    {"event": "Mixed Team Snowboard Cross", "sport": "Snowboarding", "discipline": "Snowboarding", "is_team": True, "is_prestige": False},

    # --- ICE HOCKEY (2 events) ---
    {"event": "Men's Ice Hockey", "sport": "Ice Hockey", "discipline": "Ice Hockey", "is_team": True, "is_prestige": True},
    {"event": "Women's Ice Hockey", "sport": "Ice Hockey", "discipline": "Ice Hockey", "is_team": True, "is_prestige": True},

    # --- CURLING (3 events) ---
    {"event": "Men's Curling", "sport": "Curling", "discipline": "Curling", "is_team": True, "is_prestige": False},
    {"event": "Women's Curling", "sport": "Curling", "discipline": "Curling", "is_team": True, "is_prestige": False},
    {"event": "Mixed Doubles Curling", "sport": "Curling", "discipline": "Curling", "is_team": True, "is_prestige": False},
]

def export_to_olympic_csv(event_data, filename="milano_2026_events.csv"):
    # 1. First, tally events per discipline for the Base Score math
    discipline_counts = {}
    for event in event_data:
        disc = event["discipline"]
        discipline_counts[disc] = discipline_counts.get(disc, 0) + 1

    # 2. Extract headers from the first dictionary
    # We add "base_score" as a new column for the export
    headers = list(event_data[0].keys()) + ["base_score"]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for event in event_data:
            # Create a copy to avoid modifying the original list
            row = event.copy()
            
            # Apply your logic: MIN(120 / N, 15)
            n_events = discipline_counts[row["discipline"]]
            raw_score = 120 / n_events
            row["base_score"] = round(min(raw_score, 15), 2)
            
            writer.writerow(row)

    print(f"Successfully exported {len(event_data)} events to {filename}")

# Run the export
export_to_olympic_csv(OLYMPIC_EVENTS)