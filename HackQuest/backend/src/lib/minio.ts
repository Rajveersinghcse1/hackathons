import * as Minio from 'minio';
import { config } from '../config/index.js';

export const minioClient = new Minio.Client({
  endPoint: config.minio.endpoint,
  port: config.minio.port,
  useSSL: config.minio.useSSL,
  accessKey: config.minio.accessKey,
  secretKey: config.minio.secretKey,
});

export const uploadFile = async (
  file: Buffer,
  fileName: string,
  contentType: string
): Promise<string> => {
  const bucket = config.minio.bucket;

  // Ensure bucket exists
  const bucketExists = await minioClient.bucketExists(bucket);
  if (!bucketExists) {
    await minioClient.makeBucket(bucket);
  }

  // Upload file
  await minioClient.putObject(bucket, fileName, file, file.length, {
    'Content-Type': contentType,
  });

  // Return public URL
  const protocol = config.minio.useSSL ? 'https' : 'http';
  return `${protocol}://${config.minio.endpoint}:${config.minio.port}/${bucket}/${fileName}`;
};

export const deleteFile = async (fileName: string): Promise<void> => {
  await minioClient.removeObject(config.minio.bucket, fileName);
};
