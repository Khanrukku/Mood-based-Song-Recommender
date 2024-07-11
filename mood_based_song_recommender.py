def get_songs_by_mood(mood):
    mood_to_songs = {
        "happy": [
            {"title": "Kahani", "artist": "Sonu Nigam", "link": "https://open.wynk.in/8zrTa3Alfsb?~destination=whatsapp&~feature=wynk_share&~content_id=srch_hungama_90695831"},
            {"title": "Tum se hi", "artist": "Mohit Chauhan", "link": "https://open.wynk.in/7FXpwnoGbeb?~destination=any&~feature=wynk_share&~content_id=srch_hungama_286254"},
            {"title": "Ek Zindagi", "artist": "Sachin-Jigar", "link": "https://open.wynk.in/qwyLyzmJbeb?~destination=any&~feature=wynk_share&~content_id=srch_hungama_52194779"}
        ],
        "sad": [
            {"title": "Jane Woh Kaise Log The ", "artist": "Hemant Kumar", "link": "https://open.wynk.in/nqJ9a5PJbeb?~destination=any&~feature=wynk_share&~content_id=srch_saregama_INH109541280"},
            {"title": "Kya Hua Tera Wada", "artist": "Mohammad Rafi", "link": "https://open.wynk.in/eL1yxoQJbeb?~destination=any&~feature=wynk_share&~content_id=srch_saregama_INH109534740"},
            {"title": "Pathar Ke Sanam", "artist": "Mohammad Rafi", "link": "https://open.wynk.in/dh1BRcoGbeb?~destination=any&~feature=wynk_share&~content_id=srch_saregama_INH109541570"}
        ],
        "relaxed": [
            {"title": "Main Rahoon Ya Na Rahoon", "artist": "Armaan Malik", "link": "https://open.wynk.in/lHQ8TooGbeb?~destination=any&~feature=wynk_share&~content_id=srch_hungama_16790305"},
            {"title": "Kaise Hua", "artist": "Vishal Mishra", "link": "https://open.wynk.in/LYiHsmqGbeb?~destination=any&~feature=wynk_share&~content_id=srch_hungama_48264397"},
            {"title": "Tum Mile", "artist": "Pritam", "link": "https://open.wynk.in/CrBmWFoJbeb?~destination=any&~feature=wynk_share&~content_id=srch_sonymusic_A10328E0005006453G"}
        ],
        "energetic": [
            {"title": "Slow Motion Angreza", "artist": "Shankar Ehsaan Loy", "link": "https://open.wynk.in/uO9UIJIDbeb?~destination=any&~feature=wynk_share&~content_id=srch_sonymusic_A10328E0006497806L"},
            {"title": "Nagada Nagada", "artist": "Pritam", "link": "https://open.wynk.in/MD9aCofHbeb?~destination=any&~feature=wynk_share&~content_id=srch_hungama_286256"},
            {"title": "Matarghasti", "artist": "Mohit Chauhan", "link": "https://open.wynk.in/y7NLooQJbeb?~destination=any&~feature=wynk_share&~content_id=srch_hungama_16537839"}
        ]
    }
    
    return mood_to_songs.get(mood.lower(), [{"title": "Sorry, no songs found for this mood.", "artist": "", "link": ""}])

def main():
    print("Welcome to the Mood-Based Song Recommender!")
    mood = input("Please enter your mood (happy, sad, relaxed, energetic): ").strip().lower()
    
    songs = get_songs_by_mood(mood)
    
    print(f"\nSongs for your {mood} mood:")
    for song in songs:
        print(f"- {song['title']} by {song['artist']} - Listen here: {song['link']}")

if __name__ == "__main__":
    main()
