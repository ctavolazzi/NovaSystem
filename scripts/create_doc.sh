#!/bin/bash
# NovaSystem Documentation File Creator
# This script creates new documentation files with the proper template structure.
#
# Usage:
#   ./scripts/create_doc.sh <document_type> <document_path> <document_title>
#
# Example:
#   ./scripts/create_doc.sh component components/agents/rule-based-agent.md "Rule-Based Agent Component"
#   ./scripts/create_doc.sh implementation implementation/02-enhanced-functionality/01-vector-database.md "Vector Database Integration"
#   ./scripts/create_doc.sh guide guides/getting-started/local-setup.md "Setting Up Local Development Environment"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for required arguments
if [ "$#" -lt 3 ]; then
    echo -e "${RED}Error: Insufficient arguments${NC}"
    echo "Usage: $0 <document_type> <document_path> <document_title>"
    echo ""
    echo "Document types:"
    echo "  - architecture: Architecture documentation"
    echo "  - implementation: Implementation plan document"
    echo "  - component: Component specification"
    echo "  - api: API documentation"
    echo "  - process: Process documentation"
    echo "  - guide: Development guide"
    echo "  - reference: Reference documentation"
    exit 1
fi

# Assign arguments to variables
DOC_TYPE="$1"
DOC_PATH="$2"
DOC_TITLE="$3"
FULL_PATH="docs/$DOC_PATH"
AUTHOR=$(git config user.name || echo "NovaSystem Team")
DATE=$(date "+%Y-%m-%d")

# Verify document type is valid
case "$DOC_TYPE" in
    architecture|implementation|component|api|process|guide|reference)
        echo -e "${GREEN}Creating $DOC_TYPE documentation at $FULL_PATH${NC}"
        ;;
    *)
        echo -e "${RED}Error: Invalid document type '$DOC_TYPE'${NC}"
        echo "Valid types: architecture, implementation, component, api, process, guide, reference"
        exit 1
        ;;
esac

# Check if file already exists
if [ -f "$FULL_PATH" ]; then
    echo -e "${YELLOW}Warning: File already exists at $FULL_PATH${NC}"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Operation cancelled."
        exit 0
    fi
fi

# Create directory structure if it doesn't exist
mkdir -p "$(dirname "$FULL_PATH")"

# Create template based on document type
case "$DOC_TYPE" in
    architecture)
        cat > "$FULL_PATH" << EOF
# $DOC_TITLE

## Overview

This document describes the architectural aspects of [brief description].

## Architecture Goals

- [Goal 1]
- [Goal 2]
- [Goal 3]

## Architecture Diagram

\`\`\`
[Insert diagram here]
\`\`\`

## Key Components

### [Component 1]

[Description of component 1]

### [Component 2]

[Description of component 2]

## Design Decisions

### [Decision 1]

**Context:** [What led to this decision]

**Decision:** [What was decided]

**Rationale:** [Why this decision was made]

**Consequences:** [The impacts of this decision]

## Relationships

- **Relates to:** [Related architecture documents]
- **Impacts:** [Components or implementations affected]

## References

- [Reference 1]
- [Reference 2]

---
**Author:** $AUTHOR
**Created:** $DATE
**Last Updated:** $DATE
EOF
        ;;

    implementation)
        cat > "$FULL_PATH" << EOF
# $DOC_TITLE

## Overview

This document outlines the implementation plan for [brief description].

## Objectives

- [Objective 1]
- [Objective 2]
- [Objective 3]

## Implementation Details

### [Section 1]

[Detailed implementation description]

\`\`\`python
# Example code
def example_function():
    return "Implementation example"
\`\`\`

### [Section 2]

[Detailed implementation description]

## Technical Specifications

### Data Structures

[Data structure details]

### Dependencies

- [Dependency 1] - [Purpose]
- [Dependency 2] - [Purpose]

## Implementation Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Integration Points

- [Integration point 1]
- [Integration point 2]

## Testing Strategy

- [Testing approach]
- [Key test cases]

## Deliverables

- [Deliverable 1]
- [Deliverable 2]

## Related Documents

- [Related document 1]
- [Related document 2]

---
**Author:** $AUTHOR
**Created:** $DATE
**Last Updated:** $DATE
EOF
        ;;

    component)
        cat > "$FULL_PATH" << EOF
# $DOC_TITLE

## Overview

This document provides the technical specification for the [component name] component.

## Interface

\`\`\`python
# Public interface
class ComponentName:
    def __init__(self, param1, param2):
        """Constructor description"""
        pass

    def method_name(self, arg1, arg2):
        """Method description"""
        return result
\`\`\`

## Behavior

[Detailed explanation of how the component operates]

## Dependencies

- [Dependency 1] - [Purpose]
- [Dependency 2] - [Purpose]

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| param1 | string | "default" | Description of param1 |
| param2 | int | 42 | Description of param2 |

## Usage Examples

\`\`\`python
# Example usage
component = ComponentName("value1", 100)
result = component.method_name("arg1", "arg2")
\`\`\`

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| [Condition 1] | [How it's handled] |
| [Condition 2] | [How it's handled] |

## Performance Considerations

- [Performance characteristic 1]
- [Performance characteristic 2]

## Related Components

- [Related component 1]
- [Related component 2]

---
**Author:** $AUTHOR
**Created:** $DATE
**Last Updated:** $DATE
EOF
        ;;

    api)
        cat > "$FULL_PATH" << EOF
# $DOC_TITLE

## Endpoint

\`\`\`
[HTTP Method] [Endpoint URL]
\`\`\`

## Description

[Detailed description of what this API endpoint does]

## Authentication

[Authentication requirements]

## Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| [param1] | string | Yes | Description of param1 |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| [param1] | string | No | Description of param1 |

### Request Body

\`\`\`json
{
  "property1": "value1",
  "property2": "value2"
}
\`\`\`

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| property1 | string | Yes | Description of property1 |
| property2 | string | No | Description of property2 |

## Response

### Success Response (200 OK)

\`\`\`json
{
  "id": "123456",
  "status": "success",
  "data": {
    "property1": "value1",
    "property2": "value2"
  }
}
\`\`\`

| Property | Type | Description |
|----------|------|-------------|
| id | string | Unique identifier |
| status | string | Response status |
| data | object | Response data |

### Error Responses

#### 400 Bad Request

\`\`\`json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": {
      "property1": "error details"
    }
  }
}
\`\`\`

#### 404 Not Found

\`\`\`json
{
  "error": {
    "code": "resource_not_found",
    "message": "Resource not found"
  }
}
\`\`\`

## Examples

### Example Request

\`\`\`bash
curl -X POST "https://api.novasystem.io/v1/endpoint" \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "property1": "value1",
    "property2": "value2"
  }'
\`\`\`

### Example Response

\`\`\`json
{
  "id": "123456",
  "status": "success",
  "data": {
    "property1": "value1",
    "property2": "value2"
  }
}
\`\`\`

## Related Endpoints

- [Related endpoint 1]
- [Related endpoint 2]

---
**Author:** $AUTHOR
**Created:** $DATE
**Last Updated:** $DATE
EOF
        ;;

    process)
        cat > "$FULL_PATH" << EOF
# $DOC_TITLE

## Process Overview

This document describes the [process name] process, which [brief description].

## Process Flow

\`\`\`
[Process flow diagram]
\`\`\`

## Process Steps

### 1. [Step 1 Name]

**Description:** [Detailed description of step 1]

**Inputs:**
- [Input 1]
- [Input 2]

**Actions:**
1. [Action 1]
2. [Action 2]

**Outputs:**
- [Output 1]
- [Output 2]

**Responsible:** [Role or person responsible]

### 2. [Step 2 Name]

**Description:** [Detailed description of step 2]

**Inputs:**
- [Input 1]
- [Input 2]

**Actions:**
1. [Action 1]
2. [Action 2]

**Outputs:**
- [Output 1]
- [Output 2]

**Responsible:** [Role or person responsible]

## Decision Points

### [Decision Point 1]

- **Condition:** [Condition for making the decision]
- **Option A:** [Description of option A]
- **Option B:** [Description of option B]
- **Decision Criteria:** [How to decide between options]

## Process Metrics

- **Time:** [Expected time to complete the process]
- **Success Rate:** [Expected success rate]
- **Key Performance Indicators:** [KPIs for the process]

## Tools and Resources

- [Tool/Resource 1] - [Purpose]
- [Tool/Resource 2] - [Purpose]

## Related Processes

- [Related process 1]
- [Related process 2]

---
**Author:** $AUTHOR
**Created:** $DATE
**Last Updated:** $DATE
EOF
        ;;

    guide)
        cat > "$FULL_PATH" << EOF
# $DOC_TITLE

## Introduction

This guide explains how to [brief description].

## Prerequisites

Before starting, ensure you have:

- [Prerequisite 1]
- [Prerequisite 2]
- [Prerequisite 3]

## Step-by-Step Instructions

### Step 1: [Step 1 Title]

[Detailed instructions for step 1]

\`\`\`bash
# Example command for step 1
command --option value
\`\`\`

### Step 2: [Step 2 Title]

[Detailed instructions for step 2]

\`\`\`python
# Example code for step 2
def example():
    return "Step 2 example"
\`\`\`

### Step 3: [Step 3 Title]

[Detailed instructions for step 3]

## Common Issues and Solutions

### [Issue 1]

**Problem:** [Description of issue 1]

**Solution:** [Solution for issue 1]

### [Issue 2]

**Problem:** [Description of issue 2]

**Solution:** [Solution for issue 2]

## Best Practices

- [Best practice 1]
- [Best practice 2]
- [Best practice 3]

## Next Steps

After completing this guide, you might want to:

- [Next step 1]
- [Next step 2]

## Additional Resources

- [Resource 1]
- [Resource 2]

---
**Author:** $AUTHOR
**Created:** $DATE
**Last Updated:** $DATE
EOF
        ;;

    reference)
        cat > "$FULL_PATH" << EOF
# $DOC_TITLE

## Overview

This reference document provides information about [brief description].

## Reference Content

### [Section 1]

[Detailed reference information]

### [Section 2]

[Detailed reference information]

## Data Formats

### [Format 1]

\`\`\`json
{
  "property1": "value1",
  "property2": "value2"
}
\`\`\`

| Property | Type | Description |
|----------|------|-------------|
| property1 | string | Description of property1 |
| property2 | string | Description of property2 |

## Examples

### [Example 1]

[Example 1 details]

### [Example 2]

[Example 2 details]

## Related References

- [Related reference 1]
- [Related reference 2]

## External Resources

- [External resource 1]
- [External resource 2]

---
**Author:** $AUTHOR
**Created:** $DATE
**Last Updated:** $DATE
EOF
        ;;
esac

echo -e "${GREEN}Successfully created $DOC_TYPE documentation at $FULL_PATH${NC}"
echo -e "${YELLOW}Remember to update the relevant README.md files and regenerate the documentation map:${NC}"
echo -e "${YELLOW}  python scripts/generate_doc_map.py${NC}"
exit 0