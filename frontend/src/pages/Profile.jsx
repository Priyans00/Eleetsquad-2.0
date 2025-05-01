import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import UserCard from '../components/UserCard';
import Leaderboard from '../components/Leaderboard';
import AnimatedButton from '../components/AnimatedButtons';
import { ClipLoader } from 'react-spinners';
import _ from 'lodash';
import GridBackground from '../components/GridBackground';

const API_URL = import.meta.env.VITE_API_URL ;

function Profile() {
  const [profile, setProfile] = useState(null);
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_URL}/profile`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        });
        setProfile(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleUpdateLeetcode = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/update_leetcode`,
        { leetcode_username: leetcodeUsername },
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );
      if (response.data.username) {
        setProfile({ ...profile, leetcode_username: leetcodeUsername, leetcode_stats: response.data });
        setLeetcodeUsername('');
        setError('');
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Error updating LeetCode username');
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/follow_leetcode`,
        { leetcode_username: leetcodeUsername },
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );
      const response = await axios.get(`${API_URL}/profile`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      });
      setProfile(response.data);
      setLeetcodeUsername('');
      setError('');
    } catch (error) {
      setError(error.response?.data?.error || 'Error following user');
    } finally {
      setLoading(false);
    }
  };

  const debouncedSetLeetcodeUsername = useCallback(
    _.debounce((value) => setLeetcodeUsername(value), 300),
    []
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <ClipLoader color="#00bcd4" size={50} />
      </div>
    );
  }

  if (!profile) return <div className="text-center mt-10 text-white code-font">Error loading profile</div>;

  return (
    <div className="min-h-screen w-full bg-black">
      <div className="lg:ml-64 p-6 fade-in">
        <GridBackground>
          <div className="relative min-h-screen">
            <h2 className="text-3xl font-bold text-white mb-6 code-font">Your Profile</h2>
            {error && <p className="text-red-400 mb-4">{error}</p>}
            {profile.leetcode_username ? (
              <UserCard {...profile.leetcode_stats} />
            ) : (
              <p className="text-gray-400 code-font">No LeetCode username set</p>
            )}
            <form onSubmit={handleUpdateLeetcode} className="mb-8">
              <div className="mb-4">
                <label className="block mb-2 text-sm font-semibold text-gray-300 code-font ">
                  Update LeetCode Username
                </label>
                <input
                  className="w-full max-w-md px-4 py-2 bg-gray-700 text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-code-cyan transition duration-200 code-font"
                  type="text"
                  value={leetcodeUsername}
                  onChange={(e) => debouncedSetLeetcodeUsername(e.target.value)}
                  placeholder="Enter LeetCode username"
                />
              </div>
              <AnimatedButton type="submit">Update Username</AnimatedButton>
            </form>
            <form onSubmit={handleFollow} className="mb-8">
              <div className="mb-4">
                <label className="block mb-2 text-sm font-semibold text-gray-300 code-font">
                  Follow LeetCode User
                </label>
                <input
                  className="w-full max-w-md px-4 py-2 bg-gray-700 text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-code-cyan transition duration-200 code-font"
                  type="text"
                  value={leetcodeUsername}
                  onChange={(e) => debouncedSetLeetcodeUsername(e.target.value)}
                  placeholder="Enter LeetCode username"
                />
              </div>
              <AnimatedButton type="submit">Follow User</AnimatedButton>
            </form>
            <h3 className="text-2xl font-bold text-white mb-4 code-font">Followed Users</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {profile.followed_stats.map((stats) => (
                <UserCard key={stats.username} {...stats} />
              ))}
            </div>
            <Leaderboard users={[profile.leetcode_stats, ...profile.followed_stats].filter(Boolean)} />
          </div>
        </GridBackground>
      </div>
    </div>
  );
}

export default Profile;