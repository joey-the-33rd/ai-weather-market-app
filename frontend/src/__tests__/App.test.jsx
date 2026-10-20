import React from "react";
import { act } from "react-dom/test-utils";
import { createRoot } from "react-dom/client";
import axios from "axios";
import App from "../App";

jest.mock("axios", () => ({ get: jest.fn() }));

describe("Weather dashboard", () => {
  let host;
  let root;
  beforeEach(() => {
    host = document.createElement("div");
    document.body.appendChild(host);
    root = createRoot(host);
    axios.get.mockReset();
    localStorage.clear();
  });
  afterEach(async () => {
    await act(async () => root.unmount());
    host.remove();
  });
  async function renderApp() {
    await act(async () => root.render(<App />));
  }
  async function searchFor(location) {
    const input = host.querySelector('input[placeholder="Enter location"]');
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    setter.call(input, location);
    await act(async () => input.dispatchEvent(new Event("input", { bubbles: true })));
    const button = Array.from(host.querySelectorAll("button")).find((item) => item.textContent.includes("Get Weather"));
    await act(async () => {
      button.dispatchEvent(new MouseEvent("click", { bubbles: true }));
      await Promise.resolve();
    });
  }
  test("fetches and displays forecast records for a valid location", async () => {
    axios.get.mockResolvedValueOnce({ data: [{
      recorded_at: "2026-10-20 10:00", temperature_c: 20, humidity_percent: 50,
      wind_speed_kmh: 10, pressure_hpa: 1015, precipitation_mm: 0, city: "Test City",
      country: "Test Country", latitude: 0, longitude: 0, weather_condition: "Sunny",
      weather_icon: "", uv_index: 5, air_quality_index: 1
    }]});
    await renderApp();
    await searchFor("Test City");
    expect(axios.get).toHaveBeenCalledWith("/api/weather", { params: { location: "Test City", mode: "hourly" } });
    expect(host.textContent).toContain("Test City, Test Country");
    expect(host.textContent).toContain("20°C");
    expect(host.textContent).toContain("50%");
  });
  test("shows a useful message when the weather request fails", async () => {
    axios.get.mockRejectedValueOnce(new Error("Network Error"));
    await renderApp();
    await searchFor("Test City");
    expect(host.textContent).toContain("Network Error");
  });
  test("asks for a location when the input is empty", async () => {
    await renderApp();
    const button = Array.from(host.querySelectorAll("button")).find((item) => item.textContent.includes("Get Weather"));
    await act(async () => button.dispatchEvent(new MouseEvent("click", { bubbles: true })));
    expect(host.textContent).toContain("Enter a town, city, or place");
    expect(axios.get).not.toHaveBeenCalled();
  });
});
