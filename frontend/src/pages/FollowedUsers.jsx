import { useState, useEffect } from 'react';
import axios from 'axios';
import UserCard from '../components/UserCard';
import Leaderboard from '../components/Leaderboard';
import Button from '../components/Button';
import { ClipLoader } from 'react-spinners';
import GridBackground from '../components/GridBackground';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function FollowedUsers() {
  const [followedStats, setFollowedStats] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFollowedUsers = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_URL}/following`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        });
        setFollowedStats(response.data.followed_stats);
      } catch (error) {
        console.error('Error fetching followed users:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchFollowedUsers();
  }, []);

  const handleUnfollow = async (username) => {
    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/unfollow_leetcode`,
        { leetcode_username: username },
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );
      setFollowedStats(followedStats.filter((stat) => stat.username !== username));
      setError('');
    } catch (error) {
      setError(error.response?.data?.error || 'Error unfollowing user');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <ClipLoader color="#00bcd4" size={50} />
      </div>
    );
  }

  return (
    <div className="container py-8 fade-in">
      <GridBackground>
        <h2 className="text-3xl font-bold text-white mb-6 code-font">Followed Users</h2>
        {error && <p className="text-red-400 mb-4">{error}</p>}
        {followedStats.length === 0 ? (
          <p className="text-gray-400 code-font">You are not following anyone yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {followedStats.map((stats) => (
              <div key={stats.username} className="space-y-4">
                <UserCard {...stats} />
                <Button
                  onClick={() => handleUnfollow(stats.username)}
                  className="bg-red-500 hover:bg-red-400"
                >
                  Unfollow
                </Button>
              </div>
            ))}
          </div>
        )}
        <Leaderboard users={followedStats} />
      </GridBackground>
    </div>
  );
}

export default FollowedUsers;