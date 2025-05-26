import re

raw_llm_response = 'Search Queries:\n1. Query: "Large Language Model" "material design" "material synthesis" | Description: This query targets papers discussing the application of LLMs for generating, designing, or proposing new materials and their synthetic routes.\n2. Query: "LLM" "synthesis prediction" "material property prediction" "explainable AI chemistry" | Description: This query focuses on the LLMs\' capability to predict material properties or synthesis pathways, and the explainability of such predictions in chemical contexts.\n3. Query: "LLM" "materials discovery" "evaluation" "performance assessment" "benchmarking" | Description: This query aims to find papers that critically evaluate the effectiveness, performance, and limitations of LLM-based approaches in material discovery and synthesis.\n4. Query: "generative AI" "materials science" "computational chemistry" "autonomous synthesis" "feasibility" | Description: This query broadens the scope to generative AI (including LLMs) in materials science, focusing on computational methods, autonomous synthesis, and the practical feasibility of these approaches.\n5. Query: "Large Language Model" "novel materials" "advanced materials" "chemical synthesis" | Description: This query specifically looks for research where LLMs are used for the discovery and synthesis of novel or advanced materials, emphasizing the chemical synthesis aspect.'

query_pattern = r"^\d+\.\s*Query:\s*(.+?)\s*\|\s*Description:\s*(.+?)$"

matches = re.findall(query_pattern, raw_llm_response, re.MULTILINE)

print("--- Regex Parser Test Results ---")
print("Raw LLM Response (first 100 chars):")
print(raw_llm_response[:100] + "...")
print("\nQuery Pattern:")
print(query_pattern)
print("\nMatches Found:")
if matches:
    for i, match in enumerate(matches):
        print(f"  Match {i+1}:")
        print(f"    Query: {match[0]}")
        print(f"    Description: {match[1]}")
else:
    print("  No matches found.")
print("--- End of Regex Parser Test Results ---")
