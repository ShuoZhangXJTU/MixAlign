BASIC_TEMPLATE = {
    'user_simulator': {
        "template": "You are a user of a QA system. You know: '{detail}'. "
                    "You just asked '{question}' and the system throw back a clarifying question '{sys_question}'."
                    "Please answer the clarifying question precisely. Do not respond with anything else besides the primary subject asked by the clarifying question."
                    "\nAnswer:",
        "input_variables": ["question", "detail", 'sys_question']
    },
    'answer-select': {
            "template": "Answer candidate: {grounding}\n\nClarifying information: {clarify}\n\nQuestion: {question}\n\nAnswer the question.",
            "input_variables": ["grounding", "clarify", 'question']
        },
    'describe_attributes': {
        "template": "Column names along with potential values:\n{attribute}\n\n"
                    "Generate a concise phrase that accurately describes each column name. "
                    "If the column names lack sufficient semantic clarity or descriptiveness, furnish them with additional context or explanations. "
                    "Respond with list of 'column name: meaning of it'",
        "input_variables": ["attribute"]
    },
    'extract_constraints': {
        "template": "Your assignment is to meticulously examine the supplied question, "
                    "discerning any phrases or subquestions that act as conditions or constraints relating to each column name. You must not consider the primary subject of the question as a condition or constraint. "
                    "The desired output should be in the form of 'column-span' pairs, where the 'span' signifies the corresponding condition or constraint embedded in the question. "
                    "If you are not confident that there's an applicable span for a column, signify this with 'None'."
                    "\n\nInput:\n\nQuestion: {question}\n\nColumn names with representative values:\n\n{columns}\n\nOutput:\nColumn|Condition\n",
        "input_variables": ["question", "columns"]
    },
    'confident_match_values': {
        "template": "Evaluate the constraint \"{constraint}\" in the question and inference the corresponding option it refers to. "
                    "If there is any ambiguity or uncertainty, where multiple options seem equally probable, or no options clearly match, respond with \"None\"."
                    "\n\nQuestion: {question}\n\nOptions:\n\n{options}\n\nYour response should be in the format: \"{constraint} refers to [detailed option content]\", or \"None\" if no confident match is found.\n\n",
        "input_variables": ["constraint","question", "options"]
    },
    'align-ask': {
        "template": "You are not confident about which value in '{grounding}' the '{question}' refers to. "
                    "Generate a clarifying question for the user to confirm the value. The user does not know the values in advance, you have to present them to the user.\n\n"
                    "Clarifying question:",
        "input_variables": ["question", "grounding"]
    },
    'select-and-ask': {
        "template": "Context:\n{grounding}\n\nUser question: {question}\n\n"
                    "To answer the user question within the context, choose an attribute from {attrs} that distinguishes the candidates in the context and is also likely for the user to know or respond to."
                    " Then, pose a clarifying question to confirm the attribute's value. Respond with the clarifying question only.",
        "input_variables": ["grounding", "question", "attrs"]
    },

    'e2e-hallucination': {
        "template": "Human Evaluation of Question Answering Systems:\n\n"
                    "Factual Consistency: Does the system answer untruthful or misleading facts that are not supported by the question, context, and gold answer?\n\n"
                    "Question:\n{question}\nContext:\n{context}\nGold Answer\n:{gold}\nModel answer: {summary}\n\nDoes the model answer contain factual inconsistency?\nAnswer:",
        "input_variables": ["question", "context", "gold", "summary"]
    },
    'e2e-coverage': {
        "template": "Human Evaluation of Question Answering Systems:\n\n"
                    "Coverage: Is the system answer consistent with the gold answer?\n\n"
                    "Gold Answer:\n{gold}\nModel answer: {summary}\n\nDoes the system answer cover the gold answer?\nAnswer:",
        "input_variables": ["gold", "summary"]
    },
    'e2e-accept': {
        "template": "Human Evaluation of Clarifying Information:\n\n"
                    "Same-ask: A clarifying question is considered same-ask with the origin question if it asks the exact same thing the original question asks or it seeks the same answer as the original question does, i.e., the gold answer.\n\n"
                    "Ask for a related factor rather than the asked thing in the origin factor is not Same-ask."
                    "For instance, if the original question is about 'country', a clarifying question is same-ask if it also asks about 'country', but not same-ask if it asks about 'city'.\n\n"
                    "Original question:\n{question_ori}\nClarifying question: {question_clr}\nGold answer: {gold}\n\nIs the clarifying question same-ask? Say Yes or No first before you illustrate.\nAnswer: ",
        "input_variables": ["question_ori", "question_clr", "gold"]
    }
}


# ---------------------------------------------------------------------------------------------------
