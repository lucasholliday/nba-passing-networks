from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
from nba_api.stats.static import players
import pandas as pd
import time
import random

# === CONFIG ===
SEASON_ID = '2023-24'
CURRENT_YEAR = 2024

# === Load Player List ===
combined_df = pd.read_csv("combined_players_listEC.csv")  # must have column "Player"
name_list = combined_df['Player'].tolist()

# === Build player lookup ===
all_players = players.get_players()
name_to_id = {p['full_name']: p['id'] for p in all_players}

# === Normalize name format: "Last, First" → "First Last"
def normalize_name(name):
    parts = name.split(', ')
    return f"{parts[1]} {parts[0]}" if len(parts) == 2 else name

# === Safe API request wrapper with retries ===
def safe_api_call(api_func, *args, retries=3, sleep_min=0.6, sleep_max=1.5):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(sleep_min, sleep_max))
            return api_func(*args)
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    raise Exception("❌ All retries failed.")

# === Collect Data ===
rows = []

for raw_name in name_list:
    name = normalize_name(raw_name)
    if name not in name_to_id:
        print(f"❌ Skipping (not found): {name}")
        continue

    player_id = name_to_id[name]
    print(f"⏳ Processing: {name}")

    try:
        # --- Basic Info ---
        info_df = safe_api_call(lambda pid: commonplayerinfo.CommonPlayerInfo(player_id=pid).get_data_frames()[0], player_id)
        
        # BIRTHDATE
        birth_raw = info_df['BIRTHDATE'].values[0]
        birth_year = int(str(birth_raw).split('-')[0]) if pd.notna(birth_raw) else CURRENT_YEAR
        age = CURRENT_YEAR - birth_year

        # POSITION
        position = info_df['POSITION'].values[0] if pd.notna(info_df['POSITION'].values[0]) else ""
        guard = int(any(pos in position for pos in ['G', 'PG', 'SG']))

        # PRIME AGE
        prime_age = int(25 <= age <= 30)

        # DRAFT PICK
        draft_raw = str(info_df['DRAFT_NUMBER'].values[0])
        if draft_raw.strip().lower() == 'undrafted' or draft_raw == 'nan':
            draft_pick = 61
        else:
            try:
                draft_pick = int(draft_raw)
            except:
                draft_pick = 61

        # FIRST ROUND
        round_raw = str(info_df['DRAFT_ROUND'].values[0])
        first_round = 1 if round_raw.strip() == '1' else 0

        # --- Career Stats ---
        career_df = safe_api_call(lambda pid: playercareerstats.PlayerCareerStats(player_id=pid).get_data_frames()[0], player_id)
        season_stats = career_df[career_df['SEASON_ID'] == SEASON_ID]

        if not season_stats.empty:
            pts = float(season_stats['PTS'].values[0])
            gp = float(season_stats['GP'].values[0])
            ppg = round(pts / gp, 1) if gp > 0 else 0.0
            success = int(ppg >= 20)

            # Tenure calc
            current_team_id = season_stats['TEAM_ID'].values[0]
            team_seasons = career_df[career_df['TEAM_ID'] == current_team_id]
            if not team_seasons.empty:
                first_team_year = int(team_seasons['SEASON_ID'].values[0][:4])
                tenure_years = CURRENT_YEAR - first_team_year
            else:
                tenure_years = 0
        else:
            ppg = 0.0
            success = 0
            tenure_years = None

        # --- Save Row ---
        rows.append({
            'Player': name,
            'PPG': ppg,
            'success': success,
            'age': age,
            'tenure_years': tenure_years,
            'guard': guard,
            'prime_age': prime_age,
            'first_round': first_round,
            'draft_pick': draft_pick
        })

    except Exception as e:
        print(f"❌ Error for {name}: {e}")
        continue

# === Save Output ===
output_df = pd.DataFrame(rows)
output_df.to_csv("ALAAM_attributesEC_2023-24.csv", index=False)
print("\n✅ Saved attribute data to ALAAM_attributesEC_2023-24.csv")
