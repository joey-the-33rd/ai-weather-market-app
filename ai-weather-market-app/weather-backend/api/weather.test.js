// backend/api/weather.test.js
import request from "supertest";
import express from "express";
import weatherRoute from "./weather.js";

const app = express();
app.use("/api", weatherRoute);

describe("GET /api/weather", () => {
  it("should return 400 if location is missing", async () => {
    const res = await request(app).get("/api/weather");
    expect(res.statusCode).toBe(400);
    expect(res.body).toHaveProperty("error");
  });

  it("should return 200 with valid location", async () => {
    const res = await request(app).get("/api/weather").query({ location: "Nairobi" });
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});
