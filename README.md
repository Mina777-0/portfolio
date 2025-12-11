👋 Hi, I'm Mina Eskander

Backend Developer — Python / FastAPI / Async / Distributed Systems

I build scalable backend systems with focus on authentication, messaging, secure communication, and high‑performance async architectures. My work spans APIs, distributed systems, networking, and building tools from the ground up.

I enjoy understanding what happens under the hood — from encryption and sockets, to processes, schedulers, and message queues.

---

📬 Contact

Email: mina_eskander@outlook.com
GitHub: https://github.com/Mina777-0

---

🚀 Portfolio Projects

Below are my key backend engineering projects. Each project demonstrates real-world production concepts including async programming, cryptography, message brokers, Redis, JWT auth, scheduling, and distributed architecture.

---

1️⃣ Authentication API (FastAPI / JWT / Redis / RabbitMQ)

A complete authentication system designed for scalable microservices.

⭐ Features

* JWT authentication (access + refresh tokens)
* Email verification using Redis token storage
* RabbitMQ-powered email sending pipeline
* OTP generation and verification
* Scheduled tasks using processes / APScheduler
* Login rate limiting
* Password hashing and security best practices
* Fully async FastAPI implementation

🏛 Architecture Overview

* Auth service handles JWT + identity
* Redis stores ephemeral tokens (email verification / OTP)
* RabbitMQ triggers async email workers
* Scheduler handles periodic tasks

📦 Tech Stack

FastAPI, Redis, RabbitMQ, SQLAlchemy (async), JWT, APScheduler, Docker

---

2️⃣ Async Encrypted Message Broker

A custom-built encrypted messaging system using asynchronous networking, cryptography, and a lightweight service bus.

⭐ Features

* Fully asynchronous server and client
* End‑to‑end encrypted messaging
* Supports certificates, RSA, HMAC, JWK
* Custom binary-message middleware (routing + validation)
* Pure-bytes encoding/decoding using big/little-endian formats
* Message scheduling and delayed delivery inside the service bus
* Routing system for message types and destinations
* Custom message protocol and secure channels
* Connection management and multi-client support
* Low-level networking (no frameworks)

🧠 Why It Matters

This project demonstrates strong understanding of:

* async I/O internals
* service bus architecture
* binary protocol design
* secure communication
* encryption primitives
* socket-level networking
* routing and message dispatch systems
* secure communication design
* cryptographic primitives
* socket programming
* client/server architecture

---

3️⃣ Secure Asynchronous Connection Pooling Infrastructure

A high-performance async client–server communication layer with SSL/TLS and robust connection lifecycle management.

⭐ Features

* SSL/TLS Encrypted Communication — All client–server traffic is protected using certificates (cert1.pem + key1.pem) for secure and private data exchange.
* Fully Asynchronous I/O — Built entirely on asyncio, enabling high concurrency and non-blocking operations without threading overhead.
* Efficient Connection Pooling — A fixed-size pool of persistent encrypted connections reduces creation overhead, increases throughput, and stabilizes performance under load.
* Borrow/Return Session Manager — Connections are managed via an asynccontextmanager ensuring safe checkout and guaranteed return, preventing leaks even during exceptions.
* Concurrency-Safe Pool State — Uses asyncio.Lock and asyncio.Event to maintain consistency when multiple coroutines borrow connections or the recycler updates the pool.
* Automatic Connection Recycling — A background task periodically closes and recreates connections (based on pool_recycle) to avoid stale connections and ensure long-running stability.

🧠 What It Shows

* Infrastructure-level engineering
* Async concurrency patterns (locks, events, context managers)
* Secure client/server architecture
* Resource lifecycle management and fault tolerance
* Deep understanding of low-level network systems



---

# 🛠 Additional Tools & Skills

These tools often support my main projects:

* JWT internals** (signing, encoding, decoding)
* OTP systems (time-based tokens, email OTP flows)
* Cryptography: certificates, JWK, HMAC, RSA, signatures
* Schedulers: APScheduler, multiprocessing timers
* Distributed systems: Redis, RabbitMQ
* Async architecture: asyncio, event loops, concurrency models
* Processes and Threads: pool management, concurrency patterns

---

📚 What I’m Learning & Improving

* Deeper distributed systems patterns
* Message queues (advanced RabbitMQ patterns)
* Performance tuning and profiling
* Secure token strategies (per-user key pairs)

---

You can explore all repositories on my GitHub profile.

---

If you'd like a clean GitHub landing page or additional documentation for each project, I can help refine this further.
