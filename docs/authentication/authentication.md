---
name: Authentication
description: Gate documentation pages with Clerk — as a standalone site, or as one satellite in a network of documentation sites
endpoint: /authentication
package: authentication
icon: mdi:shield-account-outline
tier: public
---

.. llms_copy::Authentication

.. toc::

### Start here: you probably don't need this

Authentication in this template is **entirely optional and off by default**.
With no `CLERK_*` keys in the environment — which is how a fresh clone runs —
nothing on this page is active. No script injection, no session machinery, no
routes, no per-request checks. Every page is public, exactly as it would be if
this page did not exist.

That is deliberate, and it is the first design rule worth stating: **a
documentation site must never break because a deploy forgot a credential.**
Everything below fails in that direction.

Read the layer you need and stop:

| You want | Read |
|---|---|
| Public documentation, no accounts | Nothing. You're done. |
| One site, some pages behind a login | **Layer 1** |
| Several documentation sites sharing one account system | **Layer 2** |

---

### The distinction the whole design follows from

Two different questions get asked of a documentation site, and only one of them
arrives with a session attached:

| | Question | Answered by | Asked by |
|---|---|---|---|
| 1 | Who is this human? | A session cookie | A person in a browser |
| 2 | May this fetch of a text file proceed? | A key in the URL | An agent, later, elsewhere |

**A cookie can never answer question 2.** When someone signs in, copies
`https://yoursite.dev/guide/llms.txt`, and pastes it into an assistant, the
assistant fetches that URL with **no cookie**. A cookie-only gate therefore
returns the gate document to the one consumer the URL exists for, and your site
looks broken to exactly the audience `llms.txt` was built for.

So authority has to be able to travel *in the URL*:

```
https://yoursite.dev/guide/llms.txt?key=k2p_8f31…
```

Layer 1 needs only question 1. Layer 2 needs both.

---

### Layer 1 — one site, your own Clerk

The simplest useful setup: your docs, your Clerk application, some pages
requiring a login.

#### 1. Install the auth package

`dash-clerk-auth` is not on PyPI. Vendor the wheel and install it:

```bash
pip install ./vendor/dash_clerk_auth-0.9.1.tar.gz
```

It stays out of the active `requirements.txt` on purpose — a default install
should not pull in an auth stack the site does not use.

#### 2. Set the keys

```env
CLERK_SECRET_KEY=sk_test_...        # backend SDK key, never sent to the client
CLERK_PUBLISHABLE_KEY=pk_test_...   # embedded in the injected <script>
CLERK_SIGN_IN_URL=https://your-app.accounts.dev/sign-in
SESSION_SECRET=<a long random string>
```

All three `CLERK_*` values must be present. `lib/auth.py`'s `clerk_enabled()`
is the single source of truth, and it is all-or-nothing by design — a
half-configured auth stack is worse than none, because it looks enabled.

`SESSION_SECRET` is not optional in production. Without it `dash-clerk-auth`
falls back to a **public development default**, and the app warns loudly at
startup.

#### 3. Mark a page

Tiers live in the page's markdown frontmatter:

```markdown
---
name: Internal Runbook
description: How we deploy
endpoint: /runbook
tier: admin
---
```

Four tiers, least to most restrictive:

| Tier | Who may read | The document | Listed in sitemap and index? |
|---|---|---|---|
| `public` | anyone, including agents and crawlers | prose, 200 | yes |
| `auth` | any signed-in user | gate document, **200** | **yes** |
| `admin` | signed in *and* allowlisted | gate document, 200 | yes |
| `hidden` | nobody | **404** | no |

`auth` and `hidden` are genuinely different intents, and the difference is what
makes a sign-up funnel work:

- **`auth` / `admin` → gated.** "This document exists and you may not read it
  yet." The URL stays in the sitemap and the index, because a page's existence
  is public knowledge even when its content is not. An agent that fetches it
  learns what the page is and how its user gets access.
- **`hidden` → denied.** "There is nothing here." Same 404 as a page that never
  existed, delisted everywhere. Use it where advertising the URL is itself a
  disclosure.

Absent frontmatter, a page is `public`. Change the default for a whole site
with `PAGE_DEFAULT_TIER`.

#### 4. Who counts as an admin

```env
ADMIN_EMAILS=you@example.com,colleague@example.com
ADMIN_USER_IDS=user_2abc...
OWNER_EMAIL=you@example.com
```

The owner's email always counts, so a deploy that set the Clerk keys but forgot
`ADMIN_EMAILS` still lets you in.

#### 5. Local development

```env
DISABLE_CLERK=1
```

Reads as "intentionally off" without touching the `CLERK_*` values. This exists
because a shell env prefix does not survive an IDE run configuration, and
half-disabling auth by deleting one key produces confusing failures.

---

### Layer 2 — a network of documentation sites

This is what `*.2plot.dev` runs. One Clerk application serves a **primary**
domain and any number of **satellite** domains, so the same person is
recognised across every site without signing in twice.

```
2plot.ai            Clerk primary — hosts sign-in, owns the accounts
2plot.dev           satellite + network hub — mints and verifies keys
leaflet.2plot.dev   satellite
flows.2plot.dev     satellite
…                   every component documentation site
```

#### Satellite configuration

```env
CLERK_IS_SATELLITE=true
CLERK_SATELLITE_DOMAIN=flows.2plot.dev   # host only, no scheme
CLERK_FRONTEND_API=https://<app>.clerk.accounts.dev
CLERK_SIGN_IN_URL=https://2plot.ai/sign-in
CLERK_SIGN_UP_URL=https://2plot.ai/sign-up
```

`CLERK_SATELLITE_DOMAIN` defaults to the host in `APP_BASE_URL`, which every
deployment must set anyway — so in practice you set one variable and the
satellite domain follows. That is deliberate: it removes a way to announce
another site's domain to Clerk.

`CLERK_FRONTEND_API` is **required** in satellite mode. A production
custom-domain instance cannot derive it from `CLERK_SIGN_IN_URL`.

Leave satellite mode off locally — Clerk rejects satellites on `localhost`. A
`pk_test` key stays primary; a `pk_live` key with a satellite domain
auto-enables satellite mode even if `CLERK_IS_SATELLITE` was missed, so
production cannot silently boot in the wrong one.

Each subdomain must also be added to the **allowed-subdomains list in the Clerk
dashboard** before it will work.

#### The ordering that matters

`lib/access.py` resolves in this order, and the order is the design:

```
tier  ->  short-circuit public / hidden
      ->  local Clerk session          (a person in a browser)
      ->  hub verification of ?key=    (an agent, later, elsewhere)
```

**Local session first, hub only as a fallback.** A signed-in visitor is
resolved entirely on their own satellite, so the hub being down gates nothing
for them. Only the agent path — no cookie, key in the URL — needs the hub.

Reversing this couples every satellite's availability to one host for no
benefit: the fail-safe is `gated`, so a hub outage would silently gate every
restricted document on every subdomain at once. It is the single most
consequential ordering in this template.

#### Where key material lives, and why not here

A satellite holds **no key material at all**. It cannot mint keys and it cannot
verify them offline; it asks the hub.

The tempting alternative is to share the hub's signing secret so every
satellite can verify locally with no round trip. Reject it: the key is derived
by HMAC over the user, session and scope, so **anything that can verify can
also mint** — including an admin-scoped key. Sharing it puts a network-wide
admin-minting secret on twenty deployments, where one compromised satellite is
a full compromise, and rotation means redeploying all of them at once.

What a satellite *does* hold is `CROSS_APP_WEBHOOK_SECRET` — the same shared
secret the traffic reporter already uses — which authenticates *who is asking*.
It signs the request; it derives nothing. A verify endpoint open to the
internet would be a key-guessing oracle, which is why the caller is
authenticated as well as the key.

#### The hub sets the ceiling

Once the hub publishes tiers, two writers exist over one value. The rule:

```
effective_tier = more_restrictive_of(hub_tier, local_tier)
```

A satellite may lock its own page down further. It may **never** loosen what
the hub restricted. So a satellite misconfiguration cannot expose something the
network gated, and "loosen this page" stays a hub action — which is where that
authority belongs.

#### Keep the network catalogue public

The hub's `/llms.txt` is the map of what exists. **Gate individual documents,
not the map.** An agent that follows a satellite's "Network index" link and
arrives with no key should get exactly what it asked for: a list of what the
network contains.

This is also why the package never appends a key to a cross-host link. A
capability should not travel to another origin, and with a public catalogue it
does not need to.

---

### Two traps worth naming

**Do not wire the Clerk token's `iat` as "signed in since".** The session token
is refreshed roughly every 60 seconds, so `iat` is the age of the *token*, not
of the sign-in. Wiring it renders a clock that resets every minute. `lib/auth.py`
keeps a session-first-seen timestamp keyed on `ClerkUser.session_id` instead.

**Never put the visitor's identity in the network bulletin.** The bulletin is
TTL-cached and shared by every viewer of every satellite. A username in it is a
privacy bug wearing a cache. Identity is per-request and local — that is what
`configure_viewer_identity()` is for, and it renders in the HTML viewer only,
so the Markdown an agent receives is byte-identical either way.

---

### What the reader actually sees

| Reader | `auth` page | Its `llms.txt` |
|---|---|---|
| Anonymous browser | gate document | gate document, 200 |
| Signed-in browser | full prose | full prose, plus their name in the viewer banner |
| Agent, no key | gate document, 200 | gate document explaining how to get access |
| Agent with a valid key | full prose | full prose, and generated links carry the key onward |
| Any reader, `hidden` page | 404 | 404 |

The gate document is deliberately useful rather than a wall: it names the page,
says what would unlock it, and points at where to sign in. An agent that
fetches a gated document should come away knowing what it is and how its user
gets access — that is the difference between a gate and a dead end.

---

### Verifying

The checks that justify this design over the simpler ones, all automated in
`tests/test_access.py`:

```
1. Signed-in browser, hub UNREACHABLE  -> still allowed   (local resolution)
2. Agent with valid key, hub reachable -> allowed
3. Agent with valid key, hub down      -> gated, not 500, not prose
4. Satellite sets public, hub says auth -> effective auth  (ceiling holds)
5. Key never appears in sitemap.xml, canonical tags, or cross-host links
6. Identity renders in the HTML viewer only; Markdown byte-identical
7. No tiers declared -> byte-identical to a build with no access control
```

Checks 1 and 3 are the point. Check 7 is what lets a fork inherit all of this
without inheriting a gate it did not ask for.

.. source::lib/access.py
