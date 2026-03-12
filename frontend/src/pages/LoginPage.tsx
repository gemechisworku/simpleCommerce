import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';

type Step = 'phone' | 'otp';

export function LoginPage() {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<Step>('phone');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate(from, { replace: true });
    }
  }, [from, navigate]);

  const formatPhone = (v: string) => {
    const digits = v.replace(/\D/g, '');
    if (digits.startsWith('251')) return `+${digits}`;
    if (digits.startsWith('0')) return `+251${digits.slice(1)}`;
    return digits ? `+251${digits}` : '';
  };

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const formatted = formatPhone(phone);
    if (!formatted || formatted.length < 12) {
      setError('Enter a valid phone number (e.g. 0912345678)');
      return;
    }
    setLoading(true);
    try {
      await authService.requestOtp(formatted);
      setPhone(formatted);
      setStep('otp');
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message
        : 'Failed to send OTP';
      setError(msg || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!otp || otp.length !== 6) {
      setError('Enter the 6-digit OTP');
      return;
    }
    setLoading(true);
    try {
      const { user: userData } = await authService.verifyOtp(phone, otp);
      login(userData);
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message
        : 'Invalid OTP';
      setError(msg || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4 py-8">
      <div className="w-full max-w-md rounded-xl border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-black dark:text-white">simpleCommerce</h1>
        <p className="mt-1 text-black dark:text-white">Sign in to continue</p>

        {step === 'phone' ? (
          <form onSubmit={handleRequestOtp} className="mt-6 space-y-4">
            <div>
              <label htmlFor="phone" className="mb-1 block text-sm font-medium text-black dark:text-white">Phone number</label>
              <input
                id="phone"
                type="tel"
                placeholder="0912345678"
                value={phone || ''}
                onChange={(e) => setPhone(e.target.value)}
                disabled={loading}
                className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white placeholder:text-gray-2"
              />
            </div>
            <button type="submit" disabled={loading} className="w-full rounded-lg bg-primary py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50">
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="mt-6 space-y-4">
            <p className="text-sm text-black dark:text-white">OTP sent to {phone}</p>
            <div>
              <label htmlFor="otp" className="mb-1 block text-sm font-medium text-black dark:text-white">Enter 6-digit code</label>
              <input
                id="otp"
                type="text"
                inputMode="numeric"
                maxLength={6}
                placeholder="123456"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                disabled={loading}
                className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white placeholder:text-gray-2"
              />
            </div>
            <button type="submit" disabled={loading} className="w-full rounded-lg bg-primary py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50">
              {loading ? 'Verifying...' : 'Verify'}
            </button>
            <button
              type="button"
              onClick={() => { setStep('phone'); setOtp(''); setError(''); }}
              disabled={loading}
              className="w-full rounded-lg border border-stroke dark:border-strokedark py-2.5 font-medium text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10 disabled:opacity-50"
            >
              Change number
            </button>
          </form>
        )}

        {error && <p className="mt-4 text-sm text-danger">{error}</p>}
      </div>
    </div>
  );
}
