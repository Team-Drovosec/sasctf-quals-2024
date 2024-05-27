import z3
from random import randint, choice


def rand_bytes(n):
    return bytes([randint(0, 255) for _ in range(n)])


class StringBuilder:
    def __init__(self):
        self._data = []

    def print(self, text, indent=0, end='\n'):
        self._data.append(' ' * indent + text + end)

    def render(self):
        return ''.join(self._data)


class BinaryOperation:
    name = 'unk'

    def __init__(self, left, right, size):
        self.left = left
        self.right = right
        self.size = size

    def __str__(self):
        return '({} {} {})'.format(str(self.left), self.name, str(self.right))

    def __repr__(self):
        return str(self)

    def _render_to_c(self):
        return '({} {} {})'.format(self.left._render_to_c(), self.name, self.right._render_to_c())

    def get_type(self):
        if self.size == 1:
            return 'char'
        elif self.size == 2:
            return 'short'
        elif self.size == 4:
            return 'int'
        else:
            raise NotImplementedError()

    def render_to_c(self, sb, answer, indent=0):
        sb.print('if (({}){} != ({})({}))'.format(self.get_type(), self._render_to_c(), self.get_type(), answer), indent=indent)
        sb.print('return 0;', indent=indent+4)

    def eval_z3(self, data):
        return self.perform(self.left.eval_z3(data), self.right.eval_z3(data))

    def perform(self, left, right):
        raise NotImplementedError()


class Addition(BinaryOperation):
    name = '+'

    def perform(self, left, right):
        return left + right


class Subtraction(BinaryOperation):
    name = '-'

    def perform(self, left, right):
        return left - right


class Xor(BinaryOperation):
    name = '^'

    def perform(self, left, right):
        return left ^ right


class And(BinaryOperation):
    name = '&'

    def perform(self, left, right):
        return left & right


class Or(BinaryOperation):
    name = '|'

    def perform(self, left, right):
        return left | right


class Value:
    def __init__(self, value_slice):
        self.value_slice = value_slice

    def __str__(self):
        return str(self.value_slice)

    def __repr__(self):
        return str(self)

    def eval_z3(self, data):
        if self.value_slice[1] - self.value_slice[0] > 1:
            return z3.Concat(*reversed(extract_list(self.value_slice[1], self.value_slice[0], data)))
        else:
            return extract(self.value_slice[1], self.value_slice[0], data)

    def _render_to_c(self):
        size = self.value_slice[1] - self.value_slice[0]
        if size == 1:
            cast = 'char*'
        elif size == 2:
            cast = 'short*'
        elif size == 4:
            cast = 'int*'
        else:
            raise NotImplementedError()
        start = self.value_slice[0]
        return '*({})(data + {})'.format(cast, start)


def gen_rand_arg(arg_length, data_length):
    start = randint(0, data_length - arg_length)
    end = start + arg_length
    return start, end


def extract(right, left, bv):
    size = bv.size()
    ll = size - left * 8 - 1
    rr = size - right * 8
    return z3.Extract(ll, rr, bv)


def extract_list(right, left, bv):
    return [extract(left + i + 1, left + i, bv) for i in range(right - left)]


def gen_random_system(good_data, eq_count):
    result = []
    for _ in range(eq_count):
        arg_size = choice([1, 2, 4])
        args = [Value(gen_rand_arg(arg_size, len(good_data))) for _ in range(randint(2, 6))]
        ops = [choice([Addition, Subtraction, Xor, And, Or]) for _ in range(len(args) - 1)]

        qu = args
        for op in ops:
            qu.append(op(qu.pop(0), qu.pop(0), arg_size))

        result.append(qu[0])
    return result


def count_system_solutions(good_data, equations):
    sol = z3.Solver()
    x = z3.BitVec('x', 8 * len(good_data))
    y = z3.BitVec('y', 8 * len(good_data))
    sol.add(y == int.from_bytes(good_data, 'big', signed=False))
    for op in equations:
        sol.add(op.eval_z3(x) == op.eval_z3(y))

    answers = []
    solutions = 0
    while sol.check() == z3.sat:
        model = sol.model()
        ans = []
        for op in equations:
            eq = op.eval_z3(y)
            ans.append(model.eval(eq).as_signed_long())
        answers.append(ans)
        sol.add(x != model[x])
        solutions += 1

    return solutions if sol.check() != z3.unknown else -1, answers


def gen_one_solution_system(good_data, ops_count=100):
    while True:
        equations = gen_random_system(good_data, ops_count)
        count, answers = count_system_solutions(good_data, equations)
        if count == 1:
            return equations, answers[0]
        else:
            print(f'system have {count} solutions, trying another')


def render_equations_to_c(equations):
    sb = StringBuilder()
    sb.print('int check6(unsigned char* data) {')
    for op, ans in equations:
        op.render_to_c(sb, ans, indent=4)

    sb.print('return 1;', indent=4)
    sb.print('}')
    return sb.render()


def main():
    good_data = rand_bytes(32)
    eq_count = randint(40, 60)

    ops, answers = gen_one_solution_system(good_data, eq_count)
    code = render_equations_to_c(zip(ops, answers))

    print(f'Used {eq_count} equations')
    print(good_data.hex())
    with open('generated.h', 'w') as f:
        f.write(code)


if __name__ == '__main__':
    main()
