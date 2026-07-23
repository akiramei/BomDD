# DB Object Inventory

| DB ID | Type | Qualified name | Business purpose | Readers | Writers | Side effects | Lifecycle | Evidence |
|---|---|---|---|---|---|---|---|---|
| DB-OBJ-001 | table/view/trigger/procedure/index/sequence/role | | known/unknown | | | | active/legacy/unknown | |

Rules:

- `unknown` is allowed during inventory but must become blocker/non-blocker before MIG-30.
- Do not delete or rename an unknown object.
- Include triggers, procedures, views, generated values, indexes and permissions; tables alone are insufficient.

