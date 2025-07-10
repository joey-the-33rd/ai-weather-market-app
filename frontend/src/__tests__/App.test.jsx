import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import App from '../App';

import { vi } from 'vitest';
vi.mock('axios');

describe('App Integration Tests', () => {
  test('fetches and displays weather data on valid location input', async () => {
    const mockData = [
      {
        recorded_at: "2025-07-09T10:00:00.000Z",
        temperature_c: 20,
        humidity_percent: 50,
        wind_speed_kmh: 10,
        pressure_hpa: 1015,
        precipitation_mm: 0,
        city: "Test City",
        country: "Test Country",
        latitude: 0,
        longitude: 0,
        weather_condition: "Sunny",
        weather_icon: "",
        uv_index: 5,
        air_quality_index: 1
      }
    ];
    axios.get.mockResolvedValueOnce({ data: mockData });

    render(<App />);

    const input = screen.getByPlaceholderText(/enter location/i);
    fireEvent.change(input, { target: { value: 'Test City' } });

    const button = screen.getByText(/get weather/i);
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/test city, test country/i)).toBeInTheDocument();
      expect(screen.getByText(/20/i)).toBeInTheDocument();
      expect(screen.getByText(/50%/i)).toBeInTheDocument();
    });
  });

  test('displays error message on fetch failure', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network Error'));

    render(<App />);

    const input = screen.getByPlaceholderText(/enter location/i);
    fireEvent.change(input, { target: { value: 'Test City' } });

    const button = screen.getByText(/get weather/i);
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch weather data/i)).toBeInTheDocument();
    });
  });

  test('shows error if location input is empty', () => {
    render(<App />);

    const button = screen.getByText(/get weather/i);
    fireEvent.click(button);

    expect(screen.getByText(/please enter a location/i)).toBeInTheDocument();
  });
});
