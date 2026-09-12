import os
from pathlib import Path

from camunda_orchestration_sdk import (  # type: ignore[import-unresolved]
    CamundaClient,
    DecisionEvaluationByIdVariables,
    DecisionEvaluationByKey,
)

os.environ.setdefault("CAMUNDA_REST_ADDRESS", "http://127.0.0.1:8080/v2")
os.environ.setdefault("CAMUNDA_AUTH_STRATEGY", "NONE")

client = CamundaClient()
dmn_path = Path(__file__).with_name("TNSNAP.dmn")
deployment = client.deploy_resources_from_files([dmn_path])
decision_key = deployment.decisions[0].decision_definition_key

test_cases = [
    # (gross_income, net_income, household_size, expected_benefit)
    (2608, 1304, 1, 298),
    (2608, 1305, 1, 0),   
    (2609, 1305, 1, 0),  
    (5000, 1200, 1, 0),   
    (10000, 5000, 8, 0),  
    (6344, 2695 ,12, 2661)
]

for gross, net, size, expected in test_cases:
    variables = DecisionEvaluationByIdVariables.from_dict({
        "Gross Income": gross,
        "Net Income": net,
        "Household Size": size
    })
    evaluation = client.evaluate_decision(
        data=DecisionEvaluationByKey(
            decision_definition_key=decision_key,
            variables=variables,
        )
    )
    result = int(evaluation.output)
    passed = result == expected
    print(
        f"size={size} gross={gross} net={net} -> "
        f"{result} (expected {expected}) {'PASS' if passed else 'FAIL'}"
    )
    if not passed:
        raise AssertionError(f"Expected {expected}, got {result}")
