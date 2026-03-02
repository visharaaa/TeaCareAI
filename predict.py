from leaf_evaluator import LeafEvaluator

evaluator = LeafEvaluator()

leaf_input = {
    'Total_Leaf_Area_mm2': 1200,
    'Affected_Area_Pre': 400,
    'Humidity_Pct': 75,
    'Temp_Celsius': 27,
    'Disease_Type_Blister Blight': 1,
    'Disease_Type_Brown Blight': 0,
    'Disease_Type_Grey Blight': 0,
    'Disease_Type_Red Rust': 0,
    'Disease_Type_Red Spider': 0
}

predicted_improvement = evaluator.predict_improvement(leaf_input)
print(f"Predicted Health Improvement: {predicted_improvement} %")