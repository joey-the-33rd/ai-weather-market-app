// backend/server.ts
import express from "express";
import dotenv from "dotenv";
import morgan from "morgan";
// @ts-ignore
import weatherRoute from "./api/weather";

dotenv.config();

const app = express();
// Middleware to log all incoming requests
app.use((req, res, next) => {
  console.log(`Incoming request: ${req.method} ${req.url}`);
  next();
});

const PORT = process.env.PORT || 5000;

// Middleware
app.use(morgan("combined")); // Global request logging
app.use(express.json());

// Test route to verify server is reachable
app.get("/api/test", (req, res) => {
  res.json({ message: "API is working" });
});

// Routes
app.use("/api", weatherRoute);

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});