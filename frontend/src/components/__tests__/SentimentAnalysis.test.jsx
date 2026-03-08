import { render, screen } from '@testing-library/react';
import SentimentAnalysis from '../SentimentAnalysis';

describe('SentimentAnalysis Component', () => {
  test('displays caution when sentiment score is low', () => {
    const mockSentiment = [
      { sentiment: 'negative', sentiment_score: 0.2 },
    ];

    render(<SentimentAnalysis sentiment={mockSentiment} />);

    expect(screen.getByText(/Caution is advised/i)).toBeInTheDocument();
  });

  test('displays recommendation when sentiment score is high', () => {
    const mockSentiment = [
      { sentiment: 'positive', sentiment_score: 0.8 },
    ];

    render(<SentimentAnalysis sentiment={mockSentiment} />);

    expect(screen.getByText(/generally positive market attitude/i)).toBeInTheDocument();
  });
});
