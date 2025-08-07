/**
 * Mock for Next.js navigation (App Router)
 */

export const useRouter = () => ({
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  push: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
});

export const usePathname = () => '/';

export const useSearchParams = () => ({
  get: jest.fn(),
  getAll: jest.fn(),
  has: jest.fn(),
  keys: jest.fn(),
  values: jest.fn(),
  entries: jest.fn(),
  forEach: jest.fn(),
  toString: jest.fn(),
});

export const useParams = () => ({});

export const redirect = jest.fn();

export const notFound = jest.fn();