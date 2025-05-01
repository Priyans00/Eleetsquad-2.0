import { motion } from 'framer-motion';

function AnimatedButton({ children, onClick, type = 'button', className = '' }) {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      className={`px-4 py-2 bg-code-cyan text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 transition duration-100 code-font ${className}`}
      whileHover={{ scale: 1.05, boxShadow: '0 0 8px rgba(0, 188, 212, 0.5)' }}
      whileTap={{ scale: 0.95, color: 'rgba(134, 251, 0, 0.5)' }}
    >
      {children}
    </motion.button>
  );
}

export default AnimatedButton;