import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "https://profile-follow-react.vercel.app"]}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def get_db_connection():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_leetcode_stats(username):
    supabase = get_db_connection()
    # Check cache
    cache = supabase.table('leetcode_cache').select('*').eq('username', username).execute().data
    if cache and cache[0]['updated_at'] > (datetime.utcnow() - timedelta(hours=24)).isoformat():
        logger.info(f"Cache hit for {username}")
        return cache[0]['stats']

    # Fetch from LeetCode
    start_time = time.time()
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submitStats: submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }
            profile {
                ranking
            }
        }
    }
    """
    try:
        response = requests.post(url, json={'query': query, 'variables': {'username': username}})
        logger.info(f"LeetCode API call for {username} took {time.time() - start_time:.2f} seconds")
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('matchedUser'):
                user_data = data['data']['matchedUser']
                stats = user_data['submitStats']['acSubmissionNum']
                total_solved = sum(item['count'] for item in stats) // 2
                stats_data = {
                    'username': user_data['username'],
                    'total_solved': total_solved,
                    'easy': stats[1]['count'],
                    'medium': stats[2]['count'],
                    'hard': stats[3]['count'],
                    'ranking': user_data['profile']['ranking']
                }
                # Update cache
                supabase.table('leetcode_cache').upsert({
                    'username': username,
                    'stats': stats_data,
                    'updated_at': datetime.utcnow().isoformat()
                }).execute()
                return stats_data
        return None
    except Exception as e:
        logger.error(f"Error fetching LeetCode stats: {e}")
        return None

def get_leetcode_stats_parallel(usernames):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(get_leetcode_stats, usernames))
    return [result for result in results if result]

@app.route('/' , methods=['POST','GET'])
def check():
    return jsonify({"status":"working"}), 200

# Rest of the routes remain unchanged...
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    supabase = get_db_connection()
    try:
        supabase.table('users').insert({'username': username, 'password': hashed_password}).execute()
        return jsonify({'success': True}), 201
    except Exception:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    supabase = get_db_connection()
    user_data = supabase.table('users').select('*').eq('username', username).execute().data
    if user_data and check_password_hash(user_data[0]['password'], password):
        access_token = create_access_token(identity=user_data[0]['id'])
        return jsonify({'access_token': access_token}), 200
    return jsonify({'msg': 'Invalid username or password'}), 401

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    supabase = get_db_connection()
    user_data = supabase.table('users').select('leetcode_username').eq('id', user_id).execute().data
    leetcode_username = user_data[0]['leetcode_username'] if user_data else None
    followed_usernames = supabase.table('followed_leetcode').select('leetcode_username').eq('user_id', user_id).execute().data
    followed_usernames = [row['leetcode_username'] for row in followed_usernames]
    leetcode_stats = get_leetcode_stats(leetcode_username) if leetcode_username else None
    followed_stats = get_leetcode_stats_parallel(followed_usernames)
    return jsonify({
        'leetcode_username': leetcode_username,
        'leetcode_stats': leetcode_stats,
        'followed_stats': followed_stats
    })

@app.route('/api/following', methods=['GET'])
@jwt_required()
def following():
    user_id = get_jwt_identity()
    supabase = get_db_connection()
    followed_usernames = supabase.table('followed_leetcode').select('leetcode_username').eq('user_id', user_id).execute().data
    followed_usernames = [row['leetcode_username'] for row in followed_usernames]
    followed_stats = get_leetcode_stats_parallel(followed_usernames)
    return jsonify({'followed_stats': followed_stats})

@app.route('/api/update_leetcode', methods=['POST'])
@jwt_required()
def update_leetcode():
    user_id = get_jwt_identity()
    leetcode_username = request.json.get('leetcode_username')
    if not leetcode_username:
        return jsonify({'error': 'No username provided'}), 400
    stats = get_leetcode_stats(leetcode_username)
    if not stats:
        return jsonify({'error': 'Invalid LeetCode username'}), 400
    supabase = get_db_connection()
    supabase.table('users').update({'leetcode_username': leetcode_username}).eq('id', user_id).execute()
    return jsonify(stats)

@app.route('/api/follow_leetcode', methods=['POST'])
@jwt_required()
def follow_leetcode():
    user_id = get_jwt_identity()
    leetcode_username = request.json.get('leetcode_username')
    if not leetcode_username:
        return jsonify({'error': 'No username provided'}), 400
    stats = get_leetcode_stats(leetcode_username)
    if not stats:
        return jsonify({'error': 'Invalid LeetCode username'}), 400
    supabase = get_db_connection()
    try:
        supabase.table('followed_leetcode').insert({'user_id': user_id, 'leetcode_username': leetcode_username}).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/unfollow_leetcode', methods=['POST'])
@jwt_required()
def unfollow_leetcode():
    user_id = get_jwt_identity()
    leetcode_username = request.json.get('leetcode_username')
    supabase = get_db_connection()
    supabase.table('followed_leetcode').delete().eq('user_id', user_id).eq('leetcode_username', leetcode_username).execute()
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run()