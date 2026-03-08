import React from 'react';
import {
  render, screen, fireEvent, waitFor,
} from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';

// Mock toast、navigate、console.warn
const mockToast = jest.fn();
const mockNavigate = jest.fn();
jest.spyOn(console, 'warn').mockImplementation(() => {});

jest.mock('@chakra-ui/react', () => {
  const original = jest.requireActual('@chakra-ui/react');
  return {
    ...original,
    useToast: () => mockToast,
  };
});

jest.mock('react-router-dom', () => {
  const original = jest.requireActual('react-router-dom');
  return {
    ...original,
    useNavigate: () => mockNavigate,
    Link: original.Link,
  };
});

describe('Login page', () => {
  beforeEach(() => {
    mockToast.mockClear();
    mockNavigate.mockClear();
    global.fetch = jest.fn();
    sessionStorage.clear();
  });

  const renderWithWrapper = (props = {}) => render(
    <ChakraProvider>
      <BrowserRouter>
        <Login {...props} />
      </BrowserRouter>
    </ChakraProvider>,
  );

  test('renders form fields and login button', () => {
    renderWithWrapper();

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByText(/register now/i)).toBeInTheDocument();
  });

  test('shows warning when email/password missing', () => {
    renderWithWrapper();

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Please enter both email and password.',
        status: 'warning',
      }),
    );
  });

  test('successful login sets session, calls props, and navigates', async () => {
    const mockSetLogin = jest.fn();
    const mockSetSub = jest.fn();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          token: 'mock-token',
          user: {
            username: 'testuser',
            subscription: 'Free',
            user_id: 123,
            has_completed_survey: true,
            preferences: ['btc', 'eth'],
          },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          followed_currencies: ['btc', 'eth', 'usdt'],
        }),
      });

    renderWithWrapper({
      setIsLoggedIn: mockSetLogin,
      setSubscription: mockSetSub,
    });

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: '123456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Login successful' }),
      );
      expect(mockSetLogin).toHaveBeenCalledWith(true);
      expect(mockSetSub).toHaveBeenCalledWith('Free');
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    expect(sessionStorage.getItem('token')).toBe('mock-token');
    expect(sessionStorage.getItem('username')).toBe('testuser');
    expect(JSON.parse(sessionStorage.getItem('preference_coins'))).toEqual(['btc', 'eth', 'usdt']);
  });

  test('shows error toast when login fails', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ message: 'Invalid credentials' }),
    });

    renderWithWrapper();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrong' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Login failed',
          description: 'Invalid credentials',
          status: 'error',
        }),
      );
    });
  });

  test('shows toast on network error during login', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Server down'));

    renderWithWrapper();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'error@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: '123456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Failed to connect to server',
          status: 'error',
        }),
      );
    });
  });

  test('shows warning but continues when profile fetch fails', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          token: 'mock-token',
          user: {
            username: 'testuser',
            subscription: 'Free',
            user_id: 123,
            has_completed_survey: true,
            preferences: [],
          },
        }),
      })
      .mockRejectedValueOnce(new Error('Profile fetch failed'));

    renderWithWrapper();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: '123456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Login successful' }),
      );
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    // Optionally assert console.warn was triggered
    expect(console.warn).toHaveBeenCalledWith(

      expect.stringContaining('⚠️ Error fetching profile:'),
      expect.any(Error),

    );
  });
});
