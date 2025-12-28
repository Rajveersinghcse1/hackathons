import Fastify from 'fastify';
import cors from '@fastify/cors';
import jwt from '@fastify/jwt';
import multipart from '@fastify/multipart';
import rateLimit from '@fastify/rate-limit';
import { config } from './config/index.js';
import { authRoutes } from './routes/auth.js';
import { issueRoutes } from './routes/issues.js';
import { statsRoutes } from './routes/stats.js';
import { uploadRoutes } from './routes/upload.js';
import { prisma } from './lib/prisma.js';
import { startEscalationScheduler } from './jobs/escalation.js';

const fastify = Fastify({
  logger: {
    level: config.isDev ? 'debug' : 'info',
  },
});

// Register plugins
await fastify.register(cors, {
  origin: config.isDev ? true : config.corsOrigins,
  credentials: true,
});

await fastify.register(rateLimit, {
  max: 100,
  timeWindow: '1 minute',
});

await fastify.register(jwt, {
  secret: config.jwtSecret,
});

await fastify.register(multipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB max file size
  },
});

// Decorate with Prisma
fastify.decorate('prisma', prisma);

// Health check
fastify.get('/health', async () => {
  return { status: 'ok', timestamp: new Date().toISOString() };
});

// Register routes
await fastify.register(authRoutes, { prefix: '/api/auth' });
await fastify.register(issueRoutes, { prefix: '/api/issues' });
await fastify.register(statsRoutes, { prefix: '/api/stats' });
await fastify.register(uploadRoutes, { prefix: '/api/upload' });

// Graceful shutdown
const signals = ['SIGINT', 'SIGTERM'];
signals.forEach((signal) => {
  process.on(signal, async () => {
    fastify.log.info(`Received ${signal}, shutting down gracefully`);
    await fastify.close();
    await prisma.$disconnect();
    process.exit(0);
  });
});

// Start server
const start = async () => {
  try {
    await fastify.listen({ port: config.port, host: config.host });
    fastify.log.info(`🚀 Server running at http://${config.host}:${config.port}`);
    
    // Start background jobs
    startEscalationScheduler();
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();

export { fastify };
