👋 Hi, I'm Mina Eskander

Backend, Asynchronous & High-Concurrency Systems Engineer.

I don't just use frameworks; I build the infrastructure that makes them possible.

Core Obsession: High-performance, Low-latency and Memory-safe networking and concurrency. I Specialised in High-Performance Rust systems, concurrent network engines, and Python/Rust hybrid architectures, utilizing async runtimes and Py03 to deliver memory-safe, high-performance, low-latency financial and networking solutions.

---

📬 Contact

Email: mina_eskander@outlook.com
GitHub: https://github.com/Mina777-0

---

🚀 Projects

---
1- [OmniBook: Low-Latency Order L2 Book & Ingestion Engine (Rust)](./OmniBook)

A high-performance market data ingestion engine designed for low-latency processing of real-time cryptocurrency exchange order books.

⭐ Features
📡 Asynchronous Market Data Ingestion — Streams live order book updates from Binance and Bybit using tokio-tungstenite over secure WebSocket connections.
⚡ Zero-Copy Binary Processing — Implements a custom C-compatible binary protocol with cache-aware memory alignment, leveraging bytemuck for zero-copy packet deserialization and allocation-free data processing.
🔄 Lock-Free Processing Pipeline — Separates network I/O from state management through bounded tokio::sync::mpsc channels, eliminating mutex contention while preserving deterministic packet ordering.
🛡 Predictable Concurrency & Backpressure — Uses bounded channels to propagate backpressure under high market volatility and integrates CancellationToken with JoinSet for deterministic, leak-free task lifecycle management.
📚 In-Memory Order Book Engine — Maintains live bid/ask state using optimized in-memory data structures, enabling ultra-fast order book updates and efficient market state tracking.
🚀 Performance-Oriented Design — Built with memory locality, cache efficiency, and predictable latency as primary design goals, making it suitable for latency-sensitive financial systems.


🧠 What It Shows
Systems programming with Rust
Zero-copy memory techniques
Lock-free concurrent architecture
High-performance network programming
Real-time market data processing
Low-latency systems design

---
2- High-Performance Risk Management Infrastructure 

An industrial-grade, multi-language risk engine designed for high-frequency trading environments. This system utilizes a decoupled architecture to ingest binary market data, manage risk state in Rust, and provide real-time updates via a throttled WebSocket dashboard.


🏗 System Architecture
The project implements a Producer-Consumer pattern to ensure maximum stability and zero data loss during market volatility.
* Ingestion Layer (Python): A secure TCP server receives custom binary packets and instantly pushes them into an asyncio.Queue.
* The Hot Path (Rust): Background workers pull packets from the queue and interface with a Rust-based Risk Engine. This ensures thread-safe, nanosecond-latency updates to the internal book state.
* The Reporting Layer (WebSockets): A throttled aiohttp server samples the Rust engine's state at 1Hz, delivering vectorized metrics to the dashboard without impacting the performance of the ingestion workers.



🚀 Key Features
* Binary Transport Layer: Uses Python struct and SSL/TLS sockets for memory-efficient, high-speed data ingestion.
* Binary Protocol: Custom packet framing (!BIdQq) using Python’s struct module for minimal network overhead.
* Zero-Copy Strategy: Implemented a custom Circular Buffer to handle packet framing and avoid memory fragmentation.
* Memory Safety: Risk state managed in Rust (via PyO3/Maturin), providing high-speed field validation and arithmetic.
* Backpressure Management: Utilizes asyncio.Queue to decouple data receipt from processing, preventing "lag spikes" during high-volume bursts.
* Vectorized Reporting: Leverages optimized data structures to calculate Total PnL and Exposure across the entire book in a single pass.
* Unified Async Architecture: Concurrent execution of the Secure Socket Server (Inbound) and an aiohttp WebSocket Server (Outbound) on a single event loop.
* Automated Accounting: Handles Realized/Unrealized PnL, Weighted Average Entry Price, and Net Exposure with "Counterparty Logic" (Client Buy = House Short).



🛠 Tech Stack
* Languages: Python 3.11+, Rust (Edition 2021)
* Interoperability: PyO3 / Maturin
* Math: NumPy (Vectorized Risk Processing)
* Data Transport: Secure TCP Sockets (TLS/SSL)
* Templating: Jinja2 (Dynamic Dashboard)


---

3- Zero‑Copy High‑Performance Network Engine

An ultra‑low‑latency packet processing engine designed for high‑throughput secure network communication.

⭐ Features:

* Zero‑Copy Packet Processing — Uses bytearray, memoryview, and recv_into() to read network data directly into preallocated buffers, avoiding unnecessary memory copies.
* TLS‑Secured Transport — Built on SSL sockets to ensure encrypted communication without sacrificing performance.
* Circular Buffer Architecture — Implements a custom circular buffer for efficient packet streaming and continuous memory reuse.
* Binary Packet Encoding — Uses struct and msgspec for fast binary serialization and deserialization of packets.
* Ultra‑Low Latency Performance — Achieves ~2.5µs processing time per packet across ~1M packets through optimized memory access patterns.
* GC‑Friendly Memory Strategy — Static buffer allocation and memoryview slicing minimize garbage collection pressure and maintain predictable performance.
* Direct Socket Buffer Reads — ssock.recv_into() allows packets to be written directly into the circular buffer, eliminating intermediate allocations.

🧠 What It Shows

* Low‑level performance optimization in Python
* Deep understanding of memory management and GC behavior
* Network protocol engineering and packet framing
* High‑throughput async/network system design
* Systems‑level thinking beyond typical web backends

---

4- Elastic Asynchronous RPC Engine

A high‑performance, secure RPC framework built directly on TCP using asyncio and TLS 1.3.

⭐ Features

* Async RPC over Raw TCP — Custom-built RPC engine operating directly on TCP streams, eliminating HTTP/REST overhead.
* Native TLS 1.3 Security — End‑to‑end encrypted transport using ssl.SSLContext with certificate‑based authentication and modern ciphers (AES‑256‑GCM).
* Binary Framing Protocol — Implements a 4‑byte Big‑Endian length‑prefix framing layer to safely reconstruct JSON‑RPC messages over a stream‑based protocol.
* Elastic Queue Management (Spillover Strategy) — Dynamic task lanes automatically expand under load, applying backpressure and protecting the server from resource exhaustion.
* Persistent Worker Pool — Long‑lived asyncio workers eliminate task‑spawning overhead, prevent memory leaks, and maintain a stable memory footprint.
* Decorator‑Based Service Routing — Business logic is registered via @service_router.service() decorators, fully decoupling services from network internals.
* Graceful Shutdown Handling — Coordinated teardown, draining in‑flight tasks and guaranteeing zero message loss.
* Built‑in Telemetry Services — Exposes internal health metrics over RPC, including memory usage, CPU load, and queue depth.


🧠 What It Shows

* Systems‑level programming in Python
* Deep understanding of TCP, framing, and backpressure
* Async concurrency design without high‑level frameworks
* Secure distributed systems engineering
* Resource‑predictable, production‑grade infrastructure design

---

5- Async Encrypted Message Broker

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

6- Secure Asynchronous Connection Pooling Infrastructure

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
7- Authentication API (FastAPI / JWT / Redis / RabbitMQ)

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

You can explore all repositories on my GitHub profile.
