import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import axios from 'axios';
import App from '../App';

jest.mock('axios');

describe('App component', () => {
  it('renders correctly', () => {
    const { getByPlaceholderText, getByText } = render(<App />);
    expect(getByPlaceholderText('Enter city')).toBeTruthy();
    expect(getByText('Get Weather')).toBeTruthy();
  });

  it('updates city input', () => {
    const { getByPlaceholderText } = render(<App />);
    const input = getByPlaceholderText('Enter city');
    fireEvent.changeText(input, 'Nairobi');
    expect(input.props.value).toBe('Nairobi');
  });

  it('fetches and displays weather data', async () => {
    const weatherData = {
      temperature: 25,
      humidity: 60,
      weather: 'Sunny',
    };
    axios.get.mockResolvedValueOnce({ data: weatherData });

    const { getByPlaceholderText, getByText, queryByText } = render(<App />);
    const input = getByPlaceholderText('Enter city');
    fireEvent.changeText(input, 'Nairobi');
    const button = getByText('Get Weather');
    fireEvent.press(button);

    await waitFor(() => {
      expect(queryByText('Temperature: 25°C')).toBeTruthy();
      expect(queryByText('Humidity: 60%')).toBeTruthy();
      expect(queryByText('Condition: Sunny')).toBeTruthy();
    });
  });

  it('handles fetch error gracefully', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network error'));

    const { getByPlaceholderText, getByText } = render(<App />);
    const input = getByPlaceholderText('Enter city');
    fireEvent.changeText(input, 'Nairobi');
    const button = getByText('Get Weather');
    fireEvent.press(button);

    await waitFor(() => {
      // No weather data should be displayed on error
      expect(() => getByText(/Temperature:/)).toThrow();
    });
  });
});
