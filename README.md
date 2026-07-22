# CaptionAI: Deep Learning Image Caption Generator

CaptionAI is a full-stack, AI-powered web application that automatically generates highly accurate, context-aware descriptive captions for uploaded images. Built with a modern microservices architecture, it seamlessly bridges a responsive frontend with a high-performance backend, leveraging state-of-the-art Natural Language Processing (NLP) and Computer Vision models.

### 🌟 Key Features
*   **State-of-the-Art ML Inference:** Uses the advanced `Salesforce/blip-image-captioning-base` Vision-Language Transformer model (via Hugging Face and PyTorch) to generate incredibly accurate human-like descriptions of images.
*   **Asynchronous Processing:** Heavy machine learning tasks are offloaded to background workers using **Celery** and **Redis**, ensuring the web API remains blazing fast and responsive.
*   **Vector Database & Caching:** Utilizes **PostgreSQL** with the `pgvector` extension to store 768-dimensional image embeddings. Cryptographic file hashing and Redis caching are implemented to instantly return results for previously processed images, eliminating redundant ML computation.
*   **Beautiful UI/UX:** A sleek, modern, and fully responsive frontend built with **Next.js** and **Tailwind CSS**, featuring a smooth drag-and-drop upload interface and real-time polling for background job status.
*   **Robust Microservices Architecture:** The project is cleanly separated into a Frontend Client, a FastAPI Backend, an asynchronous Celery Worker Queue, and a dedicated FastAPI Machine Learning Inference service.

### 🛠️ Tech Stack
*   **Frontend:** React, Next.js, Tailwind CSS, TypeScript, Lucide Icons
*   **Backend API:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, pgvector
*   **Worker Queue:** Celery, Redis
*   **Machine Learning Service:** Python, FastAPI, PyTorch, Hugging Face Transformers (`blip-image-captioning-base`), Pillow (PIL)
