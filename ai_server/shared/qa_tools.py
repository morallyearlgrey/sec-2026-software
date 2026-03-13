# will be qa tools
import re

# not empty
def is_empty(input: str) -> bool:
    if(input==""):
        return True;

    else:
        return False;

# character length
# max 600 characters, 90 words approx
def is_valid_len(input: str) -> bool:
    if(len(input)<600 and len(input)>3):
        return True;

    else:
        return False;

# clean
def clean(input: str) -> str:
    # delete symbols, split up words
    re.sub(r'[^a-zA-Z0-9\s]', ' ', input);
    new_input = input.split(" ");
    return new_input;

# all
def prechecks(input: str) -> dict: 
    input = input.strip();
    if(is_empty(input)==False):
        new_input = clean(input);

        if(is_valid_len(new_input)):
            return {"validity": True, "reason": "good to go"};

        else:
            return {"validity": False, "reason": "response is greater than 600 characters or less than 3 characters"};

    else:
        return {"validity": False, "reason": "response is empty"};



