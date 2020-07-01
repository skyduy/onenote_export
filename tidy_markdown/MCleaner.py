import os
import re
import glob
import shutil

WORK_DIR = os.path.abspath(os.path.dirname(__file__))


class MarkdownManager:
    """
    危险：如果目标目录和原来的目录一直，且原来目录中存在其他文件，也将一并删除
    """

    def __init__(self, rewrite_to, relative_assets='assets/{filename}'):
        if os.path.isabs(rewrite_to):
            self.rewrite_to = rewrite_to
        else:
            self.rewrite_to = os.path.join(WORK_DIR, rewrite_to)
        if os.path.exists(self.rewrite_to):
            print('重写文件存放目录: {} 已存在，删除它？'.format(self.rewrite_to))
            if input('') == 'yes':
                shutil.rmtree(self.rewrite_to)
            else:
                exit(1)
        os.makedirs(self.rewrite_to)
        self.relative_asset_path = relative_assets

        self.p1 = re.compile(r'\[[^\]]*\]\((.*?)\s*("(?:.*[^"])")?\s*\)')
        self.p2 = re.compile('src=[\'\"]?([^\'\"]*)[\'\"]')

    def _parse_markdown_location(self, fn):
        abspath = os.path.abspath(fn)
        if not (abspath.startswith(WORK_DIR) and os.path.exists(fn) and fn.endswith('.md')):
            print('只能管理同级目录或子目录下的markdown文件')
            exit(1)
        markdown_path = os.path.join(self.rewrite_to, abspath[len(WORK_DIR):].lstrip('/'))
        markdown_folder, markdown_fn = os.path.split(markdown_path)
        if not os.path.exists(markdown_folder):
            os.makedirs(markdown_folder)

        markdown_fn = markdown_fn.rstrip('.md')
        asset_folder = os.path.join(markdown_folder,
                                    self.relative_asset_path.format(filename=markdown_fn))
        return markdown_path, asset_folder

    def refactor_line(self, md_file, line, asset_folder):
        md_folder, md_name = os.path.split(os.path.abspath(md_file))
        raw_urls = []
        for item in self.p1.findall(line):
            if not item[0].startswith('http') and not item[0].startswith('onenote'):
                raw_urls.append(item[0])
        for item in self.p2.findall(line):
            if not item.startswith('http') and not item.startswith('onenote'):
                raw_urls.append(item)

        if raw_urls:
            if not os.path.exists(asset_folder):
                os.makedirs(asset_folder)
        for raw_url in raw_urls:
            media_name = os.path.split(raw_url)[1]
            new_media_path = os.path.join(asset_folder, media_name)
            if not os.path.isabs(raw_url):
                old_media_path = os.path.join(md_folder, raw_url)
            else:
                old_media_path = raw_url
            shutil.copy(old_media_path, new_media_path)

            new_url_folder = self.relative_asset_path.format(filename=md_name.rstrip('.md'))
            new_url = os.path.join(new_url_folder, media_name)
            line = line.replace(raw_url, new_url)
        return line

    def refactor(self, md_file):
        new_file, asset_new_folder = self._parse_markdown_location(md_file)
        with open(md_file) as rf:
            with open(new_file, 'w') as wf:
                for line in rf:
                    line = line.replace('\\', '')
                    line = self.refactor_line(md_file, line, asset_new_folder)
                    wf.write(line)


if __name__ == '__main__':
    # 第一个参数是将新生成的文件放在哪个目录下
    # 第二个参数是图片放置到相对于markdown文件的哪个位置下
    manager = MarkdownManager('_rewrite', 'assets/{filename}')
    for fn in glob.glob('./**/*.md', recursive=True):
        print('Refactor {} to {}'.format(fn, manager.rewrite_to))
        manager.refactor(fn)
