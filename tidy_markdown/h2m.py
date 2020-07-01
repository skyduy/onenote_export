import os
import glob
import collections
import shutil
import subprocess


def copy_image_out():
    c = collections.Counter()
    for fn in glob.glob("./**/*", recursive=True):
        fn_l = fn.split('/')
        if fn_l[-2] != 'images':
            continue
        del fn_l[-3]
        folder = '/'.join(fn_l[:-1])
        if not os.path.exists(folder):
            os.makedirs(folder)
        dst = os.path.join(folder, fn_l[-1])
        # shutil.copy(fn, dst)
        c[dst] += 1
    print(c.most_common(2))


def process_line_feed():
    for src in glob.glob('./**/*.html', recursive=True):
        with open(src) as f:
            with open(src+'.html', 'w') as wf:
                print(src)
                for line in f:
                    line = line.replace('&#10;', '')
                    wf.write(line)


def html2markdown():
    for src in glob.glob('./**/*.html.html', recursive=True):
        dst_l = src.rsplit('/')[:-1]
        dst_l[-1] = dst_l[-1].split(' ', 1)[1]
        dst = '/'.join(dst_l) + '.md'
        subprocess.check_output('pandoc --wrap=preserve -f html-escaped_line_breaks-native_divs-native_spans -t markdown "{}" -o "{}"'.format(src, dst), shell=True)
        print(dst)


if __name__ == '__main__':
    process_line_feed()
    html2markdown()
