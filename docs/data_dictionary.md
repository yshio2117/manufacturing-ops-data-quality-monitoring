## Table: `review_raw` (RAW)

**Purpose:**  
Raw ingestion layer that stores source records without transformation or validation.

This layer preserves the original incoming records for traceability and audit purposes.

**Grain:** 
1 row per ingested record per run

**Keys:**
row_id: UUIDv4 (technical key per ingestion row)
review_id: Deterministic UUIDv5 generated from (source_id, source), deterministic business key; stable across runs

## Table: `review_validated` (VAL)

**Purpose:**  
Validated and standardized data layer used for downstream governed processing.

This layer applies schema validation, normalization, and data quality checks while preserving ingestion-level traceability.

**Grain:** 
1 row per ingested record per run (1:1 with review_raw via row_id)

**Keys:**
row_id: UUIDv4 (technical key per ingestion row)
review_id: Deterministic UUIDv5 generated from (source_id, source), deterministic business key; stable across runs

**Partitioning:**  
- Partition: `posted_at_iso`
- Cluster: `review_id`



## View: `review_validated_dedup`

**Purpose:**  
Curated deduplicated layer that provides one canonical record per `review_id`.

Acts as a simplified “golden record” view for downstream BI, monitoring, and analytical workflows.

**Grain:**  
1 row per `review_id`

**Deduplication rule:**  
Select the latest ingested record per `review_id`.

The view selects the most recent record per `review_id`
using the `ingested_at` timestamp:

```sql
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY review_id
               ORDER BY ingested_at DESC
           ) AS rn
    FROM review_validated
)
WHERE rn = 1
```

## Table: `review_reasons` (DERIVED)
**Purpose:** 
Stores derived analytical attributes extracted from governed customer feedback records.
This layer supports downstream analytical enrichment, issue categorization, and dashboard aggregation workflows.

**Grain:** 
1 row per extracted analytical attribute

**Keys:** 
reason_id: technical key per extracted record

**FK / Join:** 
review_id → review_validated.review_id