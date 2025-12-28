/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '9000',
        pathname: '/issues/**',
      },
    ],
  },
  experimental: {
    serverComponentsExternalPackages: ['three'],
  },
};

module.exports = nextConfig;
