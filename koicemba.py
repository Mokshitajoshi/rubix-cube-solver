class KociembaSolver:
    def __init__(self):
    
        self.moves =  ["F", "F'", "F2", "B", "B'", "B2",
                         "U", "U'", "U2", "D", "D'", "D2",
                         "L", "L'", "L2", "R", "R'", "R2"]  
        self.phase1_pruning = {}  
        self.phase2_pruning = {}  

    def solve(self, state):
        phase1_solution = self.ida_phase1(state)
        state = self.apply_moves(state, phase1_solution)
        phase2_solution = self.ida_phase2(state)
        return phase1_solution + phase2_solution

    def ida_phase1(self, state):
        
        pass

    def ida_phase2(self, state):
       
        pass

    def apply_moves(self, state, moves):
    
        pass