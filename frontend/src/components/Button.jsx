function Button({ children, onClick, type = 'button', className = '' }) {
    return (
      <button
        type={type}
        onClick={onClick}
        className={`px-4 py-2 bg-code-cyan text-white rounded-lg hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition duration-200 ${className}`}
      >
        {children}
      </button>
    );
  }
  
  export default Button;