import { Button } from "../button";

test("exports the shared button component", () => {
  expect(typeof Button).toBe("function");
});
