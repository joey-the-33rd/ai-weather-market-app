const axios = require('axios');
require('dotenv').config();

async function testWeatherAPI() {
  try {
    const response = await axios.get('http://api.weatherapi.com/v1/forecast.json', {
      params: {
        key: process.env.WEATHER_API_KEY,
        q: 'Nyahururu',
        days: 1,
        aqi: 'no',
        alerts: 'no'
      }
    });
    console.log('API response:', response.data);
  } catch (error) {
    console.error('API call error:', error.message);
  }
}

testWeatherAPI();
