import sys


class SimpleDB:
    """
    Simple in-memory key-value database with transactional blocks
    Does not support boolean or falsey values
    'stack' stores a list of layers of blocks, each item is pair of dictionaries for key/value data
    """
    stack = [[{}, {}]]
    transactional_block = 0

    def set(self, name, value):
        if self.get(name):
            self.helper_remove_value(name)
        self.stack[self.transactional_block][0][name] = value
        self.stack[self.transactional_block][1][value] = self.numequalto(value) + 1
        return False

    def get(self, name):
        i = self.transactional_block
        while i > 0 and not self.stack[i][0].get(name):
            i -= 1
        return self.stack[i][0].get(name)

    def unset(self, name):
        if self.get(name):
            self.helper_remove_value(name)
            if self.transactional_block == 0:
                del self.stack[0][0][name]
            else:
                self.stack[self.transactional_block][0][name] = None
        return False

    def numequalto(self, value):
        i = self.transactional_block
        while i >= 0:
            if self.stack[i][1].get(value):
                return self.stack[i][1][value]
            else:
                i -= 1
        return 0

    def end(self):
        sys.exit()

    def begin(self):
        self.transactional_block += 1
        self.stack.append([{}, {}])
        return False

    def rollback(self):
        if self.transactional_block == 0:
            return "INVALID ROLLBACK"
        self.transactional_block -= 1
        self.stack.pop()
        return False

    def commit(self):
        if self.transactional_block == 0:
            return False
        names, values = self.stack.pop()
        self.transactional_block -= 1
        while self.transactional_block > 0:
            names, values = self.helper_combine_two_levels(names, values)
            self.transactional_block -= 1
        names, values = self.helper_combine_two_levels(names, values)
        self.stack = [[self.helper_remove_nulls(names), self.helper_remove_nulls(values)]]
        return False

    def helper_combine_two_levels(self, names, values):
        # combine pair of dictionaries in arguments with last pair on stack, priority to arguments
        older_main, older_values = self.stack.pop()
        for entry in older_main:
            if not names.get(entry):
                names[entry] = older_main[entry]
        for entry in older_values:
            if not values.get(entry):
                values[entry] = older_values[entry]
        return names, values

    def helper_remove_nulls(self, dic):
        # remove 0/None values for better memory usage
        for entry in dic:
            if not dic[entry]:
                del dic[entry]
        return dic

    def helper_remove_value(self, name):
        # adjusts (number of) value in values hash, useful when changing value or removing key
        self.stack[self.transactional_block][1][self.get(name)] = self.numequalto(self.get(name)) - 1
        if self.transactional_block == 0 and self.stack[0][1][self.get(name)] == 0:
            del self.stack[0][1][self.get(name)]
        return False


def main():
    newDB = SimpleDB()
    while True:
        command = raw_input().split()
        try:
            func = getattr(newDB, command[0].lower())
            result = func(*command[1:])
            if type(result) != bool:
                print result
        except AttributeError:
            print "Operation not allowed"
        except TypeError:
            print "Wrong input for this operation"
        except:
            print "Something went wrong"

if __name__ == "__main__":
    main()
