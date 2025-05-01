import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

function Sidebar() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <>
      {/* Mobile Hamburger Menu */}
      <div className="lg:hidden fixed top-0 left-0 w-full bg-gray-800 p-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-white focus:outline-none"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={isOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
          </svg>
        </button>
      </div>

      {/* Sidebar */}
      <div className={`fixed lg:static lg:block top-0 left-0 h-full w-64 bg-gray-800 p-4 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition-transform duration-300 z-40`}>
        <div className="text-2xl font-bold text-white mb-8 code-font">Profile Follow</div>
        <nav>
          <Link
            to="/profile"
            className="block py-2 px-4 text-gray-200 hover:bg-cyan-700 hover:text-code-cyan rounded transition duration-200 code-font"
            onClick={() => setIsOpen(false)}
          >
            Profile
          </Link>
          <Link
            to="/following"
            className="block py-2 px-4 text-gray-200 hover:bg-cyan-700 hover:text-code-cyan rounded transition duration-100 code-font"
            onClick={() => setIsOpen(false)}
          >
            Following
          </Link>
          <button
            onClick={() => { handleLogout(); setIsOpen(false); }}
            className="w-full text-left py-2 px-4 text-gray-200 hover:bg-cyan-700 hover:text-code-cyan rounded transition duration-200 code-font"
          >
            Logout
          </button>
        </nav>
      </div>

      {/* Overlay for mobile when sidebar is open */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black opacity-50 lg:hidden z-30"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </>
  );
}

export default Sidebar;