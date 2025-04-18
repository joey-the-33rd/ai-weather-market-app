// backend/server.ts
import express from "express";
import dotenv from "dotenv";
import morgan from "morgan";
// @ts-ignore
import weatherRoute from "./api/weather";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(morgan("combined")); // Global request logging
app.use(express.json());

// Routes
app.use("/api", weatherRoute);

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});