const axios = require('axios');
require('dotenv').config();

describe('Weather API', () => {
  const baseURL = 'http://localhost:6000/api/weather';

  test('should return weather data for valid location', async () => {
    const response = await axios.get(baseURL, {
      params: {
        location: 'Nyahururu',
        mode: 'hourly'
      }
    });
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
    expect(response.data.length).toBeGreaterThan(0);
    expect(response.data[0]).toHaveProperty('temperature_c');
    expect(response.data[0]).toHaveProperty('humidity_percent');
  });

  test('should return 400 error if location is missing', async () => {
    try {
      await axios.get(baseURL);
    } catch (error) {
      expect(error.response.status).toBe(400);
      expect(error.response.data).toHaveProperty('error', 'Location is required');
    }
  });

  test('should respect rate limiting', async () => {
    const requests = [];
    for (let i = 0; i < 35; i++) {
      requests.push(
        axios.get(baseURL, {
          params: {
            location: 'Nyahururu'
          }
        }).catch(e => e.response)
      );
    }
    const responses = await Promise.all(requests);
    const rateLimitExceeded = responses.some(res => res.status === 429);
    expect(rateLimitExceeded).toBe(true);
  });
});
