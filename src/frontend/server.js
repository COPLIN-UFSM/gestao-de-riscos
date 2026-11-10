import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { extname, resolve, sep } from 'node:path';

const distPath = resolve('dist');
const contentTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon',
  '.jpeg': 'image/jpeg',
  '.jpg': 'image/jpeg',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
};

const server = createServer(async (request, response) => {
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    response.writeHead(405, { Allow: 'GET, HEAD' }).end();
    return;
  }

  let pathname;
  try {
    pathname = decodeURIComponent(new URL(request.url ?? '/', 'http://localhost').pathname);
  } catch {
    response.writeHead(400).end();
    return;
  }

  let filePath = resolve(distPath, `.${pathname}`);
  if (filePath !== distPath && !filePath.startsWith(`${distPath}${sep}`)) {
    response.writeHead(403).end();
    return;
  }

  let fileInfo;
  try {
    fileInfo = await stat(filePath);
    if (fileInfo.isDirectory()) {
      filePath = resolve(filePath, 'index.html');
      fileInfo = await stat(filePath);
    }
  } catch (error) {
    if (error.code !== 'ENOENT') {
      console.error(error);
      response.writeHead(500).end();
      return;
    }

    if (extname(pathname)) {
      response.writeHead(404).end();
      return;
    }

    filePath = resolve(distPath, 'index.html');
    try {
      fileInfo = await stat(filePath);
    } catch (fallbackError) {
      console.error(fallbackError);
      response.writeHead(500).end();
      return;
    }
  }

  if (!fileInfo.isFile()) {
    response.writeHead(404).end();
    return;
  }

  const isAsset = filePath.startsWith(`${resolve(distPath, 'assets')}${sep}`);
  response.writeHead(200, {
    'Cache-Control': isAsset ? 'public, max-age=31536000, immutable' : 'no-cache',
    'Content-Length': fileInfo.size,
    'Content-Type': contentTypes[extname(filePath).toLowerCase()] ?? 'application/octet-stream',
    'X-Content-Type-Options': 'nosniff',
  });

  if (request.method === 'HEAD') {
    response.end();
    return;
  }

  const stream = createReadStream(filePath);
  stream.on('error', (error) => {
    console.error(error);
    if (response.headersSent) {
      response.destroy(error);
    } else {
      response.writeHead(500).end();
    }
  });
  stream.pipe(response);
});

server.listen(3000, '0.0.0.0');
