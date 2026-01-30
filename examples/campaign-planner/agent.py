"""
Campaign Planner Agent Example

This example demonstrates how to build a campaign planning agent
using the simplified Strands-based wavemaker-agent-framework.
"""

import os
from dotenv import load_dotenv

from wavemaker_agent_framework import (
    BigRippleAgent,
    EntityContext,
    BrandSummary,
    BrandVoice,
    create_campaign,
    create_content,
)


# System prompt for the campaign planner
CAMPAIGN_PLANNER_PROMPT = """You are an expert marketing campaign planner for BigRipple.

Your role is to help users create effective marketing campaigns based on their:
- Brand identity and voice
- Target audience
- Marketing goals
- Available channels

When creating campaigns:
1. Consider the brand's tone and style guidelines
2. Suggest appropriate channels based on the target audience
3. Create campaigns with clear goals and descriptions
4. Also create initial content pieces for each channel

You have access to tools to create campaigns and content in BigRipple.
Always use the provided brand_id when creating entities.

After creating a campaign, summarize what you created and suggest next steps."""


def create_sample_context() -> EntityContext:
    """Create sample context for demonstration."""
    return EntityContext(
        userId="user_demo_123",
        brandId="brand_demo_456",
        brands=[
            BrandSummary(
                id="brand_demo_456",
                name="TechStartup Inc",
                slug="techstartup-inc",
                description="B2B SaaS company focused on productivity tools",
            )
        ],
        brandVoice=BrandVoice(
            tone="professional",
            personality=["innovative", "helpful", "straightforward"],
            vocabulary=["innovative", "efficient", "collaborative", "streamlined"],
            avoidWords=["jargon", "buzzwords", "aggressive sales language"],
            targetAudience="B2B decision makers and team leads at growing companies",
            brandValues=["efficiency", "collaboration", "simplicity"],
        ),
        campaigns=[],
    )


def main():
    """Run the campaign planner example."""
    # Load environment variables
    load_dotenv(os.path.expanduser("~/Projects/big-ripple/.env"))

    print("Campaign Planner Agent Example (Strands SDK)")
    print("=" * 50)

    # Create the agent with BigRipple tools
    agent = BigRippleAgent(
        system_prompt=CAMPAIGN_PLANNER_PROMPT,
        api_key=os.getenv("OPENAI_API_KEY"),
        model_id="gpt-4o",
        tools=[create_campaign, create_content],
    )

    # Create sample context
    context = create_sample_context()

    # Sample prompt
    prompt = """
    Create a product launch campaign for our new AI-powered analytics feature.

    Goals:
    - Generate awareness among existing customers
    - Drive 500 free trial signups in the first month
    - Establish thought leadership in the AI analytics space

    Target channels: LinkedIn, Twitter, and Email
    Launch date: Next Monday

    Please create the campaign AND 3 initial content pieces (one for each channel).
    """

    print(f"\nUser Prompt:\n{prompt}")
    print("\n" + "=" * 50)

    # Run the agent
    try:
        result = agent.run(
            prompt=prompt,
            context=context,
            execution_id="campaign_planner_demo",
        )

        if result.success:
            print("\nAgent Output:")
            print(result.output)
            print(f"\nDuration: {result.duration_ms}ms")

            if result.entity_operations:
                print(f"\nEntity Operations ({len(result.entity_operations)}):")
                for i, op in enumerate(result.entity_operations, 1):
                    op_type = op.get("type", "unknown")
                    name = op.get("data", {}).get("name") or op.get("data", {}).get("title", "N/A")
                    print(f"  {i}. {op_type}: {name}")
        else:
            print(f"\nAgent Error: {result.error}")

    except Exception as e:
        print(f"\nError running agent: {e}")
        print("\nNote: This example requires a valid OPENAI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
