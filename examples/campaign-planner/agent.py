"""
Campaign Planner Agent Example

This example demonstrates how to build a campaign planning agent
that integrates with BigRipple using the wavemaker-agent-framework.
"""

import asyncio
from openai import AsyncOpenAI

from wavemaker_agent_framework.core import (
    AgentRuntime,
    AgentExecutionInput,
    AgentExecutionOutput,
    create_default_runtime,
)
from wavemaker_agent_framework.context import EntityContext, BrandSummary, BrandVoice
from wavemaker_agent_framework.tools.bigripple import create_bigripple_registry


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
4. Recommend content types for each channel

You have access to tools to create campaigns and content in BigRipple.
Always use the provided brand_id when creating entities.

After creating a campaign, summarize what you created and suggest next steps."""


async def run_campaign_planner(
    prompt: str,
    context: EntityContext,
    openai_api_key: str | None = None,
) -> AgentExecutionOutput:
    """
    Run the campaign planner agent.

    Args:
        prompt: User's campaign planning request
        context: Entity context from BigRipple
        openai_api_key: Optional OpenAI API key (uses env var if not provided)

    Returns:
        AgentExecutionOutput with created campaigns and content
    """
    # Create OpenAI client
    client = AsyncOpenAI(api_key=openai_api_key)

    # Create runtime with BigRipple tools
    runtime = create_default_runtime(client, include_bigripple_tools=True)

    # Prepare execution input
    input_data = AgentExecutionInput(
        input_data={"prompt": prompt},
        context=context,
        execution_id=f"campaign_planner_{context.user_id}",
        system_prompt=CAMPAIGN_PLANNER_PROMPT,
        enabled_tools=[
            "bigripple.campaign.create",
            "bigripple.content.create",
            "bigripple.knowledge.search",
            "bigripple.knowledge.guidelines",
        ],
        model="gpt-4o",
        temperature=0.7,
    )

    # Execute the agent
    result = await runtime.execute(input_data)

    return result


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


async def main():
    """Run the campaign planner example."""
    print("Campaign Planner Agent Example")
    print("=" * 50)

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
    """

    print(f"\nUser Prompt:\n{prompt}")
    print("\n" + "=" * 50)

    # Run the agent
    try:
        result = await run_campaign_planner(prompt, context)

        if result.success:
            print("\nAgent Output:")
            print(result.output)
            print(f"\nToken Usage: {result.tokens_used}")
            print(f"Duration: {result.duration_ms}ms")

            if result.entity_operations:
                print(f"\nEntity Operations ({len(result.entity_operations)}):")
                for i, op in enumerate(result.entity_operations, 1):
                    print(f"  {i}. {op['type']}: {op.get('data', {}).get('name', 'N/A')}")

            if result.tool_calls:
                print(f"\nTool Calls ({len(result.tool_calls)}):")
                for call in result.tool_calls:
                    print(f"  - {call['name']}")
        else:
            print(f"\nAgent Error: {result.error}")

    except Exception as e:
        print(f"\nError running agent: {e}")
        print("\nNote: This example requires a valid OPENAI_API_KEY environment variable.")


if __name__ == "__main__":
    asyncio.run(main())
