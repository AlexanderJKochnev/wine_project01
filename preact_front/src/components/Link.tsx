// src/components/Link.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';

export const Link = ({ href, children, className, class: classProp, onClick, variant = 'default', ...props }: { href: string; children: any; className?: string; class?: string; onClick?: () => void; variant?: 'default' | 'primary' | 'secondary' | 'ghost' | 'link'; [key: string]: any }) => {
  const router = useLocation();
  
  const handleClick = (e: MouseEvent) => {
    e.preventDefault();
    if (onClick) onClick();
    router.route(href);
  };

  // Determine button classes based on variant using pure CSS
  let linkClass = 'btn ';
  
  switch(variant) {
    case 'primary':
      linkClass += 'btn-primary ';
      break;
    case 'secondary':
      linkClass += 'btn-secondary ';
      break;
    case 'ghost':
      linkClass += 'btn-ghost ';
      break;
    case 'link':
      linkClass += 'btn-ghost text-blue-600 hover:underline ';
      break;
    default:
      linkClass += 'btn-primary ';
  }

  // Add any additional classes provided
  linkClass += className || classProp || '';

  return (
    <a 
      href={href} 
      onClick={handleClick} 
      className={linkClass} 
      {...props}
    >
      {children}
    </a>
  );
};