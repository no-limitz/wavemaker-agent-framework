"""
Content Writer Agent Example

This example demonstrates how to build a content writing agent
using the simplified Strands-based wavemaker-agent-framework.
"""

import os
from typing import Literal
from dotenv import load_dotenv

from bigripple import (
    BigRippleAgent,
    AgentResult,
    EntityContext,
    BrandSummary,
    BrandVoice,
    CampaignSummary,
    create_content,
)


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

You have access to the create_content tool to save content in BigRipple.
Always use the provided brand_id when creating entities."""


ContentType = Literal["SOCIAL_POST", "BLOG_POST", "EMAIL", "AD_COPY", "NEWSLETTER"]
Channel = Literal["linkedin", "twitter", "email", "blog", "facebook", "instagram"]


def create_content_agent(api_key: str | None = None) -> BigRippleAgent:
    """Create a content writer agent.

    Args:
        api_key: Optional OpenAI API key (uses env var if not provided)

    Returns:
        Configured BigRippleAgent for content writing
    """
    return BigRippleAgent(
        system_prompt=CONTENT_WRITER_PROMPT,
        api_key=api_key,
        model_id="gpt-4o",
        temperature=0.8,  # Slightly higher for creative writing
        tools=[create_content],
    )


def run_content_writer(
    agent: BigRippleAgent,
    prompt: str,
    context: EntityContext,
    content_type: ContentType = "SOCIAL_POST",
    channel: Channel = "linkedin",
) -> AgentResult:
    """
    Run the content writer agent.

    Args:
        agent: The BigRipple content writer agent
        prompt: User's content request
        context: Entity context from BigRipple
        content_type: Type of content to create
        channel: Target channel for the content

    Returns:
        AgentResult with created content
    """
    # Enhanced prompt with content specifications
    full_prompt = f"""
Content Type: {content_type}
Target Channel: {channel}

Request: {prompt}

Please create content that matches these specifications and follows the brand guidelines.
Use the create_content tool to save the content.
"""

    return agent.run(
        prompt=full_prompt,
        context=context,
        execution_id=f"content_writer_{context.user_id}",
    )


def create_sample_context() -> EntityContext:
    """Create sample context for demonstration."""
    return EntityContext(
        userId="user_demo_123",
        brandId="brand_demo_456",
        brands=[
            BrandSummary(
                id="brand_demo_456",
                name="EcoTech Solutions",
                slug="ecotech-solutions",
                description="Sustainable technology solutions for modern businesses",
            )
        ],
        brandVoice=BrandVoice(
            tone="optimistic and empowering",
            personality=["innovative", "trustworthy", "forward-thinking"],
            vocabulary=[
                "sustainable",
                "innovative",
                "planet-friendly",
                "future-forward",
                "responsible",
            ],
            avoidWords=[
                "greenwashing",
                "guilt-tripping",
                "preachy",
                "doom and gloom",
            ],
            targetAudience="Sustainability officers and CFOs at mid-size companies",
            brandValues=["sustainability", "innovation", "transparency"],
        ),
        campaigns=[
            CampaignSummary(
                id="camp_789",
                name="Earth Month 2024",
                status="ACTIVE",
                channels=["linkedin", "twitter", "email"],
            )
        ],
    )


def main():
    """Run the content writer example."""
    # Load environment variables
    load_dotenv(os.path.expanduser("~/Projects/big-ripple/.env"))

    print("Content Writer Agent Example (Strands SDK)")
    print("=" * 50)

    # Create the agent
    agent = create_content_agent(api_key=os.getenv("OPENAI_API_KEY"))

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
        result = run_content_writer(
            agent=agent,
            prompt=prompt,
            context=context,
            content_type="SOCIAL_POST",
            channel="linkedin",
        )

        if result.success:
            print("\nGenerated Content:")
            print(result.output)
            print(f"\nDuration: {result.duration_ms}ms")

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


if __name__ == "__main__":
    main()
