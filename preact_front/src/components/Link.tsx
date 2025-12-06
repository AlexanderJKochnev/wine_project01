// src/components/Link.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';

export const Link = ({ href, children, className, class: classProp, onClick, ...props }: { href: string; children: any; className?: string; class?: string; onClick?: () => void; [key: string]: any }) => {
  const router = useLocation();
  
  const handleClick = (e: MouseEvent) => {
    e.preventDefault();
    if (onClick) onClick();
    router.route(href);
  };

  return (
    <a 
      href={href} 
      onClick={handleClick} 
      className={className || classProp} 
      {...props}
    >
      {children}
    </a>
  );
};