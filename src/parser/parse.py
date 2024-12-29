from parser.tokens import Token
from parser.tables import ClassifierTable, Transitiontable, TokenTypeTable
from parser.scan_stream import StreamReader
import logging


class Parser:
    def __init__(self, html: str):
        self.html = html.replace("\n", "")
        self.tokens = []
        self.classifier_table = ClassifierTable('src/tables/classifier_table.csv')
        self.transition_table = Transitiontable('src/tables/transition_table_new.csv')
        self.token_type_table = TokenTypeTable('src/tables/token_type_table_new.csv')
        self.stream_reader = StreamReader(self.html)
        self.dom = None
    
    def add(self, token:Token):
        logging.debug(f"Adding token to list: token_type={token.get_name()}, lexeme={token.get_attribute()}")
        self.tokens.append(token)


    # Build token list from inputted html
    def build_token_list(self):
        logging.debug("=============== Building Token List ===============")
        while not self.stream_reader.eof:
            token:Token|None = self.next_token()
            if token is not None:
                self.add(token)
        logging.debug("=============== Finished Building Token List ===============")

    """
        Method: next_token
        Purpose:
        Notes: 
            + None is the error state
    """
    def next_token(self):
        logging.debug("=============== Getting Next Token ===============")
        stack = []
        curr = 0
        cat = None
        state = "START"
        lexeme = ""

        # Clear stack and push "bad" to the stack
        stack.append("bad")

        # While not in the error state
        while state != None: # state.compareTo("error") != 0){
            try:
                curr = self.stream_reader.next(); # This throws an eof error // Gets the next character
                if curr is None:
                    self.stream_reader.set_eof(True)
                    
            except Exception as e:
                state = None # "error" # This might need to be none
                curr = 0
        
            if curr is not None:
                lexeme += curr; # Append curr to the end of lexeme

            accept = self.token_type_table.getTokenType(state=state)
            # If an accept state clear stack
            if accept is not None:
                stack.clear()
            

            stack.append(state); # Push state onto stack

            cat = self.classifier_table.getClassification(curr) # Get the current character's Category
            state = self.transition_table.getTransition(state=state, transition=cat) # Get the new State from the TransitionTable given the current state and cat

        # While not an accept state and state is not "bad"
        accept = self.token_type_table.getTokenType(state=state) 
        while accept is None and state != "bad":
            state = stack.pop() # Pop the stack and set result as the new state
            accept = self.token_type_table.getTokenType(state=state) 

        # Try to remove the last character from lexeme and rollback the ss iterator or throw an exception and continue
        try:
            lexeme = self.stream_reader.truncate(string=lexeme)
            self.stream_reader.rollback() 
        except Exception as e:
            print(f"An error occurred: {e}")

        # If an accept state return a Token with the type and lexeme or return error
        if self.token_type_table.getTokenType(state=state) is not None and state != "bad":
            logging.debug("=============== Returning Token ===============")
            return Token(name=self.token_type_table.getTokenType(state=state), attribute_value=lexeme) # new Token(getTokenType(state), lexeme)
        else:
            logging.debug("=============== Returning None ===============")
            return None
        

    
    def get_tokens(self) -> list:
        return self.tokens


    def print_tokens(self) -> None:
        logging.debug("=============== PRINTING TOKEN INFORMATION ===============")
        for token in self.tokens:
            logging.debug(f"Token: {token.get_name()} : {token.get_attribute()}")

    # Main Method for the Parser
    def parse(self):
        self.build_token_list()
    
    def clear_parser(self):
        self.tokens = []




