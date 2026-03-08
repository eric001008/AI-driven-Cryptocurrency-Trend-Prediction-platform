// src/pages/__tests__/Register.test.jsx
import React from 'react';
import {
  render, screen, fireEvent, waitFor,
} from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter } from 'react-router-dom';
import Register from '../Register';

const renderWithProviders = () => render(
  <ChakraProvider>
    <BrowserRouter>
      <Register />
    </BrowserRouter>
  </ChakraProvider>,
);

describe('Register Page', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders register form elements', () => {
    renderWithProviders();

    expect(screen.getByPlaceholderText('Enter your username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter 6-digit code')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Create a password')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Confirm your password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send code/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  test('shows error when passwords do not match', async () => {
    renderWithProviders();

    fireEvent.change(screen.getByPlaceholderText('Enter your username'), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByPlaceholderText('you@example.com'), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter 6-digit code'), {
      target: { value: '123456' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { value: 'password123' },
    });
    fireEvent.change(screen.getByPlaceholderText('Confirm your password'), {
      target: { value: 'wrongpass' },
    });

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  test('submits correctly when fields are valid', async () => {
    global.fetch = jest.fn(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ user: { username: 'testuser' } }),
    }));

    renderWithProviders();

    fireEvent.change(screen.getByPlaceholderText('Enter your username'), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByPlaceholderText('you@example.com'), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter 6-digit code'), {
      target: { value: '123456' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { value: 'password123' },
    });
    fireEvent.change(screen.getByPlaceholderText('Confirm your password'), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5001/api/register',
      expect.objectContaining({
        method: 'POST',
      }),
    ));
  });
});
