import sys
import os
if __name__ == '__main__':
    [token] = sys.argv
    target_path = f'src{os.sep}tools{os.sep}'
    target_src_config = f'{target_path}config.sample.py'
    target_config = f'{target_path}config.py'
    with open(target_src_config, 'r', encoding='utf-8') as f:
        data = f.read()
        data = data.replace('jx3_token = ""', f'jx3_token = "{token}"')
