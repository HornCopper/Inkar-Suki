import sys
import os


def replacer(raw: str, target_field: str, value: str) -> str:
    return raw.replace(f'{target_field} = ""', f'{target_field} = "{value}"')


if __name__ == '__main__':
    argv = sys.argv
    expected_args_count = 5
    if len(argv) < expected_args_count:
        params = ['invalid'] * expected_args_count
    else:
        params = sys.argv

    [
        runner,
        token,
        jx3api_link,
        sfapi_wslink,
        sfapi_wstoken,
    ] = params

    target_path = f'src{os.sep}tools{os.sep}'
    target_src_config = f'{target_path}config.sample.py'
    target_config = f'{target_path}config.py'
    with open(target_src_config, 'r', encoding='utf-8') as f:
        data = f.read()
        data = replacer(data, 'jx3_token', token)
        data = replacer(data, 'jx3api_link', jx3api_link)
        data = replacer(data, 'jx3api_link', jx3api_link)
        data = replacer(data, 'sfapi_wslink', sfapi_wslink)
        data = replacer(data, 'sfapi_wstoken', sfapi_wstoken)

    with open(target_config, 'w', encoding='utf-8') as f:
        f.write(data)
