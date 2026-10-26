# VeritasAI Security Architecture & Guardrails

## 1. Threat Model & Untrusted Inputs
In an investigative news verification platform, all inputs—URLs, user text, uploaded images, and external web content—must be treated as untrusted and potentially adversarial.

Threat vectors addressed:
1. **Server-Side Request Forgery (SSRF)**: Malicious URLs pointing to internal infrastructure, cloud metadata endpoints, or local ports.
2. **Decompression Bombs & Image Exploits**: Corrupted or giant image payloads designed to cause denial of service.
3. **Prompt Injection**: Malicious instructions embedded in news articles attempting to hijack LLM behavior.
4. **Credential Leakage**: Accidental exposure of API secrets in logs, client bundles, or error traces.

---

## 2. Implemented Defense Mechanisms

### 2.1 SSRF Protection (`backend/app/core/security.py`)
- **Protocol Enforce**: Only `http://` and `https://` schemes are accepted. Protocols such as `file://`, `ftp://`, and `gopher://` are rejected at the parsing boundary.
- **DNS IP Range Validation**: Before opening a network connection to any user-submitted URL:
  1. The hostname is extracted and resolved using `socket.getaddrinfo()`.
  2. Each resolved IP is verified against `ipaddress.ip_network` exclusions:
     - `127.0.0.0/8` (Loopback)
     - `10.0.0.0/8` (Private RFC 1918)
     - `172.16.0.0/12` (Private RFC 1918)
     - `192.168.0.0/16` (Private RFC 1918)
     - `169.254.0.0/16` (Link-local / Cloud Metadata)
     - `0.0.0.0/8` (Current network)
     - `224.0.0.0/4` (Multicast)
     - `::1/128` (IPv6 Loopback)
     - `fc00::/7` (IPv6 Unique Local)
     - `fe80::/10` (IPv6 Link-Local)
- **Redirect Traversal Protection**: If an HTTP redirect occurs, the destination URL is re-validated through the SSRF filter before being followed.

### 2.2 Image File Security
- **MIME & Format Whitelist**: Only JPEG, PNG, and WEBP formats are accepted.
- **Size Limit**: Maximum upload size is strictly capped at 5 MB.
- **Decompression Bomb Protection**: Maximum image dimensions are bounded to $6000 \times 6000$ pixels.
- **Integrity Verification**: `PIL.Image.verify()` is invoked before memory decompression to detect malformed byte streams.

### 2.3 Prompt Injection Defense
- Articles retrieved from the internet are strictly encapsulated as quoted, untrusted evidence text within structured extraction prompts.
- Output formats are constrained by strict JSON schema definitions validated via Pydantic. Malformed outputs are rejected.

### 2.4 Error Sanitization & Credential Protection
- A global exception handler catches unhandled exceptions and returns generic structured error responses (`500 Internal Server Error`). Internal stack traces and file paths are never exposed to the frontend.
- API keys are read via environment variables or `.env` files; the `/api/providers/status` endpoint exposes only safe boolean indicators (`configured: true/false`).
