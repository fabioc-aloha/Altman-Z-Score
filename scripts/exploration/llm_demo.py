"""
LLM Client Demo - Shows Non-Cached Behavior

This script demonstrates how the LLM client saves prompts and responses 
to ticker folders instead of caching them like other APIs.

Key Points:
- LLM calls are NOT cached (each call can provide different insights)
- All prompts and responses saved to output/{ticker}/llm_interactions/
- Azure OpenAI configuration from environment variables
- Thread-safe file operations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_llm_configuration():
    """Test LLM configuration and environment setup."""
    print("🤖 LLM Configuration Test")
    print("-" * 30)
    
    # Check environment variables
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_DEPLOYMENT"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var:
                masked = f"{value[:8]}..." if len(value) > 8 else "***"
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
    
    if missing_vars:
        print(f"⚠️  Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def test_llm_client_import():
    """Test LLM client import and initialization."""
    print("\n📦 LLM Client Import Test")
    print("-" * 30)
    
    try:
        from altman_zscore.layers.data_fetch.llm_client import LLMClient
        print("✅ LLM client imported successfully")
        
        # Try to initialize (will fail gracefully if config missing)
        try:
            client = LLMClient()
            print("✅ LLM client initialized successfully")
            print(f"   Endpoint: {client.config.endpoint}")
            print(f"   Deployment: {client.config.deployment}")
            return client
        except Exception as e:
            print(f"⚠️  LLM client initialization failed: {e}")
            print("   This is expected if Azure OpenAI is not configured")
            return None
            
    except Exception as e:
        print(f"❌ LLM client import failed: {e}")
        return None

def demo_llm_interaction_logging(client):
    """Demonstrate LLM interaction logging (without actual API calls)."""
    print("\n💾 LLM Interaction Logging Demo")
    print("-" * 30)
    
    if not client:
        print("⚠️  No LLM client - skipping interaction demo")
        return
    
    # Demo ticker
    ticker = "DEMO"
    
    # Check if output directory exists
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ Created output directory: {output_dir}")
    
    # Show where interactions would be saved
    interaction_dir = os.path.join(output_dir, ticker, "llm_interactions")
    print(f"📁 LLM interactions for {ticker} will be saved to:")
    print(f"   {interaction_dir}")
    
    # Demo the logging functionality (without actual API call)
    try:
        # This would be called internally by the LLM client
        from altman_zscore.layers.data_fetch.llm_client import LLMInteractionLogger
        
        logger = LLMInteractionLogger(output_dir)
        
        # Save a demo interaction
        demo_prompt = "Analyze the financial health of DEMO company"
        demo_response = "Based on the financial data, DEMO company shows strong fundamentals..."
        demo_metadata = {
            "temperature": 0.3,
            "max_tokens": 1000,
            "model": "model-router",
            "demo": True
        }
        
        filepath = logger.log_interaction(
            ticker=ticker,
            interaction_type="financial_analysis_demo",
            prompt=demo_prompt,
            response=demo_response,
            metadata=demo_metadata
        )
        
        print(f"✅ Demo interaction saved to: {filepath}")
        
        # Show interaction history
        history = logger.get_interaction_history(ticker)
        print(f"📜 Interaction history for {ticker}: {len(history)} interactions")
        
        if history:
            latest = history[-1]
            print(f"   Latest: {latest['interaction_type']} at {latest['timestamp']}")
        
    except Exception as e:
        print(f"❌ Interaction logging demo failed: {e}")

def show_llm_vs_api_caching():
    """Show the difference between LLM and API caching approaches."""
    print("\n🔄 LLM vs API Caching Comparison")
    print("-" * 30)
    
    print("📊 FMP/Yahoo APIs (CACHED):")
    print("   ✅ Same request → Same cached response (48 hours)")
    print("   ⚡ ~95% faster response time for cache hits")
    print("   💾 Cache stored in .cache/ directory")
    print("   🔄 Cache expires after 48 hours")
    print("   🎯 Goal: Reduce API quota usage")
    
    print("\n🤖 LLM APIs (NOT CACHED):")
    print("   ❌ Same request → Different responses possible")
    print("   🎲 Variability provides fresh insights each time")
    print("   📝 All interactions saved to output/{ticker}/llm_interactions/")
    print("   🔍 Saved for troubleshooting and analysis")
    print("   🎯 Goal: Preserve LLM creativity and variability")
    
    print("\n💡 Key Design Decisions:")
    print("   • Financial data: Cache for efficiency")
    print("   • LLM insights: No cache for variety")
    print("   • All interactions: Logged for debugging")

def main():
    """Run comprehensive LLM demo."""
    print("🎯 LLM Client - Non-Cached API Demo")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_llm_configuration()
    
    # Test import and initialization  
    client = test_llm_client_import()
    
    # Demo interaction logging
    demo_llm_interaction_logging(client)
    
    # Show comparison
    show_llm_vs_api_caching()
    
    print("\n" + "=" * 50)
    print("✅ LLM Client Demo Complete!")
    print("")
    print("🎯 Summary:")
    if config_ok and client:
        print("   🤖 Azure OpenAI: Configured and ready")
        print("   📝 Interactions: Will be saved to ticker folders")
        print("   🚫 Caching: Disabled (intentional for LLM variability)")
    else:
        print("   ⚠️  Azure OpenAI: Not configured (set environment variables)")
        print("   📝 Logging: Ready (will work when configured)")
        print("   🚫 Caching: Disabled by design")
    
    print("")
    print("🔧 To enable LLM functionality:")
    print("   1. Set AZURE_OPENAI_ENDPOINT in .env")
    print("   2. Set AZURE_OPENAI_API_KEY in .env") 
    print("   3. Set AZURE_OPENAI_DEPLOYMENT in .env")
    print("   4. All interactions will be saved to output/{ticker}/llm_interactions/")

if __name__ == "__main__":
    main()
