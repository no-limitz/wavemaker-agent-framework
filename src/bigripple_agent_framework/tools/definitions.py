"""
Tool definition types for agent tool calling.

Provides base types for defining tools that can be registered with the
ToolRegistry and called by agents during execution.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ToolCategory(str, Enum):
    """Categories of tools available to agents."""
    ENTITY = "entity"        # BigRipple entity CRUD operations
    KNOWLEDGE = "knowledge"  # RAG/search operations
    UTILITY = "utility"      # General utilities
    CUSTOM = "custom"        # User-defined tools


class ToolParameter(BaseModel):
    """Schema for a single tool parameter."""
    name: str
    type: str = Field(
        description="JSON Schema type: string, number, integer, boolean, array, object"
    )
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None
    items: Optional[Dict[str, Any]] = Field(
        None,
        description="For array types, the schema of array items"
    )

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema property format."""
        schema: Dict[str, Any] = {
            "type": self.type,
            "description": self.description,
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        if self.items:
            schema["items"] = self.items
        return schema


class ToolDefinition(BaseModel):
    """Definition of a callable tool.

    Defines the schema and metadata for a tool that can be registered
    with the ToolRegistry and made available to agents.
    """
    id: str = Field(
        description="Unique tool identifier, e.g., 'bigripple.campaign.create'"
    )
    name: str = Field(
        description="Function name for LLM, e.g., 'create_campaign'"
    )
    description: str = Field(
        description="Clear description for LLM to understand when to use this tool"
    )
    category: ToolCategory
    parameters: List[ToolParameter]
    returns_entity_operation: bool = Field(
        False,
        description="If True, tool result includes an EntityOperation for BigRipple"
    )

    def get_required_params(self) -> List[str]:
        """Get list of required parameter names."""
        return [p.name for p in self.parameters if p.required]

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }


class ToolResult(BaseModel):
    """Result from executing a tool.

    Returned by tool handlers after execution. If the tool creates or
    updates a BigRipple entity, entity_operation should be populated.
    """
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    entity_operation: Optional[Dict[str, Any]] = Field(
        None,
        alias="entityOperation",
        description="If tool creates/updates an entity, include the operation schema"
    )

    @classmethod
    def ok(cls, data: Any = None, entity_operation: Optional[Dict] = None) -> "ToolResult":
        """Create a successful result."""
        return cls(success=True, data=data, entity_operation=entity_operation)

    @classmethod
    def fail(cls, code: str, message: str, details: Any = None) -> "ToolResult":
        """Create a failed result."""
        return cls(
            success=False,
            error={"code": code, "message": message, "details": details}
        )
