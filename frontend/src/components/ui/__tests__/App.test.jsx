import React from "react";
import { render, screen } from "@testing-library/react";
import { Button } from "../button";

test("renders the shared button component", () => {
  render(<Button>Forecast</Button>);
  expect(screen.getByRole("button", { name: "Forecast" })).toBeTruthy();
});
