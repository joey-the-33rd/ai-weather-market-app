const axios = require('axios');

const BASE_URL = 'http://localhost:6000/api/weather';
const LOCATION = 'Nyahururu';
const REQUESTS = 100;
const CONCURRENCY = 10;

/**
 * Sends a request to the weather API and returns the HTTP status code.
 * @returns {Promise<number|null>} The HTTP status code of the response, or null if the request failed.
 */
async function sendRequest() {
  try {
    const response = await axios.get(BASE_URL, {
      params: { location: LOCATION }
    });
    return response.status;
  } catch (error) {
    if (error.response) {
      return error.response.status;
    }
    return null;
  }
}

/**
 * Runs a load test by sending a specified number of requests to the weather API
 * in batches of a specified concurrency level. The HTTP status code of each
 * response is logged to the console after each batch is completed.
 */
async function runLoadTest() {
  const promises = [];
  for (let i = 0; i < REQUESTS; i++) {
    promises.push(sendRequest());
    if (promises.length >= CONCURRENCY) {
      const results = await Promise.all(promises);
      console.log('Batch results:', results);
      promises.length = 0;
    }
  }
  if (promises.length > 0) {
    const results = await Promise.all(promises);
    console.log('Final batch results:', results);
  }
  console.log('Load test completed');
}

runLoadTest();
