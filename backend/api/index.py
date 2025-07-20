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
import sys
import traceback
import json     
from supabase_jwt_required import supabase_jwt_required     

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Environment variables check
required_env_vars = {
    'SUPABASE_URL': os.environ.get('SUPABASE_URL'),
    'SUPABASE_KEY': os.environ.get('SUPABASE_KEY'),
    'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY'),
    'SUPABASE_JWT_SECRET': os.environ.get('SUPABASE_JWT_SECRET')
}

# Log environment status
logger.info("Environment variables status:")
for var, value in required_env_vars.items():
    logger.info(f"{var}: {'✓ Set' if value else '✗ Missing'}")

# Configure JWT
app.config['JWT_SECRET_KEY'] = required_env_vars['JWT_SECRET_KEY'] or 'your-secret-key'
jwt = JWTManager(app)

# Configure CORS
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173","http://localhost:3000", "https://eleetsquad.netlify.app", "https://eleet-squad.vercel.app/"]}})

# Supabase configuration
SUPABASE_URL = required_env_vars['SUPABASE_URL']
SUPABASE_KEY = required_env_vars['SUPABASE_KEY']

def get_db_connection():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {str(e)}")
        logger.error(traceback.format_exc())
        raise

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

def ensure_user_exists(user_id):
    supabase = get_db_connection()
    user = supabase.table('users').select('id').eq('id', user_id).execute().data
    if not user:
        # Insert a new user row with just the id
        supabase.table('users').insert({'id': user_id}).execute()

# Health check endpoint
@app.route('/health')
def health_check():
    try:
        env_status = {
            var: bool(value) for var, value in required_env_vars.items()
        }
        try:
            db = get_db_connection()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return jsonify({
            "status": "ok",
            "environment_variables": env_status,
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

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
@supabase_jwt_required
def profile():
    user_id = request.supabase_user['sub']  # Supabase user id claim
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
@supabase_jwt_required  # This decorator will ensure the user is authenticated with a valid JWT token and has a valid user_id in the token's claims dat
def following():
    user_id = request.supabase_user['sub']
    supabase = get_db_connection()
    followed_usernames = supabase.table('followed_leetcode').select('leetcode_username').eq('user_id', user_id).execute().data
    followed_usernames = [row['leetcode_username'] for row in followed_usernames]
    followed_stats = get_leetcode_stats_parallel(followed_usernames)
    return jsonify({'followed_stats': followed_stats})

@app.route('/api/update_leetcode', methods=['POST'])
@supabase_jwt_required
def update_leetcode():
    user_id = request.supabase_user['sub']
    ensure_user_exists(user_id)
    leetcode_username = request.json.get('leetcode_username')
    if not leetcode_username:
        return jsonify({'error': 'No username provided'}), 400
    stats = get_leetcode_stats(leetcode_username)
    if not stats:
        return jsonify({'error': 'Invalid LeetCode username'}), 400
    supabase = get_db_connection()
    supabase.table('users').update({'leetcode_username': leetcode_username}).eq('id', user_id).execute()
    # Fetch updated profile data
    user_data = supabase.table('users').select('leetcode_username').eq('id', user_id).execute().data
    followed_usernames = supabase.table('followed_leetcode').select('leetcode_username').eq('user_id', user_id).execute().data
    followed_usernames = [row['leetcode_username'] for row in followed_usernames]
    followed_stats = get_leetcode_stats_parallel(followed_usernames)
    return jsonify({
        'leetcode_username': leetcode_username,
        'leetcode_stats': stats,
        'followed_stats': followed_stats
    })

@app.route('/api/follow_leetcode', methods=['POST'])
@supabase_jwt_required  # This decorator will ensure the user is authenticated with a valid JWT toke
def follow_leetcode():
    user_id = request.supabase_user['sub']
    ensure_user_exists(user_id)
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
@supabase_jwt_required
def unfollow_leetcode():
    user_id = request.supabase_user['sub']
    leetcode_username = request.json.get('leetcode_username')
    supabase = get_db_connection()
    supabase.table('followed_leetcode').delete().eq('user_id', user_id).eq('leetcode_username', leetcode_username).execute()
    return jsonify({'success': True})

# Vercel handler
@app.route('/')
def home():
    try:
        return jsonify({
            "status": "ok",
            "message": "API is running",
            "health_check": "/health"
        })
    except Exception as e:
        logger.error(f"Home route error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

# Error handlers
@app.errorhandler(500)
def handle_500_error(e):
    logger.error(f"Internal Server Error: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        "error": "Internal Server Error",
        "message": str(e),
        "traceback": traceback.format_exc()
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        "error": "Server Error",
        "message": str(e),
        "traceback": traceback.format_exc()
    }), 500

# This is important for Vercel
def handler(event, context):
    try:
        return app(event, context)
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "traceback": traceback.format_exc()
            })
        }

# For local development
if __name__ == "__main__":
    app.run()