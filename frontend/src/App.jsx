import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import FollowedUsers from './pages/FollowedUsers';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <Router>
      <div className="flex">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Login />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Sidebar />
                <div className="flex-1">
                  <Profile />
                </div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/following"
            element={
              <ProtectedRoute>
                <Sidebar />
                <div className="flex-1">
                  <FollowedUsers />
                </div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;