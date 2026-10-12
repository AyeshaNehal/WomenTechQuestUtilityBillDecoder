import json
import re
import math
from typing import Dict, List, Any
from pydantic import BaseModel
from source import config, safe_eval
from source.providers.google import generate_structured
from source.schema import ExtractionResult

class NamedExpression(BaseModel):
    name: str
    expr: str

class PlanItem(BaseModel):
    question_id: str
    expressions: List[NamedExpression]

class StepAPlan(BaseModel):
    plans: List[PlanItem]

class AnswerItem(BaseModel):
    question_id: str
    answer: str
    supporting_numbers: List[float]
    reason: str

class StepBAnswers(BaseModel):
    answers: List[AnswerItem]

def extract_numbers(text: str) -> List[float]:
    text = text.replace(',', '')
    matches = re.findall(r'-?\d+\.?\d*', text)
    return [float(m) for m in matches]

def check_grounding(answer_nums: List[float], allowed_nums: set) -> bool:
    for n in answer_nums:
        found = False
        for a in allowed_nums:
            if math.isclose(n, a, abs_tol=1.0) or math.isclose(n, round(a), abs_tol=0.1):
                found = True
                break
        if not found:
            return False
    return True

def run_explain(questions: List[Dict[str, str]], result: ExtractionResult, facts: Dict[str, Any]) -> Dict[str, str]:
    if not questions:
        return {}

    context_str = json.dumps({
        "level1": result.level1.model_dump(),
        "extras": result.extras.model_dump(),
        "facts": facts
    }, default=str)
    
    questions_str = json.dumps(questions, indent=2)

    prompt_a = f"""
You are planning calculations to answer customer questions about their electricity bill.
Data: {context_str}
Questions: {questions_str}
For each question_id, provide named Python expressions to calculate the needed numbers.
You can use variables from the data (like `level1['current_bill']` or `facts['usage_avg']`).
If no calculation is needed, return an empty list for that question's expressions.
"""
    try:
        plan_result = generate_structured(prompt_a, None, StepAPlan, task_name='explain_step_a')
    except Exception as e:
        print(f"Step A failed: {e}")
        plan_result = StepAPlan(plans=[PlanItem(question_id=q['question_id'], expressions=[]) for q in questions])

    computed_results = {}
    eval_context = {
        'level1': result.level1.model_dump(),
        'extras': result.extras.model_dump(),
        'facts': facts
    }
    
    for plan in plan_result.plans:
        qid = plan.question_id
        computed_results[qid] = {}
        for expr_obj in plan.expressions:
            name = expr_obj.name
            expr = expr_obj.expr
            if name and expr:
                val = safe_eval.safe_eval(expr, eval_context)
                computed_results[qid][name] = val

    prompt_b = f"""
Answer customer questions based strictly on the bill.
Data: {context_str}
Computed Math Results: {json.dumps(computed_results, default=str)}
Questions: {questions_str}

RULES:
1. Use ONLY plain English.
2. Direct answer first: Start with a direct answer using "PKR" and thousands separators (e.g., PKR 3,430).
3. Number formatting: Format all whole numbers strictly as integers without ".0" (e.g., "PKR 498" instead of "PKR 498.0", and "65 units" instead of "65.0 units").
4. List the specifics: List the specific bill lines or months behind the number.
5. Include percentages: Include the percentage or comparison where relevant.
6. Threshold/Count logic: For threshold/count questions, state if the current month is included and give the count both ways if it differs.
7. Estimates: Label estimates and show the calculation method.
8. Missing values: If the bill lacks the needed value, explicitly say "The bill does not show...".
9. Grounding: Ground every number strictly in the bill data or computed facts.
10. Length: Aim for 2 to 4 sentences.
"""
    try:
        final_answers = generate_structured(prompt_b, None, StepBAnswers, task_name='explain_step_b')
    except Exception as e:
        print(f"Step B failed: {e}")
        return {q['question_id']: "Information unavailable or calculation failed." for q in questions}

    output = {}
    for item in final_answers.answers:
        output[item.question_id] = item.answer

    return output
