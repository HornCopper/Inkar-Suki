import sys
import os

<<<<<<< HEAD
if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 1:
        token = 'invalid'
    else:
        [runner, token] = sys.argv
=======

def replacer(raw: str, target_field: str, value: str) -> str:
    return raw.replace(f'{target_field} = ""', f'{target_field} = "{value}"')


if __name__ == '__main__':
    argv = sys.argv
    expected_args_count = 4
    if len(argv) < expected_args_count:
        params = ['invalid'] * (expected_args_count + 1)
    else:
        params = sys.argv

    [
        runner,
        token,
        jx3api_link,
        sfapi_wslink,
        sfapi_wstoken,
    ] = params

>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    target_path = f'src{os.sep}tools{os.sep}'
    target_src_config = f'{target_path}config.sample.py'
    target_config = f'{target_path}config.py'
    with open(target_src_config, 'r', encoding='utf-8') as f:
        data = f.read()
<<<<<<< HEAD
        data = data.replace('jx3_token = ""', f'jx3_token = "{token}"')
=======
        data = replacer(data, 'jx3_token', token)
        data = replacer(data, 'jx3api_link', jx3api_link)
        data = replacer(data, 'sfapi_wslink', sfapi_wslink)
        data = replacer(data, 'sfapi_wstoken', sfapi_wstoken)

>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    with open(target_config, 'w', encoding='utf-8') as f:
        f.write(data)
