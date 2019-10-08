import json


continueStatements = ["CONTINUE", "NEXT", "NEXT SCENE", "LETS GO TO THE NEXT SCENE", "GO TO THE NEXT SCENE", "GO TO NEXT SCENE"]

def typeOfStatement(statement):
    if statement in continueStatements:
        return "cont"