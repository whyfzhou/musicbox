#!/usr/bin/env python3

import functools
import subprocess
import os
import curses


def putsc(s, stdscr):
    stdscr.clear()
    total_rows, total_columns = stdscr.getmaxyx()
    if len(s) <= total_columns:
        row = total_rows // 2 - 1
        col = (total_columns - len(s)) // 2 - 1
        if col < 0:
            col = 0
        stdscr.addstr(row, col, s)
    elif ' ' in s or '-' in s:
        words = functools.reduce(
            lambda a, b: a + b,
            [[s3 + '-' if not (s2.endswith(s3) or len(s2.split('-')) == 1) else s3
              for s3 in (s2 + ' ' if not s.endswith(s2) else s2).split('-')]
             for s2 in s.split()]
        )
        lines = []
        j = 0
        for k, _ in enumerate(words[:-1]):
            s1 = '' .join(words[j:k+1])
            s2 = '' .join(words[j:k+2])
            if len(s2) <total_columns:
                continue
            lines.append(s1)
            j = k + 1
        if j < len(words):
            lines.append(''.join(words[j:]))
        if len(lines) > total_rows:
            lines = lines[:total_rows]
        row = (total_rows - len(lines)) // 2 - 1
        if row < 0:
            row = 0
        for line in lines:
            col = (total_columns - len(line)) // 2 - 1
            if col < 0:
                col = 0
            stdscr.addstr(row, col, line)
            row += 1


def get_file_names(list_name, n):
    li = []
    for _, _, files in os.walk(os.path.join(os.curdir, 'music', list_name)):
        for f in files:
            if os.path.splitext(f)[-1].lower().endswith('mp3'):
                li.append(os.path.abspath(os.path.join(os.curdir, 'music', list_name, f)))
    # print(f'{n} of {len(li)} returned')
    return li[:n]


def get_list():
    daddy_keys = ['KEY_HOME', 'KEY_UP', 'KEY_PPAGE',
        'KEY_LEFT', 'KEY_RIGHT',
        'KEY_END', 'KEY_DOWN', 'KEY_NPAGE',
        'KEY_IC', 'KEY_DC']
    mommy_keys = ['/', '*', 'KEY_BACKSPACE',
        '7', '8', '9', '-',
        '4', '5', '6', '+',
        '1', '2', '3', '\n'
        '0', '.']
    daddy_list = get_file_names('Daddy', 10)
    mommy_list = get_file_names('Mommy', 17)
    return {k: v for k, v in zip(daddy_keys + mommy_keys, daddy_list + mommy_list)}


def play(file):
    # player = subprocess.Popen(['omxplayer', '-o', 'local', '-b', '--vol', '-1000', file],
    #     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    player = subprocess.Popen(['omxplayer', '-o', 'local', file],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    return player


def stop(player):
    try:
        player.stdin.write(b'q')
        player.stdin.flush()
    except:
        pass
    player.terminate()


def main(stdscr):
    playlist = get_list()

    putsc('MUSIC BOX (press "q" to quit)', stdscr)

    PASSWORD = '3.14159265358979323846'
    key_sequence = []
    player = None
    playing = None
    while True:
        c =  stdscr.getkey()
        key_sequence.insert(0, c)
        if len(key_sequence) > len(PASSWORD):
            key_sequence.pop()
        if c == 'q' or c == 'Q' or PASSWORD == ''.join(key_sequence[::-1]):
            if player is not None:
                stop(player)
            break

        song = playlist.get(c, '')
        if song and (player is not None and player.poll() is not None or c != playing):
            if player is not None:
                stop(player)
            player = play(song)
            playing = c

        title = os.path.splitext(os.path.basename(song))[0]
        putsc(title, stdscr)


if __name__ == '__main__':
    curses.wrapper(main)
