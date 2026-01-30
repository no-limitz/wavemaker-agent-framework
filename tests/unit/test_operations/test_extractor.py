"""Tests for OperationExtractor."""

import sys
import os

# Add src to path to import directly without triggering package __init__
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import pytest

# Import directly from module to avoid langfuse import in main __init__
from bigripple_agent_framework.operations.extractor import OperationExtractor


class TestOperationExtractor:
    """Tests for OperationExtractor."""

    @pytest.fixture
    def extractor(self):
        """Create an extractor."""
        return OperationExtractor()

    def test_extract_explicit_operations(self, extractor):
        """Extracts explicit entityOperations from output."""
        output = {
            "analysis": "Some analysis",
            "entityOperations": [
                {
                    "type": "create_campaign",
                    "brandId": "brand_123",
                    "data": {"name": "Test Campaign", "channels": ["linkedin"]},
                },
            ],
        }

        cleaned, operations = extractor.extract(output)

        assert len(operations) == 1
        assert operations[0]["type"] == "create_campaign"
        # entityOperations should be removed from cleaned output
        assert "entityOperations" not in cleaned
        assert "analysis" in cleaned

    def test_extract_from_tool_results(self, extractor):
        """Extracts operations from tool results."""
        tool_results = [
            {
                "success": True,
                "entity_operation": {
                    "type": "create_content",
                    "brandId": "brand_123",
                    "data": {"type": "SOCIAL_POST", "channel": "twitter", "body": "Hello!"},
                },
            },
        ]

        _, operations = extractor.extract({}, tool_results=tool_results)

        assert len(operations) == 1
        assert operations[0]["type"] == "create_content"

    def test_extract_from_camelcase_tool_results(self, extractor):
        """Extracts operations from camelCase tool results."""
        tool_results = [
            {
                "success": True,
                "entityOperation": {  # camelCase
                    "type": "create_campaign",
                    "brandId": "brand_123",
                    "data": {"name": "Test", "channels": []},
                },
            },
        ]

        _, operations = extractor.extract({}, tool_results=tool_results)

        assert len(operations) == 1

    def test_infer_campaigns_with_flag(self, extractor):
        """Infers campaign operations when createInSystem flag is set."""
        output = {
            "campaigns": [
                {
                    "name": "Spring Campaign",
                    "channels": ["facebook", "instagram"],
                    "goal": "Increase awareness",
                    "createInSystem": True,
                },
                {
                    "name": "Draft Campaign",
                    "channels": ["linkedin"],
                    # No create flag - should be skipped
                },
            ],
        }

        _, operations = extractor.extract(output, brand_id="brand_123")

        assert len(operations) == 1
        assert operations[0]["data"]["name"] == "Spring Campaign"

    def test_infer_contents_with_flag(self, extractor):
        """Infers content operations when create flag is set."""
        output = {
            "posts": [
                {
                    "channel": "linkedin",
                    "body": "Check out our new feature!",
                    "saveToDatabase": True,
                },
            ],
        }

        _, operations = extractor.extract(output, brand_id="brand_123")

        assert len(operations) == 1
        assert operations[0]["type"] == "create_content"
        assert operations[0]["data"]["body"] == "Check out our new feature!"

    def test_infer_content_type(self, extractor):
        """Correctly infers content type from channel."""
        output = {
            "suggestedContent": [
                {"channel": "linkedin", "body": "Post", "create": True},
                {"channel": "blog", "body": "Article", "create": True},
                {"channel": "email", "body": "Newsletter", "create": True},
            ],
        }

        _, operations = extractor.extract(output, brand_id="brand_123")

        assert len(operations) == 3
        assert operations[0]["data"]["type"] == "SOCIAL_POST"
        assert operations[1]["data"]["type"] == "BLOG_POST"
        assert operations[2]["data"]["type"] == "EMAIL"

    def test_skip_without_brand_id(self, extractor):
        """Skips operations without brand ID."""
        output = {
            "campaigns": [
                {"name": "Test", "channels": [], "createInSystem": True},
            ],
        }

        # No brand_id provided
        _, operations = extractor.extract(output)

        assert len(operations) == 0  # Skipped due to missing brandId

    def test_disable_inference(self):
        """Can disable operation inference."""
        extractor = OperationExtractor(infer_operations=False)
        output = {
            "campaigns": [
                {"name": "Test", "channels": [], "createInSystem": True},
            ],
        }

        _, operations = extractor.extract(output, brand_id="brand_123")

        assert len(operations) == 0  # Inference disabled

    def test_disable_require_create_flag(self):
        """Can create operations without create flag."""
        extractor = OperationExtractor(require_create_flag=False)
        output = {
            "campaigns": [
                {"name": "Auto Campaign", "channels": ["twitter"]},
                # No create flag, but should still be created
            ],
        }

        _, operations = extractor.extract(output, brand_id="brand_123")

        assert len(operations) == 1

    def test_handles_non_dict_output(self, extractor):
        """Handles non-dict output gracefully."""
        _, operations = extractor.extract("Just a string response")
        assert len(operations) == 0

        _, operations = extractor.extract(None)
        assert len(operations) == 0

    def test_extracts_body_from_various_keys(self, extractor):
        """Extracts body content from various key names."""
        output = {
            "contentItems": [
                {"channel": "twitter", "text": "Tweet text", "create": True},
                {"channel": "linkedin", "content": "LinkedIn content", "create": True},
                {"channel": "facebook", "message": "Facebook message", "create": True},
            ],
        }

        _, operations = extractor.extract(output, brand_id="brand_123")

        assert len(operations) == 3
        assert operations[0]["data"]["body"] == "Tweet text"
        assert operations[1]["data"]["body"] == "LinkedIn content"
        assert operations[2]["data"]["body"] == "Facebook message"
