import { prisma } from '../lib/prisma.js';
import { IssueStatus, Prisma } from '@prisma/client';

const ESCALATION_THRESHOLD_HOURS = 48;

export async function runEscalationJob() {
  console.log('Running escalation job...');
  
  const thresholdDate = new Date();
  thresholdDate.setHours(thresholdDate.getHours() - ESCALATION_THRESHOLD_HOURS);

  try {
    // Find issues that need escalation
    const issuesToEscalate = await prisma.issue.findMany({
      where: {
        status: {
          in: [IssueStatus.OPEN, IssueStatus.ACKNOWLEDGED, IssueStatus.IN_PROGRESS]
        },
        createdAt: {
          lt: thresholdDate
        },
        escalatedAt: null
      }
    });

    if (issuesToEscalate.length === 0) {
      console.log('No issues to escalate.');
      return;
    }

    console.log(`Found ${issuesToEscalate.length} issues to escalate.`);

    // Get system admin user for logging
    const systemUser = await prisma.user.findUnique({
      where: { email: 'sarpanch@gramseva.in' }
    });

    if (!systemUser) {
      console.error('System admin user not found. Cannot log escalation activity.');
      return;
    }

    for (const issue of issuesToEscalate) {
      await prisma.$transaction(async (tx: Prisma.TransactionClient) => {
        // Update issue status
        await tx.issue.update({
          where: { id: issue.id },
          data: {
            status: IssueStatus.ESCALATED,
            escalatedAt: new Date(),
            escalationLevel: { increment: 1 }
          }
        });

        // Log activity
        await tx.activityLog.create({
          data: {
            action: 'ISSUE_ESCALATED',
            issueId: issue.id,
            userId: systemUser.id,
            details: { reason: `Auto-escalated after ${ESCALATION_THRESHOLD_HOURS} hours of inactivity` },
          }
        });
      });
      
      console.log(`Escalated issue ${issue.id}`);
    }
  } catch (error) {
    console.error('Error running escalation job:', error);
  }
}

export function startEscalationScheduler(intervalMinutes = 60) {
  // Run immediately on startup
  runEscalationJob();

  // Schedule
  setInterval(runEscalationJob, intervalMinutes * 60 * 1000);
  console.log(`Escalation scheduler started (interval: ${intervalMinutes}m)`);
}
