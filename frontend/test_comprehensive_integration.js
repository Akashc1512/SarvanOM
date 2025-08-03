/**
 * Test script to verify comprehensive query integration
 * This script tests the frontend-backend integration for the comprehensive query feature
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function testComprehensiveQuery() {
  console.log("🧪 Testing Comprehensive Query Integration...");
  
  try {
    // Test 1: Submit a comprehensive query
    console.log("\n1. Testing query submission...");
    const response = await fetch(`${API_URL}/query/comprehensive`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token' // Add auth if needed
      },
      body: JSON.stringify({
        query: "What are the latest developments in quantum computing?",
        context: "research",
        preferences: {
          factcheck: true,
          citations: true,
          priority: "normal"
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("✅ Query submitted successfully");
    console.log("Query ID:", data.query_id);
    console.log("Status:", data.status);

    // Test 2: Check if answer contains citations
    if (data.answer) {
      console.log("\n2. Testing citation parsing...");
      const hasCitations = /\[\d+\]/.test(data.answer);
      console.log(hasCitations ? "✅ Answer contains citations" : "⚠️ No citations found in answer");
      
      if (data.sources && data.sources.length > 0) {
        console.log("✅ Sources provided:", data.sources.length);
        data.sources.forEach((source, index) => {
          console.log(`  ${index + 1}. ${source.title} (${source.url})`);
        });
      } else {
        console.log("⚠️ No sources provided");
      }
    }

    // Test 3: Verify fact-checking integration
    console.log("\n3. Testing fact-checking integration...");
    if (data.confidence !== undefined) {
      console.log("✅ Confidence score provided:", data.confidence);
    } else {
      console.log("⚠️ No confidence score");
    }

    console.log("\n🎉 Comprehensive query integration test completed successfully!");
    
  } catch (error) {
    console.error("❌ Test failed:", error.message);
    console.error("Full error:", error);
  }
}

// Run the test
testComprehensiveQuery(); 