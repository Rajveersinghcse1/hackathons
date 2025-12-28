import { PrismaClient, Role, Category, Priority, IssueStatus } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create admin user
  const adminPassword = await bcrypt.hash('admin123', 12);
  const admin = await prisma.user.upsert({
    where: { email: 'sarpanch@gramseva.in' },
    update: {},
    create: {
      email: 'sarpanch@gramseva.in',
      passwordHash: adminPassword,
      name: 'Sarpanch Ji',
      role: Role.ADMIN,
      department: 'Panchayat',
    },
  });
  console.log('✅ Created admin user:', admin.email);

  // Create staff users
  const staffPassword = await bcrypt.hash('staff123', 12);
  const staff1 = await prisma.user.upsert({
    where: { email: 'engineer1@gramseva.in' },
    update: {},
    create: {
      email: 'engineer1@gramseva.in',
      passwordHash: staffPassword,
      name: 'Ramesh Kumar',
      role: Role.STAFF,
      department: 'Public Works',
    },
  });

  const staff2 = await prisma.user.upsert({
    where: { email: 'health1@gramseva.in' },
    update: {},
    create: {
      email: 'health1@gramseva.in',
      passwordHash: staffPassword,
      name: 'Dr. Suresh',
      role: Role.STAFF,
      department: 'Health',
    },
  });
  console.log('✅ Created staff users');

  // Create student users (Villagers)
  const villagerPassword = await bcrypt.hash('villager123', 12);
  const villagers = [];
  const villagerData = [
    { email: 'ramu@gramseva.in', name: 'Ramu Kaka', department: 'Farmer' },
    { email: 'sita@gramseva.in', name: 'Sita Devi', department: 'Teacher' },
    { email: 'mohan@gramseva.in', name: 'Mohan Lal', department: 'Shopkeeper' },
  ];

  for (const data of villagerData) {
    const villager = await prisma.user.upsert({
      where: { email: data.email },
      update: {},
      create: {
        email: data.email,
        passwordHash: villagerPassword,
        name: data.name,
        role: Role.CITIZEN, // Villager role
        department: data.department,
      },
    });
    villagers.push(villager);
  }
  console.log('✅ Created villager users');

  // Create buildings (Rural Locations)
  const locations = [
    { name: 'Panchayat Bhawan', code: 'PANCHAYAT', latitude: 13.0305, longitude: 77.5659, floors: 1 },
    { name: 'Primary School', code: 'SCHOOL', latitude: 13.0302, longitude: 77.5655, floors: 1 },
    { name: 'Health Center', code: 'PHC', latitude: 13.0308, longitude: 77.5662, floors: 1 },
    { name: 'Market Area', code: 'MARKET', latitude: 13.0300, longitude: 77.5658, floors: 0 },
    { name: 'Water Tank', code: 'TANK', latitude: 13.0304, longitude: 77.5651, floors: 2 },
    { name: 'Community Hall', code: 'HALL', latitude: 13.0306, longitude: 77.5660, floors: 1 },
  ];

  for (const loc of locations) {
    await prisma.building.upsert({
      where: { code: loc.code },
      update: {},
      create: loc,
    });
  }
  console.log('✅ Created rural locations');

  // Create sample issues
  const issues = [
    {
      title: 'Broken Handpump',
      description: 'The main handpump near the market is not working since 2 days.',
      category: Category.WATER,
      priority: Priority.HIGH,
      status: IssueStatus.OPEN,
      locationDescription: 'Market Area',
      latitude: 13.0300,
      longitude: 77.5658,
      reporterId: villagers[0].id,
      photoUrl: 'https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?q=80&w=1000&auto=format&fit=crop',
    },
    {
      title: 'Pothole on Main Road',
      description: 'Large pothole causing accidents near the school entrance.',
      category: Category.ROADS,
      priority: Priority.CRITICAL,
      status: IssueStatus.IN_PROGRESS,
      locationDescription: 'Primary School Road',
      latitude: 13.0302,
      longitude: 77.5655,
      reporterId: villagers[1].id,
      photoUrl: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?q=80&w=1000&auto=format&fit=crop',
    },
    {
      title: 'Streetlight Flickering',
      description: 'Streetlight No. 45 is flickering and needs bulb replacement.',
      category: Category.ELECTRICITY,
      priority: Priority.MEDIUM,
      status: IssueStatus.RESOLVED,
      locationDescription: 'Near Panchayat Bhawan',
      latitude: 13.0305,
      longitude: 77.5659,
      reporterId: villagers[2].id,
      photoUrl: 'https://images.unsplash.com/photo-1563298723-dcfebaa392e3?q=80&w=1000&auto=format&fit=crop',
    },
  ];

  for (const issue of issues) {
    await prisma.issue.create({
      data: issue,
    });
  }
  console.log('✅ Created sample issues');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
