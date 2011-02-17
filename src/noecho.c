/* NOECHO.C

    (c) Martin Richards 2004 (and certainly earlier)
    (c) Reuben Thomas 1995-2011

    void init_keyb(void)  initialises the keyboard interface.
    void restore_keyb(void) restores the keyboard to its original state.

*/


#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <termios.h>


/* Use this variable to remember original terminal attributes */
static struct termios saved_stdin;

int init_keyb(void)
{
    struct termios tattr;

    if (!isatty(STDIN_FILENO)) return -1;

    /* Save the terminal attributes so we can restore them later */
    tcgetattr(STDIN_FILENO, &saved_stdin);

    /* Set the funny terminal modes */
    tcgetattr(STDIN_FILENO, &tattr);
    tattr.c_lflag &= ~(ICANON | ECHO);   /* Clear ICANON and ECHO */
    tattr.c_cc[VMIN] = 1;
    tattr.c_cc[VTIME] = 0;
    tcsetattr (STDIN_FILENO, TCSAFLUSH, &tattr);

    setbuf(stdout, NULL);

    return 0;
}

int restore_keyb(void)
{
    tcsetattr(STDIN_FILENO, TCSANOW, &saved_stdin);
    return 0;
}
