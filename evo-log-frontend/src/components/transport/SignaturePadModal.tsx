import React, { useRef, useState, useEffect } from 'react';
import { X, Eraser, Check } from 'lucide-react';

interface SignaturePadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (signatureBase64: string, name: string) => void;
}

export default function SignaturePadModal({ isOpen, onClose, onSave }: SignaturePadModalProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  // Setup canvas context when modal opens
  useEffect(() => {
    if (isOpen && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
      }
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDrawing(true);
    draw(e);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) ctx.beginPath(); // Reset the path
    }
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Get coordinates depending on mouse vs touch
    let clientX, clientY;
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = (e as React.MouseEvent).clientX;
      clientY = (e as React.MouseEvent).clientY;
    }

    const rect = canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;

    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
    setError(''); // Clear error if they start drawing
  };

  const clearPad = () => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  const handleSave = () => {
    if (!name.trim()) {
      setError('Veuillez entrer le nom du réceptionnaire.');
      return;
    }
    if (canvasRef.current) {
      const dataUrl = canvasRef.current.toDataURL('image/png');
      onSave(dataUrl, name);
    }
  };

  return (
    <div className="relative z-50">
      {/* The backdrop */}
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" aria-hidden="true" onClick={onClose} />

      {/* Full-screen container to center the panel */}
      <div className="fixed inset-0 flex items-center justify-center p-4 pointer-events-none">
        <div className="w-full max-w-md bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col pointer-events-auto">
          
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
            <h2 className="text-lg font-semibold text-gray-900">
              Validation de Livraison (E-POD)
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 space-y-5">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Nom du Réceptionnaire <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-blue-500 focus:ring-blue-500 transition-colors"
                placeholder="Ex: Jean Dupont"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-sm font-medium text-gray-700">
                  Signature <span className="text-red-500">*</span>
                </label>
                <button
                  type="button"
                  onClick={clearPad}
                  className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium"
                >
                  <Eraser className="w-3.5 h-3.5" />
                  Effacer
                </button>
              </div>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg overflow-hidden bg-gray-50">
                <canvas
                  ref={canvasRef}
                  width={380}
                  height={200}
                  className="w-full h-[200px] touch-none cursor-crosshair bg-white"
                  onMouseDown={startDrawing}
                  onMouseUp={stopDrawing}
                  onMouseOut={stopDrawing}
                  onMouseMove={draw}
                  onTouchStart={startDrawing}
                  onTouchEnd={stopDrawing}
                  onTouchMove={draw}
                />
              </div>
            </div>

            {error && (
              <p className="text-sm text-red-600 font-medium">{error}</p>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200 transition-colors"
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <Check className="w-4 h-4" />
              Confirmer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
