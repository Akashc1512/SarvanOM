/**
 * Jest Module Name Mapping for Static Assets
 * Maps static assets to mock implementations for testing
 */

module.exports = {
  // Handle CSS imports (with CSS modules)
  '^.+\\.module\\.(css|sass|scss)$': 'identity-obj-proxy',

  // Handle CSS imports (without CSS modules)
  '^.+\\.(css|sass|scss)$': '<rootDir>/src/__mocks__/styleMock.js',

  // Handle image imports
  '^.+\\.(png|jpg|jpeg|gif|webp|avif|ico|bmp|svg)$': '<rootDir>/src/__mocks__/fileMock.js',

  // Handle font imports
  '^.+\\.(woff|woff2|eot|ttf|otf)$': '<rootDir>/src/__mocks__/fileMock.js',

  // Handle video imports
  '^.+\\.(mp4|webm|ogg|mp3|wav|flac|aac)$': '<rootDir>/src/__mocks__/fileMock.js',

  // Handle JSON imports
  '^.+\\.json$': '<rootDir>/src/__mocks__/jsonMock.js',

  // Handle worker imports
  '^.+\\.worker\\.(js|ts)$': '<rootDir>/src/__mocks__/workerMock.js',

  // Handle specific library mocks
  '^vis-network$': '<rootDir>/src/__mocks__/vis-network.js',
  '^vis-data$': '<rootDir>/src/__mocks__/vis-data.js',
  '^chart\\.js$': '<rootDir>/src/__mocks__/chart.js',
  '^react-chartjs-2$': '<rootDir>/src/__mocks__/react-chartjs-2.js',

  // Handle Next.js specific imports
  '^next/image$': '<rootDir>/src/__mocks__/next-image.js',
  '^next/router$': '<rootDir>/src/__mocks__/next-router.js',
  '^next/navigation$': '<rootDir>/src/__mocks__/next-navigation.js',
  '^next/headers$': '<rootDir>/src/__mocks__/next-headers.js',

  // Handle module aliases
  '^@/(.*)$': '<rootDir>/src/$1',
};