import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { prisma } from '../lib/prisma.js';
import { cacheGet, cacheSet } from '../lib/redis.js';
import { Role } from '@prisma/client';

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

export async function statsRoutes(fastify: FastifyInstance) {
  // Public dashboard stats
  fastify.get('/dashboard', async (request: FastifyRequest, reply: FastifyReply) => {
    const cacheKey = 'stats:dashboard';
    const cached = await cacheGet<any>(cacheKey);
    if (cached) {
      return reply.send(cached);
    }

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    const [
      totalIssues,
      openIssues,
      resolvedThisWeek,
      categoryStats,
      priorityStats,
      recentIssues,
      topReporters,
      avgResolutionTime,
    ] = await Promise.all([
      // Total issues
      prisma.issue.count(),

      // Open issues
      prisma.issue.count({
        where: {
          status: { in: ['OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS', 'ESCALATED'] },
        },
      }),

      // Resolved this week
      prisma.issue.count({
        where: {
          status: 'RESOLVED',
          resolvedAt: { gte: weekAgo },
        },
      }),

      // Issues by category
      prisma.issue.groupBy({
        by: ['category'],
        _count: { id: true },
        where: {
          status: { in: ['OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS', 'ESCALATED'] },
        },
      }),

      // Issues by priority
      prisma.issue.groupBy({
        by: ['priority'],
        _count: { id: true },
        where: {
          status: { in: ['OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS', 'ESCALATED'] },
        },
      }),

      // Recent issues
      prisma.issue.findMany({
        take: 5,
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          title: true,
          category: true,
          status: true,
          createdAt: true,
          building: true,
        },
      }),

      // Top reporters (leaderboard)
      prisma.user.findMany({
        take: 10,
        orderBy: {
          reportedIssues: { _count: 'desc' },
        },
        select: {
          id: true,
          name: true,
          avatarUrl: true,
          department: true,
          _count: {
            select: { reportedIssues: true },
          },
        },
      }),

      // Average resolution time (in hours)
      prisma.$queryRaw<[{ avg_hours: number }]>`
        SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600) as avg_hours
        FROM issues
        WHERE resolved_at IS NOT NULL
        AND created_at > ${weekAgo}
      `,
    ]);

    const stats = {
      totalIssues,
      openIssues,
      resolvedThisWeek,
      resolutionRate: totalIssues > 0 
        ? Math.round(((totalIssues - openIssues) / totalIssues) * 100) 
        : 0,
      avgResolutionHours: avgResolutionTime[0]?.avg_hours 
        ? Math.round(avgResolutionTime[0].avg_hours) 
        : null,
      categoryStats: categoryStats.map(c => ({
        category: c.category,
        count: c._count.id,
      })),
      priorityStats: priorityStats.map(p => ({
        priority: p.priority,
        count: p._count.id,
      })),
      recentIssues,
      topReporters: topReporters.map(u => ({
        id: u.id,
        name: u.name,
        avatarUrl: u.avatarUrl,
        department: u.department,
        issueCount: u._count.reportedIssues,
      })),
    };

    // Cache for 5 minutes
    await cacheSet(cacheKey, stats, 300);

    return reply.send(stats);
  });

  // Heat map data (for 3D visualization)
  fastify.get('/heatmap', async (request: FastifyRequest, reply: FastifyReply) => {
    const cacheKey = 'stats:heatmap';
    const cached = await cacheGet<any>(cacheKey);
    if (cached) {
      return reply.send(cached);
    }

    const issues = await prisma.issue.findMany({
      where: {
        status: { in: ['OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS', 'ESCALATED'] },
      },
      select: {
        id: true,
        latitude: true,
        longitude: true,
        category: true,
        priority: true,
        building: true,
        _count: {
          select: { upvotes: true },
        },
      },
    });

    // Group by building for aggregated heat map
    const buildingStats = await prisma.issue.groupBy({
      by: ['building'],
      _count: { id: true },
      where: {
        building: { not: null },
        status: { in: ['OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS', 'ESCALATED'] },
      },
    });

    const heatmapData = {
      points: issues.map(i => ({
        id: i.id,
        lat: i.latitude,
        lng: i.longitude,
        weight: i.priority === 'CRITICAL' ? 4 : 
                i.priority === 'HIGH' ? 3 : 
                i.priority === 'MEDIUM' ? 2 : 1,
        category: i.category,
        building: i.building,
        upvotes: i._count.upvotes,
      })),
      buildings: buildingStats.map(b => ({
        name: b.building,
        count: b._count.id,
      })),
    };

    // Cache for 2 minutes
    await cacheSet(cacheKey, heatmapData, 120);

    return reply.send(heatmapData);
  });

  // Admin-only detailed stats
  fastify.get('/admin', {
    preHandler: async (request, reply) => {
      await authenticate(request, reply);
      const { role } = request.user as { role: Role };
      if (role !== 'ADMIN') {
        reply.status(403).send({ error: 'Admin access required' });
      }
    },
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const [
      dailyIssues,
      staffPerformance,
      escalatedIssues,
      overduIssues,
    ] = await Promise.all([
      // Daily issue counts for last 30 days
      prisma.$queryRaw<Array<{ date: Date; count: bigint }>>`
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM issues
        WHERE created_at >= ${thirtyDaysAgo}
        GROUP BY DATE(created_at)
        ORDER BY date
      `,

      // Staff performance
      prisma.user.findMany({
        where: { role: 'STAFF' },
        select: {
          id: true,
          name: true,
          assignedIssues: {
            select: {
              id: true,
              status: true,
              createdAt: true,
              resolvedAt: true,
            },
            where: {
              createdAt: { gte: thirtyDaysAgo },
            },
          },
        },
      }),

      // Escalated issues
      prisma.issue.count({
        where: { status: 'ESCALATED' },
      }),

      // Overdue issues (open for more than 48 hours)
      prisma.issue.count({
        where: {
          status: { in: ['OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS'] },
          createdAt: {
            lt: new Date(Date.now() - 48 * 60 * 60 * 1000),
          },
        },
      }),
    ]);

    const adminStats = {
      dailyIssues: dailyIssues.map(d => ({
        date: d.date,
        count: Number(d.count),
      })),
      staffPerformance: staffPerformance.map(s => {
        const resolved = s.assignedIssues.filter(i => i.status === 'RESOLVED');
        const avgTime = resolved.length > 0
          ? resolved.reduce((acc, i) => {
              const time = i.resolvedAt 
                ? (i.resolvedAt.getTime() - i.createdAt.getTime()) / (1000 * 60 * 60)
                : 0;
              return acc + time;
            }, 0) / resolved.length
          : null;

        return {
          id: s.id,
          name: s.name,
          assigned: s.assignedIssues.length,
          resolved: resolved.length,
          avgResolutionHours: avgTime ? Math.round(avgTime) : null,
        };
      }),
      escalatedIssues,
      overdueIssues: overduIssues,
    };

    return reply.send(adminStats);
  });
}
