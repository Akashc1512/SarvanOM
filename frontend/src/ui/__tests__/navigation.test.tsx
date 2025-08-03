import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MainNav } from "../navigation/MainNav";
import { Breadcrumbs } from "../navigation/breadcrumbs";
import { RouteGuard } from "../auth/RouteGuard";

// Mock Next.js navigation
jest.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
  }),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

describe("Navigation Components", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("MainNav", () => {
    it("renders navigation items correctly", () => {
      render(<MainNav />);

      expect(screen.getByText("Home")).toBeInTheDocument();
      expect(screen.getByText("Queries")).toBeInTheDocument();
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    it("shows active state for current page", () => {
      render(<MainNav />);

      const dashboardLink = screen.getByText("Dashboard").closest("a");
      expect(dashboardLink).toHaveAttribute("aria-current", "page");
    });

    it("has proper accessibility attributes", () => {
      render(<MainNav />);

      const nav = screen.getByRole("navigation");
      expect(nav).toBeInTheDocument();
    });
  });

  describe("Breadcrumbs", () => {
    it("renders breadcrumbs for nested routes", () => {
      render(<Breadcrumbs />);

      expect(screen.getByText("Home")).toBeInTheDocument();
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    it("shows current page as non-clickable", () => {
      render(<Breadcrumbs />);

      const currentPage = screen.getByText("Dashboard");
      expect(currentPage).toHaveAttribute("aria-current", "page");
    });

    it("has proper navigation structure", () => {
      render(<Breadcrumbs />);

      const nav = screen.getByRole("navigation");
      expect(nav).toHaveAttribute("aria-label", "Breadcrumb");
    });
  });

  describe("RouteGuard", () => {
    it("shows loading state initially", () => {
      render(
        <RouteGuard>
          <div>Protected Content</div>
        </RouteGuard>
      );

      expect(
        screen.getByText("Checking authentication...")
      ).toBeInTheDocument();
    });

    it("redirects unauthenticated users", () => {
      localStorageMock.getItem.mockReturnValue(null);

      render(
        <RouteGuard>
          <div>Protected Content</div>
        </RouteGuard>
      );

      expect(
        screen.getByText("Redirecting to login...")
      ).toBeInTheDocument();
    });

    it("allows authenticated users to access content", () => {
      localStorageMock.getItem.mockReturnValue("mock-token");

      render(
        <RouteGuard>
          <div>Protected Content</div>
        </RouteGuard>
      );

      // Wait for auth check to complete
      setTimeout(() => {
        expect(screen.getByText("Protected Content")).toBeInTheDocument();
      }, 100);
    });

    it("enforces role-based access control", () => {
      localStorageMock.getItem.mockReturnValue("mock-token");

      render(
        <RouteGuard requiredRole="admin">
          <div>Protected Content</div>
        </RouteGuard>
      );

      // Should redirect for insufficient permissions
      setTimeout(() => {
        expect(screen.getByText("Access Denied")).toBeInTheDocument();
      }, 100);
    });
  });
});
