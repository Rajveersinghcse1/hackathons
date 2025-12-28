import 'dotenv/config';

export const config = {
  // Server
  port: parseInt(process.env.PORT || '4000', 10),
  host: process.env.HOST || '0.0.0.0',
  isDev: process.env.NODE_ENV !== 'production',
  corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],

  // JWT
  jwtSecret: process.env.JWT_SECRET || 'default-secret-change-me',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '7d',

  // MinIO
  minio: {
    endpoint: process.env.MINIO_ENDPOINT || 'localhost',
    port: parseInt(process.env.MINIO_PORT || '9000', 10),
    accessKey: process.env.MINIO_ACCESS_KEY || 'campusfixit',
    secretKey: process.env.MINIO_SECRET_KEY || 'campusfixit_secret',
    bucket: process.env.MINIO_BUCKET || 'issues',
    useSSL: process.env.MINIO_USE_SSL === 'true',
  },

  // Redis
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',

  // Escalation
  escalationThresholdHours: parseInt(process.env.ESCALATION_THRESHOLD_HOURS || '48', 10),
  criticalEscalationHours: parseInt(process.env.CRITICAL_ESCALATION_HOURS || '24', 10),
};
