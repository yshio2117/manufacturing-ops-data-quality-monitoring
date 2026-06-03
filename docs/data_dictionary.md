### Table: `shift_log_raw` (RAW)

**Purpose:**  
Raw ingestion layer that stores source records without transformation or validation.

This layer preserves the original incoming records for traceability and audit purposes.

**Grain:** 
1 row per ingested record per run

**Keys:**
row_id: UUIDv4 (technical key per ingestion row)


### Table: `shift_log_validated` (VAL)

**Purpose:**  
Validated and standardized data layer used for downstream governed processing.

This layer applies schema validation and data quality checks while preserving ingestion-level traceability.

**Grain:** 
1 row per ingested record per run (1:1 with shift_log_raw via row_id)

**Keys:**
row_id: UUIDv4 (technical key per ingestion row)
shift_log_id: Deterministic UUIDv5 generated from (date, line, shift), deterministic business key; stable across runs

**Clustering:**  
- Cluster: `shift_log_id`, `ingested_at`, `row_id`

Note: set clustering by these 3 columns to optimize query performance when creating the dedup-view (described as below)

### View: `shift_log_validated_dedup`

**Purpose:**  
Curated deduplicated layer that provides one canonical record per `shift_log_id`.

Acts as a simplified “golden record” view for downstream BI.

**Grain:**  
1 row per `shift_log_id`

**Deduplication rule:**  
Select the latest ingested record per `shift_log_id`.

The view selects the most recent record per `shift_log_id`
using the `ingested_at` timestamp and `row_id` as below:

```sql
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY review_id
               ORDER BY ingested_at DESC, row_id DESC
           ) AS rn
    FROM shift_log_validated
)
WHERE rn = 1
```