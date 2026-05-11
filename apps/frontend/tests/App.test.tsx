import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "../src/App";

describe("App", () => {
  it("renders the heading and submit button", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /code critic/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /critique/i })).toBeInTheDocument();
  });

  it("disables the submit button when the input is empty", () => {
    render(<App />);
    const button = screen.getByRole("button", { name: /critique/i });
    expect(button).toBeDisabled();
  });
});
