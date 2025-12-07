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

  // Determine button classes based on variant and size
  const variantClasses = {
    default: 'btn-neutral',
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    accent: 'btn-accent',
    ghost: 'btn-ghost',
    link: 'btn-link',
    info: 'btn-info',
    success: 'btn-success',
    warning: 'btn-warning',
    error: 'btn-error'
  };

  const sizeClasses = {
    xs: 'btn-xs',
    sm: 'btn-sm',
    md: 'btn-md',
    lg: 'btn-lg'
  };

  // If className contains btn classes, don't override them
  const btnClass = className?.includes('btn') 
    ? className 
    : `btn ${variantClasses[variant]} ${sizeClasses[size]} ${className || classProp || ''}`;

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