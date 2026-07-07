# Connector configuration reference

This gateway (`.env` in the project root) only needs **three** variables — see
`.env.example`. But it talks to a much bigger piece of infrastructure: your own
True Connector / ECC docker-compose stack (DAPS, ECC provider/consumer,
MongoDB, Orion-LD, notarization, etc). This doc maps that stack's `.env`
variables to whether you must customize them per deployment, or can leave the
shared defaults as-is.

## How this gateway's `.env` relates to the connector's `.env`

| Gateway variable | Where it comes from in the connector stack |
|---|---|
| `DATASPACE_ENPOWER_BASE_URL` | Same host as the connector's `API_URL`, **without** the trailing `/api` (the gateway appends its own `/api/...` paths) |
| `DATASPACE_CONNECTOR_BASE_URL` | Wherever the ECC's Local API is exposed. Not explicitly named as its own variable in the connector `.env` below — by default this gateway assumes it's reachable at the **provider ECC's** public endpoint (`PROVIDER_PORT`, fronted by whatever reverse proxy/nginx config you deployed). Confirm the actual exposed host:port from your `docker-compose.yml`/nginx config once you're ready to point at a real instance. |
| `DATASPACE_REQUEST_TIMEOUT` | No connector equivalent; purely a gateway-side HTTP client setting |

## Connector `.env` — must customize per deployment

These are unique to your company/instance. Using the sample/default values
either breaks interoperability (two connectors can't share the same identity)
or leaves known-insecure secrets in place.

| Variable | Why it must change |
|---|---|
| `PROVIDER_ISSUER_CONNECTOR_URI` | Must be **your own** connector's unique IDS identifier, not ENG's example URI |
| `CONSUMER_ISSUER_CONNECTOR_URI` | Same — must be unique to your connector |
| `PROVIDER_DAPS_KEYSTORE_NAME` / `CONSUMER_DAPS_KEYSTORE_NAME` | `smart-energy.eng.it.p12` is ENG's sample identity keystore — you need your own DAPS-issued keystore |
| `PROVIDER_DAPS_KEYSTORE_PASSWORD` / `CONSUMER_DAPS_KEYSTORE_PASSWORD` | Default `password` — must match whatever password protects your own keystore |
| `KEY_PASSWORD`, `KEYSTORE_PASSWORD` | Default `changeit` — rotate for anything beyond local testing |
| `TRUSTORE_PASSWORD` | Default `allpassword` — rotate |
| `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` | Default `onenet` / `true2022` — rotate for anything beyond local testing |
| `CLEARING_HOUSE` | Placeholder IP; only matters if `IS_ENABLED_CLEARINGHOUSE=true` |
| `API_URL` | Points at a specific dataspace's Middleware — differs per dataspace; see the real value in your own `.env`, not committed here |
| `DATA_APP_NAME` | Must be `data-app-provider` or `data-app-consumer` depending on which role this instance plays |
| `NOTARIZATION_OWNER` | Your blockchain wallet address — empty by default, required only if `NOTARIZATION_ENABLED=true` |
| `MNEMONIC` | Your wallet seed phrase — **never commit this**, only needed if notarization is enabled |
| `SEPOLIA_API_KEY`, `MUMBAI_API_KEY`, `AMOY_API_KEY` | Your own blockchain RPC provider keys — only needed if notarization is enabled. **The values pasted in this conversation look like live keys, not placeholders — rotate them if so.** |
| `NOTARIZATION_NETWORK` | Depends on which chain/testnet you're notarizing against |
| `PROVIDER_DAPS_KEYSTORE_ALIAS` / `CONSUMER_DAPS_KEYSTORE_ALIAS` | Depends on how your keystore was generated; `1` is just this sample's alias |

## Connector `.env` — fixed / shared defaults

These come from the reference docker-compose setup and are the same for
every participant running the standard stack. Leave as-is unless you have a
specific reason to change them (e.g. port conflicts on your host).

| Variable | Default | Notes |
|---|---|---|
| `BROKER_URL` | `broker.ids.isst.fraunhofer.de/infrastructure` | Shared IDS broker, same for all participants unless your dataspace runs its own |
| `IS_ENABLED_DAPS_INTERACTION`, `IS_ENABLED_CLEARINGHOUSE`, `IS_ENABLED_USAGE_CONTROL` | `false` | Feature flags — enable only if your dataspace requires them |
| `MONGO_HOST_IP`, `MONGO_HOST_PORT` | `db-mongo:27017` | Docker-compose service name/port |
| `CONTEXT_BROKER_PROTOCOL`, `CONTEXT_BROKER_IP`, `CONTEXT_BROKER_PORT` | `http://fiware-orion:1026` | Docker-compose service name/port |
| `CONTEXT_BROKER_PROVIDER_PATH`, `CONTEXT_BROKER_REGISTRATION_PATH` | NGSI-LD standard paths | Protocol-fixed |
| `DISABLE_SSL_VALIDATION` | `true` | Dev/test convenience for self-signed certs — set `false` once you have real certs |
| `SERVER_SSL_ENABLED`, `REST_ENABLE_HTTPS` | `true` | Standard for this stack |
| `KEYSTORE_NAME`, `TRUSTORE_NAME`, `ALIAS` | `ssl-server.jks` / `truststoreEcc.jks` / `execution-core-container` | File names/alias from the reference setup |
| `CACHE_TOKEN`, `FETCH_TOKEN_ON_STARTUP` | `true` | Standard DAPS token handling |
| `INTERNAL_REST_PORT` | `8449` | Standard ECC internal port |
| `MULTIPART_ECC`, `PROVIDER_MULTIPART_EDGE`, `CONSUMER_MULTIPART_EDGE` | `form` | Communication mode between ECCs |
| `WS_ECC`, `IDSCP2`, `PROVIDER_WS_EDGE`, `CONSUMER_WS_EDGE` | `false` | Alternate transport protocols, off by default |
| `EXTRACT_PAYLOAD_FROM_RESPONSE` | `true` | Standard behavior |
| `PROVIDER_PORT`, `CONSUMER_PORT` | `8090` / `8091` | Standard unless you have a port conflict |
| `PROVIDER_DATA_APP_ENDPOINT`, `CONSUMER_DATA_APP_ENDPOINT` | `be-dataapp-provider:8083` / `be-dataapp-consumer:8084` | Docker-compose service names/ports |
| `MONGO_INITDB_DATABASE` | `orion` | Standard database name |
| `LOCAL_API_DATA_PART_SIZE`, `LOCAL_API_DATA_SUBPART_NUMBER` | `63999` / `150` | Tuned to Orion-LD's attribute size limit — don't change unless you understand the limit |
| `NOTARIZATION_ENABLED` | `false` | Off by default |
| `NOTARIZATION_PROTOCOL`, `NOTARIZATION_HOST`, `NOTARIZATION_PORT`, `NOTARIZATION_PATH` | `http://blockchain-notarization:8092/api/contracts` | Docker-compose service, only relevant if notarization is enabled |
| `NOTARIZATION_PREFIX_FILTER_LIST` | `urn:ngsi-ld:dataentity:,` | Standard NGSI-LD entity prefix |
| `SERVER_PORT` | `8092` | Standard notarization service port |
| `PUSH_ENABLED` | `true` | Standard push-scenario flag |

## Once you have real values

Update this gateway's own `.env` (not the connector's) with:

```bash
DATASPACE_ENPOWER_BASE_URL=<your dataspace's Middleware host, no trailing /api>
DATASPACE_CONNECTOR_BASE_URL=<host:port where your ECC's Local API is actually exposed>
```

The gateway doesn't need any of the connector's DAPS/keystore/Mongo/notarization
settings directly — it only ever calls the Local API's `/api/provide-data` and
`/api/consume-data/by-id` routes over HTTP(S), so all of that complexity stays
inside your connector deployment.
