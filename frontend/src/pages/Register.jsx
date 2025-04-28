import { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import Button from '../components/Button';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function Register() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/register`, formData);
      if (response.data.success) {
        window.location.href = '/login';
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Registration failed');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 fade-in">
      <div className="p-8 bg-gray-800 rounded-lg shadow-lg w-full max-w-md">
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
            />
          </div>
          <Button type="submit" className="w-full">
            Register
          </Button>
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