import React from 'react';

import {
  render,
  screen,
  fireEvent,
  waitFor,
} from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter } from 'react-router-dom';
import Survey from '../Survey';

const mockNavigate = jest.fn();
const mockToast = jest.fn();

jest.mock('react-router-dom', () => {
  const original = jest.requireActual('react-router-dom');
  return {
    ...original,
    useNavigate: () => mockNavigate,
  };
});

jest.mock('@chakra-ui/react', () => {
  const original = jest.requireActual('@chakra-ui/react');
  return {
    ...original,
    useToast: () => mockToast,
  };
});

beforeEach(() => {
  localStorage.setItem(
    'tempUser',
    JSON.stringify({ user_id: 42, username: 'testuser' }),
  );
  mockToast.mockClear();
});

afterEach(() => {
  localStorage.clear();
  jest.clearAllMocks();
  global.fetch = undefined;
});

const renderSurvey = () => render(
  <ChakraProvider>
    <BrowserRouter>
      <Survey />
    </BrowserRouter>
  </ChakraProvider>,
);

test('renders all 6 survey questions', async () => {
  renderSurvey();
  const questions = await screen.findAllByRole('combobox');
  expect(questions).toHaveLength(6);
});

test('shows warning toast when not all questions are answered', async () => {
  renderSurvey();
  const submitButton = screen.getByRole('button', { name: /submit survey/i });
  fireEvent.click(submitButton);

  await waitFor(() => {
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Incomplete Survey',
        description: expect.stringContaining('Please answer all 6 questions'),
        status: 'warning',
      }),
    );
  });
});

test('submits successfully when all answers provided', async () => {
  jest.useFakeTimers();

  global.fetch = jest.fn(() => Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  }));

  renderSurvey();

  const selects = await screen.findAllByRole('combobox');
  selects.forEach((select) => {
    fireEvent.change(select, { target: { value: 'dummy' } });
  });

  fireEvent.click(screen.getByRole('button', { name: /submit survey/i }));

  await waitFor(() => {
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Survey Submitted Successfully!',
        description: expect.stringContaining('Thank you'),
        status: 'success',
      }),
    );
  });

  jest.advanceTimersByTime(3000);

  await waitFor(() => {
    expect(localStorage.getItem('tempUser')).toBeNull();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  jest.useRealTimers();
});

test('shows error alert if tempUser not found at load time', () => {
  localStorage.removeItem('tempUser');
  renderSurvey();

  expect(
    screen.getByText(/user information not found/i),
  ).toBeInTheDocument();
});

test('shows error toast if currentUser is null but form is visible', async () => {
  renderSurvey();
  localStorage.removeItem('tempUser');

  const selects = await screen.findAllByRole('combobox');
  selects.forEach((select) => {
    fireEvent.change(select, { target: { value: 'dummy' } });
  });

  fireEvent.click(screen.getByRole('button', { name: /submit survey/i }));

  await waitFor(() => {
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'User Error',
        description: expect.stringContaining('Unable to retrieve registration info'),
        status: 'error',
      }),
    );
  });
});

test('shows error toast if survey submission fails', async () => {
  global.fetch = jest.fn(() => Promise.resolve({
    ok: false,
    json: () => Promise.resolve({ message: 'Invalid payload' }),
  }));

  renderSurvey();

  const selects = await screen.findAllByRole('combobox');
  selects.forEach((select) => {
    fireEvent.change(select, { target: { value: 'dummy' } });
  });

  fireEvent.click(screen.getByRole('button', { name: /submit survey/i }));

  await waitFor(() => {
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Submission failed.',
        description: 'Invalid payload',
        status: 'error',
      }),
    );
  });
});

test('shows error toast if submission throws exception', async () => {
  global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));

  renderSurvey();

  const selects = await screen.findAllByRole('combobox');
  selects.forEach((select) => {
    fireEvent.change(select, { target: { value: 'dummy' } });
  });

  fireEvent.click(screen.getByRole('button', { name: /submit survey/i }));

  await waitFor(() => {
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Submission failed.',
        description: 'Network error',
        status: 'error',
      }),
    );
  });
});
