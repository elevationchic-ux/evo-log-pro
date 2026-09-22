'use client';

import React, { useState, useEffect, useId } from 'react';

export type SmartInputType = 'container' | 'currency' | 'phone' | 'plate' | 'text';

interface SmartInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
  smartType?: SmartInputType;
  label?: string;
  hint?: string;
  error?: string;
  value: string | number;
  onChange: (formattedValue: string, rawValue: string) => void;
  showValidationIcon?: boolean;
}

/**
 * Calcul de la clé de contrôle ISO 6346 pour conteneurs maritimes
 */
function isValidContainerISO(str: string): boolean {
  const cleaned = str.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  if (cleaned.length !== 11) return false;

  const charValues: Record<string, number> = {
    A: 10, B: 12, C: 13, D: 14, E: 15, F: 16, G: 17, H: 18, I: 19, J: 20,
    K: 21, L: 23, M: 24, N: 25, O: 26, P: 27, Q: 28, R: 29, S: 30, T: 31,
    U: 32, V: 34, W: 35, X: 36, Y: 37, Z: 38,
  };

  let sum = 0;
  for (let i = 0; i < 10; i++) {
    const char = cleaned[i];
    const val = isNaN(Number(char)) ? charValues[char] || 0 : Number(char);
    sum += val * Math.pow(2, i);
  }

  const checkDigit = (sum % 11) % 10;
  return checkDigit === Number(cleaned[10]);
}

/**
 * Formate un conteneur en AAAA 123456-7
 */
function formatContainer(input: string): { formatted: string; raw: string; isValid: boolean } {
  const raw = input.replace(/[^A-Za-z0-9]/g, '').toUpperCase().slice(0, 11);
  let formatted = '';

  if (raw.length > 0) {
    formatted = raw.slice(0, 4);
    if (raw.length > 4) {
      formatted += ' ' + raw.slice(4, 10);
      if (raw.length > 10) {
        formatted += '-' + raw.slice(10, 11);
      }
    }
  }

  const isValid = raw.length === 11 && isValidContainerISO(raw);
  return { formatted, raw, isValid };
}

/**
 * Formate un montant financier avec séparateur de milliers
 */
function formatCurrency(input: string | number): { formatted: string; raw: string; isValid: boolean } {
  const strVal = String(input);
  const raw = strVal.replace(/[^\d]/g, '');
  if (!raw) return { formatted: '', raw: '', isValid: false };

  const num = parseInt(raw, 10);
  if (isNaN(num)) return { formatted: '', raw: '', isValid: false };

  const formatted = num.toLocaleString('fr-FR');
  return { formatted, raw, isValid: num > 0 };
}

/**
 * Formate un numéro de téléphone CEMAC (+237 6XX XX XX XX)
 */
function formatPhone(input: string): { formatted: string; raw: string; isValid: boolean } {
  let cleaned = input.replace(/[^\d+]/g, '');
  if (cleaned.startsWith('00237')) cleaned = '+237' + cleaned.slice(5);
  if (!cleaned.startsWith('+237') && cleaned.startsWith('237')) cleaned = '+' + cleaned;
  if (!cleaned.startsWith('+237') && cleaned.length > 0) cleaned = '+237' + cleaned.replace(/^\+/, '');

  const raw = cleaned;
  const digitsOnly = cleaned.replace(/[^\d]/g, '');
  // Format: +237 6XX XX XX XX
  let formatted = '+237';
  const national = digitsOnly.slice(3, 12);

  if (national.length > 0) {
    formatted += ' ' + national.slice(0, 3);
    if (national.length > 3) {
      formatted += ' ' + national.slice(3, 5);
      if (national.length > 5) {
        formatted += ' ' + national.slice(5, 7);
        if (national.length > 7) {
          formatted += ' ' + national.slice(7, 9);
        }
      }
    }
  }

  const isValid = national.length === 9;
  return { formatted, raw, isValid };
}

/**
 * Formate une plaque d'immatriculation (LT 1234 A)
 */
function formatPlate(input: string): { formatted: string; raw: string; isValid: boolean } {
  const raw = input.replace(/[^A-Za-z0-9]/g, '').toUpperCase().slice(0, 8);
  let formatted = '';

  if (raw.length > 0) {
    formatted = raw.slice(0, 2);
    if (raw.length > 2) {
      formatted += ' ' + raw.slice(2, 6);
      if (raw.length > 6) {
        formatted += ' ' + raw.slice(6, 8);
      }
    }
  }

  const isValid = /^[A-Z]{2}\s\d{3,4}\s[A-Z]{1,2}$/.test(formatted);
  return { formatted, raw, isValid };
}

export function SmartInput({
  smartType = 'text',
  label,
  hint,
  error,
  value,
  onChange,
  showValidationIcon = true,
  className = '',
  placeholder,
  disabled = false,
  required = false,
  ...rest
}: SmartInputProps) {
  const id = useId();
  const [displayValue, setDisplayValue] = useState<string>('');
  const [isValid, setIsValid] = useState<boolean>(false);
  const [isFocused, setIsFocused] = useState<boolean>(false);

  useEffect(() => {
    const rawString = String(value || '');
    if (smartType === 'container') {
      const res = formatContainer(rawString);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
    } else if (smartType === 'currency') {
      const res = formatCurrency(rawString);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
    } else if (smartType === 'phone') {
      const res = formatPhone(rawString);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
    } else if (smartType === 'plate') {
      const res = formatPlate(rawString);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
    } else {
      setDisplayValue(rawString);
      setIsValid(rawString.trim().length > 0);
    }
  }, [value, smartType]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputVal = e.target.value;

    if (smartType === 'container') {
      const res = formatContainer(inputVal);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
      onChange(res.formatted, res.raw);
    } else if (smartType === 'currency') {
      const res = formatCurrency(inputVal);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
      onChange(res.formatted, res.raw);
    } else if (smartType === 'phone') {
      const res = formatPhone(inputVal);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
      onChange(res.formatted, res.raw);
    } else if (smartType === 'plate') {
      const res = formatPlate(inputVal);
      setDisplayValue(res.formatted);
      setIsValid(res.isValid);
      onChange(res.formatted, res.raw);
    } else {
      setDisplayValue(inputVal);
      setIsValid(inputVal.trim().length > 0);
      onChange(inputVal, inputVal);
    }
  };

  const defaultPlaceholders: Record<SmartInputType, string> = {
    container: 'MSKU 123456-7',
    currency: '1 500 000',
    phone: '+237 699 00 00 00',
    plate: 'LT 1234 A',
    text: '',
  };

  const defaultHints: Record<SmartInputType, string> = {
    container: 'Format ISO 6346 : 4 lettres + 6 chiffres + 1 clé de contrôle',
    currency: 'Montant en FCFA (séparateur de milliers automatique)',
    phone: 'Numéro mobile Cameroun / CEMAC',
    plate: 'Immatriculation officielle CEMAC',
    text: '',
  };

  return (
    <div className="w-full space-y-1.5 text-left">
      {label && (
        <label htmlFor={id} className="block text-[13px] font-semibold text-on-surface">
          {label} {required && <span className="text-error">*</span>}
        </label>
      )}

      <div className="relative group">
        <input
          id={id}
          value={displayValue}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder || defaultPlaceholders[smartType]}
          disabled={disabled}
          required={required}
          className={`
            w-full rounded-xl border py-2.5 pl-3.5 pr-10 text-sm transition-all duration-200
            ${smartType === 'currency' ? 'font-mono tabular-nums text-right pr-14' : ''}
            ${smartType === 'container' ? 'font-mono tracking-wider' : ''}
            ${
              error
                ? 'border-error bg-error/5 text-on-surface focus:border-error focus:ring-2 focus:ring-error/20'
                : isValid && !isFocused && displayValue
                ? 'border-emerald-500/50 bg-emerald-500/5 text-on-surface focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20'
                : 'border-outline bg-surface-container-low text-on-surface hover:border-outline-variant focus:border-primary focus:bg-surface focus:ring-2 focus:ring-primary/20'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed bg-surface-container' : ''}
            ${className}
          `}
          {...rest}
        />

        {/* Currency suffix */}
        {smartType === 'currency' && (
          <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-[12px] font-bold text-on-surface-variant">
            XAF
          </span>
        )}

        {/* Validation Icon feedback */}
        {showValidationIcon && smartType !== 'currency' && (
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
            {error ? (
              <span className="material-symbols-outlined text-[18px] text-error animate-in zoom-in-95">error</span>
            ) : isValid && displayValue ? (
              <span
                className="material-symbols-outlined text-[18px] text-emerald-600 dark:text-emerald-400 animate-in zoom-in-95"
                title="Format valide conforme"
              >
                check_circle
              </span>
            ) : isFocused && smartType === 'container' ? (
              <span className="text-[11px] font-mono font-bold text-on-surface-variant">
                {displayValue.replace(/[^A-Z0-9]/gi, '').length}/11
              </span>
            ) : null}
          </div>
        )}
      </div>

      {/* Helper text / error */}
      {error ? (
        <p className="text-[12px] font-medium text-error flex items-center gap-1 animate-in fade-in">
          <span className="material-symbols-outlined text-[14px]">info</span>
          {error}
        </p>
      ) : hint || defaultHints[smartType] ? (
        <p className="text-[11px] text-on-surface-variant flex items-center gap-1">
          {isValid && smartType === 'container' && (
            <span className="inline-flex items-center text-emerald-600 dark:text-emerald-400 font-semibold gap-0.5">
              <span className="material-symbols-outlined text-[13px]">verified</span>
              Conteneur certifié ISO 6346
            </span>
          )}
          {(!isValid || smartType !== 'container') && (
            <span>{hint || defaultHints[smartType]}</span>
          )}
        </p>
      ) : null}
    </div>
  );
}
