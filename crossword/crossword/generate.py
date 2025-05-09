import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            new_words = set()  # maintain new words
            for word in self.domains[var]:
                if len(word) == var.length:  # check unary constraint
                    new_words.add(word)  # add word if consistent
            self.domains[var] = new_words  # assign node consistent words to domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        if self.crossword.overlaps[x, y] is None:  # return if no overlap
            return revised
        else:
            x_char_index = self.crossword.overlaps[x, y][0]  # x's character
            y_char_index = self.crossword.overlaps[x, y][1]  # y's matching position

            x_words = self.domains[x]
            new_words = set()

            # for each word in x's domain check if any word in y has same character at intersection
            for word in x_words:
                is_consistent = False
                for word_y in self.domains[y]:
                    if word[x_char_index] == word_y[y_char_index]:
                        is_consistent = True  # consistent so break
                        break

                if is_consistent:
                    new_words.add(word)  # add word
                else:
                    revised = True  # if some word missed means revised

            self.domains[x] = new_words
            return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        arcs_list = []
        if arcs is not None:
            arcs_list = arcs
        else:
            # create a list of arcs
            for vars in self.crossword.overlaps:
                arcs_list.append((vars[0], vars[1]))

        while len(arcs_list) != 0:
            arc = arcs_list.pop(0)  # take the frst variable in list
            if self.revise(arc[0], arc[1]):  # revise each arc
                if len(self.domains[arc[0]]) == 0:  # no solution possible
                    return False
                # update arcs_list to re-revise with new domains
                for z in self.crossword.neighbors(arc[0]):
                    if z != arc[1]:
                        arcs_list.append((z, arc[0]))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        is_complete = True
        for var in self.crossword.variables:
            if var not in assignment or len(assignment[var]) <= 0:
                return False

        return is_complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        is_consistent = True
        all_values = []
        for var in assignment:
            all_values.append(assignment[var])
            if len(assignment[var]) != var.length:  # check unary constraint
                return False

            for neighbor in self.crossword.neighbors(var):  # check binary constraint
                overlap = self.crossword.overlaps[var, neighbor]
                # check only the neighbors which are already assigned values
                if neighbor in assignment and assignment[var][overlap[0]] != assignment[neighbor][overlap[1]]:
                    return False

        if len(all_values) != len(set(all_values)):  # check all distinct values
            return False

        return is_consistent

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # keep track of changes for value in domain of var
        changes = dict()
        for word in self.domains[var]:
            vals_ruled_out = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    # check if any word in neighbour gets ruled out
                    for n_word in self.domains[neighbor]:
                        if word[overlap[0]] != n_word[overlap[1]]:
                            vals_ruled_out += 1
            changes[word] = vals_ruled_out  # populate the dict

        return sorted(changes, key=changes.get)  # convert to sorted list of keys

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        domain_val_count = dict()

        for var in self.crossword.variables:
            if var not in assignment:
                domain_val_count[var] = len(self.domains[var])

        sorted_vars = sorted(domain_val_count.items(), key=lambda item: item[1])

        # check if least value is tied
        tied_vars = []

        for var in sorted_vars:
            if var[1] == sorted_vars[0][1]:
                tied_vars.append(var)
            else:
                break

        if len(tied_vars) == 1:
            return tied_vars[0][0]

        # if tied go for least-degree heuristic
        final_sort = sorted(tied_vars, key=lambda item: len(self.crossword.neighbors(item[0])))

        return final_sort[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)

        for val in self.order_domain_values(var, assignment):
            assignment[var] = val  # add {var:val} to assignment
            if self.consistent(assignment):  # check if consistent

                # arcs for the selected var
                arcs = [(neighbor, var) for neighbor in self.crossword.neighbors(var)]

                # interleave search if cannot enforece arc consistency with the new assignment
                if self.ac3(arcs) is None:
                    del assignment[var]
                    return None

                # recursively backtrack with this new assignment
                result = self.backtrack(assignment)
                if result is not None:  # if no issue, means found a solution so return the assignment
                    return result
            else:
                del assignment[var]  # not consistent so remove {var:val}
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
