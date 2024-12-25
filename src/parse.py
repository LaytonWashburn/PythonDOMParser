import tokens
import tables
import logging

# Configure logging
logging.basicConfig(level=logging.INFO) # Change this to INFO to not have the debug and DEBUG for debugging

class StreamReader:
    def __init__(self, data:str):
        self.data = data
        self.index = 0
    
    def next(self):
        if self.index < len(self.data):
            char = self.data[self.index]
            self.index += 1
            return char
        return None

    def rollback(self):
        if self.index == 0:
            return 0
        self.index = self.index - 1
    
    def truncate(self, string:str):
        if len(string) == 0:
            return ""
        return string[:-1], string[len(string)-1]

class Parser:
    def __init__(self, html: str):
        self.html = html.replace("\n", "")#.replace(" ", "")
        self.tokens = []
        self.classifier_table = tables.ClassifierTable('src/classifier_table.csv')
        self.transition_table = tables.Transitiontable('src/transition_table.csv')
        self.token_type_table = tables.TokenTypeTable('src/token_type_table.csv')
        self.dom = None
        self.stream_reader = StreamReader(self.html)
    


    def build_token_list(self):

        state = "START" # Set initial state to start
        lexeme = "" # Set the lexeme to empty string
        current = self.stream_reader.next() # Get the first character

        while current != "END":

            logging.debug("=============== STARTING INTERATION ===============")
            logging.debug(f"Current character: {current}")
            logging.debug(f"Current state: {state}")
            logging.debug(f"Current lexeme: {lexeme}")
                
            token_type = self.token_type_table.getTokenType(state=state)

            if token_type is not None: # If the state is an accept state

                if token_type == "ATTRIBUTE":
                    logging.debug(f"Token Type: Attribute")
                    lexeme, old_char = self.stream_reader.truncate(lexeme) # Remove the last character and return new lexeme and removed character
                    logging.debug(f"Lexeme is: {lexeme}")
                    logging.debug(f"Old char: {old_char}")
                    logging.debug(f"The old index is: {self.stream_reader.index}")
                    self.stream_reader.rollback() # Move the stream reader's index back one
                    logging.debug(f"The new index is: {self.stream_reader.index}")

                    self.tokens.append(tokens.Token(name=self.token_type_table.getTokenType(state=state), 
                                                attribute_value=lexeme))
                    lexeme = ""
                    current = old_char
                    logging.debug(f"Setting current to: {current}")

                elif current == None:
                    self.tokens.append(tokens.Token(name=self.token_type_table.getTokenType(state=state), 
                                               attribute_value=lexeme))
                    current = "END"
                    logging.debug("=============== ENDING INTERATION ===============")
                    continue # This will force the loop to the top and check the condition and then quit
                else:
                    self.tokens.append(tokens.Token(name=self.token_type_table.getTokenType(state=state), 
                                               attribute_value=lexeme))
                    lexeme = ""
                    state = "START"

            lexeme += current # Update the lexeme

            # Update the state : get the new state from the transition table
            state = self.transition_table.getTransition(state=state, transition=self.classifier_table.getClassification(current))
        
            current = self.stream_reader.next() # Get next character

            logging.debug(f"New character: {current}")
            logging.debug(f"New state: {state}")
            logging.debug(f"New lexeme: {lexeme}")
            logging.debug("=============== ENDING INTERATION ===============")

    def get_tokens(self) -> list:
        return self.tokens

    # Main Method for the Parser
    def parse(self):
        self.build_token_list()
        self.dom = tokens.DOM(self.tokens)
        self.dom.build()
        self.dom.get_dom()
    
    def clear_parser(self):
        self.tokens = []
