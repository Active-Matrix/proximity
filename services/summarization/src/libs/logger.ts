import pino from "pino";
import dotenv from "dotenv";

dotenv.config({ path: '../../.env' });

const env = process.env.NODE_ENV || 'development';

const transport = pino.transport({
  target: 'pino-pretty',
  options: {
    colorize: true,
    translateTime: 'SYS:standard',
    ignore: 'pid,hostname',
  }
});

export const logger = pino({
  level: env === 'development' ? 'debug' : 'info',
  base: {
    service: 'summarizer-service',
  },
  redact: {
    paths: ['*.password', '*.secret', '*.key'],
    remove: true,
  },
  formatters: {
    level: (label) => {
      return { level: label.toUpperCase() };
    },
  },
  timestamp: () => `,"time":"${new Date(Date.now()).toISOString()}"`,
}, transport)
