#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# =====================================================================
# CONFIGURATION
# =====================================================================
PROJECT_ID="platform-metadata"   # Your GCP Project ID
DATASET_ID="metadata_governance" # Your BigQuery Dataset ID
LOCATION="europe-west2"          # London region

echo "Using Project: ${PROJECT_ID}"
echo "Using Dataset: ${DATASET_ID}"
echo "Location:      ${LOCATION}"

# Create the dataset if it does not exist
echo "Ensuring BigQuery dataset '${DATASET_ID}' exists..."
bq show --project_id="${PROJECT_ID}" "${DATASET_ID}" > /dev/null 2>&1 || \
bq --project_id="${PROJECT_ID}" mk --dataset --location="${LOCATION}" "${DATASET_ID}"

# Helper function to read schema from stdin and create the clustered table
create_table() {
  local table_name=$1
  local clustering_fields=$2

  echo "Creating table: ${table_name} (Clustered by: ${clustering_fields})..."
  
  # Read schema from stdin and write to a temporary file
  cat > "/tmp/${table_name}_schema.json"
  
  # Create the table using the schema file and clustering configuration
  bq --project_id="${PROJECT_ID}" mk \
    --table \
    --clustering_fields="${clustering_fields}" \
    "${DATASET_ID}.${table_name}" \
    "/tmp/${table_name}_schema.json"

  # Clean up the temp file
  rm "/tmp/${table_name}_schema.json"
}

# =====================================================================
# TABLE 1: resource_snapshot
# =====================================================================
create_table "resource_snapshot" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "snapshot_time",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING"
  },
  {
    "name": "asset_type",
    "type": "STRING"
  },
  {
    "name": "resource_name",
    "type": "STRING"
  },
  {
    "name": "location",
    "type": "STRING"
  },
  {
    "name": "labels",
    "type": "STRING"
  },
  {
    "name": "tags",
    "type": "STRING"
  }
]
EOF

# =====================================================================
# TABLE 2: compliance_snapshot
# =====================================================================
create_table "compliance_snapshot" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "evaluated_time",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING"
  },
  {
    "name": "asset_type",
    "type": "STRING"
  },
  {
    "name": "resource_name",
    "type": "STRING"
  },
  {
    "name": "compliant",
    "type": "BOOL"
  },
  {
    "name": "missing_labels",
    "type": "STRING"
  },
  {
    "name": "incorrect_labels",
    "type": "STRING"
  }
]
EOF

# =====================================================================
# TABLE 3: remediation_plan
# =====================================================================
create_table "remediation_plan" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "asset_type",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "resource_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "missing_labels",
    "type": "JSON",
    "mode": "REQUIRED"
  },
  {
    "name": "planned_labels",
    "type": "JSON",
    "mode": "REQUIRED"
  },
  {
    "name": "planned_tags",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "status",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "created_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }
]
EOF

# =====================================================================
# TABLE 4: remediation_execution
# =====================================================================
create_table "remediation_execution" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "execution_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "asset_type",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "resource_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "managed_labels",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "status",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "error_message",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "executed_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "execution_mode",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "service_name",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "method_name",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "duration_ms",
    "type": "INT64",
    "mode": "NULLABLE"
  }
]
EOF

# =====================================================================
# TABLE 5: label_ownership
# =====================================================================
create_table "label_ownership" "resource_name" <<'EOF'
[
  {
    "name": "resource_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "managed_labels",
    "type": "JSON",
    "mode": "NULLABLE"
  },
  {
    "name": "managed_tags",
    "type": "JSON",
    "mode": "NULLABLE"
  },
  {
    "name": "updated_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }
]
EOF

echo "All BigQuery tables created and clustered successfully in region ${LOCATION}!"
