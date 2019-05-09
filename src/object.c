// Load and save object files.
//
// (c) Mit authors 1995-2019
//
// The package is distributed under the MIT/X11 License.
//
// THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
// RISK.

#include "config.h"

#include <unistd.h>
#include <string.h>

#include "mit/mit.h"


#define HEADER_LENGTH 8
#define HEADER_MAGIC "MIT\0\0"

ptrdiff_t mit_load_object(mit_state *S, mit_UWORD addr, int fd)
{
    // Skip any #! header
    char buf[sizeof("#!") - 1];
    ssize_t res;
    if ((res = read(fd, &buf[0], sizeof(buf))) == -1)
        return -1;
    else if (res != (ssize_t)sizeof(buf))
        return -2;
    size_t nread = 2;
    if (buf[0] == '#' && buf[1] == '!') {
        char eol[1];
        do {
            res = read(fd, &eol[0], 1);
        } while (res == 1 && eol[0] != '\n');
        if (res == -1)
            return -1;
        nread = 0;
    }

    // Read and check header
    char header[HEADER_LENGTH] = {'\0'};
    mit_UWORD endism;
    mit_UWORD _WORD_BYTES;
    memcpy(header, buf, nread);
    if ((res = read(fd, &header[nread], sizeof(header) - nread)) == -1)
        return -1;
    if (res != (ssize_t)(sizeof(header) - nread) ||
        memcmp(header, HEADER_MAGIC, sizeof(HEADER_MAGIC)) ||
        (endism = header[sizeof(HEADER_MAGIC)]) > 1)
        return -2;
    if (endism != ENDISM ||
        (_WORD_BYTES = header[sizeof(HEADER_MAGIC) + 1]) != WORD_BYTES)
        return -3;

    // Read and check size, and ensure code will fit in memory
    mit_UWORD len = 0;
    if ((res = read(fd, &len, sizeof(len))) == -1)
        return -1;
    if (ENDISM != HOST_ENDISM)
        len = reverse_endianness(mit_WORD_BIT, len);
    if (res != sizeof(len))
        return -2;
    uint8_t *ptr = mit_native_address_of_range(S, addr, len);
    if (ptr == NULL || !is_aligned(addr, mit_SIZE_WORD))
        return -4;

    // Read code
    if ((res = read(fd, ptr, len)) == -1)
        return -1;
    else if (res != (ssize_t)len)
        return -2;

    return (ssize_t)len;
}

int mit_save_object(mit_state *S, mit_UWORD addr, mit_UWORD len, int fd)
{
    uint8_t *ptr = mit_native_address_of_range(S, addr, len);
    if (!is_aligned(addr, mit_SIZE_WORD) || ptr == NULL)
        return -2;

    mit_BYTE buf[HEADER_LENGTH] = HEADER_MAGIC;
    buf[sizeof(HEADER_MAGIC)] = ENDISM;
    buf[sizeof(HEADER_MAGIC) + 1] = WORD_BYTES;

    mit_UWORD len_save = len;
    if (ENDISM != HOST_ENDISM)
        len_save = reverse_endianness(mit_WORD_BIT, len_save);

    if (write(fd, &buf[0], HEADER_LENGTH) != HEADER_LENGTH ||
        write(fd, &len_save, sizeof(len_save)) != sizeof(len_save) ||
        write(fd, ptr, len) != (ssize_t)len)
        return -1;

    return 0;
}
