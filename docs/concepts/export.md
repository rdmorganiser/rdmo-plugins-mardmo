# Export Pipeline

Clicking "Export to MaRDI Portal" on an RDMO project page starts a multi-step pipeline that validates the questionnaire, builds a structured Wikibase payload, authenticates the user against the MaRDI Portal, and uploads the data.  This page walks through every step in order.

## 1. Preview

The first click on "Export to MaRDI Portal" renders an **HTML documentation preview** — a human-readable rendering of everything the user has entered in the questionnaire.  Errors, invalid URLs, and important missing fields are already flagged with red text at this stage, giving the user a chance to review and correct the documentation before committing to the export.  A second "Export to MaRDI Portal" button at the bottom of the preview page triggers the actual export.

## 2. Credential and Catalog Check

`submit()` immediately checks two preconditions:

- **OAuth2 credentials**: if `oauth2_client_id` or `oauth2_client_secret` are missing from the Django settings, an error page is returned before any data processing happens.
- **Catalog support**: if the active project catalog is not one of the supported MaRDMO catalogs, an error page is returned.

## 3. Collecting Answers

`get_post_data()` reads all RDMO project values and assembles them into a nested Python dict via `process_question_dict()`, organised by entity type (e.g. `{"model": {...}, "formulation": {...}, "publication": {...}}`).

## 4. Validation Checks

`Checks.run_X()` validates the collected answers for completeness and consistency.  In addition, for every entity that would be newly created on the MaRDI Portal, a request is sent to the portal to check whether an item with the same label and description combination already exists.  If any check fails, a readable error list is returned and the export is aborted.

## 5. Payload Construction

`PrepareX().export()` translates the answers dict into a Wikibase-ready payload dict and a dependency graph:

- **`unique_items()`** deduplicates all entities referenced across the questionnaire.
- **`process_items()`** assigns each unique item to one of two tracks:
    - Items already on the MaRDI Portal (`mardi:` prefix) are registered with their real QID.
    - All other items (from Wikidata, or newly defined) are again checked against the MaRDI Portal for duplicates (`_check_mardi_and_raise`), then registered as new with an empty QID and a seed list of statements (Wikidata QID, ORCiD, zbMath code, or ISSN as appropriate).
- **`add_answer()` calls** accumulate statements:
    - For **new items**: statements are appended to the item's payload and will be created together with the item in a single API call.
    - For **existing items**: each statement becomes a separate `RELATION<n>` entry that will be posted individually.
- **Relation existence check**: `build_relation_check_query()` generates a SPARQL query that checks, for every `RELATION` entry targeting an existing item, whether that exact statement already exists on the MaRDI Portal.  Only genuinely new relations are posted during upload.  For `math`-datatype statements a separate API-based check is used, because SPARQL returns MathML while the MaRDI Portal stores LaTeX.
- **Dependency graph**: whenever a new item's statement references another new item (identified by an `Item<n>` placeholder), that dependency is recorded so that items can be created in the correct order.

## 6. Cyclic Dependency Check

`is_cyclic(dependency)` inspects the dependency graph before proceeding.  If a cycle is detected an error page is returned.

## 7. OAuth2 Authentication

`post()` serialises the payload and the topological item order into the Django session and redirects the user to the MaRDI Portal OAuth2 authorisation endpoint.  After the user approves the access, the portal redirects back to the MaRDMO callback URL.  `callback()` validates the CSRF state token, exchanges the authorisation code for an access token, and launches the background upload.

## 8. Background Upload

The upload runs in a **daemon thread** so the browser can display a live progress page immediately.  The upload proceeds in two phases:

**Phase 1 — New items** (in topological dependency order):
Each new item is posted to the Wikibase REST API as a single request containing its label, description, aliases, and **all** its statements at once.  Once the MaRDI Portal assigns a real QID, every remaining `Item<n>` placeholder in the payload is replaced with that QID, so subsequent items that depend on it reference the correct identifier.

**Phase 2 — Relations**:
`RELATION<n>` entries (statements targeting existing items) and `ALIAS<n>` entries are posted **individually**, one statement per request.  Relations already flagged as existing by the SPARQL check in step 5 are skipped.

### Error Handling

The upload layer handles MaRDI Portal communication errors gracefully:

| Condition | Behaviour |
|---|---|
| Timeout / connection error | Retry up to 5 times with exponential back-off |
| HTTP 429 (rate limit) | Wait for the `Retry-After` duration, then retry |
| HTTP 403 / 5xx | Exponential back-off retry |
| HTTP 422 `item-label-description-duplicate` | Reuse the conflicting item's QID and continue |
| Any other HTTP error | Extract a human-readable message from the response and surface it to the user |

## 9. Success Page

After all items and relations have been posted, `post_success()` compares the initial payload (before upload) with the final payload (after upload, containing real QIDs) and renders a success page listing all newly created MaRDI Portal items with clickable links.
