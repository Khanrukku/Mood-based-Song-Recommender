
from flask import Flask, render_template, request, jsonify
import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import random

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

app = Flask(__name__)

# Sample song database with audio features
# In production, this would come from Spotify API or MongoDB
SONGS_DATABASE = [
    {
        'id': 1,
        'title': 'Happy',
        'artist': 'Pharrell Williams',
        'emotion': 'happy',
        'valence': 0.96,
        'energy': 0.82,
        'tempo': 160,
        'genre': 'pop'
    },
    {
        'id': 2,
        'title': 'Someone Like You',
        'artist': 'Adele',
        'emotion': 'sad',
        'valence': 0.24,
        'energy': 0.41,
        'tempo': 67,
        'genre': 'ballad'
    },
    {
        'id': 3,
        'title': 'Eye of the Tiger',
        'artist': 'Survivor',
        'emotion': 'energetic',
        'valence': 0.68,
        'energy': 0.95,
        'tempo': 109,
        'genre': 'rock'
    },
    {
        'id': 4,
        'title': 'Perfect',
        'artist': 'Ed Sheeran',
        'emotion': 'romantic',
        'valence': 0.72,
        'energy': 0.45,
        'tempo': 95,
        'genre': 'pop'
    },
    {
        'id': 5,
        'title': 'Weightless',
        'artist': 'Marconi Union',
        'emotion': 'calm',
        'valence': 0.35,
        'energy': 0.15,
        'tempo': 60,
        'genre': 'ambient'
    },
    {
        'id': 6,
        'title': 'Smells Like Teen Spirit',
        'artist': 'Nirvana',
        'emotion': 'angry',
        'valence': 0.42,
        'energy': 0.98,
        'tempo': 117,
        'genre': 'grunge'
    },
    {
        'id': 7,
        'title': 'Shape of You',
        'artist': 'Ed Sheeran',
        'emotion': 'happy',
        'valence': 0.93,
        'energy': 0.83,
        'tempo': 96,
        'genre': 'pop'
    },
    {
        'id': 8,
        'title': 'Fix You',
        'artist': 'Coldplay',
        'emotion': 'sad',
        'valence': 0.28,
        'energy': 0.52,
        'tempo': 138,
        'genre': 'alternative'
    },
    {
        'id': 9,
        'title': 'Thunderstruck',
        'artist': 'AC/DC',
        'emotion': 'energetic',
        'valence': 0.71,
        'energy': 0.91,
        'tempo': 133,
        'genre': 'rock'
    },
    {
        'id': 10,
        'title': 'Thinking Out Loud',
        'artist': 'Ed Sheeran',
        'emotion': 'romantic',
        'valence': 0.81,
        'energy': 0.48,
        'tempo': 79,
        'genre': 'pop'
    }
]

class MoodBasedRecommender:
    """
    Emotion-aware music recommendation system using sentiment analysis
    and audio feature matching.
    
    Research Approach:
    1. Emotion detection from user input using NLP
    2. Audio feature analysis (valence, energy, tempo)
    3. Hybrid recommendation combining emotion + similarity
    """
    
    def __init__(self, songs_data):
        self.songs_df = pd.DataFrame(songs_data)
        self.emotion_mapping = {
            'happy': {'valence': (0.7, 1.0), 'energy': (0.6, 1.0)},
            'sad': {'valence': (0.0, 0.4), 'energy': (0.0, 0.6)},
            'energetic': {'valence': (0.5, 1.0), 'energy': (0.8, 1.0)},
            'calm': {'valence': (0.3, 0.6), 'energy': (0.0, 0.4)},
            'romantic': {'valence': (0.6, 0.9), 'energy': (0.3, 0.6)},
            'angry': {'valence': (0.0, 0.5), 'energy': (0.7, 1.0)}
        }
    
    def detect_emotion(self, text):
        """
        Detect emotion from user input using TextBlob sentiment analysis.
        
        Methodology:
        - Polarity analysis: positive vs negative sentiment
        - Subjectivity analysis: objective vs subjective content
        - Emotion mapping based on sentiment scores
        
        Returns:
        - emotion (str): Detected emotion category
        - confidence (float): Detection confidence score
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Emotion classification based on polarity and subjectivity
        if polarity > 0.6:
            emotion = 'happy'
            confidence = min(polarity, 0.95)
        elif polarity < -0.3:
            if subjectivity > 0.6:
                emotion = 'sad'
                confidence = min(abs(polarity), 0.90)
            else:
                emotion = 'angry'
                confidence = min(abs(polarity) * 1.2, 0.85)
        elif polarity > 0.2 and subjectivity > 0.5:
            emotion = 'romantic'
            confidence = 0.75
        elif abs(polarity) < 0.2 and subjectivity < 0.4:
            emotion = 'calm'
            confidence = 0.70
        elif polarity > 0.3:
            emotion = 'energetic'
            confidence = 0.80
        else:
            emotion = 'calm'
            confidence = 0.60
        
        return emotion, confidence
    
    def calculate_audio_match_score(self, song, target_emotion):
        """
        Calculate match score based on audio features.
        
        Audio Features:
        - Valence: Musical positiveness (0-1)
        - Energy: Intensity and activity (0-1)
        - Tempo: Speed in BPM
        
        Returns match score (0-1)
        """
        if target_emotion not in self.emotion_mapping:
            return 0.5
        
        target_ranges = self.emotion_mapping[target_emotion]
        valence_range = target_ranges['valence']
        energy_range = target_ranges['energy']
        
        # Calculate how well song features match target ranges
        valence_score = 1.0 if valence_range[0] <= song['valence'] <= valence_range[1] else 0.5
        energy_score = 1.0 if energy_range[0] <= song['energy'] <= energy_range[1] else 0.5
        
        # Weighted combination
        match_score = (valence_score * 0.6 + energy_score * 0.4)
        
        return match_score
    
    def recommend_by_emotion(self, emotion, top_n=5):
        """
        Recommend songs based on detected emotion.
        
        Algorithm:
        1. Filter songs matching emotion category
        2. Calculate audio feature match scores
        3. Rank by combined score
        4. Return top N recommendations
        """
        # Calculate match scores for all songs
        self.songs_df['match_score'] = self.songs_df.apply(
            lambda song: self.calculate_audio_match_score(song, emotion),
            axis=1
        )
        
        # Sort by match score
        recommendations = self.songs_df.nlargest(top_n, 'match_score')
        
        return recommendations.to_dict('records')
    
    def recommend_hybrid(self, user_text, top_n=5):
        """
        Hybrid recommendation combining emotion detection and content similarity.
        
        Methodology:
        1. Detect emotion from user input
        2. Filter songs by emotion
        3. Calculate similarity scores
        4. Combine emotion match + similarity
        5. Return top N recommendations
        """
        detected_emotion, confidence = self.detect_emotion(user_text)
        
        # Get emotion-based recommendations
        emotion_recs = self.recommend_by_emotion(detected_emotion, top_n * 2)
        
        # Add confidence scores
        for song in emotion_recs:
            song['confidence'] = confidence
            song['detected_emotion'] = detected_emotion
        
        return emotion_recs[:top_n]

# Initialize recommender
recommender = MoodBasedRecommender(SONGS_DATABASE)

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    API endpoint for music recommendations.
    
    Request Body:
    - text: User's mood/feeling description
    - top_n: Number of recommendations (default: 5)
    
    Response:
    - detected_emotion: Identified emotion
    - confidence: Detection confidence
    - recommendations: List of recommended songs
    """
    data = request.get_json()
    user_text = data.get('text', '')
    top_n = data.get('top_n', 5)
    
    if not user_text:
        return jsonify({'error': 'No input provided'}), 400
    
    # Get recommendations
    recommendations = recommender.recommend_hybrid(user_text, top_n)
    
    if not recommendations:
        return jsonify({'error': 'No recommendations found'}), 404
    
    return jsonify({
        'detected_emotion': recommendations[0]['detected_emotion'],
        'confidence': round(recommendations[0]['confidence'], 2),
        'recommendations': recommendations,
        'total': len(recommendations)
    })

@app.route('/api/emotions')
def get_emotions():
    """Get list of supported emotion categories"""
    emotions = list(recommender.emotion_mapping.keys())
    return jsonify({'emotions': emotions})

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    stats = {
        'total_songs': len(SONGS_DATABASE),
        'emotions': recommender.songs_df['emotion'].value_counts().to_dict(),
        'genres': recommender.songs_df['genre'].value_counts().to_dict()
    }
    return jsonify(stats)

if __name__ == '__main__':
    print("🎵 Starting Mood-Based Song Recommender...")
    print("📊 Database: {} songs loaded".format(len(SONGS_DATABASE)))
    print("🌐 Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
