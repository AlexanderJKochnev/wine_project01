// src/components/Link.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';

export const Link = ({ href, children, className, class: classProp, onClick, variant = 'default', size = 'md', ...props }: { href: string; children: any; className?: string; class?: string; onClick?: () => void; variant?: 'default' | 'primary' | 'secondary' | 'accent' | 'ghost' | 'link' | 'info' | 'success' | 'warning' | 'error'; size?: 'xs' | 'sm' | 'md' | 'lg'; [key: string]: any }) => {
  const router = useLocation();
  
  const handleClick = (e: MouseEvent) => {
    e.preventDefault();
    if (onClick) onClick();
    router.route(href);
  };

  // Determine button classes based on variant and size using Tailwind CSS
  const variantClasses = {
    default: 'bg-gray-200 hover:bg-gray-300 text-gray-800 border-gray-300',
    primary: 'bg-blue-600 hover:bg-blue-700 text-white border-blue-700',
    secondary: 'bg-purple-600 hover:bg-purple-700 text-white border-purple-700',
    accent: 'bg-amber-600 hover:bg-amber-700 text-white border-amber-700',
    ghost: 'bg-transparent hover:bg-gray-200 text-gray-700 border-transparent',
    link: 'bg-transparent hover:underline text-blue-600 border-transparent',
    info: 'bg-cyan-600 hover:bg-cyan-700 text-white border-cyan-700',
    success: 'bg-green-600 hover:bg-green-700 text-white border-green-700',
    warning: 'bg-yellow-500 hover:bg-yellow-600 text-white border-yellow-600',
    error: 'bg-red-600 hover:bg-red-700 text-white border-red-700'
  };

  const sizeClasses = {
    xs: 'text-xs px-2 py-1',
    sm: 'text-sm px-3 py-1.5',
    md: 'text-base px-4 py-2',
    lg: 'text-lg px-6 py-3'
  };

  // If className contains button classes, don't override them
  const btnClass = className?.includes('btn') 
    ? className 
    : `inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${variantClasses[variant]} ${sizeClasses[size]} ${className || classProp || ''}`;

  return (
    <a 
      href={href} 
      onClick={handleClick} 
      className={btnClass} 
      {...props}
    >
      {children}
    </a>
  );
};