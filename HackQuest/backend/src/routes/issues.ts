import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { prisma } from '../lib/prisma.js';
import { cacheGet, cacheSet, cacheDeletePattern } from '../lib/redis.js';
import { Category, Priority, IssueStatus, Role } from '@prisma/client';

// Validation schemas
const createIssueSchema = z.object({
  title: z.string().min(5).max(200),
  description: z.string().max(2000).optional(),
  category: z.nativeEnum(Category),
  priority: z.nativeEnum(Priority).optional(),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  building: z.string().optional(),
  floor: z.string().optional(),
  room: z.string().optional(),
  locationDescription: z.string().optional(),
  photoUrl: z.string().url(),
});

const updateIssueSchema = z.object({
  status: z.nativeEnum(IssueStatus).optional(),
  priority: z.nativeEnum(Priority).optional(),
  assigneeId: z.string().uuid().optional(),
  resolvedPhotoUrl: z.string().url().optional(),
});

const querySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(50).default(20),
  status: z.nativeEnum(IssueStatus).optional(),
  category: z.nativeEnum(Category).optional(),
  priority: z.nativeEnum(Priority).optional(),
  sortBy: z.enum(['createdAt', 'upvotes', 'priority']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
  search: z.string().optional(),
  reporterId: z.string().uuid().optional(),
  assigneeId: z.string().uuid().optional(),
  upvotedBy: z.string().uuid().optional(),
});

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

// Admin/Staff only middleware
const requireStaff = async (request: FastifyRequest, reply: FastifyReply) => {
  await authenticate(request, reply);
  const { role } = request.user as { role: Role };
  if (role !== 'STAFF' && role !== 'ADMIN') {
    reply.status(403).send({ error: 'Forbidden: Staff access required' });
  }
};

export async function issueRoutes(fastify: FastifyInstance) {
  // Get all issues (public)
  fastify.get('/', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const query = querySchema.parse(request.query);
      const { page, limit, status, category, priority, sortBy, sortOrder, search, reporterId, assigneeId, upvotedBy } = query;

      const skip = (page - 1) * limit;

      // Build where clause
      const where: any = {};
      if (status) where.status = status;
      if (category) where.category = category;
      if (priority) where.priority = priority;
      if (reporterId) where.reporterId = reporterId;
      if (assigneeId) where.assigneeId = assigneeId;
      if (upvotedBy) {
        where.upvotes = {
          some: {
            userId: upvotedBy
          }
        };
      }
      if (search) {
        where.OR = [
          { title: { contains: search, mode: 'insensitive' } },
          { description: { contains: search, mode: 'insensitive' } },
          { building: { contains: search, mode: 'insensitive' } },
        ];
      }

      // Build orderBy
      let orderBy: any = { [sortBy]: sortOrder };
      if (sortBy === 'upvotes') {
        orderBy = { upvotes: { _count: sortOrder } };
      }

      const [issues, total] = await Promise.all([
        prisma.issue.findMany({
          where,
          skip,
          take: limit,
          orderBy,
          include: {
            reporter: {
              select: { id: true, name: true, avatarUrl: true },
            },
            assignee: {
              select: { id: true, name: true, avatarUrl: true },
            },
            _count: {
              select: { upvotes: true, comments: true },
            },
          },
        }),
        prisma.issue.count({ where }),
      ]);

      return reply.send({
        issues,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit),
        },
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return reply.status(400).send({ error: 'Validation failed', details: error.errors });
      }
      throw error;
    }
  });

  // Get single issue (public)
  fastify.get('/:id', async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    const { id } = request.params;

    const issue = await prisma.issue.findUnique({
      where: { id },
      include: {
        reporter: {
          select: { id: true, name: true, avatarUrl: true, department: true },
        },
        assignee: {
          select: { id: true, name: true, avatarUrl: true },
        },
        comments: {
          orderBy: { createdAt: 'asc' },
          include: {
            user: {
              select: { id: true, name: true, avatarUrl: true, role: true },
            },
          },
        },
        activityLogs: {
          orderBy: { createdAt: 'desc' },
          take: 20,
          include: {
            user: {
              select: { id: true, name: true, role: true },
            },
          },
        },
        _count: {
          select: { upvotes: true },
        },
      },
    });

    if (!issue) {
      return reply.status(404).send({ error: 'Issue not found' });
    }

    return reply.send({ issue });
  });

  // Create issue (authenticated)
  fastify.post('/', {
    preHandler: authenticate,
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const body = createIssueSchema.parse(request.body);
      const { userId } = request.user as { userId: string };

      const issue = await prisma.issue.create({
        data: {
          ...body,
          reporterId: userId,
        },
        include: {
          reporter: {
            select: { id: true, name: true, avatarUrl: true },
          },
          _count: {
            select: { upvotes: true },
          },
        },
      });

      // Log activity
      await prisma.activityLog.create({
        data: {
          action: 'ISSUE_CREATED',
          issueId: issue.id,
          userId,
          details: { category: issue.category, priority: issue.priority },
        },
      });

      // Invalidate cache
      await cacheDeletePattern('stats:*');

      return reply.status(201).send({ issue });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return reply.status(400).send({ error: 'Validation failed', details: error.errors });
      }
      throw error;
    }
  });

  // Update issue (staff/admin only)
  fastify.patch('/:id', {
    preHandler: requireStaff,
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    try {
      const { id } = request.params;
      const body = updateIssueSchema.parse(request.body);
      const { userId } = request.user as { userId: string };

      const existingIssue = await prisma.issue.findUnique({ where: { id } });
      if (!existingIssue) {
        return reply.status(404).send({ error: 'Issue not found' });
      }

      // Update timestamps based on status
      const updateData: any = { ...body };
      if (body.status === 'ACKNOWLEDGED' && !existingIssue.acknowledgedAt) {
        updateData.acknowledgedAt = new Date();
      }
      if (body.status === 'RESOLVED' && !existingIssue.resolvedAt) {
        updateData.resolvedAt = new Date();
      }
      if (body.status === 'ESCALATED' && !existingIssue.escalatedAt) {
        updateData.escalatedAt = new Date();
        updateData.escalationLevel = existingIssue.escalationLevel + 1;
      }

      const issue = await prisma.issue.update({
        where: { id },
        data: updateData,
        include: {
          reporter: {
            select: { id: true, name: true, avatarUrl: true },
          },
          assignee: {
            select: { id: true, name: true, avatarUrl: true },
          },
        },
      });

      // Log activity
      await prisma.activityLog.create({
        data: {
          action: 'ISSUE_UPDATED',
          issueId: id,
          userId,
          details: { changes: body },
        },
      });

      // Invalidate cache
      await cacheDeletePattern('stats:*');

      return reply.send({ issue });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return reply.status(400).send({ error: 'Validation failed', details: error.errors });
      }
      throw error;
    }
  });

  // Upvote issue (authenticated)
  fastify.post('/:id/upvote', {
    preHandler: authenticate,
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    const { id } = request.params;
    const { userId } = request.user as { userId: string };

    const existingUpvote = await prisma.upvote.findUnique({
      where: {
        userId_issueId: { userId, issueId: id },
      },
    });

    if (existingUpvote) {
      // Remove upvote
      await prisma.upvote.delete({
        where: { id: existingUpvote.id },
      });
      return reply.send({ upvoted: false });
    }

    // Add upvote
    await prisma.upvote.create({
      data: {
        userId,
        issueId: id,
      },
    });

    return reply.send({ upvoted: true });
  });

  // Add comment (authenticated)
  fastify.post('/:id/comments', {
    preHandler: authenticate,
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    const { id } = request.params;
    const { userId } = request.user as { userId: string };
    const commentSchema = z.object({
      content: z.string().min(1).max(1000),
    });

    try {
      const { content } = commentSchema.parse(request.body);

      const comment = await prisma.comment.create({
        data: {
          content,
          userId,
          issueId: id,
        },
        include: {
          user: {
            select: { id: true, name: true, avatarUrl: true, role: true },
          },
        },
      });

      // Log activity
      await prisma.activityLog.create({
        data: {
          action: 'COMMENT_ADDED',
          issueId: id,
          userId,
        },
      });

      return reply.status(201).send({ comment });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return reply.status(400).send({ error: 'Validation failed', details: error.errors });
      }
      throw error;
    }
  });

  // Get issues near location (for map)
  fastify.get('/nearby', async (request: FastifyRequest, reply: FastifyReply) => {
    const nearbySchema = z.object({
      lat: z.coerce.number().min(-90).max(90),
      lng: z.coerce.number().min(-180).max(180),
      radius: z.coerce.number().min(10).max(5000).default(500), // meters
    });

    try {
      const { lat, lng, radius } = nearbySchema.parse(request.query);

      // Simple bounding box query (for demo - PostGIS would be better)
      const latDelta = radius / 111000; // 1 degree ≈ 111km
      const lngDelta = radius / (111000 * Math.cos(lat * Math.PI / 180));

      const issues = await prisma.issue.findMany({
        where: {
          latitude: {
            gte: lat - latDelta,
            lte: lat + latDelta,
          },
          longitude: {
            gte: lng - lngDelta,
            lte: lng + lngDelta,
          },
        },
        include: {
          _count: {
            select: { upvotes: true },
          },
        },
      });

      return reply.send({ issues });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return reply.status(400).send({ error: 'Validation failed', details: error.errors });
      }
      throw error;
    }
  });
}
