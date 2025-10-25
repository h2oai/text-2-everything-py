"""
Schema metadata models for the Text2Everything SDK.
"""

from typing import Optional, Dict, Any
from .base import BaseModel, BaseResponse


class SchemaMetadataBase(BaseModel):
    """Base schema metadata model."""
    
    name: str
    description: Optional[str] = None
    schema_data: Dict[str, Any]
    is_always_displayed: bool = False


class SchemaMetadataCreate(SchemaMetadataBase):
    """Model for creating new schema metadata."""
    pass


class SchemaMetadataUpdate(BaseModel):
    """Model for updating schema metadata."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    schema_data: Optional[Dict[str, Any]] = None
    is_always_displayed: Optional[bool] = None


class SchemaMetadata(SchemaMetadataBase, BaseResponse):
    """Complete schema metadata model with all fields."""
    
    project_id: str
    h2ogpte_doc_id: Optional[str] = None
    split_group_id: Optional[str] = None
    split_index: Optional[int] = None
    total_splits: Optional[int] = None


class SchemaMetadataResponse(SchemaMetadata):
    """Schema metadata response with collection ID."""
    
    collection_id: Optional[str] = None


# Helper functions for schema validation (used by the validator)
def validate_table_schema(schema_data: Dict[str, Any]) -> list[str]:
    """Validate table schema structure.
    
    Requirements:
    - schema_data.table (object)
    - schema_data.table.columns (array)
    """
    errors = []
    
    # Check schema_data.table
    if "table" not in schema_data:
        errors.append("Missing required field: schema_data.table")
        return errors
    
    table = schema_data["table"]
    if not isinstance(table, dict):
        errors.append("Field schema_data.table must be an object")
        return errors
    
    # Check schema_data.table.columns
    if "columns" not in table:
        errors.append("Missing required field: schema_data.table.columns")
    elif not isinstance(table["columns"], list):
        errors.append("Field schema_data.table.columns must be an array")
    
    return errors


def validate_dimension_schema(schema_data: Dict[str, Any]) -> list[str]:
    """Validate dimension schema structure.
    
    Requirements:
    - schema_data.table (object)
    - schema_data.table.dimension (object)
    - schema_data.table.dimension.content (object)
    """
    errors = []
    
    # Check schema_data.table
    if "table" not in schema_data:
        errors.append("Missing required field: schema_data.table")
        return errors
    
    table = schema_data["table"]
    if not isinstance(table, dict):
        errors.append("Field schema_data.table must be an object")
        return errors
    
    # Check schema_data.table.dimension
    if "dimension" not in table:
        errors.append("Missing required field: schema_data.table.dimension")
        return errors
    
    dimension = table["dimension"]
    if not isinstance(dimension, dict):
        errors.append("Field schema_data.table.dimension must be an object")
        return errors
    
    # Check schema_data.table.dimension.content
    if "content" not in dimension:
        errors.append("Missing required field: schema_data.table.dimension.content")
    elif not isinstance(dimension["content"], dict):
        errors.append("Field schema_data.table.dimension.content must be an object")
    
    return errors


def validate_metric_schema(schema_data: Dict[str, Any]) -> list[str]:
    """Validate metric schema structure.
    
    Requirements:
    - schema_data.table (object)
    - schema_data.table.metric (object)
    - schema_data.table.metric.content (object)
    """
    errors = []
    
    # Check schema_data.table
    if "table" not in schema_data:
        errors.append("Missing required field: schema_data.table")
        return errors
    
    table = schema_data["table"]
    if not isinstance(table, dict):
        errors.append("Field schema_data.table must be an object")
        return errors
    
    # Check schema_data.table.metric
    if "metric" not in table:
        errors.append("Missing required field: schema_data.table.metric")
        return errors
    
    metric = table["metric"]
    if not isinstance(metric, dict):
        errors.append("Field schema_data.table.metric must be an object")
        return errors
    
    # Check schema_data.table.metric.content
    if "content" not in metric:
        errors.append("Missing required field: schema_data.table.metric.content")
    elif not isinstance(metric["content"], dict):
        errors.append("Field schema_data.table.metric.content must be an object")
    
    return errors


def validate_relationship_schema(schema_data: Dict[str, Any]) -> list[str]:
    """Validate relationship schema structure.
    
    Requirements:
    - schema_data.relationship (object)
    """
    errors = []
    
    # Check schema_data.relationship
    if "relationship" not in schema_data:
        errors.append("Missing required field: schema_data.relationship")
        return errors
    
    relationship = schema_data["relationship"]
    if not isinstance(relationship, dict):
        errors.append("Field schema_data.relationship must be an object")
    
    return errors


def detect_schema_type(schema_data: Dict[str, Any]) -> Optional[str]:
    """Detect the type of schema based on its structure."""
    if "table" in schema_data:
        table = schema_data["table"]
        if isinstance(table, dict):
            if "dimension" in table:
                return "dimension"
            elif "metric" in table:
                return "metric"
            elif "columns" in table:
                return "table"
    elif "relationship" in schema_data:
        return "relationship"
    
    return None


def validate_schema_metadata(schema_metadata: Dict[str, Any], expected_type: Optional[str] = None) -> list[str]:
    """Validate schema metadata with nested required field checks.
    
    Args:
        schema_metadata: The schema metadata dictionary to validate
        expected_type: Optional expected type ('table', 'dimension', 'metric', 'relationship')
                      If not provided, will auto-detect from schema_data structure
    
    Returns:
        List of validation error messages. Empty list means validation passed.
    """
    errors = []
    
    # Basic structure validation
    if not isinstance(schema_metadata, dict):
        errors.append("Schema metadata must be an object")
        return errors
    
    # Check required top-level fields
    required_fields = ["name", "schema_data"]
    for field in required_fields:
        if field not in schema_metadata:
            errors.append(f"Missing required field: {field}")
    
    # Validate schema_data exists and is an object
    if "schema_data" not in schema_metadata:
        return errors  # Can't continue without schema_data
    
    schema_data = schema_metadata["schema_data"]
    if not isinstance(schema_data, dict):
        errors.append("Field schema_data must be an object")
        return errors
    
    # Detect or use provided schema type
    schema_type = expected_type or detect_schema_type(schema_data)
    
    if not schema_type:
        errors.append("Unable to determine schema type from schema_data structure")
        return errors
    
    # Apply type-specific validation with nested field checks
    if schema_type == "table":
        validation_errors = validate_table_schema(schema_data)
        errors.extend(validation_errors)
    elif schema_type == "dimension":
        validation_errors = validate_dimension_schema(schema_data)
        errors.extend(validation_errors)
    elif schema_type == "metric":
        validation_errors = validate_metric_schema(schema_data)
        errors.extend(validation_errors)
    elif schema_type == "relationship":
        validation_errors = validate_relationship_schema(schema_data)
        errors.extend(validation_errors)
    else:
        errors.append(f"Unknown schema type: {schema_type}")
    
    return errors


def validate_schema_metadata_create(schema_metadata_create: SchemaMetadataCreate) -> list[str]:
    """Validate a SchemaMetadataCreate object with nested field validation."""
    # Convert Pydantic model to dict for validation
    schema_dict = schema_metadata_create.model_dump()
    return validate_schema_metadata(schema_dict)


def validate_schema_metadata_update(schema_metadata_update: SchemaMetadataUpdate) -> list[str]:
    """Validate a SchemaMetadataUpdate object with nested field validation."""
    errors = []
    
    # Convert Pydantic model to dict for validation
    schema_dict = schema_metadata_update.model_dump(exclude_unset=True)
    
    # If schema_data is being updated, validate it
    if "schema_data" in schema_dict and schema_dict["schema_data"] is not None:
        # For updates, we need to validate the schema_data structure
        schema_data = schema_dict["schema_data"]
        if not isinstance(schema_data, dict):
            errors.append("Field schema_data must be an object")
            return errors
        
        # Detect schema type and validate
        schema_type = detect_schema_type(schema_data)
        if schema_type:
            if schema_type == "table":
                validation_errors = validate_table_schema(schema_data)
                errors.extend(validation_errors)
            elif schema_type == "dimension":
                validation_errors = validate_dimension_schema(schema_data)
                errors.extend(validation_errors)
            elif schema_type == "metric":
                validation_errors = validate_metric_schema(schema_data)
                errors.extend(validation_errors)
            elif schema_type == "relationship":
                validation_errors = validate_relationship_schema(schema_data)
                errors.extend(validation_errors)
        else:
            errors.append("Unable to determine schema type from schema_data structure")
    
    return errors
