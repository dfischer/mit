# External extra instructions.
#
# (c) Mit authors 1994-2019
#
# The package is distributed under the MIT/X11 License.
#
# THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
# RISK.

from enum import Enum, unique

from mit_core.instruction import AbstractInstruction
from mit_core.vm_data import Register
from mit_core.instruction_gen import pop_stack_type


@unique
class LibcLib(AbstractInstruction):
    ARGC = (0x0, [], ['argc'], '''\
        argc = S->main_argc;
    ''')

    ARG = (0x1, ['u'], ['arg:char *'], '''\
        arg = S->main_argv[u];
    ''')

    EXIT = (0x2, ['ret_code'], [], '''\
        exit(ret_code);
    ''')

    STRLEN = (0x3, ['s:const char *'], ['len'], '''\
        len = (mit_word)(mit_uword)strlen(s);
    ''')

    STRNCPY = (0x4, ['dest:char *', 'src:const char *', 'n'], ['ret:char *'], '''\
        ret = strncpy(dest, src, (size_t)n);
    ''')

    STDIN = (0x5, [], ['fd:int'], '''\
        fd = (mit_word)STDIN_FILENO;
    ''')

    STDOUT = (0x6, [], ['fd:int'], '''\
        fd = (mit_word)STDOUT_FILENO;
    ''')

    STDERR = (0x7, [], ['fd:int'], '''\
        fd = (mit_word)STDERR_FILENO;
    ''')

    O_RDONLY = (0x8, [], ['flag'], '''\
        flag = (mit_word)O_RDONLY;
    ''')

    O_WRONLY = (0x9, [], ['flag'], '''\
        flag = (mit_word)O_WRONLY;
    ''')

    O_RDWR = (0xa, [], ['flag'], '''\
        flag = (mit_word)O_RDWR;
    ''')

    O_CREAT = (0xb, [], ['flag'], '''\
        flag = (mit_word)O_CREAT;
    ''')

    O_TRUNC = (0xc, [], ['flag'], '''\
        flag = (mit_word)O_TRUNC;
    ''')

    OPEN = (0xd, ['str', 'flags'], ['fd:int'], '''\
        {
            char *s = (char *)mit_native_address_of_range(S, str, 0);
            fd = s ? open(s, flags, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH | S_IWOTH) : -1;
            set_binary_mode(fd, O_BINARY); // Best effort
        }
    ''')

    CLOSE = (0xe, ['fd:int'], ['ret:int'], '''\
        ret = (mit_word)close(fd);
    ''')

    READ = (0xf, ['buf', 'nbytes', 'fd:int'], ['nread:int'], '''\
        {
            nread = -1;
            uint8_t *ptr = mit_native_address_of_range(S, buf, nbytes);
            if (ptr)
                nread = read(fd, ptr, nbytes);
        }
    ''')

    WRITE = (0x10, ['buf', 'nbytes', 'fd:int'], ['nwritten'], '''\
        {
            nwritten = -1;
            uint8_t *ptr = mit_native_address_of_range(S, buf, nbytes);
            if (ptr)
                nwritten = write(fd, ptr, nbytes);
        }
    ''')

    SEEK_SET = (0x11, [], ['whence'], '''\
        whence = (mit_word)SEEK_SET;
    ''')

    SEEK_CUR = (0x12, [], ['whence'], '''\
        whence = (mit_word)SEEK_CUR;
    ''')

    SEEK_END = (0x13, [], ['whence'], '''\
        whence = (mit_word)SEEK_END;
    ''')

    LSEEK = (0x14, ['fd:int', 'offset:off_t', 'whence'], ['pos:off_t'], '''\
        pos = lseek(fd, offset, whence);
    ''')

    FDATASYNC = (0x15, ['fd:int'], ['ret:int'], '''\
        ret = fdatasync(fd);
    ''')

    RENAME = (0x16, ['old_name', 'new_name'], ['ret:int'], '''\
        {
            char *s1 = (char *)mit_native_address_of_range(S, old_name, 0);
            char *s2 = (char *)mit_native_address_of_range(S, new_name, 0);
            if (s1 == NULL || s2 == NULL)
                RAISE(MIT_ERROR_INVALID_MEMORY_READ);
            ret = rename(s1, s2);
        }
    ''')

    REMOVE = (0x17, ['name'], ['ret:int'], '''\
        {
            char *s = (char *)mit_native_address_of_range(S, name, 0);
            if (s == NULL)
                RAISE(MIT_ERROR_INVALID_MEMORY_READ);
            ret = remove(s);
        }
    ''')

    # FIXME: Expose stat(2). This requires struct mapping!
    FILE_SIZE = (0x18, ['fd:int'], ['size:off_t', 'ret:int'], '''\
        {
            struct stat st;
            ret = fstat(fd, &st);
            size = st.st_size;
        }
    ''')

    RESIZE_FILE = (0x19, ['size:off_t', 'fd:int'], ['ret:int'], '''\
        ret = ftruncate(fd, size);
    ''')

    FILE_STATUS = (0x1a, ['fd:int'], ['mode:mode_t', 'ret:int'], '''\
        {
            struct stat st;
            ret = fstat(fd, &st);
            mode = st.st_mode;
        }
    ''')

mit_lib = {
    'CURRENT_STATE': (0x0, [], ['state:mit_state *'], '''\
        state = S;
    '''),

    'NATIVE_ADDRESS_OF_RANGE': (0x1, ['addr', 'len', 'inner_state:mit_state *'], ['ptr:uint8_t *'], '''\
        ptr = mit_native_address_of_range(inner_state, addr, len);
    '''),

    'LOAD': (0x2, ['addr', 'size', 'inner_state:mit_state *'], ['value', 'ret:int'], '''\
        value = 0;
        ret = load(inner_state, addr, size, &value);
    '''),

    'STORE': (0x3, ['value', 'addr', 'size', 'inner_state:mit_state *'], ['ret:int'], '''\
        ret = store(inner_state, addr, size, value);
    '''),

    'INIT': (0x4, ['memory_size', 'stack_size'], ['new_state:mit_state *'], '''\
        new_state = mit_init((size_t)memory_size, (size_t)stack_size);
    '''),

    'REALLOC_MEMORY': (0x5, ['u', 'inner_state:mit_state *'], ['ret:int'], '''\
        ret = mit_realloc_memory(inner_state, (size_t)u);
    '''),

    'REALLOC_STACK': (0x6, ['u', 'inner_state:mit_state *'], ['ret:int'], '''\
        ret = mit_realloc_stack(inner_state, (size_t)u);
    '''),

    'DESTROY': (0x7, ['inner_state:mit_state *'], [], '''\
        mit_destroy(inner_state);
    '''),

    'RUN': (0x8, ['inner_state:mit_state *'], ['ret'], '''\
        ret = mit_run(inner_state);
    '''),

    'SINGLE_STEP': (0x9, ['inner_state:mit_state *'], ['ret'], '''\
        ret = mit_single_step(inner_state);
    '''),

    'LOAD_OBJECT': (0xa, ['fd:int', 'addr', 'inner_state:mit_state *'], ['ret:int'], '''\
        ret = mit_load_object(inner_state, addr, fd);
    '''),

    'SAVE_OBJECT': (0xb, ['fd:int', 'addr', 'len', 'inner_state:mit_state *'], ['ret:int'], '''\
        ret = mit_save_object(inner_state, addr, len, fd);
    '''),

    'REGISTER_ARGS': (0xc, ['argv:char **', 'argc:int', 'inner_state:mit_state *'], ['ret:int'], '''\
        ret = mit_register_args(inner_state, argc, argv);
    '''),
}

for register in Register:
    mit_lib['GET_{}'.format(register.name.upper())] = (
        len(mit_lib), None, None, '''\
    mit_state *inner_state;
{}
    push_stack(S, mit_get_{}(inner_state));
'''.format(pop_stack_type('inner_state', 'mit_state *'),
           register.name))
    mit_lib['SET_{}'.format(register.name.upper())] = (
        len(mit_lib), None, None, '''\
    mit_state *inner_state;
{}
    mit_word value;
    int ret = pop_stack(S, &value);
    if (ret != 0)
        RAISE(ret);
    mit_set_{}(inner_state, value);
'''.format(pop_stack_type('inner_state', 'mit_state *'),
           register.name))

MitLib = AbstractInstruction('MitLib', mit_lib)

class Library(AbstractInstruction):
    '''Wrap an Instruction enumeration as a library.'''
    def __init__(self, opcode, library, includes):
        super().__init__(opcode, None, None, '''\
{{
    mit_word function;
    int ret = pop_stack(S, &function);
    if (ret != 0)
        RAISE(ret);
    ret = extra_{}(S, function);
    if (ret != 0)
        RAISE(ret);
}}''')
        self.library = library
        self.includes = includes

    @staticmethod
    def _item_type(name_and_type):
        l = name_and_type.split(':')
        return l[1] if len(l) > 1 else 'mit_word'

    def types(self):
        '''Return a list of all types used in the library.'''
        return list(set(
            [self._item_type(item)
             for function in self.library
             if function.args is not None or function.results is not None
             for item in function.args + function.results
            ]
        ))

@unique
class LibInstruction(Library):
    '''VM instruction instructions to access external libraries.'''
    LIB_MIT = (0x01, MitLib, '''\
#include "mit/mit.h"
#include "mit/features.h"
''')
    LIB_C = (0x02, LibcLib, '''\
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include "binary-io.h"
''')

# Inject name into each library's code
for instruction in LibInstruction:
    instruction.code = instruction.code.format(str.lower(instruction.name))