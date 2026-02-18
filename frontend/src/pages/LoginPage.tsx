import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import './LoginPage.css';

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
    <div className="login-page">
      <div className="login-card">
        <h1>simpleCommerce</h1>
        <p className="login-subtitle">Sign in to continue</p>

        {step === 'phone' ? (
          <form onSubmit={handleRequestOtp}>
            <label htmlFor="phone">Phone number</label>
            <input
              id="phone"
              type="tel"
              placeholder="0912345678"
              value={phone || ''}
              onChange={(e) => setPhone(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp}>
            <p className="otp-sent">OTP sent to {phone}</p>
            <label htmlFor="otp">Enter 6-digit code</label>
            <input
              id="otp"
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="123456"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Verifying...' : 'Verify'}
            </button>
            <button
              type="button"
              className="btn-back"
              onClick={() => { setStep('phone'); setOtp(''); setError(''); }}
              disabled={loading}
            >
              Change number
            </button>
          </form>
        )}

        {error && <p className="error-msg">{error}</p>}
      </div>
    </div>
  );
}
