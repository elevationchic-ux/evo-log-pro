'use client';

import React, { useState, useRef } from 'react';

interface SearchInputProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onSearch?: (value: string) => void;
  suggestions?: Array<{ label: string; value: string }>;
  onSuggestionClick?: (suggestion: { label: string; value: string }) => void;
  loading?: boolean;
  className?: string;
  debounce?: number;
}

export function SearchInput({
  placeholder = 'Rechercher...',
  value: controlledValue,
  onChange,
  onSearch,
  suggestions = [],
  onSuggestionClick,
  loading = false,
  className = '',
  debounce = 300,
}: SearchInputProps) {
  const [internalValue, setInternalValue] = useState(controlledValue || '');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    onChange?.(newValue);
    
    // Debounce
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (debounce > 0 && onSearch) {
      debounceRef.current = setTimeout(() => {
        onSearch(newValue);
      }, debounce);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      onSearch?.(value);
      setShowSuggestions(false);
    }
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: { label: string; value: string }) => {
    setInternalValue(suggestion.label);
    onSuggestionClick?.(suggestion);
    setShowSuggestions(false);
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">
          search
        </span>
        <input
          type="text"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-2.5 rounded-lg border border-outline bg-surface-container-low text-on-surface placeholder:text-on-surface-variant focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
        />
        {loading ? (
          <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant animate-spin">
            sync
          </span>
        ) : value && (
          <button
            onClick={() => {
              setInternalValue('');
              onChange?.('');
              onSearch?.('');
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        )}
      </div>

      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-surface border border-outline rounded-lg shadow-xl overflow-hidden">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="w-full px-4 py-2.5 text-left text-sm text-on-surface hover:bg-surface-container transition-colors flex items-center justify-between"
            >
              <span>{suggestion.label}</span>
              <span className="text-xs text-on-surface-variant">Appuyez Entrée</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchInput;