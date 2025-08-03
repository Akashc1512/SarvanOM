import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryForm } from "../QueryForm";

// Mock dependencies
jest.mock("@/store/query-store");
jest.mock("@/hooks/useToast");
jest.mock("@/hooks/useDebounce");
jest.mock("@/hooks/usePolling");
jest.mock("@/lib/api");

const mockUseQueryStore = require("@/store/query-store").useQueryStore as jest.MockedFunction<any>;

const mockUseToast = require("@/hooks/useToast").useToast as jest.MockedFunction<any>;

describe("QueryForm", () => {
  const mockToast = jest.fn();
  const mockSubmitQuery = jest.fn();
  const mockUpdateQuery = jest.fn();
  const mockClearError = jest.fn();

  beforeEach(() => {
    mockUseQueryStore.mockReturnValue({
      currentQuery: null,
      submitQuery: mockSubmitQuery,
      updateQuery: mockUpdateQuery,
      clearError: mockClearError,
      error: null,
      isSubmitting: false,
    });

    mockUseToast.mockReturnValue({
      toast: mockToast,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the search form", () => {
    render(<QueryForm />);

    expect(
      screen.getByPlaceholderText("Enter your research question...")
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: /submit/i })
    ).toBeInTheDocument();

    expect(
      screen.getByText(/research tips/i)
    ).toBeInTheDocument();
  });

  it("disables submit button when query is empty", () => {
    render(<QueryForm />);

    const submitButton = screen.getByRole("button", { name: /submit/i });
    expect(submitButton).toBeDisabled();
  });

  it("enables submit button when query has content", async () => {
    const user = userEvent.setup();
    render(<QueryForm />);

    const input = screen.getByPlaceholderText("Enter your research question...");
    await user.type(input, "Test query");

    const submitButton = screen.getByRole("button", { name: /submit/i });
    expect(submitButton).toBeEnabled();
  });

  it("submits query when form is submitted", async () => {
    const user = userEvent.setup();
    render(<QueryForm />);

    const input = screen.getByPlaceholderText("Enter your research question...");
    const submitButton = screen.getByRole("button", { name: /submit/i });

    await user.type(input, "Test query");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockSubmitQuery).toHaveBeenCalledWith({
        query: "Test query",
      });
    });
  });

  it("shows loading state during submission", async () => {
    mockUseQueryStore.mockReturnValue({
      currentQuery: null,
      submitQuery: mockSubmitQuery,
      updateQuery: mockUpdateQuery,
      clearError: mockClearError,
      error: null,
      isSubmitting: true,
    });

    render(<QueryForm />);

    expect(screen.getByText(/processing/i)).toBeInTheDocument();
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("shows error message when submission fails", async () => {
    const errorMessage = "Failed to submit query";
    mockUseQueryStore.mockReturnValue({
      currentQuery: null,
      submitQuery: mockSubmitQuery,
      updateQuery: mockUpdateQuery,
      clearError: mockClearError,
      error: errorMessage,
      isSubmitting: false,
    });

    render(<QueryForm />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("shows query status card when current query exists", () => {
    const mockQuery = {
      query_id: "test-123",
      query: "Test query",
      status: "processing",
      created_at: "2024-01-01T00:00:00Z",
    };

    mockUseQueryStore.mockReturnValue({
      currentQuery: mockQuery,
      submitQuery: mockSubmitQuery,
      updateQuery: mockUpdateQuery,
      clearError: mockClearError,
      error: null,
      isSubmitting: false,
    });

    render(<QueryForm />);

    expect(screen.getByText(/query status/i)).toBeInTheDocument();
    expect(screen.getByText(/test-123/i)).toBeInTheDocument();
  });

  it("clears error when input changes", async () => {
    const user = userEvent.setup();
    render(<QueryForm />);

    const input = screen.getByPlaceholderText("Enter your research question...");
    await user.type(input, "Test");

    expect(mockClearError).toHaveBeenCalled();
  });

  it("provides helpful accessibility attributes", () => {
    render(<QueryForm />);

    const input = screen.getByPlaceholderText("Enter your research question...");
    expect(input).toHaveAttribute("aria-describedby", "query-help");

    const submitButton = screen.getByRole("button", { name: /submit/i });
    expect(submitButton).toHaveAttribute("aria-describedby", "submit-help");
  });

  it("shows research tips", () => {
    render(<QueryForm />);

    expect(screen.getByText(/research tips/i)).toBeInTheDocument();
    expect(
      screen.getByText(/be specific and detailed/i)
    ).toBeInTheDocument();
  });
});
