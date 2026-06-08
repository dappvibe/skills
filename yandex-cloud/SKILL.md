---
name: yandex-cloud
description: Authoritative reference for working with Yandex Cloud services in this project — YDB local development, ydb-sdk QueryClient rules, Yandex Cloud Functions adapter pattern, and API Gateway configuration. Apply whenever touching YDB, Cloud Functions, or API Gateway code.
---

# Yandex Cloud Engineering Standards

## 1. YDB Local Development (Docker Compose)

### Port

Use port **2136** (non-TLS gRPC). Port 2135 is TLS-only — skip it for local dev and tests.  
Connection string always includes the database path: `grpc://localhost:2136/local`

### Required compose fields

```yaml
ydb:
  image: ydbplatform/local-ydb:latest
  hostname: localhost          # CRITICAL — see note below
  ports:
    - "2136:2136"
  environment:
    - YDB_USE_IN_MEMORY_PDISK=1      # integer 1, not string "true"
    - YDB_KAFKA_PROXY_PORT=0         # disables IPv6-only Kafka proxy
  healthcheck:
    test: ["CMD-SHELL", "/health_check"]
    interval: 5s
    timeout: 3s
    retries: 24
    start_period: 10s
```

**`hostname: localhost`** — YDB announces its own hostname in service discovery. Without this, the SDK resolves the container's random Docker hostname (e.g. `4ab48cd50763:2136`) which is unreachable from the host. Always set this.

**`YDB_KAFKA_PROXY_PORT=0`** — The Kafka proxy tries to bind an IPv6 socket. On hosts without IPv6, this crashes the YDB process at startup with `errno# 97 EAFNOSUPPORT`. Setting this to `0` disables the proxy entirely.

### Connecting from another container (bridge network isolation)

When a service in the same compose stack needs to connect to YDB without `network_mode: host`, the `hostname: localhost` trick breaks: YDB announces `localhost:2136` in service discovery, and the SDK then tries to reconnect to `localhost:2136` — the connecting container's own loopback, not YDB.

**Fix**: Set `YDB_ENDPOINT=grpc://ydb:2136` (without database path) in the connecting container's environment. The ydb-sdk `Endpoint.toString()` reads this env var and overrides all discovered endpoints, so all gRPC clients connect to `ydb:2136` (resolved via Docker DNS) instead of `localhost:2136`. Carry the database path separately as `YDB_DATABASE=/local` and concatenate in `loadConfig()`:

```yaml
# compose service that needs to talk to YDB
environment:
  - YDB_ENDPOINT=grpc://ydb:2136     # SDK override — must NOT include database path
  - YDB_DATABASE=/local               # concatenated by app to form connection string
  - YDB_ANONYMOUS_CREDENTIALS=1
```

**Why no database path in `YDB_ENDPOINT`**: `Endpoint.toString()` strips the `grpc://` scheme prefix and returns the remainder as a raw gRPC target. grpc-js's `splitHostPort` parses `ydb:2136` → `{host:'ydb', port:2136}` ✓, but `ydb:2136/local` → returns `null` (the `/local` suffix makes the port field non-numeric), causing name resolution failure.

**Host integration tests**: Never set `YDB_ENDPOINT` in the test process. With `YDB_ENDPOINT` absent, `Endpoint.toString()` falls through to the discovered `this.address:this.port` which is `localhost:2136` (the `hostname: localhost` announcement) — correct for tests connecting via the published port.

### Authentication

For local and test environments, set `YDB_ANONYMOUS_CREDENTIALS=1` before creating the driver. In test `before()` hooks:

```typescript
process.env['YDB_ANONYMOUS_CREDENTIALS'] = '1';
const driver = createDriver('grpc://localhost:2136/local');
await driver.ready(10_000);
```

Clean up in `after()`:
```typescript
delete process.env['YDB_ANONYMOUS_CREDENTIALS'];
await driver.destroy();
```

In production (Yandex Cloud Functions), the SDK picks up IAM/Metadata credentials automatically via `getCredentialsFromEnv()` — no code change needed between environments.

---

## 2. ydb-sdk QueryClient Rules

The project uses **QueryClient** (QueryService), not TableClient (TableService). These two APIs have different behaviours.

### DECLARE statements are mandatory

QueryClient does not infer parameter types from the schema. Every parameterized query must open with `DECLARE` statements:

```typescript
const result = await session.execute({
  text: `
    DECLARE $user_id AS Utf8;
    DECLARE $name AS Utf8;
    DECLARE $username AS Utf8?;
    SELECT user_id FROM users WHERE user_id = $user_id
  `,
  parameters: {
    '$user_id': TypedValues.utf8(id),
    '$name': TypedValues.utf8(name),
    '$username': TypedValues.optionalNull(Types.UTF8),
  },
});
```

### Column names come back as camelCase

QueryClient converts snake_case schema column names to camelCase in row data. This is silent — `row['user_id']` returns `undefined` with no error.

| Schema column     | Row key in code     |
|-------------------|---------------------|
| `user_id`         | `userId`            |
| `max_user_id`     | `maxUserId`         |
| `agreed_to_terms` | `agreedToTerms`     |
| `last_access`     | `lastAccess`        |
| `created_at`      | `createdAt`         |
| `chat_id`         | `chatId`            |
| `message_id`      | `messageId`         |

**The silent failure mode**: `row['user_id']` → `undefined` → `TypedValues.utf8(undefined)` → empty protobuf value (case 0) → YDB rejects with `Invalid value representation for type: Utf8, expected value case: 9, but current: 0`. If you see this error, check column name casing first.

### Always await `result.opFinished`

Call `await result.opFinished` after consuming all result sets. This releases the session back to the pool:

```typescript
for await (const rs of result.resultSets) {
  for await (const row of rs.rows) { /* ... */ }
}
await result.opFinished;
```

### Optional columns

Use `TypedValues.optionalNull(Types.UTF8)` for `null`, and `TypedValues.optional(TypedValues.utf8(value))` for non-null optional values. Never pass `undefined` to any `TypedValues` method.

---

## 3. Idempotent Schema Creation

`session.createTable` throws if the table already exists. Wrap each call to make `createSchema` safe to call multiple times (tests call it on every run):

```typescript
for (const [name, desc] of tables) {
  try {
    await session.createTable(name, desc);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    if (!msg.includes('ALREADY_EXISTS') && !msg.includes('already exists')) throw err;
  }
}
```

---

## 4. Yandex Cloud Functions Adapter

Cloud Functions receive an AWS-compatible v2.0 payload. Adapt it to a standard `Request` and delegate to the Hono app:

```typescript
export const handler = async (event: Record<string, unknown>): Promise<Record<string, unknown>> => {
  const method  = (event['httpMethod'] as string | undefined) ?? 'POST';
  const path    = (event['path'] as string | undefined) ?? '/';
  const headers = (event['headers'] as Record<string, string> | undefined) ?? {};
  const body    = (event['body'] as string | undefined) ?? '';

  const request = new Request(`https://localhost${path}`, {
    method,
    headers,
    body: method !== 'GET' && method !== 'HEAD' ? body : undefined,
  });

  const response = await app.fetch(request);
  return {
    statusCode: response.status,
    headers: Object.fromEntries(response.headers.entries()),
    body: await response.text(),
  };
};
```

Set `payload_format_version: "2.0"` in the API Gateway spec to match this format.

---

## 5. API Gateway (openapi.yml)

Route calls to a Cloud Function using the `x-yc-apigateway-integration` extension:

```yaml
paths:
  /webhook/max:
    post:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: ${FUNCTION_ID}
        payload_format_version: "2.0"
```

Always add throttling at the root level to prevent Denial-of-Wallet attacks:

```yaml
x-yc-apigateway:
  throttling:
    rps: 10
```

---

## 6. Structured Logging for Cloud Functions

Cloud Functions capture `stdout` as structured logs. Emit one JSON object per request. Use a Hono middleware that records the start time, calls `next()`, then writes after the handler returns:

```typescript
app.use('*', async (c, next) => {
  const start = Date.now();
  try {
    await next();
    process.stdout.write(JSON.stringify({
      level: 'INFO',
      message: `${c.req.method} ${c.req.path}`,
      status: c.res.status,
      duration_ms: Date.now() - start,
    }) + '\n');
  } catch (err) {
    process.stdout.write(JSON.stringify({
      level: 'ERROR',
      message: `${c.req.method} ${c.req.path}`,
      error: err instanceof Error ? err.message : String(err),
      duration_ms: Date.now() - start,
    }) + '\n');
    throw err;
  }
});
```
