from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
from nba_api.stats.static import players
import pandas as pd
import time

# === CONFIG ===
SEASON_ID = '2023-24'
CURRENT_YEAR = 2024

# === Load Player List ===
combined_df = pd.read_csv("combined_players_list.csv")  # must have column "Player"
name_list = combined_df['Player'].tolist()

# === Build player lookup ===
all_players = players.get_players()
name_to_id = {p['full_name']: p['id'] for p in all_players}

# === Normalize name format: "Last, First" → "First Last"
def normalize_name(name):
    parts = name.split(', ')
    return f"{parts[1]} {parts[0]}" if len(parts) == 2 else name

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
        time.sleep(0.6)

        # Basic info
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
        birth_year = int(info['BIRTHDATE'].values[0].split('-')[0])
        age = CURRENT_YEAR - birth_year
        position = info['POSITION'].values[0]
        guard = int(any(pos in position for pos in ['G', 'PG', 'SG']))
        prime_age = int(25 <= age <= 30)

        # Draft pick continous
        print(info['DRAFT_NUMBER'].values[0])
        # Get draft pick number: use 61 if undrafted
        draft_raw = info['DRAFT_NUMBER'].values[0]

        if isinstance(draft_raw, str) and draft_raw.strip().lower() == 'Undrafted':
            draft_pick = 61
        else:
            try:
                draft_pick = int(draft_raw)
            except:
                draft_pick = 61  # fallback just in case of other bad formats

        # Draft round binary
        round_raw = info['DRAFT_ROUND'].values[0]
        if pd.notna(round_raw) and str(round_raw).strip() == '1':
            first_round = 1
        else:
            first_round = 0

        # Career stats and current season stats
        career_df = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
        season_stats = career_df[career_df['SEASON_ID'] == SEASON_ID]

        if not season_stats.empty:
            pts = float(season_stats['PTS'].values[0])
            gp = float(season_stats['GP'].values[0])
            ppg = round(pts / gp, 1) if gp > 0 else 0.0
            success = int(ppg >= 20)

            # Get current team tenure
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

        # Append row
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

# === Save Output ===
output_df = pd.DataFrame(rows)
output_df.to_csv("ALAAM_attributes_2023-24.csv", index=False)
print("\n✅ Saved attribute data to ALAAM_attributes_2023-24.csv")





# from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
# from nba_api.stats.static import players
# import pandas as pd
# import datetime
# import time

# # === CONFIG ===
# SEASON_ID = '2023-24'
# CURRENT_YEAR = 2024

# # === Load Player List ===
# combined_df = pd.read_csv("combined_players_list.csv")  # must have column "Player"
# name_list = combined_df['Player'].tolist()

# # === Build player lookup ===
# all_players = players.get_players()
# name_to_id = {p['full_name']: p['id'] for p in all_players}

# # === Standardize name matching (Last, First to First Last) ===
# def normalize_name(name):
#     parts = name.split(', ')
#     return f"{parts[1]} {parts[0]}" if len(parts) == 2 else name

# # === Collect Data ===
# rows = []

# for raw_name in name_list:
#     name = normalize_name(raw_name)
#     if name not in name_to_id:
#         print(f"❌ Skipping (not found): {name}")
#         continue

#     player_id = name_to_id[name]
#     print(f"⏳ Processing: {name}")

#     try:
#         time.sleep(0.6)  # avoid rate limits

#         # Basic info
#         info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
#         birth_year = int(info['BIRTHDATE'].values[0].split('-')[0])
#         from_year = int(info['FROM_YEAR'].values[0])
#         position = info['POSITION'].values[0]

#         age = CURRENT_YEAR - birth_year

#         tenure = CURRENT_YEAR - from_year

        
#         guard = int(any(pos in position for pos in ['G', 'PG', 'SG']))
#         prime_age = int(25 <= age <= 30)

#         # Career stats for 2023-24
#         stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
#         season_stats = stats[stats['SEASON_ID'] == SEASON_ID]

#         if not season_stats.empty:
#             pts = float(season_stats['PTS'].values[0])
#             gp = float(season_stats['GP'].values[0])
#             ppg = round(pts / gp, 1) if gp > 0 else 0.0
#         else:
#             ppg = 0.0

#         success = int(ppg >= 20)

#         # Draft pick (rookie season only)
#         if 'DRAFT_NUMBER' in stats.columns and not pd.isna(stats['DRAFT_NUMBER'].values[0]):
#             draft_pick = int(stats['DRAFT_NUMBER'].values[0])
#         else:
#             draft_pick = None

#         round_raw = info['DRAFT_ROUND'].values[0]
#         if pd.notna(round_raw) and str(round_raw).strip() == '1':
#             first_round = 1
#         else:
#             first_round = 0

#         rows.append({
#             'Player': name,
#             'PPG': ppg,
#             'success': success,
#             'age': age,
#             'tenure_years': tenure,
#             'guard': guard,
#             'prime_age': prime_age,
#             'first_round': first_round
#         })

#     except Exception as e:
#         print(f"❌ Error for {name}: {e}")

# # === Output ===
# output_df = pd.DataFrame(rows)
# output_df.to_csv("ALAAM_attributes_2023-24.csv", index=False)
# print("\n✅ Saved attribute data to ALAAM_attributes_2023-24.csv")



# from nba_api.stats.endpoints import commonteamroster, playercareerstats
# from nba_api.stats.static import teams
# import pandas as pd
# import time

# # === CONFIG ===
# SEASON = '2023-24'  # Must be in 'YYYY-YY' format
# input_team = input("Input team name (e.g., Golden State Warriors): ")

# # === Get Team ID ===
# nba_teams = teams.get_teams()
# team_info = [team for team in nba_teams if team['full_name'] == input_team][0]
# team_id = team_info['id']

# # === Get Roster ===
# roster_df = commonteamroster.CommonTeamRoster(team_id=team_id, season=SEASON).get_data_frames()[0]
# players = roster_df[['PLAYER', 'PLAYER_ID']].to_dict(orient='records')

# # === Get PPG for each player ===
# player_ppg_list = []

# print("⏳ Gathering Points Per Game (PPG) for players...")

# for player in players:
#     try:
#         time.sleep(0.5)  # to avoid rate limits
#         career = playercareerstats.PlayerCareerStats(player_id=player['PLAYER_ID'])
#         df = career.get_data_frames()[0]
#         season_stats = df[df['SEASON_ID'] == SEASON]

#         if not season_stats.empty:
#             ppg = float(season_stats['PTS'].values[0])
#             gp = float(season_stats['GP'].values[0])
#             ppg = round(ppg / gp, 1) if gp > 0 else 0.0
#             player_ppg_list.append({
#                 'Player': player['PLAYER'],
#                 'PPG': ppg
#             })
#             print(f"🟢 {player['PLAYER']}: {ppg} PPG")
#         else:
#             print(f"⚠️ No stats for {player['PLAYER']} in {SEASON}")

#     except Exception as e:
#         print(f"❌ Error for {player['PLAYER']}: {e}")

# # === Save to CSV ===
# if player_ppg_list:
#     ppg_df = pd.DataFrame(player_ppg_list)
#     csv_name = input_team.replace(" ", "_") + "_PPG_" + SEASON + ".csv"
#     ppg_df.to_csv(csv_name, index=False)
#     print(f"\n✅ CSV saved as {csv_name}")
# else:
#     print("❌ No PPG data found.")