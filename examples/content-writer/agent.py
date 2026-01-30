"""
Content Writer Agent Example

This example demonstrates how to build a content writing agent
that creates brand-aligned content using the wavemaker-agent-framework.
"""

import asyncio
from typing import Literal
from openai import AsyncOpenAI

from wavemaker_agent_framework.core import (
    AgentRuntime,
    AgentExecutionInput,
    AgentExecutionResult,
    create_default_runtime,
)
from wavemaker_agent_framework.context import (
    EntityContext,
    BrandSummary,
    BrandVoice,
    CampaignSummary,
)
from wavemaker_agent_framework.tools.bigripple import create_bigripple_registry


# System prompt for the content writer
CONTENT_WRITER_PROMPT = """You are an expert content writer for BigRipple.

Your role is to create compelling, brand-aligned content based on:
- Brand voice and style guidelines
- Campaign objectives
- Target channel requirements
- Content type specifications

Content Guidelines:
1. ALWAYS follow the brand voice guidelines provided in the context
2. Adapt content length and format for the target channel
3. Include relevant hashtags for social media posts
4. Create engaging headlines that capture attention
5. Ensure content aligns with campaign goals

Channel-specific guidance:
- LinkedIn: Professional tone, longer posts (1300 chars), industry insights
- Twitter/X: Concise (280 chars), punchy, use threads for longer content
- Email: Personal, clear CTAs, scannable format
- Blog: SEO-friendly, comprehensive, include subheadings

You have access to tools to create content in BigRipple.
Always use the provided brand_id when creating entities."""


ContentType = Literal["SOCIAL_POST", "BLOG_POST", "EMAIL", "AD_COPY", "NEWSLETTER"]
Channel = Literal["linkedin", "twitter", "email", "blog", "facebook", "instagram"]


async def run_content_writer(
    prompt: str,
    context: EntityContext,
    content_type: ContentType = "SOCIAL_POST",
    channel: Channel = "linkedin",
    openai_api_key: str | None = None,
) -> AgentExecutionResult:
    """
    Run the content writer agent.

    Args:
        prompt: User's content request
        context: Entity context from BigRipple
        content_type: Type of content to create
        channel: Target channel for the content
        openai_api_key: Optional OpenAI API key

    Returns:
        AgentExecutionResult with created content
    """
    # Create OpenAI client
    client = AsyncOpenAI(api_key=openai_api_key)

    # Create runtime with BigRipple tools
    runtime = create_default_runtime(client, include_bigripple_tools=True)

    # Enhanced prompt with content specifications
    full_prompt = f"""
Content Type: {content_type}
Target Channel: {channel}

Request: {prompt}

Please create content that matches these specifications and follows the brand guidelines.
"""

    # Prepare execution input
    input_data = AgentExecutionInput(
        input_data={"prompt": full_prompt},
        context=context,
        execution_id=f"content_writer_{context.user_id}",
        system_prompt=CONTENT_WRITER_PROMPT,
        enabled_tools=[
            "bigripple.content.create",
            "bigripple.knowledge.guidelines",
            "bigripple.knowledge.search",
        ],
        model="gpt-4o",
        temperature=0.8,  # Slightly higher for creative writing
    )

    # Execute the agent
    result = await runtime.execute(input_data)

    return result


async def create_content_batch(
    prompts: list[dict],
    context: EntityContext,
    openai_api_key: str | None = None,
) -> list[AgentExecutionResult]:
    """
    Create multiple pieces of content in sequence.

    Args:
        prompts: List of dicts with 'prompt', 'content_type', 'channel' keys
        context: Entity context from BigRipple
        openai_api_key: Optional OpenAI API key

    Returns:
        List of AgentExecutionResults
    """
    results = []

    for item in prompts:
        result = await run_content_writer(
            prompt=item["prompt"],
            context=context,
            content_type=item.get("content_type", "SOCIAL_POST"),
            channel=item.get("channel", "linkedin"),
            openai_api_key=openai_api_key,
        )
        results.append(result)

    return results


def create_sample_context() -> EntityContext:
    """Create sample context for demonstration."""
    return EntityContext(
        userId="user_demo_123",
        brandId="brand_demo_456",
        brands=[
            BrandSummary(
                id="brand_demo_456",
                name="EcoTech Solutions",
                industry="Sustainability",
                description="Sustainable technology solutions for modern businesses",
            )
        ],
        brandVoice=BrandVoice(
            tone="optimistic and empowering",
            style="clear, action-oriented, environmentally conscious",
            vocabulary=[
                "sustainable",
                "innovative",
                "planet-friendly",
                "future-forward",
                "responsible",
            ],
            avoid=[
                "greenwashing",
                "guilt-tripping",
                "preachy",
                "doom and gloom",
            ],
            examples=[
                "Small changes, big impact. See how companies are reducing their carbon footprint by 40%.",
                "The future of business is green. And it's more profitable than you think.",
            ],
        ),
        campaigns=[
            CampaignSummary(
                id="camp_789",
                name="Earth Month 2024",
                status="ACTIVE",
                channels=["linkedin", "twitter", "email"],
                startDate="2024-04-01",
                endDate="2024-04-30",
            )
        ],
        recentContent=[],
    )


async def main():
    """Run the content writer example."""
    print("Content Writer Agent Example")
    print("=" * 50)

    # Create sample context
    context = create_sample_context()

    # Example: Single content piece
    print("\n--- Single Content Creation ---\n")

    prompt = """
    Write a LinkedIn post announcing our new carbon footprint calculator tool.
    Key features:
    - Free to use
    - Real-time tracking
    - Integrates with popular accounting software
    - Provides actionable recommendations

    Target audience: Sustainability officers and CFOs at mid-size companies
    """

    print(f"User Prompt: {prompt.strip()}")
    print("\n" + "-" * 50)

    try:
        result = await run_content_writer(
            prompt=prompt,
            context=context,
            content_type="SOCIAL_POST",
            channel="linkedin",
        )

        if result.success:
            print("\nGenerated Content:")
            print(result.output)

            if result.entity_operations:
                print(f"\nCreated {len(result.entity_operations)} content item(s)")
                for op in result.entity_operations:
                    data = op.get("data", {})
                    print(f"  - Type: {data.get('type', 'N/A')}")
                    print(f"    Channel: {data.get('channel', 'N/A')}")
        else:
            print(f"\nError: {result.error}")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This example requires a valid OPENAI_API_KEY environment variable.")

    # Example: Batch content creation
    print("\n\n--- Batch Content Creation ---\n")

    batch_prompts = [
        {
            "prompt": "Create a teaser tweet about the carbon calculator launch",
            "content_type": "SOCIAL_POST",
            "channel": "twitter",
        },
        {
            "prompt": "Write an email subject line and preview text for the calculator announcement",
            "content_type": "EMAIL",
            "channel": "email",
        },
    ]

    print("Batch requests:")
    for i, p in enumerate(batch_prompts, 1):
        print(f"  {i}. {p['channel']}: {p['prompt'][:50]}...")

    print("\n(Batch execution would run here with valid API key)")


if __name__ == "__main__":
    asyncio.run(main())
