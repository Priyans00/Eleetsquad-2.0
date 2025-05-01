import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import axios from 'axios';
import AnimatedButton from '../components/AnimatedButtons';
import GridBackground from '../components/GridBackground';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function Register() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/register`, formData);
      if (response.data.success) {
        window.location.href = '/login';
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center  justify-center w-full w-md min-h-screen bg-gray-900 fade-in inset-0 bg-[linear-gradient(rgba(255,255,255,0.15)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.15)_1px,transparent_1px)] bg-[size:64px_64px]">
      
        <div className="p-8 bg-gray-800 h-lg items-center justify-center rounded-lg shadow-lg">
          <h2 className="text-3xl font-bold text-white mb-6 text-center code-font">Register</h2>
          {error && <p className="text-red-400 text-center mb-4">{error}</p>}
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block mb-2 text-sm font-semibold text-gray-300 code-font">
                Username
              </label>
              <input
                className="w-full px-4 py-2 bg-gray-700 text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-code-cyan transition duration-200 code-font"
                id="username"
                name="username"
                type="text"
                placeholder="Enter username"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>
            <div className="mb-6">
              <label className="block mb-2 text-sm font-semibold text-gray-300 code-font">
                Password
              </label>
              <input
                className="w-full px-4 py-2 bg-gray-700 text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-code-cyan transition duration-200 code-font"
                id="password"
                name="password"
                type="password"
                placeholder="Enter password"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>
            <AnimatedButton type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <div className="flex justify-center">
                  <ClipLoader color="#00FFFF" size={20} />
                </div>
              ) : (
                'Register'
              )}
            </AnimatedButton>
          </form>
          <p className="mt-4 text-center text-gray-300">
            Already have an account?{' '}
            <Link to="/login" className="text-code-cyan hover:underline code-font">
              Login
            </Link>
          </p>
        </div>
    </div>
  );
}

export default Register;