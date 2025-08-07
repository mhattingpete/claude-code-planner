#!/usr/bin/env python3
"""
Example of using the Design Assistant Simulator programmatically.
"""

import asyncio
from pathlib import Path

from claude_code_designer.simulator import DesignSimulator, ScenarioGenerator


async def run_single_cycle_example():
    """Example: Run a single simulation cycle."""
    print("🔬 Single Cycle Simulation Example")
    print("=" * 40)
    
    simulator = DesignSimulator(
        conversation_dir="./example_simulation_conversations",
        evaluation_dir="./example_simulation_evaluations", 
        results_dir="./example_simulation_results"
    )
    
    # Generate a specific app scenario
    generator = ScenarioGenerator()
    app_scenario = generator.generate_app_scenario()
    
    print(f"Generated scenario: {app_scenario.name}")
    print(f"Type: {app_scenario.scenario_type}")
    print(f"Description: {app_scenario.description}")
    
    # Run the cycle
    result = await simulator.run_single_cycle(app_scenario)
    
    if result["success"]:
        print(f"✅ Cycle completed successfully!")
        if result["design_session"]:
            print(f"   Messages: {result['design_session']['output']['message_count']}")
        if result["evaluation"]:
            print(f"   Evaluation messages: {result['evaluation'].get('message_count', 'N/A')}")
    else:
        print(f"❌ Cycle failed: {result['error']}")
    
    return result


async def run_small_simulation_loop():
    """Example: Run a small simulation loop."""
    print("\n🔄 Small Simulation Loop Example")
    print("=" * 40)
    
    simulator = DesignSimulator(
        conversation_dir="./example_simulation_conversations",
        evaluation_dir="./example_simulation_evaluations",
        results_dir="./example_simulation_results"
    )
    
    # Run 3 cycles with 1 second delay
    results = await simulator.run_simulation_loop(
        max_cycles=3,
        delay_seconds=1.0,
        scenario_type=None  # Mixed scenarios
    )
    
    print(f"Completed {len(results)} cycles")
    successful = sum(1 for r in results if r["success"])
    print(f"Success rate: {successful}/{len(results)} ({successful/len(results):.1%})")
    
    return results


async def test_scenario_generator():
    """Example: Test the scenario generator."""
    print("\n🎯 Scenario Generator Test")
    print("=" * 40)
    
    generator = ScenarioGenerator()
    
    print("App scenarios:")
    for i in range(3):
        scenario = generator.generate_app_scenario()
        print(f"  {i+1}. {scenario.name} ({scenario.parameters['project_type']})")
    
    print("\nFeature scenarios:")
    for i in range(3):
        scenario = generator.generate_feature_scenario()
        print(f"  {i+1}. {scenario.name[:50]}...")
    
    print("\nRandom scenarios:")
    for i in range(3):
        scenario = generator.generate_random_scenario()
        print(f"  {i+1}. {scenario.scenario_type}: {scenario.name[:40]}...")


async def cleanup_example_files():
    """Clean up example simulation files."""
    print("\n🧹 Cleaning up example files...")
    
    dirs_to_clean = [
        "./example_simulation_conversations",
        "./example_simulation_evaluations", 
        "./example_simulation_results"
    ]
    
    import shutil
    
    for dir_path in dirs_to_clean:
        path = Path(dir_path)
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed: {dir_path}")
    
    print("✅ Cleanup completed")


if __name__ == "__main__":
    print("🚀 Design Assistant Simulator Examples")
    print("=" * 50)
    
    # Test scenario generation
    asyncio.run(test_scenario_generator())
    
    # Run single cycle
    asyncio.run(run_single_cycle_example())
    
    # Run small loop
    asyncio.run(run_small_simulation_loop())
    
    # Clean up
    asyncio.run(cleanup_example_files())