import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import { TELEGRAM_BOT_USERNAME } from '../constants/api';

type Step = 'phone' | 'otp';

function isInTelegramMiniApp(): boolean {
  const tg = (window as unknown as { Telegram?: { WebApp?: unknown } }).Telegram;
  return typeof tg?.WebApp !== 'undefined';
}

export function LoginPage() {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<Step>('phone');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [telegramRetrying, setTelegramRetrying] = useState(false);
  const [telegramOtpLink, setTelegramOtpLink] = useState<string | null>(null);
  const [otpSentVia, setOtpSentVia] = useState<'telegram' | 'telegram_link' | 'sms' | 'log' | undefined>(undefined);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';
  const inTelegram = isInTelegramMiniApp();

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
    setTelegramOtpLink(null);
    setOtpSentVia(undefined);
    try {
      const res = await authService.requestOtp(formatted);
      setPhone(formatted);
      if (res.telegram_otp_link) setTelegramOtpLink(res.telegram_otp_link);
      if (res.otp_sent_via) setOtpSentVia(res.otp_sent_via);
      setStep('otp');
    } catch (err: unknown) {
      const res = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { message?: string; error?: { message?: string } }; status?: number } }).response
        : undefined;
      const msg = res?.data?.message ?? res?.data?.error?.message ?? 'Failed to send OTP';
      setError(msg);
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
      const res = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { message?: string; error?: { message?: string } } } }).response
        : undefined;
      const msg = res?.data?.message ?? res?.data?.error?.message ?? 'Invalid OTP';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleTelegramRetry = async () => {
    const tg = (window as unknown as { Telegram?: { WebApp?: { initData?: string } } }).Telegram;
    const initData = tg?.WebApp?.initData;
    if (!initData?.length) return;
    setError('');
    setTelegramRetrying(true);
    try {
      const userData = await authService.verifyTelegram(initData);
      login(userData);
      navigate(from, { replace: true });
    } catch {
      setError('Could not log in with Telegram. Try opening the app from Telegram again.');
    } finally {
      setTelegramRetrying(false);
    }
  };

  if (inTelegram) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4 py-8">
        <div className="w-full max-w-md rounded-xl border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-black dark:text-white">simpleCommerce</h1>
          <p className="mt-4 text-black dark:text-white">This app uses your Telegram account to sign you in. No password or code is sent.
          </p>
          <p className="mt-2 text-sm text-black/70 dark:text-white/70">
            Tap below to allow access and continue. We will create your account or sign you in using your Telegram profile.
          </p>
          <button
            type="button"
            onClick={handleTelegramRetry}
            disabled={telegramRetrying}
            className="mt-6 w-full rounded-lg bg-primary py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50"
          >
            {telegramRetrying ? 'Continuing...' : 'Continue with Telegram'}
          </button>
          {error && <p className="mt-4 text-sm text-danger">{error}</p>}
        </div>
      </div>
    );
  }

  const telegramAppUrl = TELEGRAM_BOT_USERNAME
    ? `https://t.me/${TELEGRAM_BOT_USERNAME.replace(/^@/, '')}`
    : '';

  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4 py-8">
      <div className="w-full max-w-md rounded-xl border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-black dark:text-white">simpleCommerce</h1>
        <p className="mt-1 text-black dark:text-white">Sign in to continue</p>

        {telegramAppUrl && (
          <div className="mt-6 rounded-lg border border-stroke dark:border-strokedark bg-meta-4/30 p-4">
            <p className="text-sm text-black dark:text-white mb-3">You can also sign in with your Telegram account.</p>
            <a
              href={telegramAppUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex w-full justify-center rounded-lg bg-[#0088cc] py-2.5 font-medium text-white hover:opacity-90"
            >
              Continue with Telegram
            </a>
          </div>
        )}

        <p className="mt-4 text-sm text-black/70 dark:text-white/70">Or sign in with your phone number</p>

        {step === 'phone' ? (
          <form onSubmit={handleRequestOtp} className="mt-4 space-y-4">
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
            {otpSentVia === 'telegram' && (
              <p className="text-sm text-black dark:text-white">We sent the code to your Telegram. Enter it below.</p>
            )}
            {otpSentVia === 'telegram_link' && telegramOtpLink && (
              <div className="rounded-lg border border-stroke dark:border-strokedark bg-meta-4/50 p-3">
                <p className="text-sm text-black dark:text-white mb-2">Open the link below once to receive your 6-digit code in Telegram. Then enter the code here.</p>
                <a
                  href={telegramOtpLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-primary hover:underline break-all"
                >
                  {telegramOtpLink}
                </a>
              </div>
            )}
            {otpSentVia === 'sms' && (
              <p className="text-sm text-black dark:text-white">We sent a code to your phone. Enter it below.</p>
            )}
            {otpSentVia === 'log' && (
              <p className="text-sm text-black dark:text-white">Check server logs for the code (development). Enter it below.</p>
            )}
            {!otpSentVia && (
              <p className="text-sm text-black dark:text-white">Enter the 6-digit code we sent you for {phone}.</p>
            )}
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
              onClick={() => { setStep('phone'); setOtp(''); setError(''); setTelegramOtpLink(null); setOtpSentVia(undefined); }}
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
