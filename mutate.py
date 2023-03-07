import os
import sys
import ast
import astor
import random
import copy

def main():
    if len(sys.argv) != 3:
        sys.exit("Incorrect arguments")

    output_count = int(sys.argv[2])

    #seed random generator with num of output mutations
    random.seed(output_count)
    
    with open(sys.argv[1], "r") as source:
        tree = ast.parse(source.read())
        tree_orig = copy.deepcopy(tree)
    
        for i in range(output_count):
            visitor = MyVisitor()
            visitor.visit(tree)
            tree = MyTransformer(visitor).visit(tree)
            ast.fix_missing_locations(tree)
            filename = str(i) + ".py"
            if os.path.exists(filename):
                os.remove(filename)
            f = open(filename, "x")
            astor.dump_tree(tree)

            f.write(astor.to_source(tree))
            f.close()
            tree = copy.deepcopy(tree_orig)


class MyVisitor(ast.NodeVisitor):

    def __init__(self):   
        self.BinOps = 0
        self.Compares = 0    
        self.BoolOps = 0
        self.Calls = 0 
        self.Assigns = 0

    def visit_BinOp(self, node):
        print("Visitor sees a BinOp: ", ast.dump(node), " aka ", astor.to_source(node))
        print(node.left, ", ", node.op, ", ", node.right)
        self.BinOps += 1
    
    def visit_Compare(self, node):
        print("Visitor sees a Compare: ", ast.dump(node), " aka ", astor.to_source(node))
        print(node.left, ", ", node.ops, ", ", node.comparators)
        self.Compares += 1
    
    def visit_BoolOp(self, node):   
        print("Visitor sees a BoolOp: ", ast.dump(node), " aka ", astor.to_source(node))
        print(node.op, ", ", node.values)
        self.BoolOps += 1
    
    def visit_Call(self, node):
        print("Visitor sees a Call: ", ast.dump(node), " aka ", astor.to_source(node))
        self.Calls += 1


class MyTransformer(ast.NodeTransformer):
    
    def __init__(self, visitor):
        self.BinOpChance = 0
        self.CompareChance = 0
        self.BoolOpChance = 0
        self.CallChance = 0
        self.AssignChance = 0

        if visitor.BinOps != 0:
            self.BinOpChance = 1.0 / float(visitor.BinOps)
        
        if visitor.Compares != 0:
            self.CompareChance = 1.0 / float(visitor.Compares)
               
        if visitor.BoolOps != 0:
            self.BoolOpChance = 1.0 / float(visitor.BoolOps)

        if visitor.Calls != 0:
            self.CallChance = 1.0 / float(visitor.Calls)

    def visit_BinOp(self, node):
        if random.random() >= self.BinOpChance:
            self.generic_visit(node)
            return node
    
        new_node = copy.deepcopy(node)
        if isinstance(node.op, ast.Add):
            new_node.op = ast.Sub()
        elif isinstance(node.op, ast.Sub):
             new_node.op = ast.Add()
        elif isinstance(node.op, ast.Mult):
            new_node.op = ast.Div()
        elif isinstance(node.op, ast.Div):
            new_node.op = ast.Mult()

        self.generic_visit(node)
        return ast.copy_location(new_node, node)

    def visit_Compare(self, node):
        if random.random() >= self.CompareChance:
            self.generic_visit(node)
            return node
        
        if isinstance(node.left, ast.Name) and node.left.id == "__name__":
            self.generic_visit(node)
            return node
        
        new_node = copy.deepcopy(node)
        for i, op in enumerate(node.ops):
            if isinstance(op, ast.Eq):
                new_node.ops[i] = ast.NotEq()
            elif isinstance(op, ast.NotEq):
                new_node.ops[i] = ast.Eq()
            elif isinstance(op, ast.Lt):
                new_node.ops[i] = ast.Gt()                
            elif isinstance(op, ast.LtE):
                new_node.ops[i] = ast.GtE()
            elif isinstance(op, ast.Gt):
                new_node.ops[i] = ast.Lt()
            elif isinstance(op, ast.GtE):
                new_node.ops[i] = ast.LtE()
            elif isinstance(op, ast.Is):
                new_node.ops[i] = ast.IsNot()
            elif isinstance(op, ast.IsNot):
                new_node.ops[i] = ast.Is()
            elif isinstance(op, ast.In):
                new_node.ops[i] = ast.NotIn()
            elif isinstance(op, ast.NotIn):
                new_node.ops[i] = ast.In()

        self.generic_visit(node)
        return ast.copy_location(new_node, node)

    def visit_Call(self, node):
        if random.random() >= self.CallChance:
            self.generic_visit(node)
            return node

        new_node = ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=[], keywords=[])

        self.generic_visit(node)
        return ast.copy_location(new_node, node)


#switch ands and ors potentially
    def visit_BoolOp(self, node):
        if random.random() >= self.BoolOpChance:
            self.generic_visit(node)
            return node
        else:

            new_node = copy.deepcopy(node)

            if isinstance(node.op, ast.And):
                new_node.op = ast.Or()
            elif isinstance(node.op, ast.Or):
                new_node.op = ast.And()

            self.generic_visit(node)
            return ast.copy_location(new_node, node)

if __name__ == "__main__":
    main()
