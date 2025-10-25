import { logger } from "./libs/logger";
import { SummerizerService } from "./summerize";

import dontenv from 'dotenv';
dontenv.config();

(async () => {
  try {
    logger.info("Booting up summarization service...")
    const summarizerService = new SummerizerService();
    summarizerService.summerize();
    logger.info("Summarization complete")
  }
  catch (error) {
    logger.error(error)
  }
})()
