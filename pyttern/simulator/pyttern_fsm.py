"""
This module contains the FSM class and the Movement enum.
"""

from enum import Enum


class Movement(Enum):
    """
    Enum class for the movements of the FSM.
    We only have three movements: moveto-leftchild, moveto-rightsibling, and moveto-parent.
    """

    MLC = "moveto-leftchild"
    MRS = "moveto-rightsibling"
    MP  = "moveto-parent"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class FSM:
    default_name = 1

    def __init__(self, name=None, var=None, start=None, end=None):
        # transition(next_node: FSM, types: tuple(type), movement: Movement[])
        self.transitions = []
        self.name = str(FSM.default_name)
        self.start = start
        self.end = end

        if name is not None:
            self.name += f" ({name})"
        FSM.default_name += 1
        self.var = var

    def add_transition(self, next_node, func, movement):
        for transition in self.transitions:
            if transition[0] == next_node and transition[1] == func and transition[2] == movement:
                break
        self.transitions.append((next_node, func, movement))
        return self

    def get_transitions(self):
        yield from self.transitions

    def get_out_transitions(self):
        for transition in self.transitions:
            if transition[0] != self:
                yield transition

    def __str__(self):
        return self.name

    @staticmethod
    def get_next_nodes(node, clazz=None):
        visited = set()
        stack = [node]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for next_node, func, _ in node.get_out_transitions():
                if clazz is None or func == clazz:
                    yield next_node
                stack.append(next_node)
