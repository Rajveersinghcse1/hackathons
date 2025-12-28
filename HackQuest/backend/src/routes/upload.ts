import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { nanoid } from 'nanoid';
import { uploadFile } from '../lib/minio.js';

import { prisma } from '../lib/prisma.js';

// Auth middleware
const authenticate = async (request: FastifyRequest, reply: FastifyReply) => {
  try {
    await request.jwtVerify();
    const { userId } = request.user as { userId: string };
    const user = await prisma.user.findUnique({ where: { id: userId } });
    if (!user) {
      return reply.status(401).send({ error: 'User not found' });
    }
  } catch (err) {
    reply.status(401).send({ error: 'Unauthorized' });
  }
};

export async function uploadRoutes(fastify: FastifyInstance) {
  // Upload image
  fastify.post('/image', {
    preHandler: authenticate,
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    const data = await request.file();

    if (!data) {
      return reply.status(400).send({ error: 'No file uploaded' });
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/heic'];
    if (!allowedTypes.includes(data.mimetype)) {
      return reply.status(400).send({ 
        error: 'Invalid file type. Allowed: JPG, PNG, WebP, HEIC' 
      });
    }

    try {
      // Generate unique filename
      const extension = data.filename.split('.').pop() || 'jpg';
      const fileName = `${nanoid()}.${extension}`;

      // Read file buffer
      const buffer = await data.toBuffer();

      // Upload to MinIO
      const url = await uploadFile(buffer, fileName, data.mimetype);

      return reply.send({ 
        url,
        fileName,
        size: buffer.length,
      });
    } catch (error) {
      fastify.log.error(error);
      return reply.status(500).send({ error: 'Failed to upload file' });
    }
  });
}
