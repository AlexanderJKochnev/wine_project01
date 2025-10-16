// src/components/LangExpandable.tsx
import { h } from 'preact'; // ← h из 'preact'
import { useState } from 'preact/hooks';

interface LangExpandableProps {
  en: Record<string, any>;
  ru?: Record<string, any>;
  fr?: Record<string, any>;
  field: string;
  label: string;
}

export const LangExpandable = ({ en, ru, fr, field, label }: LangExpandableProps) => {
  const [expanded, setExpanded] = useState(false);

  const getValue = (obj: Record<string, any> | undefined, key: string) =>
    obj?.[key] ?? '—';

  const baseValue = getValue(en, field);
  const ruValue = getValue(ru, field);
  const frValue = getValue(fr, field);

  if (!ruValue && !frValue) {
    return <span>{baseValue}</span>;
  }

  return (
    <div>
      <span onClick={() => setExpanded(!expanded)} style={{ cursor: 'pointer', textDecoration: 'underline' }}>
        {baseValue} {expanded ? '▲' : '▼'}
      </span>
      {expanded && (
        <div style={{ fontSize: '0.9em', color: '#555', marginTop: '4px' }}>
          <div>🇷🇺 {ruValue}</div>
          <div>🇫🇷 {frValue}</div>
        </div>
      )}
    </div>
  );
};