<h1 align="center">
  <img src="https://github.com/Active-Matrix/proximity/blob/main/apps/web/public/images/Logo.png?raw=true" height="30"/> 
  Proximity
</h1>

<p align="center">
  <img src=".github/assets/images/proximity-mockup-1.png" alt="Proximity Mockup" width="100%" height="auto">
</p>

<p align="center">
  <img src="https://badgen.net/badge/license/MIT/white" alt="License"/>
  <img src="https://badgen.net/github/stars/Active-Matrix/proximity?color=white" alt="GitHub Stars"/>
  <img src="https://badgen.net/github/issues/Active-Matrix/proximity?color=white" alt="GitHub Issues"/>
  <img src="https://badgen.net/github/forks/Active-Matrix/proximity?color=white" alt="GitHub Forks"/>
</p>

---

## 🚀 About Proximity

**Proximity** is an AI-powered news indexer, scraper, and TL;DR generator designed for fast, efficient, and clutter-free news consumption. By combining real-time web scraping with AI-driven summarization, Proximity delivers concise news updates tailored to your preferences.

---

## 🔥 Key Features

- **Automated News Scraping** → Event-driven system fetching news from trusted sources
- **AI-Powered Summarization** → LLama 3.2 1B Instruct model generates concise summaries
- **Real-time Updates** → Event-driven architecture ensures instant news delivery
- **Modern Web Interface** → Built with Next.js for a smooth and responsive experience
- **Personalized Feeds** → News recommendations based on user interests
- **Scalable Architecture** → Kubernetes-based infrastructure for seamless scaling

---

## 🏗 Architecture Overview

### 📌 Core Services

| Service                                                                                                        | Description                                           |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **🖥 [Web App](https://github.com/Active-Matrix/proximity/tree/main/apps/web)**                                | Next.js frontend with an intuitive UI                 |
| **🕷 [Crawler Service](https://github.com/Active-Matrix/proximity/tree/main/services/crawler)**                | Cheerio-based lightweight web crawler                 |
| **🔍 [Scraper Service](https://github.com/Active-Matrix/proximity/tree/main/services/scraper)**                | Puppeteer/Cheerio-powered message-driven scraper      |
| **🧠 [Summarization Service](https://github.com/Active-Matrix/proximity/tree/main/services/summarization)**                     | AI-powered summarization engine                       |
| **🎯 [Recommendation Service](https://github.com/Active-Matrix/proximity/tree/main/services/recommendations)** | Personalized news recommendations                     |
| **🔐 [Auth Service](https://github.com/Active-Matrix/proximity/tree/main/infra/k8s/ory-kratos)**               | Ory Hydra + Kratos for authentication & authorization |
| **📖 Search Service [TODO]**                                                                                   | Full-text search powered by Elasticsearch             |
| **📢 Notification Service [TODO]**                                                                             | Event-driven notifications and alerts                 |

---

## 🛠 Technology Stack

| Component          | Technologies Used                            |
| ------------------ | -------------------------------------------- |
| **Frontend**       | Next.js, TypeScript, Tailwind CSS, Shadcn UI |
| **Backend**        | Node.js, Python, FastAPI, Fastify            |
| **AI/ML**          | LLama 3.2 1B Instruct                        |
| **Message Queue**  | RabbitMQ                                     |
| **Databases**      | MongoDB, PostgreSQL, Redis                   |
| **Search**         | Elasticsearch                                |
| **Infrastructure** | Kubernetes, GCP, Docker, Terraform           |
| **CI/CD**          | GitHub Actions                               |
| **Monitoring**     | Prometheus, Grafana                          |

---

## 🔧 Getting Started

Set up Proximity on your local machine by following the [Getting Started Guide](https://github.com/Active-Matrix/proximity/blob/main/docs/getting-started.md).

---

## 📜 Contributing

We welcome contributions! Check out our [Contributor’s Guide](https://github.com/Active-Matrix/proximity/blob/main/CONTRIBUTING.md) to get started.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Active-Matrix/proximity/blob/main/LICENSE) file for details.

---

## ⭐ Support & Feedback

If you find Proximity useful, give us a ⭐ on GitHub!  
For feedback, feature requests, or issues, open an issue [here](https://github.com/Active-Matrix/proximity/issues).
